import time, csv
from threading import Thread
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler,HTTPServer
PORT_NUMBER = 8082


import asyncio
import websockets


CLIENTS = set()

async def handler(websocket):
    CLIENTS.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        CLIENTS.remove(websocket)


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever
        
        


def requestHandler_index(message):
    return "Options are 'say', 'color', and 'anim'!"


def requestHandler_say(message):
    global CLIENTS

    
    with open('swearWords.csv') as swearWords_file:
        swearWords = list(csv.reader(swearWords_file, delimiter=','))[0]
        
        
        
        for word in swearWords:
            if message.find(" " + word + " ") != -1:
                return "Sorry, your message contained a banned word!"
    
    if len(message) > 200:
        return "Messages are limited to 200 characters!  Please try again."
    else:
        websockets.broadcast(CLIENTS, """{"messagetype": "say", "message": """" + message + """"}""")
                             
        return "Saying: {msg}".format(msg = message)
        
    
    



httpRequests = {''      : requestHandler_index,
                'say'   : requestHandler_say,
				}

class myHandler(BaseHTTPRequestHandler):
	
	#Handler for the GET requests
    def do_GET(self):
        jam = urlparse(self.path)
        elements = parse_qs(jam.query)
        if len(elements) > 0:
            body = elements['Body'][0]
            
            print ("body: ", body)
            
            messageType = body.split(" ")[0]
            message = body.split(" ", 1)[1]
            
            print ("messageType: ", messageType)
            print ("message: ", message)

            responseFound = False
            for httpRequest, httpHandler in httpRequests.items():
                if messageType == httpRequest: # in other words, if the first part matches
                    response = httpHandler(message)
                    responseFound = True

            if not responseFound:
                response = requestHandler_index(message)

            self.send_response(200)
            self.send_header('Content-type', "text/plain")
            self.end_headers()
            self.wfile.write(bytes(response, "utf-8"))
			
        return


def httpRun():
    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print('Started httpserver on port ' , PORT_NUMBER)

    server.serve_forever()
    

    


if __name__ == "__main__":
    httpRunThread = Thread(target=httpRun)
    httpRunThread.daemon = True
    httpRunThread.start()
    
    asyncio.run(main())

    while True:
        time.sleep(0.1)
        
        
        

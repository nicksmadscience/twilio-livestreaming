import time, csv, os.path
from threading import Thread
from urllib.parse import urlparse, parse_qsl
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
        

def bannedNumber(number):
    if os.path.exists("banlist.txt"):
        with open("banlist.txt", "r") as banlist_file:
            if number in banlist_file.read():
                return True
    return False


def log(event):
    if not os.path.exists("log.csv"):
        with open("log.csv", "w") as log_file:
            logwriter = csv.writer(log_file)
            logwriter.writerow(event.keys())
        
    with open("log.csv", "a") as log_file:
        logwriter = csv.writer(log_file)
        logwriter.writerow(event.values())


def requestHandler_index(message):
    return "Options are 'Say', 'Color', and 'Effect'!"


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
        websockets.broadcast(CLIENTS, "{\"messagetype\": \"say\", \"message\": \"" + message + "\"}")
                             
        return "Saying: {msg}".format(msg = message)
    
    
def requestHandler_color(message):
    global CLIENTS
    
    websockets.broadcast(CLIENTS, "{\"messagetype\": \"color\", \"message\": \"" + message + "\"}")
    
    return "Changed color to {color}".format(color = message)



def requestHandler_effect(message):
    global CLIENTS
    
    if message in ["fireworks", "snow", "warpspeed", "yahoo"]:
        websockets.broadcast(CLIENTS, "{\"messagetype\": \"effect\", \"message\": \"" + message + "\"}")
        return "Playing " + message
    else:
        return "Possible effects are: fireworks, snow, warpspeed, and yahoo"
        
    
    



httpRequests = {''      : requestHandler_index,
                'Say'   : requestHandler_say,
                'Color' : requestHandler_color,
                'Effect': requestHandler_effect,
				}

class myHandler(BaseHTTPRequestHandler):
	
	#Handler for the GET requests
    def do_GET(self):
        jam = urlparse(self.path)
        elements = dict(parse_qsl(jam.query))
        log(elements)
        if len(elements) > 0:
            
            if bannedNumber(elements['From']):
                response = "You have been banned from this service."
                
            else:
                body = elements['Body']
                
                messageType = body.split(" ")[0]
                message = body.split(" ", 1)[1]

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
        
        
        

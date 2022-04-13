
import time
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
        
        


def requestHandler_index():
    global CLIENTS
    
    websockets.broadcast(CLIENTS, '{"messagetype": "test", "payload": "roffle"}')
    
    return "Hello"



httpRequests = {''      : requestHandler_index
				}

class myHandler(BaseHTTPRequestHandler):
	
	#Handler for the GET requests
    def do_GET(self):
        jam = urlparse(self.path)
        elements = parse_qs(jam.query)
        body = elements['Body']

        responseFound = False
        for httpRequest, httpHandler in httpRequests.items():
            if body == httpRequest: # in other words, if the first part matches
                response = httpHandler()
                responseFound = True

        if not responseFound:
            response = requestHandler_index()

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
        
        
        

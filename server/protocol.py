from autobahn.websocket import (WebSocketServerFactory,
                                WebSocketServerProtocol,
                                )
                                

import hashlib, json, datetime

def generateId():
    m = hashlib.md5()
    m.update(datetime.datetime.now().isoformat(' '))
    return m.hexdigest()


class MMFEServerProtocol(WebSocketServerProcol):
    '''
    Basic protocol for each client connection to this server.
    On connection, sends the client it's id, and the current state
    of the game. 
    '''

    def onOpen(self):
        self.id = self.factory.register(self)
        data = {
                'id' : self.id,
                'state' : {}
                }
        self.sendMessage(json.dumps(data))

    def connectionLost(self, reason):
        super(self, WebSocketServerProtocol).connectionLost(self, reason)
        self.factory.unregister(self.id)

class MMFEServer(WebSocketServerFactory):

    def __init__(self, url, debug=False, debugCodePaths=False):
        super(self, WebSocketServerFactory).__init__(self, url, debug=debug, debugCodePaths=debugCodePaths)
        self.clients = {}

    def register(self, client):
        while True:
            i = generateId()
            if i not in self.clients:
                self.clients[i] = client
                return i

    def unregister(self, clientId):
        if clientId in self.clients:
            self.clients.pop(clientId)

    def broadcast(self, payload):
        if type(payload, dict):
            msg = json.dumps(payload)
        else:
            msg = payload

        for cl in self.clients.values():
            cl.sendMessage(msg)

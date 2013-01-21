import datetime, hashlib, json, random, string
from autobahn.websocket import (WebSocketServerFactory,
                                WebSocketServerProtocol,
                                listenWS
                                )
from twisted.internet import reactor
                                


def generateId():
    m = hashlib.md5()
    m.update(datetime.datetime.now().isoformat(' '))
    return m.hexdigest()


class MMFEServerProtocol(WebSocketServerProtocol):
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
        self.factory.broadcast('HELLO!!!!')
        self.send_new_label()

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self.id)

    def send_new_label(self):
        new_label = ''.join([random.choice(string.letters) for i in xrange(1, 20)])
        print 'broadcasting a new label: %s' % new_label
        self.sendMessage({'label': new_label})
        reactor.callLater(1, self.send_new_label)

    def sendMessage(self, payload, binary=False):
        if isinstance(payload, dict) and not binary:
            msg = json.dumps(payload)
        else:
            msg = json.dumps({'message': payload})

        WebSocketServerProtocol.sendMessage(self, msg, binary=binary)

class MMFEServer(WebSocketServerFactory):

    def __init__(self, url, debug=False, debugCodePaths=False):
        WebSocketServerFactory.__init__(self, url, debug=debug, debugCodePaths=debugCodePaths)
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
        if isinstance(payload, dict):
            msg = json.dumps(payload)
        else:
            msg = json.dumps({'message' : payload})

        for cl in self.clients.values():
            cl.sendMessage(msg)

if __name__ == '__main__':
    factory = MMFEServer("ws://localhost:9000", debug=False)
    factory.protocol = MMFEServerProtocol
    listenWS(factory)
       
    reactor.run()


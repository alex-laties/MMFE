import json
from autobahn.websocket import WebSocketClientProtocol, WebSocketClientFactory
from twisted.internet import reactor

class MMFEClientProtocol(WebSocketClientProtocol):
    def __init__(self, *args, **kwargs):
        self.id = None

    def pull_recv_queue(self):
        if not self.factory.recvQ.empty():
            todo = self.factory.recvQ.get()
            self.sendMessage(json.dumps(todo))
        reactor.callLater(1, self.pull_recv_queue)

    def onMessage(self, msg, binary):
        data = json.loads(msg)
        print data
        if not self.factory.sendQ.full():
            self.factory.sendQ.put(data)

class MMFEClient(WebSocketClientFactory):
    def __init__(self, recvQ=None, sendQ=None, *args, **kwargs):
        WebSocketClientFactory.__init__(self, *args, **kwargs)
        self.recvQ = recvQ
        self.sendQ = sendQ

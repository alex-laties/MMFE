from autobahn.websocket import WebSocketClientFactory, connectWS
from client.protocol import MMFEClientProtocol, MMFEClient
from multiprocessing import Pipe, Process, Queue
from pyglet import app, text, window
from time import sleep
from twisted.internet import reactor

def main():
    sendQ = Queue()
    recvQ = Queue()
    #setup net stack
    factory = MMFEClient(recvQ=sendQ, sendQ=recvQ, url="ws://localhost:9000", debug=False)
    factory.protocol = MMFEClientProtocol
    connectWS(factory)
    net = Process(target=reactor.run)

    #setup game stack
    game_window = window.Window()
    label = text.Label('Hello, world', font_name='Arial', font_size=16, x=game_window.width//2, y=game_window.height//2, anchor_x='center', anchor_y='center')
    @game_window.event
    def on_draw():
        game_window.clear()
        label.draw()
        if not recvQ.empty():
            data = recvQ.get()
            if 'label' in data:
                label.text = data['label']

    net.start()
    app.run()

if __name__ == "__main__":
    main()

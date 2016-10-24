from .exceptions import *
from zashel.basehandler import BaseHandler

class WebSocketBaseHandler(BaseHandler):

    @property
    def is_websocket_connected(self):
        return "websocket" in self._connected_stuff
        
    def websocket_connect(self, websocket):
        self.connect_stuff(websocket=websocket) 

    def handle(self, signal, addr):
        if self.is_websocket_connected:
            try:
                self.get_signal(signal.action)(signal, addr)
            except KeyError:
                pass
        else:
            raise WebsocketNotConnectedError()

    #Signals        
    def signal_bye(self, signal, addr):
        self._close_connection(addr)

    def signal_message(self, signal, addr):
        print(signal.text) # Implement it yourself

    def signal_ping(self, signal, addr):
        pass

    def signal_pong(self, signal, addr):
        pass
        

from . import WebSocket
from .exceptions import *
from zashel.basehandler import BaseHandler

class WebSocketBaseHandler(BaseHandler):

    @property
    def is_websocket_connected(self):
        return "websocket" in self._connected_stuff
        
    def connect_websocket(self, websocket):
        if isinstance(websocket, WebSocket):
            self.connect_stuff(websocket=websocket)
        else:
            raise WebSocketError()

    #Signals        
    def signal_bye(self, signal, addr):
        self._close_connection(addr)

    def signal_message(self, signal, addr):
        print(signal.text) # Implement it yourself

    def signal_ping(self, signal, addr):
        pass

    def signal_pong(self, signal, addr):
        pass
        

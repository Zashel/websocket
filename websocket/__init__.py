from .exceptions import *
from .signals import *
from .handler import *
from zashel.utils import search_win_drive, daemonize
import base64
import http.client
import hashlib
import io
import random
import re
import socket
import struct
import time

DEFAULT_BUFFER = 4096
DEFAULT_LISTENING = 10
DEFAULT_TIMEOUT = 300

BUFFER = DEFAULT_BUFFER
LISTENING = DEFAULT_LISTENING
PAYLOAD_OFFSET = 6
TIMEOUT = DEFAULT_TIMEOUT

class WebSocket(object):
    '''A WebSocket like the HTML5 homonim.
    '''
    def __init__(self, conn_tuple, handler):
        '''It creates a WebSocket to play with the HTML5 homonim.

        conn_tuple: as in socket.socket, a tuple with the IP and the port.
        handler: a WebSocketBaseHandler.
         default, to play with.
        '''
        self._connections = dict()
        self._socket = socket.socket()
        assert isinstance(conn_tuple, tuple) or isinstance(conn_tuple, list)
        assert len(conn_tuple)==2
        addr, port = conn_tuple
        port = int(port) #Chapuza
        assert isinstance(addr, str)
        assert isinstance(port, int)
        self.socket.bind((addr ,port))
        self._port = port
        self._handler = handler
        self._handler.connect_websocket(self)
        self._pongs = dict()

    def __del__(self):
        '''Close all connections.
        '''
        for addr in self.connections:
            self._close_connection(addr)
        self.socket.close()        

    @property
    def connections(self):
        '''Connections property. Returns the dictionary.
        TODO: Aliases?
        '''
        return self._connections

    @property
    def handler(self):
        '''Returns the handler given at the instantiating.
        '''
        return self._handler

    @property
    def socket(self):
        '''Returns the socket associated.
        '''
        return self._socket

    @property
    def port(self):
        '''Returns the port of the socket.
        '''
        return self._port

    @daemonize
    def listen(self):
        '''Once it's instantiated, you may make it listen to connect
        and receive.
        '''
        self.socket.listen(LISTENING)
        while True:
            conn, addr = self.socket.accept()
            self.connections[addr] = conn
            response = conn.recv(1024)
            response = response.decode("utf-8").split("\r\n")
            self._send_accept(conn, response)
            self._get_answer(addr, conn)            

    @daemonize
    def _get_answer(self, addr, conn, buff=BUFFER):
        '''A daemon to receive data. Don't use it directly.
        '''
        conn.settimeout(TIMEOUT) #This way always closes
        while True:
            try:
                received = from_json(self.decode(conn.recv(buff)))
                self.handler.handle(received, addr)
                if isinstance(received, PongSignal):
                    self._pongs[addr] = received
            except RecievedNotString as error:
                if error.type == 8:
                    self._close_connection(addr, conn)
                    print("Closing {}".format(addr))
                    break
                else:
                    raise error
            except socket.timeout:
                if self._is_alive(addr, conn) is not True:
                    break

    def _close_connection(self, addr, conn=None):
        '''To close a connection giving an address.
        Do I make it "public"?
        '''
        if conn is None:
            conn = self._connections[addr]
        self.send(ByeSignal(), conn)
        conn.close()
        del(self.connections[addr])

    def _is_alive(self, addr, conn):
        '''Checks a connection is alive and closes it otherwise.
        '''
        self.send(PingSignal(), conn)
        received = None
        for t in range(20):
            if addr in self._pongs:
                received = self._pongs[addr]
                del(self._pongs[addr])
                break
            time.sleep(1)
        if not isinstance(received, PongSignal):
            self._close_connection(addr, conn)
            return False
        else:
            return True

    def _send_accept(self, conn, response):
        '''Sends eh accept string to the websocket.
        '''
        headers = dict()
        for line in response:
            data = re.findall("([\w\W]+): ([\w\W]+)", line)
            if data != list(): 
                headers[data[0][0]]=data[0][1]
        key = headers["Sec-WebSocket-Key"]
        key = "".join((key, "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"))
        key = hashlib.sha1(bytes(key, "utf-8"))
        key = base64.b64encode(key.digest()).decode("utf-8")
        accept = "HTTP/1.1 101 Switching Protocols\r\n"
        accept = "".join((accept, "Upgrade: websocket\r\n"))
        accept = "".join((accept, "Connection: Upgrade\r\n"))
        accept = "".join((accept, "Sec-WebSocket-Accept: {}\r\n\r\n".format(key)))
        self.send(accept, conn)
        print("Acepted")

    def decode(self, message): # String messages first. Blob and ByteArray for another moment
        '''Decodes a received message.
        May it be "private"?
        '''
        first_byte = message[0]
        second_byte = message[1]
        message_type = first_byte & 0x0F
        masked = (first_byte & 128) == 128
        payload_length = second_byte & 0x7F
        if message_type != 1:
            raise RecievedNotString(message_type)
        if masked is not True:
            return message[2:].decode("utf-8")
        else:
            mask = list()
            for index in range(2, 6):
                mask.append(message[index])
            full_data_length = payload_length + PAYLOAD_OFFSET
            unmasked_message = list()
            for index in range(PAYLOAD_OFFSET, full_data_length):
                mask_index = (index - PAYLOAD_OFFSET)%4
                unmasked_message.append(message[index] ^ mask[mask_index])
            return bytes(unmasked_message).decode("utf-8")

    def send_all(self, data):
        '''Send a signal to all connected clients.
        '''
        addrs = [addr for addr in self.connections]
        for addr in addrs: # "for addr in self.connections" is a really bad idea
            conn = self.connections[addr]
            if self._is_alive(addr, conn) is True:
                self.send(data, self.connections[addr])

    def send(self, data, conn):
        '''Sends a signal to given connection.
        '''
        try:
            try:
                data = data.to_json()
            except:
                pass
            output = io.BytesIO()
            # Prepare the header
            head1 = 0b10000000
            head1 |= 0x01
            head2 = 0
            length = len(data)
            if length < 0x7e:
                output.write(struct.pack('!BB', head1, head2 | length))
            elif length < 0x10000:
                output.write(struct.pack('!BBH', head1, head2 | 126, length))
            else:
                output.write(struct.pack('!BBQ', head1, head2 | 127, length))
            data = bytes(data, "utf-8")
            output.write(data)
            conn.sendall(output.getvalue())
        except Exception:
            raise

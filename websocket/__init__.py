from .exceptions import *
from zashel.utils import search_win_drive, daemonize
from zashel.basehandler import BaseHandler
import base64
import http.client
import hashlib
import io
import re
import socket
import struct

DEFAULT_BUFFER = 4096
DEFAULT_LISTENING = 10
DEFAULT_TIMEOUT = 300

BUFFER = DEFAULT_BUFFER
LISTENING = DEFAULT_LISTENING
PAYLOAD_OFFSET = 6
TIMEOUT = DEFAULT_TIMEOUT

class WebSocket(object):
    def __init__(self, port, handler=BaseHandler()):
        self._socket = socket.socket()
        self.socket.bind(("",port))
        self.listen()
        self._connections = dict()
        self._port = port
        self._handler = handler

    def __del__(self):
        for addr in self.connections:
            self._close_connection(addr)
        self.socket.close()
        
    @property
    def connections(self):
        return self._connections

    @property
    def handler(self):
        return self._handler

    @property
    def socket(self):
        return self._socket

    @property
    def port(self):
        return self._port

    @daemonize
    def listen(self):
        self.socket.listen(LISTENING)
        while True:
            conn, addr = self.socket.accept()
            print(addr)
            self.connections[addr] = conn
            response = conn.recv(1024)
            response = response.decode("utf-8").split("\r\n")
            self._send_accept(conn, response)
            self.get_answer(addr, conn)
            
    @daemonize
    def get_answer(self, addr, conn, buff=BUFFER):
        conn.settimeout(TIMEOUT) #This way always closes
        while True:
            try:
                print(self.decode(conn.recv(buff))) #Handle Answer
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

    def _close_connection(self, addr, conn):
        self.send("Bye", conn, True) #Change to signal ByeSignal when written
        conn.close()
        del(self.connections[addr])

    def _is_alive(self, addr, conn):
        conn.send(PingSignal())
        conn.recv(buff)

    def _send_accept(self, conn, response):
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
        for data in message:
            print(data)
        

    def send(self, data, conn, mask=False):
        try:
            print(data)
            output = io.BytesIO()
            # Prepare the header
            head1 = 0b10000000
            head1 |= 0x01
            head2 = 0b10000000 if mask else 0
            length = len(data)
            if length < 0x7e:
                output.write(struct.pack('!BB', head1, head2 | length))
            elif length < 0x10000:
                output.write(struct.pack('!BBH', head1, head2 | 126, length))
            else:
                output.write(struct.pack('!BBQ', head1, head2 | 127, length))
            if mask:
                mask_bits = struct.pack('!I', random.getrandbits(32))
                output.write(mask_bits)
            # Prepare the data
            if mask:
                data = bytes(b ^ mask_bits[i % 4] for i, b in enumerate(data))
            output.write(bytes(data, "utf-8"))
            conn.sendall(output.getvalue())
        except Exception:
            raise

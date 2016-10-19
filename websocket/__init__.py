from ..utils import search_win_drive, daemonize
import base64
import http.client
import hashlib
import socket

class WebSocket(object):
    def __init__(self, port):
        self._socket = socket.socket()
        self.sock.bind(("",port))
        self.listen()
        self.conn, self.addr = None, None
        self._port = port

    @property
    def socket(self):
        return self._socket

    @property
    def port(self):
        return self._port

    @daemonize
    def listen(self):
        self.sock.listen(10)
        while True:
            self.conn, self.addr = self.sock.accept()
            response = self.conn.recv(1024)
            response = response.decode("utf-8").split("\r\n")
            self.headers = dict()  #Sacar Fuera
            for line in response:
                data = re.findall("([\w\W]+): ([\w\W]+)", line)
                if data != list(): self.headers[data[0][0]]=data[0][1]
            if "Sec-WebSocket-Key" in self.headers:
                key = self.headers["Sec-WebSocket-Key"]
                key = "".join((key, "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"))
                key = hashlib.sha1(bytes(key, "utf-8"))
                key = base64.b64encode(key.digest()).decode("utf-8")
                accept = "HTTP/1.1 101 Switching Protocols\r\n"
                accept = "".join((accept, "Upgrade: websocket\r\n"))
                accept = "".join((accept, "Connection: Upgrade\r\n"))
                accept = "".join((accept, "Sec-WebSocket-Accept: {}\r\n\r\n".format(key)))
                self.send(accept)
            else:
                pass #TODO: implement handler

    def send(self, data, mask=False):
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
            self.conn.sendall(output.getvalue())
        except:
            pass

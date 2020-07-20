import socket
import threading

class Client():
    def __init__(self, ip):
        self.stream = self.init_connection(ip)
        self.queue = []
        thread = threading.Thread(target=self.wait_for_server, daemon=True)
        thread.start()

        
    def init_connection(self, ip):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((ip, 4242))
        sock.settimeout(None)
        return sock
    
    def _read_server(self):
        msg = self.stream.recv(1024).decode()
        msg = msg.split("|")
        for elem in msg:
            self.queue.append(elem)

    def _send_server(self, msg):
        self.stream.send(msg.encode())

    def wait_for_server(self):
        while True:
            msg = self._read_server()

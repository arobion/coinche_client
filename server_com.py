# -*- coding: utf-8 -*-
import socket
import threading

class Client():
    def __init__(self):
        self.queue = []
        self.stream = None

    def _init_connection(self, ip):
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

    def _wait_for_server(self):
        while True:
            msg = self._read_server()

    def connect(self, ip):
        self.stream = self._init_connection(ip)

    def listen(self):
        thread = threading.Thread(target=self._wait_for_server, daemon=True)
        thread.start()
        
    def send_server(self, msg):
        self.stream.send(msg.encode())
    
    def start(self, ip):
        self.connect(ip)
        self.listen()

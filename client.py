# -*- coding: utf-8 -*-

import socket


class Client():
    def __init__(self):
        self.sock = self._create_sock()
        self.queue = []

    def _create_sock(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(None)
            return sock
        except OSError as e:
            raise e

    def read_server(self):
        recv = self.sock.recv(1024).decode('utf-8')
        self.queue.append(recv)

    def connect(self, ip):
        try:
            self.sock.connect((ip, 4242))
        except OSError:
            return True
        return False

    def write_server(self, msg):
        self.sock.send(msg.encode('utf-8'))

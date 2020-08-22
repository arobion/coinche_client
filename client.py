# -*- coding: utf-8 -*-

import socket
import threading

class Client():
    def __init__(self):
        self.sock = self._create_sock()
        self.lock = threading.Lock()
        self.queue = []

    def _create_sock(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(None)
            return sock
        except OSError as e:
            raise e

    def _read_server(self):
        recv = self.sock.recv(1024).decode('utf-8')
        self.lock.acquire()
        self.queue.append(recv)
        self.lock.release()

    def _wait_for_server(self):
        while True:
            self._read_server()

    def _run_client(self):
        thread = threading.Thread(target=self._wait_for_server, daemon=True)
        thread.start()

    def connect(self, ip):
        try:
            self.sock.connect((ip, 4242))
        except OSError as e:
            return True
        self._run_client()
        return False

    def write_server(self, msg):
        self.sock.send(msg.encode('utf-8'))

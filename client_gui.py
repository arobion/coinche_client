# -*- coding: utf-8 -*-

import threading

from client import Client


class ClientGUI(Client):
    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()

    def _wait_for_server(self):
        while True:
            self.read_server()

    def run_client(self):
        thread = threading.Thread(target=self._wait_for_server, daemon=True)
        thread.start()
    
    def read_server(self):
        recv = self.sock.recv(1024).decode('utf-8')
        self.lock.acquire()
        self.queue.append(recv)
        self.lock.release()

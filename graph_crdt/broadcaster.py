import socket
import requests
from graph_crdt.utils import get_logger

logger = get_logger("Broadcaster")


class DatabaseWorker:
    def __init__(self, host="127.0.0.1", port="20001"):
        self.host = host
        self.port = port
        self.bufferSize = 2048
        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def execute(self):
        self.UDPServerSocket.bind((self.host, self.port))

        msg = "Gotcha! Received message from"
        while True:
            bytes_address_pair = self.UDPServerSocket.recvfrom(self.bufferSize)
            message, address = bytes_address_pair
            bytes_to_send = str.encode(f"{msg} {address}")
            self.UDPServerSocket.sendto(bytes_to_send, address)

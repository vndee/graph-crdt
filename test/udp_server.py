import time
import socket

local_ip = "127.0.0.1"
local_port = 20001
bufferSize = 1024

msg_from_server = "Hello UDP client"
bytes_to_send = str.encode(msg_from_server)

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

UDPServerSocket.bind((local_ip, local_port))

print("UDP server up and listening")


while True:
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

    message = bytesAddressPair[0]

    address = bytesAddressPair[1]

    clientMsg = "Message from Client:{}".format(message)
    clientIP = "Client IP Address:{}".format(address)

    # Sending a reply to client

    UDPServerSocket.sendto(bytes_to_send, address)
    print(clientMsg)
    print(clientIP)

    # time.sleep(1000)

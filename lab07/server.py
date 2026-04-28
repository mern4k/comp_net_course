import random
from socket import socket, AF_INET, SOCK_DGRAM


if __name__ == "__main__":
    server_port = 12345
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind(('localhost', server_port))
    while True:
        message, client_address = server_socket.recvfrom(2048)
        if random.random() < 0.2:
            print("Packet loss")
            continue
        print("Received message:", message.decode())
        server_socket.sendto(message.upper(), client_address)

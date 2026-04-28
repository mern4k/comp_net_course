import time 
import random
from socket import socket, AF_INET, SOCK_DGRAM


if __name__ == "__main__":
    server_name = 'localhost'
    server_port = 12345
    client_socket = socket(AF_INET, SOCK_DGRAM)
    count = random.randint(5, 10)
    print(f"Number of messages to send: {count}")
    for i in range(1, 1 + count):
        time.sleep(1)
        now = time.time()
        message = f"{i} {now}".encode()
        print(f"Sending message: {message.decode()}")
        client_socket.sendto(message, (server_name, server_port))
    client_socket.close()

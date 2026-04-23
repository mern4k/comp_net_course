import time
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST
from datetime import datetime

if __name__ == "__main__":
    server_port = 12345
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    print(f"Server is listening on port {server_port}...")
    while True:
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"Current server time: {current_time}")  
        server_socket.sendto(current_time.encode(), ('<broadcast>', server_port))
        time.sleep(1)
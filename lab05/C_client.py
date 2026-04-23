from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR

if __name__ == "__main__":
    server_port = 12345
    client_name = input("Enter client name: ")
    client_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    client_socket.bind(("", server_port))
    
    while True:
        data, addr = client_socket.recvfrom(4096)
        print(f"Name: {client_name} - Recieved data from server: {data.decode()}")
    
    client_socket.close()

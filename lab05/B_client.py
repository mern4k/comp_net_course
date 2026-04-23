from socket import socket, AF_INET, SOCK_STREAM

if __name__ == "__main__":
    server_name = 'localhost'
    server_port = 12345
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((server_name, server_port))
    command = input("Enter a command to send to the server: ")
    client_socket.send(command.encode())
    response = b""
    while True:
        chunk = client_socket.recv(4096)
        if not chunk:
            break
        response += chunk
    print(response.decode())
    print(f"Response from server: {response.decode()}")
    client_socket.close()

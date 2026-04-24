from socket import socket, AF_INET, SOCK_STREAM
from dotenv import load_dotenv
import os
load_dotenv()
PASSWORD = os.getenv("TEST_USER_PASSWORD") or ""


def check_response(sock, expected_code):
    response = sock.recv(1024).decode()
    if not response.startswith(str(expected_code)):
        print(f"Expected response code {expected_code}, but got: {response}")
        sock.close()
        exit(1)
    

def connect_to_server(server_name, server_port, username, password):
    print("Connecting to FTP server...")
    control_socket = socket(AF_INET, SOCK_STREAM)
    control_socket.connect((server_name, server_port))
    check_response(control_socket, 220)
    control_socket.sendall(f"USER {username}\r\n".encode())
    response = control_socket.recv(1024).decode()
    if response.startswith("331"):
        print("Username accepted, please enter password.")
    else:
        print("Username rejected.")
        control_socket.close()
        exit(1)
    
    control_socket.sendall(f"PASS {password}\r\n".encode())
    response = control_socket.recv(1024).decode()
    if response.startswith("230"):
        print("Login successful.")
    else:
        print("Login failed.")
        control_socket.close()
        exit(1)

    return control_socket


def get_data_socket(control_socket, server_name):
    print(60 * '=')
    control_socket.sendall("PASV\r\n".encode())
    response = control_socket.recv(1024).decode()
    if response.startswith("227"):
        data_port = int(response.split(",")[-2]) * 256 + int(response.split(",")[-1].split(")")[0])
    else:
        print("Failed to enter passive mode.")
        control_socket.close()
        exit(1)
    data_socket = socket(AF_INET, SOCK_STREAM)
    data_socket.connect((server_name, data_port))

    return data_socket


def list_files(control_socket, data_socket):
    control_socket.sendall("NLST\r\n".encode())
    check_response(control_socket, 150)
    response = b""
    chunk = data_socket.recv(1024)
    while chunk:
        response += chunk
        chunk = data_socket.recv(1024)
    data_socket.close()
    check_response(control_socket, 226)
    print(f"Response:\n {response.decode()}")
    return response.decode().splitlines()
    

def get_file(control_socket, data_socket, filename):
    control_socket.sendall(f"RETR {filename}\r\n".encode())
    check_response(control_socket, 150)
    with open(filename, 'wb') as f:
        chunk = data_socket.recv(1024)
        while chunk:
            f.write(chunk)
            chunk = data_socket.recv(1024)
    data_socket.close()
    check_response(control_socket, 226)
    print(f"File '{filename}' downloaded successfully.")
    

def get_file_content(control_socket, data_socket, filename):
    control_socket.sendall(f"RETR {filename}\r\n".encode())
    check_response(control_socket, 150)
    content = b""
    chunk = data_socket.recv(1024)
    while chunk:
        content += chunk
        chunk = data_socket.recv(1024)
    data_socket.close()
    check_response(control_socket, 226)
    print(f"File '{filename}' downloaded successfully.")
    return content


def put_file(control_socket, data_socket, filename):
    if not os.path.isfile(filename):
        print(f"File '{filename}' does not exist.")
        data_socket.close()
        return
    control_socket.sendall(f"STOR {filename}\r\n".encode())
    check_response(control_socket, 150)
    with open(filename, 'rb') as f:
        data_socket.sendall(f.read())
    data_socket.close()
    check_response(control_socket, 226)
    print(f"File '{filename}' uploaded successfully.")


def put_content(control_socket, data_socket, filename, content: bytes):
    control_socket.sendall(f"STOR {filename}\r\n".encode())
    check_response(control_socket, 150)
    data_socket.sendall(content)
    data_socket.close()
    check_response(control_socket, 226)

    
def del_file(control_socket, filename):
    control_socket.sendall(f"DELE {filename}\r\n".encode())
    check_response(control_socket, 250)
    print(f"File '{filename}' deleted successfully.")


def make_directory(control_socket, dirname):
    control_socket.sendall(f"MKD {dirname}\r\n".encode())
    check_response(control_socket, 257)
    print(f"Directory '{dirname}' created successfully.")


if __name__ == "__main__":
    server_name = 'localhost'
    server_port = 21
    username = 'TestUser'
    password = PASSWORD
    control_socket = connect_to_server(server_name, server_port, username, password)
    
    while True:
        command = input(
            "\nEnter command:\n"
            "  list            — list files\n"
            "  get <filename>  — download file\n"
            "  put <filename>  — upload file\n"
            "  quit            — disconnect\n"
            "> "
        )
        if command.lower() == "quit":
            control_socket.sendall("QUIT\r\n".encode())
            break
        if command.lower() == "list":
            data_socket = get_data_socket(control_socket, server_name)
            list_files(control_socket, data_socket)
        elif command.lower().startswith("get "):
            filename = command[4:].strip()
            data_socket = get_data_socket(control_socket, server_name)
            get_file(control_socket, data_socket, filename)
        elif command.lower().startswith("put "):
            filename = command[4:].strip()
            data_socket = get_data_socket(control_socket, server_name)
            put_file(control_socket, data_socket, filename)
        else:
            print("Unknown command.")

    control_socket.close()
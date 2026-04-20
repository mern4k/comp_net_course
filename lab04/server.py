import logging
import threading
import json
import re
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

from config import FORBIDDEN_DOMAINS, FORBIDDEN_URLS


logging.basicConfig(
    filename='proxy.log',
    level=logging.INFO,
    format='- %(asctime)s %(message)s'
)

def get_server_path(path):
    if path.startswith("http://"):
        without_scheme = path[len("http://"):]
        if "/" in without_scheme:
            server_name, path = without_scheme.split("/", 1)
            path = "/" + path
        else:
            server_name = without_scheme
            path = "/"
    else:
        server_name = path.split("/")[1]
        path = "/" + "/".join(path.split("/")[2:])
    return server_name, path


try:
    cache = json.load(open("cache.json"))
except FileNotFoundError:
    cache = {}

def handle_connection(connection_socket, addr):
    logging.info(f"Received connection from {addr}")
    request = connection_socket.recv(4096).decode()
    request_lines = request.split("\r\n")
    command = request_lines[0].split()
    if not command:
        connection_socket.close()
        return
    method = command[0]
    server_port = 80
    request_path = command[1]
    cache_path = "cache/" + request_path.replace("/", "_") + ".bin"
    server_name, path = get_server_path(request_path)
    logging.info(f"Received {method} request for {request_path}")

    if request_path in FORBIDDEN_URLS or server_name in FORBIDDEN_DOMAINS:
        logging.info(f"Blocked request for {request_path}")
        body = b"<html><body><h1>403 Forbidden</h1><p>This site is blocked.</p></body></html>"
        response = (
            b"HTTP/1.1 403 Forbidden\r\n"
            b"Content-Type: text/html\r\n"
            b"Content-Length: " + str(len(body)).encode() + b"\r\n"
            b"Connection: close\r\n"
            b"\r\n" + body
        )
        connection_socket.send(response)
        connection_socket.close()
        return
        
    if method == "GET":
        request = re.sub(r'If-None-Match: [^\r\n]+\r\n', '', request)
        request = re.sub(r'If-Modified-Since: [^\r\n]+\r\n', '', request)
        if request_path in cache:
            logging.info("Cache hit for " + request_path)
            etag = cache[request_path]["etag"]
            last_modified = cache[request_path]["last-modified"]
            extra = ""
            if etag:
                extra += f'\r\nIf-None-Match: "{etag}"'
            if last_modified:
                extra += f"\r\nIf-Modified-Since: {last_modified}"
            request = request.replace("\r\n\r\n", extra + "\r\n\r\n", 1)
        else:
            logging.info("Cache miss for " + request_path)
    
    request = request.replace(request_lines[0], f"{method} {path} HTTP/1.1")
    request = request.replace("Connection: keep-alive", "Connection: close")
    request = request.replace(request_lines[1], "Host: " + server_name).encode()

    if method in ("GET", "POST"):
        client_socket = socket(AF_INET, SOCK_STREAM)
        try:
            client_socket.connect((server_name, server_port))
        except OSError:
            connection_socket.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
            connection_socket.close()
            return
        client_socket.send(request)
        response = b""
        while True:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            response += chunk
        logging.info(f"Status: {response.split(b"\r\n")[0]}")
        if method == "GET":
            if b"304" in response.split(b"\r\n")[0]:
                logging.info("Resource not modified, loading from cache")
                with open(cache_path, "rb") as f:
                    response = f.read()
            else:
                logging.info("Resource not in cache, loading from response")
                etag = ""
                last_modified = ""
                for line in response.split(b"\r\n"):
                    if line.lower().startswith(b"etag:"):
                        etag = line.split(b": ", 1)[1].decode().strip('"')
                    if line.lower().startswith(b"last-modified:"):
                        last_modified = line.split(b": ", 1)[1].decode()
                cache[request_path] = {"etag": etag, "last-modified": last_modified}
                json.dump(cache, open("cache.json", "w"))
                with open(cache_path, "wb") as f:
                    f.write(response)
        connection_socket.send(response)
        client_socket.close()
    connection_socket.close()

proxy_port = 12000
proxy_socket = socket(AF_INET, SOCK_STREAM)
proxy_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
proxy_socket.bind(('', proxy_port))
proxy_socket.listen(10)
logging.info(f"Proxy server is listening on port {proxy_port}...")
while True:
    connection_socket, addr = proxy_socket.accept()
    thread = threading.Thread(target=handle_connection, args=(connection_socket, addr))
    thread.start()

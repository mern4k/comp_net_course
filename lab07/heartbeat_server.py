import random
import time
from socket import socket, AF_INET, SOCK_DGRAM

MAX_TIME_NO_PACKETS = 5


if __name__ == "__main__":
    server_port = 12345
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind(('localhost', server_port))
    server_socket.settimeout(1)
    last_message_time = {}
    last_message_index = {}
    while True:
        addreses_to_remove = []
        for client_address in last_message_time:
            if time.time() - last_message_time[client_address] > MAX_TIME_NO_PACKETS:
                print(f"[{client_address[0]}:{client_address[1]}] Client stopped (no heartbeat for {MAX_TIME_NO_PACKETS}s)")
                addreses_to_remove.append(client_address)
        for client_address in addreses_to_remove:
            del last_message_time[client_address]
            del last_message_index[client_address]

        try:
            message, client_address = server_socket.recvfrom(2048)
            client_str = f"{client_address[0]}:{client_address[1]}"
            if random.random() < 0.2:
                print(f"[{client_str}] Packet loss")
                continue
            now = time.time()
            message_index = int(message.decode().split()[0])
            message_time = float(message.decode().split()[1])
            prev_index = last_message_index.get(client_address, 0)
            if message_index > prev_index + 1:
                print(f"[{client_str}] Lost packets: index {prev_index + 1} to {message_index - 1}")
            last_message_index[client_address] = max(prev_index, message_index)
            if client_address not in last_message_time:
                print(f"[{client_str}] New client connected")
            last_message_time[client_address] = now
            print(f"[{client_str}] Heartbeat #{message_index}, delay: {now - message_time:.4f}s")
        except TimeoutError:
            pass


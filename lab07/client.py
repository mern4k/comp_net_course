import time 
from socket import socket, AF_INET, SOCK_DGRAM


if __name__ == "__main__":
    server_name = 'localhost'
    server_port = 12345
    client_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.settimeout(1)
    min_rtt = float('inf')
    max_rtt = float('-inf')
    sum_rtt = 0
    lost_count = 0
    for i in range(1, 11):
        now = time.time()
        send_time = time.strftime("%H:%M:%S", time.localtime(now))
        message = f"Ping {i} {send_time}".encode()
        print(f"Sending message: {message.decode()}")
        client_socket.sendto(message, (server_name, server_port))
        try:
            response, _ = client_socket.recvfrom(2048)
            rtt = time.time() - now
            min_rtt = min(min_rtt, rtt)
            max_rtt = max(max_rtt, rtt)
            sum_rtt += rtt
            print("Received response:", response.decode())
            print(f"""RTT: {rtt:.6f} s, Min RTT: {min_rtt:.6f} s, Max RTT: {max_rtt:.6f} s, Average RTT: {sum_rtt / (i - lost_count):.6f} s""")
        except TimeoutError:
            print("Request timed out")
            lost_count += 1 
    client_socket.close()
    print(f"Packet loss rate: {lost_count * 10}%")

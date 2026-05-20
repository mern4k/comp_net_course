import socket
import psutil


if __name__ == "__main__":
    ip = socket.gethostbyname(socket.gethostname())
    print(f"IP: {ip}")
    for key, value in psutil.net_if_addrs().items():
        for item in value:
            if item.family == socket.AF_INET and item.address == ip:
                print(f"Mask: {item.netmask}")
        
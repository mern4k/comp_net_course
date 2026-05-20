from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR
import time

START_MESSAGE = "Started node on port "
RESPONSE_MESSAGE = "Node alive on port "
CLOSE_MESSAGE = "Closed node on port "
BROADCAST_PORT = 9999

class socket_node:
    def __init__(self, ip, port, message_time_interval = 3.0, dead_interval_amounts = 3):
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.sock.bind(('', BROADCAST_PORT))
        self.sock.settimeout(0.5)
        self.ip = ip
        self.port = port
        self.message_time_interval = message_time_interval
        self.dead_interval_amounts = dead_interval_amounts

        self.broadcast((START_MESSAGE + str(self.port)).encode())
        self.addr = (self.ip, self.port)
        self.alive_dict = {self.addr: time.time()}

    def main_loop(self):
        last_time_broadcasted = time.time()
        while True:
            self.alive_dict[self.addr] = time.time()
            if time.time() - last_time_broadcasted > self.message_time_interval:
                self.broadcast((RESPONSE_MESSAGE + str(self.port)).encode())
                last_time_broadcasted = time.time()
            
            for addr in list(self.alive_dict.keys()):
                if time.time() - self.alive_dict[addr] > self.dead_interval_amounts * self.message_time_interval:
                    print("Node on port " + str(addr[1]) + " is dead")
                    self.alive_dict.pop(addr, None)
            try:
                response, addr = self.sock.recvfrom(1024)
                response = response.decode()
                out_port = int(response.split()[-1])
                logical_addr = (addr[0], out_port)
                if response.startswith(START_MESSAGE):
                    self.alive_dict[logical_addr] = time.time()
                    self.send_to((RESPONSE_MESSAGE + str(self.port)).encode(), addr)
                elif response.startswith(CLOSE_MESSAGE):
                    self.alive_dict.pop(logical_addr, None)
                elif response.startswith(RESPONSE_MESSAGE):
                    self.alive_dict[logical_addr] = time.time()
                    print("Node on port " + str(out_port) + " is alive")
                else:
                    raise NotImplementedError("Unknown message")
            except TimeoutError:
                pass

    def clean_up(self):
        self.broadcast((CLOSE_MESSAGE + str(self.port)).encode())
        self.sock.close()

    def broadcast(self, msg, port=BROADCAST_PORT):
        self.sock.sendto(msg, ('255.255.255.255', port))

    def send_to(self, msg, addr):
        self.sock.sendto(msg, addr)

    def set_message_time_interval(self, message_time_interval):
        self.message_time_interval = message_time_interval

    def set_dead_interval_amounts(self, dead_interval_amounts):
        self.dead_interval_amounts = dead_interval_amounts
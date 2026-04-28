import random
from socket import socket, AF_INET, SOCK_DGRAM
from checksum import compute_checksum

TIMEOUT = 0.5

def split_into_packets(filename="lena.jpeg", packet_size=4096):
    with open(filename, "rb") as f:
        file_data = f.read()
    chunk_size = packet_size - 4
    chunks = [file_data[i:i+chunk_size] for i in range(0, len(file_data), chunk_size)]
    packets = []
    for i, chunk in enumerate(chunks):
        seq_num = i % 2
        is_last = 1 if i == len(chunks) - 1 else 0
        checksum = compute_checksum(chunk)
        packet = bytes([seq_num]) + bytes([is_last]) + checksum.to_bytes(2, 'big') + chunk
        packets.append(packet)
    return packets


if __name__ == "__main__":
    packets = split_into_packets()
    client_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.settimeout(TIMEOUT)
    server_port = 12345
    server_address = ('localhost', server_port)
    for packet in packets:
        while True:
            print("Sending packet", packet[0], "...")
            if random.random() < 0.3:
                print("Packet loss, not sending")
                continue
            if random.random() < 0.1:
                corrupted = bytearray(packet)
                corrupted[random.randint(4, len(corrupted)-1)] ^= 0x01
                packet_to_send = bytes(corrupted)
                print("Bit corruption simulated")
            else:
                packet_to_send = packet
            client_socket.sendto(packet_to_send, server_address)
            try:
                ack, _ = client_socket.recvfrom(2048)
                if ack[0] == packet[0]:
                    print("ACK received for packet", ack[0])
                    break
                else:
                    print("Received ACK for wrong packet", ack[0])
            except TimeoutError:
                print("Timeout, resending packet", packet[0])

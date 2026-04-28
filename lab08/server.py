import random
from socket import socket, AF_INET, SOCK_DGRAM
from checksum import verify_checksum

if __name__ == "__main__":
    server_port = 12345
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind(('localhost', server_port))
    all_data = b''
    expected_seq = 0
    while True:
        packet, client_address = server_socket.recvfrom(4096)
        if random.random() < 0.3:
            print("Packet loss")
            continue
        print("Received packet from", client_address, ":", packet[0:10], "...")
        seq_num = packet[0]
        is_last = packet[1]
        checksum =  int.from_bytes(packet[2:4], 'big')
        data = packet[4:]
        ack_packet = bytes([seq_num])
        if not verify_checksum(data, checksum):
            print("Checksum invalid, dropping")
            continue
        if seq_num != expected_seq:
            print("Duplicate packet", seq_num)
            server_socket.sendto(ack_packet, client_address)
            continue
        all_data += data
        server_socket.sendto(ack_packet, client_address)
        expected_seq = 1 - expected_seq
        if is_last:
            print("Last packet received")
            break

    with open("received_image.jpeg", "wb") as f:
        f.write(all_data)
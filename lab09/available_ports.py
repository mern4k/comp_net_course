from socket import AF_INET, SOCK_STREAM, socket
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip")
    parser.add_argument("--start", type=int)
    parser.add_argument("--end", type=int)
    args = parser.parse_args()
    ip = args.ip
    start = args.start
    end = args.end

    available_ports = []
    unavailable_ports = []
    for port in range(start, end + 1):
        ok = True
        try:
            connection_socket = socket(AF_INET, SOCK_STREAM)
            connection_socket.bind((ip, port))
        except OSError:
            ok = False

        if ok:
            available_ports.append(port)
        else:
            unavailable_ports.append(port)
        connection_socket.close()

    
    if available_ports:
        print(f"Found {len(available_ports)} available ports:")
        for port in available_ports:
            print(port, end=', ')
    print("\n")
    if unavailable_ports:
        print(f"Found {len(unavailable_ports)} unavailable ports:")
        for port in unavailable_ports:
            print(port, end=', ')


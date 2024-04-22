import socket


# TCP Client used to contact TCP Server
def tcp_client(message: str):

    # Assign server and port
    server_address = '127.0.0.1'
    server_port = 12345

    # Create a Socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Establish a Connection:
        sock.connect((server_address, server_port))

        # Send Data:
        sock.sendall(message.encode())

        # Receive Data:
        response = sock.recv(1024)
        return response.decode()

    finally:
        # Close the Connection:
        sock.close()

import socket


# TCP Client used to contact TCP Server
def tcp_client():

    # Assign server and port
    server_address = '127.0.0.1'
    server_port = 12345

    # Create a Socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Establish a Connection:
        sock.connect((server_address, server_port))

        # Send Data:
        message = "Hello"
        print(f"Sending: {message}")
        sock.sendall(message.encode())

        # Receive Data:
        response = sock.recv(1024)
        print(f"Received: {response.decode()}")

    finally:
        # Close the Connection:
        sock.close()

# TCP Server to Listen for Communications


def tcp_server():

    # Assign server and port
    server_address = '127.0.0.1'
    server_port = 12345

    # Create a Socket:
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the Socket:
    server_sock.bind((server_address, server_port))

    # Listen for Incoming Connections:
    server_sock.listen(5)  # Argument is number of backlogged connections

    print("TCP Echo Server listening for incoming connections...")

    try:
        while True:
            # Accept Connections
            client_sock, client_address = server_sock.accept()
            print(f"Connection from {client_address}")

            try:
                # Receive Data:
                message = client_sock.recv(1024)
                print(f"Received message: {message.decode()}")

                # Send Data:
                response = "Message received"
                client_sock.sendall(response.encode())

            finally:
                # Close the Client Connection:
                client_sock.close()
                print(f"Connection with {client_address} closed")

    except KeyboardInterrupt:
        print("Server is shutting down")

    finally:
        # Close Server Socket:
        server_sock.close()
        print("Server socket was closed")


# UDP Client used to communicate with UDP Servers
def udp_client():

    # Assign server and port
    server_address = '127.0.0.1'
    server_port = 12345

    # Create a Datagram Socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Send Data:
        message = 'Hello, UDP Server!'
        print(f"Sending: {message}")
        sock.sendto(message.encode(), (server_address, server_port))

        # Receive Data:
        response, server = sock.recvfrom(1024)
        print(f"Received: {response.decode()} from {server}")

    finally:
        # Close the Socket:
        sock.close()


# UDP Server for listening for UDP communications
def udp_server():

    # Assign server and port
    server_address = '127.0.0.1'
    server_port = 12345

    # Create  Datagram Socket:
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the Socket:
    server_sock.bind((server_address, server_port))

    print("UDP Server is listening for messages...")

    try:
        while True:
            # Receive Data:
            message, client_address = server_sock.recvfrom(1024)
            print(f"Received message:\
                  {message.decode()} from {client_address}")

            # Send Data:
            response = "Message received"
            server_sock.sendto(response.encode(), client_address)

    except KeyboardInterrupt:
        print("Server is shutting down")

    finally:
        # Close the Socket
        server_sock.close()
        print("Server socket closed")

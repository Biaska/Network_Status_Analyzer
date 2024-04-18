import socket


def tcp_echo_server():

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
                message = client_sock.recv(1024).decode()
                print(f"Received message: {message}")

                match message.lower():

                    case "exit":
                        response = "Shutting down echo server"
                        client_sock.sendall(response.encode())
                        client_sock.close()
                        print(f"Connection with {client_address} closed")
                        raise KeyboardInterrupt

                    case _:
                        response = "Message received"
                        client_sock.sendall(response.encode())

            finally:
                # Close the Client Connection:
                client_sock.close()
                print(f"Connection with {client_address} closed")

    except KeyboardInterrupt:
        print("Echo server is shutting down")

    finally:
        # Close Server Socket:
        server_sock.close()
        print("Server socket was closed")


if __name__ == "__main__":
    tcp_echo_server()
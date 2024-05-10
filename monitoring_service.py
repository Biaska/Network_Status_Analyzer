import socket
import signal
import os
import sys
import threading

server_port = 12345


def create_server_id() -> str:
    return ""


def handle_client_connection(stop_event: threading.Event, server_sock: socket.socket):
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
                        response = "Shutting down server"
                        client_sock.sendall(response.encode())
                        client_sock.close()
                        print(f"Connection with {client_address} closed")
                        raise KeyboardInterrupt
                    
                    case "create":
                        # handle creating a new service check
                        pass

                    case "delete":
                        # handle deleting a servicc check
                        pass

                    case "status":
                        # handle checking the status of the server
                        pass

                    case _:
                        response = "Server is running."
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


def tcp_server():
    global server_port

    # Assign server and port
    server_address = '127.0.0.1'
    port = server_port
    server_port += 1

    # Create a Socket:
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the Socket:
    server_sock.bind((server_address, port))

    # Listen for Incoming Connections:
    server_sock.listen(5)  # Argument is number of backlogged connections

    print("Server listening for incoming connections...")

    stop_event: threading.Event = threading.Event()
    worker_thread: threading.Thread = threading.Thread(target=handle_client_connection, args=(stop_event, server_sock))
    worker_thread.start()

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
                        response = "Echo server running."
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
    tcp_server()

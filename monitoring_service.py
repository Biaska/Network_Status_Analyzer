import socket
import signal
import os
import sys
import threading
import time
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.patch_stdout import patch_stdout
from Echo_Client import tcp_client
from timestamp_printing import timestamped_print
from network_monitoring_functions import ping, traceroute, check_server_http, \
    check_server_https, check_ntp_server, check_dns_server_status, check_tcp_port,\
        check_udp_port, check_echo_server

# Make this into a json import
global_config = {}

def create_server_id() -> str:
    # Create a unique server ID
    return ""

def print_config():
    # Print the configuration settings to the console
    pass

def print_commands():
    # Print the valid command line actions
    pass

# Worker thread function
def service_check(stop_event: threading.Event, config: object) -> None:
    """
    Prints a message every 5 seconds until stop_event is set.
    """
    server, service = config['server'], config['service']
    while not stop_event.is_set():

        match config['service']:

            # Run HTTP Tests
            case 'HTTP':
                success, code = check_server_http(server)
                timestamped_print(
                    f"{service:<6}| {'PASS' if success else 'FAIL'} - (server: {server} code: {code})")

            # Run HTTPS Tests
            case 'HTTPS':
                success, code, message = check_server_https(server, config['timeout'])
                timestamped_print(f"{service:<6}| {'PASS' if success else 'FAIL'} - (server: {server} code: {code} message: {message})")

            # Run ICMP Tests
            case 'ICMP':
                reply_address, response_time = ping(config['server'], 64, config['timeout'])
                timestamped_print(f"{service:<6}| {'PASS' if response_time else 'FAIL'} - (server: {server} reply-address: {reply_address} time: {response_time})")

            case 'DNS':
                status, results = check_dns_server_status(config['dns'][1], config['server'], config['dns_type'])
                timestamped_print(f"{service:<6}| {'PASS' if status else 'FAIL'} - ({config['dns'][0]}[{config['dns_type']}]  query: {server} results: {results})")

            case 'NTP':
                status, _ = check_ntp_server(config['server'])
                timestamped_print(f"{service:<6}| {'PASS' if status else 'FAIL'} - (server-status: {server} {'is up.' if status else 'is down.'})")

            case 'TCP':
                status, message = check_tcp_port(config['server'], config['port'])
                timestamped_print(f"{service:<6}| {'PASS' if status else 'FAIL'} - (response-description: {message})")

            case 'UDP':
                status, message = check_tcp_port(config['server'], config['port'])
                timestamped_print(f"{service:<6}| {'PASS' if status else 'FAIL'} - (response-description: {message})")

            case 'ECHO':
                message = tcp_client('Echo test.')
                timestamped_print(f"{service:<6}| {'PASS' if message else 'FAIL'} - (server-message: {message})")

        time.sleep(config['time'])
        pass


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

    # Assign server and port
    server_address = '127.0.0.1'

    # Get port number from command line argument
    try:
        server_port = int(sys.argv()[1])
        if server_port < 0 or server_port > 65535:
            print("Incorrect port.")
            return
    except ValueError:
        print("Invalid input.")
        return
    except IndexError:
        print("Enter a port number to start the server on.")
        return


    # Create a Socket:
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the Socket:
    server_sock.bind((server_address, server_port))

    # Listen for Incoming Connections:
    server_sock.listen(5)  # Argument is number of backlogged connections

    print("Server listening for incoming connections...")

    stop_event: threading.Event = threading.Event()
    worker_thread: threading.Thread = threading.Thread(target=handle_client_connection, args=(stop_event, server_sock))
    worker_thread.start()

    # Command completer for auto-complete
    command_completer: WordCompleter = WordCompleter(
        ['exit', 'test', 'start', 'stop', 'config', 'set', 'delete'], ignore_case=True)

    # Create a prompt session
    session: PromptSession = PromptSession(completer=command_completer)

    # Variable to control the main loop
    is_running: bool = True

    try:
        with patch_stdout():
            while is_running:
                # Using prompt-toolkit for input with auto-completion
                user_input: str = session.prompt("Enter command: ")

                match user_input:

                    case 'start':
                        # Start continuous tests wtih current configuration
                        # Create and start the worker thread
                        stop_event: threading.Event = threading.Event()
                        for service_config in global_config:
                            worker_thread: threading.Thread = threading.Thread(
                                target=service_check, args=(stop_event, service_config))
                            worker_thread.start()

                    case 'stop':
                        if worker_thread.is_alive():
                            stop_event.set()
                            worker_thread.join()
                        else:
                            print("Network tests have not been started.")

                    case 'config':
                        print_config()

                    case 'exit':
                        print("Exiting application...")
                        is_running = False

                    case _:
                        print("Invalid command.")
                        print_commands()

    except KeyboardInterrupt:
        print("Exiting application...")

    finally:
        # Signal the worker thread to stop and wait for its completion
        if worker_thread:
            if worker_thread.is_alive():
                stop_event.set()
                worker_thread.join()

    # try:
    #     while True:
    #         # Accept Connections
    #         client_sock, client_address = server_sock.accept()
    #         print(f"Connection from {client_address}")

    #         try:
    #             # Receive Data:
    #             message = client_sock.recv(1024).decode()
    #             print(f"Received message: {message}")

    #             match message.lower():

    #                 case "exit":
    #                     response = "Shutting down echo server"
    #                     client_sock.sendall(response.encode())
    #                     client_sock.close()
    #                     print(f"Connection with {client_address} closed")
    #                     raise KeyboardInterrupt

    #                 case _:
    #                     response = "Server running."
    #                     client_sock.sendall(response.encode())

    #         finally:
    #             # Close the Client Connection:
    #             client_sock.close()
    #             print(f"Connection with {client_address} closed")

    # except KeyboardInterrupt:
    #     print("Server is shutting down")

    # finally:
    #     # Close Server Socket:
    #     server_sock.close()
    #     print("Server socket was closed")


if __name__ == "__main__":
    tcp_server()

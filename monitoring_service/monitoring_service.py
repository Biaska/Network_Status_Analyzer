import socket
import signal
import os
import sys
import threading
import time
import json
from queue import Queue
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.patch_stdout import patch_stdout
from timestamp_printing import timestamped_string
from network_monitoring_functions import ping, traceroute, check_server_http, \
    check_server_https, check_ntp_server, check_dns_server_status, check_tcp_port,\
        check_udp_port, check_echo_server
from utils import is_ipv4_address, is_valid_port


class NA_Monitor:

    def __init__(self):
        self.status = "Offline"
        self.task_results = []
        self.status_number = 0
        self.stop_flag = False
        self.task_stop_flag = False
        self.set_config(self.get_config())
    

    def update_tasks(self, tasks):
        """
        Updates the current task list with the new version from the client.
        """
        self.task_results = tasks
        self.save_config()

    def add_result(self, result):
        self.task_results.append(result)
    

    def clear_results(self):
        self.task_results = []


    def get_config(self):
        # get configuration settings from config.json
        with open('config.json', 'r') as file:
            return json.load(file)


    def set_config(self, config):
        # overwrite configuration settings from config.json
        self.id = config['id']
        self.ip_address = config['ip_address']
        self.port = config['port']
        self.tasks_list = config['tasks']
        self.status_number = config['status_number']
        self.save_config()     


    def save_config(self):
        config = {
            "id": self.id,
            "ip_address": self.ip_address,
            "port": self.port,
            "status_number": self.status_number,
            "tasks": self.tasks_list
        }
        with open("config.json", 'w') as file:
            json.dump(config, file, indent=4)
            print("Config file updated.")
    

    def set_status(self, status: str):
        """
        Set the status of the monitor service.
        """
        self.status = status


    def incr_status_number(self):
        self.status_number += 1


    def print_config(self):
        # Print the configuration settings to the console
        pass


    def print_commands(self):
        # Print the valid command line actions
        commands = """
            start - start the configured service tasks and add them to the queue.
                    sends the status updates to the client when it is connected.
            stop  - stop the task workers and stop sending the status updates.
            help  - print these commands. 
            exit  - exit the application.
        """
        print(commands)


    def command_line_handler(self):
        """
        Command line handler to responsd and validate commands.
        """

        worker_thread = False

        # Command completer for auto-complete
        command_completer: WordCompleter = WordCompleter(
            ['exit','start', 'stop'], ignore_case=True)

        # Create a prompt session
        session: PromptSession = PromptSession(completer=command_completer)

        try:
            with patch_stdout():
                while not self.stop_flag:
                    # Using prompt-toolkit for input with auto-completion
                    user_input: str = session.prompt("Enter command: ")

                    match user_input:

                        case 'start':
                            # Start continuous tests wtih current configuration
                            # Create and start the worker thread
                            print("Starting service workers.")
                            self.task_stop_flag = False
                            self.status = "Online"
                            for task in self.tasks_list:
                                worker_thread: threading.Thread = threading.Thread(
                                    target=self.service_check, args=(task,))
                                worker_thread.start()

                        case 'stop':
                            self.task_stop_flag = True
                            if not worker_thread:
                                print("Network tests have not been started.")
                            self.status = "Offline"
                        
                        case 'help':
                            self.print_commands()

                        case 'exit':
                            self.task_stop_flag = True
                            self.stop_flag = True

                        case _:
                            print("Invalid command.")
                            self.print_commands()

        except KeyboardInterrupt:
            print("Exiting application...")


    # Service check thread worker that runs one service check at the configured
    # time frequency
    def service_check(self, task: object) -> None:
        """
        Prints a message every 5 seconds until stop_event is set.
        """
        config = task['config']
        server, service = config['server'], config['service']
        while not self.task_stop_flag:

            match config['service']:

                # Run HTTP Tests
                case 'HTTP':
                    success, code = check_server_http(server)
                    message = timestamped_string(
                        f"{service:<6}| {'PASS' if success else 'FAIL'} - (server: {server} code: {code})")

                # Run HTTPS Tests
                case 'HTTPS':
                    success, code, message = check_server_https(server, config['timeout'])
                    message = timestamped_string(f"{service:<6}| {'PASS' if success else 'FAIL'} - (server: {server} code: {code} message: {message})")

                # Run ICMP Tests
                case 'ICMP':
                    reply_address, response_time = ping(config['server'], 64, config['timeout'])
                    message = timestamped_string(f"{service:<6}| {'PASS' if response_time else 'FAIL'} - (server: {server} reply-address: {reply_address} time: {response_time})")

                case 'DNS':
                    status, results = check_dns_server_status(config['dns'][1], config['server'], config['dns_type'])
                    message = timestamped_string(f"{service:<6}| {'PASS' if status else 'FAIL'} - ({config['dns'][0]}[{config['dns_type']}]  query: {server} results: {results})")

                case 'NTP':
                    status, _ = check_ntp_server(config['server'])
                    message = timestamped_string(f"{service:<6}| {'PASS' if status else 'FAIL'} - (server-status: {server} {'is up.' if status else 'is down.'})")

                case 'TCP':
                    status, message = check_tcp_port(config['server'], config['port'])
                    message = timestamped_string(f"{service:<6}| {'PASS' if status else 'FAIL'} - (response-description: {message})")

                case 'UDP':
                    status, message = check_tcp_port(config['server'], config['port'])
                    message = timestamped_string(f"{service:<6}| {'PASS' if status else 'FAIL'} - (response-description: {message})")

            self.add_result(message)
            time.sleep(config['time'])
            pass


    def handle_client_connection(self, client_sock: socket.socket):
        """
        Handles tcp connection from a tcp client. 
        :param: server_sock = socket used for tcp connections
        """
        try:    
            while not self.stop_flag:
                # Receive Data:
                message = client_sock.recv(1024)
                if not message:
                    break
                message = message.decode()
                message = json.loads(message)

                response = {
                    "action": '',
                    "status_message": None,
                    "messages": [],
                    "status_number": None
                }
                match message['action'].lower():
                    
                    case "initialize":
                        # Initialize service config from the client configuration
                        service = message['service']
                        status_message = f"Server {service['id']} Initialized."

                        self.set_config(service)
                        self.incr_status_number()

                        response['action'] = "Initialized"
                        response['status_message'] = status_message
                        
                    case "continue":
                        # Continue sending results
                        response['action'] = 'Continue'
                        response['messages'] = self.task_results
                        response['status_message'] = "Sending current results."

                        # Only clear results if the most recent delivery 
                        # is not confirmed.
                        if message['status_number'] < self.status_number:
                            self.clear_results()
                            self.incr_status_number()
                    
                    # send the current status
                    case "status":
                        response['action'] = 'Status'
                        response['status_message'] = self.status

                    # update the current task list
                    case "changed":
                        response['action'] = 'Updated'
                        response['status_message'] = "Task list updated."
            
                response['status_number'] = self.status_number
                response = json.dumps(response)
                client_sock.sendall(response.encode())

        except socket.error as e:
            print("There was an error with the client connection.")
            print(e)
        
        finally:
            print("Client socket closed.")
            client_sock.close()

    def start_server(self, server_address, server_port):
        if not is_ipv4_address(server_address):
            print("Incorrect IP address argument.")
            return

        if not is_valid_port(server_port):
            print("Invalid port number.")
            return
        
        self.print_commands()

        server_port = int(server_port)

        # Create a Socket:
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind((server_address, server_port))
        server_sock.listen(5)  # Argument is number of backlogged connections
        server_sock.settimeout(1)

        print(f"Server listening on port {server_port}")

        # Start service worker to handle client connection
        worker_thread: threading.Thread = threading.Thread(
            target=self.command_line_handler)
        worker_thread.start()

        try:
            while not self.stop_flag:
                try: 
                    # Accept Connections
                    client_sock, client_address = server_sock.accept()
                    print(f"Connection from {client_address}")

                    worker_thread: threading.Thread = threading.Thread(
                        target=self.handle_client_connection, args=(client_sock,))
                    worker_thread.start()
                
                except socket.timeout:
                    continue

                except Exception as e:
                    print(e)
            print(f"Server shutdown initiated.")
        finally: 
            server_sock.close()
            self.stop_flag = True



if __name__ == "__main__":
    try:
        address = sys.argv[1]
        port = sys.argv[2]
        monitor = NA_Monitor()
        monitor.start_server(address, port)
    except IndexError:
        print("Must specify a server IP and port number.")
    
 
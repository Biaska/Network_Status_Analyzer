import socket
import threading
import time
import json
from Echo_Client import tcp_client
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.patch_stdout import patch_stdout
import subprocess
import sys
import os
import re
from applescript import tell
from management_service.utils import banner, print_commands, print_service_list
from management_service.set_config_sequence import set_config_sequence


class NA_Manager:
    def __init__(self,config_file):
        self.config_file = config_file
        config = self.get_config()
        self.set_config(config)

    def set_config(self, config: any):
        # overwrite configuration in management_service_config.json
        try:    
            self.no_of_services = len(config["monitoring_services_list"])
            self.no_of_tasks = len(config["monitoring_task_list"])
            self.monitoring_services_list = config["monitoring_services_list"]
            self.monitoring_task_list = config["monitoring_task_list"]
            self.config_options = config["config_options"]
            with open(self.config_file, "w") as file:
                json.dump(config, file)
                print("Config file updated.")
        except KeyError:
            print("Incorrect configuration settings.")

    def get_config(self):
        # get config object from management_service_config.json
        with open(self.config_file, "r") as file:
            return json.load(file)


    def get_service_monitor(self, services, service_id):
        # Get service details from config 
        for i in range(len(services)):
            if services[i]["id"] == service_id:
                return services[i]


    def delete_monitoring_service(self):
        """
        Prompts user to delete configuration object from the global config.
        """
        print_service_list()
        service = -1
        while service < 0 or service > self.no_of_services:
            service = input("Enter the service number to delete(Enter 0 to cancel): ")
            try:
                service_no = int(service)

                # Return to CLI
                if service_no == 0:
                    return
                
                # Set service index
                service = int(service) - 1
            except ValueError:
                print("Invalid service number.")
        del self.monitoring_services_list[service]
        self.no_of_services -= 1
        print('Service deleted.')

    def command_line_handler(self):
        """
        Main function to handle user input and manage threads.
        Uses prompt-toolkit for handling user input with auto-completion and 
        ensures the prompt stays at the bottom of the terminal.
        """
        banner()

        # Event to signal the worker thread to stop
        stop_event: threading.Event = threading.Event()

        worker_thread = False

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
                            for service in self.monitoring_services_list:
                                worker_thread: threading.Thread = threading.Thread(
                                    target=handle_monitoring_services, args=(stop_event, service))      # change worker to the service handler
                                worker_thread.start()

                        case 'stop':
                            if worker_thread.is_alive():
                                stop_event.set()
                                worker_thread.join()
                            else:
                                print("Network tests have not been started.")

                        case 'config':
                            print_service_list(self.monitoring_services_list, True)

                        case 'set':
                            self.set_config(set_config_sequence(self))

                        case 'delete':
                            self.delete_monitoring_service()

                        case 'exit':
                            print("Exiting application...")
                            is_running = False

                        case _:
                            print("Invalid command.")
                            print_commands()

        except KeyboardInterrupt:
            message = tcp_client('exit')
            print(message)

        finally:
            # Signal the worker thread to stop and wait for its completion
            if worker_thread:
                if worker_thread.is_alive():
                    stop_event.set()
                    worker_thread.join()


def reconnect():
    # handle reconnecting to the service
    pass


def handle_monitoring_services():
    # worker thread that creates and maintains TCP connections to services
    pass


# TCP Client used to contact TCP Server
def start_client(message: str):

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

if __name__ == "__main__":
    na_manager = NA_Manager()
    na_manager.command_line_handler()
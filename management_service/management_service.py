import socket
import threading
import time
import json
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.patch_stdout import patch_stdout
import subprocess
import sys
import os
import re
from applescript import tell
from utils import banner, print_commands, print_service_list, get_unrelated_tasks, get_unrelated_services
from config_sequence import task_config_sequence, service_config_sequence

config_file = "config.json"

class NA_Manager:
    """
    Manager object that manages configuration settings for each service.
    """
    def __init__(self,config_file):
        self.config_file = config_file
        self.stop_flag = False
        self.services_stop_flag = False
        config = self.get_config()
        self.set_config(config)


    def get_config(self):
        """
        Get the config state from the config file. 
        """
        # get config object from config file
        with open(self.config_file, "r") as file:
            return json.load(file)


    def set_config(self, config: any):
        """
        Set the config state and save to config file.
        """
        # overwrite configuration in config file
        try:    
            self.no_of_services = len(config["monitoring_services_list"])
            self.no_of_tasks = len(config["monitoring_task_list"])
            self.monitoring_services_list = config["monitoring_services_list"]
            self.monitoring_task_list = config["monitoring_task_list"]
            self.__config_options = config["config_options"]
            self.status_messages = []
            self.save_config()
        except KeyError:
            print("Incorrect configuration settings.")


    def save_config(self):
        """
        Get the current config from the object and save it in config file.
        """
        config = {
            "monitoring_services_list": self.monitoring_services_list,
            "monitoring_task_list": self.monitoring_task_list,
            "config_options": self.get_config_options()
        }
        with open(self.config_file, "w") as file:
                json.dump(config, file, indent=4)
                print("Config file updated.")


    def get_config_options(self):
        """
        Return the config options used to create configurations.
        """
        return self.__config_options


    def get_monitor_service(self, service_id):
        """
        Get the monitor service from the unique id. 
        """
        # Get service details from config 
        for i in range(self.no_of_services):
            if self.monitoring_services_list[i]["id"] == service_id:
                return self.monitoring_services_list[i]
            

    def delete_monitoring_service(self):
        """
        Prompts user to delete configuration object from the global config.
        """
        # Print services and get user input selection
        print_service_list(self.monitoring_services_list)
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

        # delete service and update config
        del self.monitoring_services_list[service]
        self.no_of_services -= 1
        self.save_config()
        print('Service deleted.')

    
    def add_task_to_service(self, service_id, task):
        """
        Add a task to a service from the monitoring service list.
        """
        for i in range(self.no_of_services):
            if self.monitoring_services_list[i]['id'] == service_id:
                self.monitoring_services_list[i]['tasks'].append(task)
                self.monitoring_services_list[i]['changed'] = True
                self.save_config()
                return
    
    def add_task(self, task):
        """
        Add a task to the task list and update config.
        """
        self.monitoring_task_list.append(task)
        self.no_of_tasks += 1
        self.save_config()
        return
    

    def add_service(self, service):
        """
        Add a service to the config state and update config.
        """
        self.monitoring_services_list.append(service)
        self.no_of_services += 1
        self.save_config()
        return


    def set_service_variable(self, id, changed=None, status=None, initialized=None, status_number=None):
        """
        Set the flag variables that change program behavior. 
        """
        for i in range(self.no_of_services):
            if self.monitoring_services_list[i]['id'] == id:
                if changed is not None:
                    self.monitoring_services_list[i]['changed'] = changed
                if status is not None:
                    self.monitoring_services_list[i]['status'] = status
                if initialized is not None:
                    self.monitoring_services_list[i]['initialized'] = initialized
                if status_number is not None:
                    self.monitoring_services_list[i]['status_number'] = status_number


    def set_config_sequence(self):
        """
        Creates a new config object by getting user input. 
        """

        print("""
            Create a service or task:
            
                1. Service
                2. Task
            
        """)
        option = 0
        while option < 1 or option > 2:
            try: 
                option = input("Enter a number: ")
                option = int(option)
            except ValueError:
                print("Invalid input.")

        if option == 1:
            service = service_config_sequence(self.get_config_options())
            self.add_service(service)
        else:
            # Create task
            config, task_config = task_config_sequence(self.get_config())

            # Save new config options
            self.set_config(config)

            # Add task
            self.add_task(task_config)

            services = get_unrelated_services(self.monitoring_services_list, task_config['id'])

            # Choose services to add the task to
            choosing_services = True
            while choosing_services:
                print("Choose a service to add the task to:\n\n")
                print_service_list(services)
                option = -1
                while option < 0 or option > len(services):
                    try:
                        option = input("Enter a number (0 to finish): ")
                        option = int(option)

                        # Finished adding services
                        if option == 0:
                            choosing_services = False
                        
                        elif option > 0 and option <= len(services):
                            self.add_task_to_service(services[option-1]['id'], task_config)
                            services.pop(option - 1)

                        else:
                            print('Incorrect input.')

                    except ValueError:
                        print("Incorrect input.")


    def reconnect(self, service):
        # handle reconnecting to the service
        while not self.services_stop_flag:
            try:
                print("Attempting to reconnect to server...")
                time.sleep(3)
                self.start_worker(service)
                break
            except socket.error:
                print("Error reconnecting to the server. Trying again in 5 seconds...")
                time.sleep(5)

    
    def get_services_status(self):
        """
        Signals to the thread workers to get the status from their 
        respective services. 
        """
        # Set status flag for worker threads
        for i in range(self.no_of_services):
            self.monitoring_services_list[i]['status'] = True

        # wait for all status messages to return
        while len(self.status_messages) != self.no_of_services:
            time.sleep(1)
        
        # print status messages
        for message in self.status_messages:
            print(f"[Server {message['service']} Status]: {message['status']}")
        
        # clear messages
        self.status_messages = []
            

    def handle_monitoring_services(self, sock: socket.socket, service):
        """
        Worker thread that creates and maintains TCP connections to services.
        """
        try:
            while not self.stop_flag:
                try:
                    # get most up to date service details
                    service = self.get_monitor_service(service['id'])
                    message = {
                        "action": None,
                        "status_number": service['status_number']
                    }

                    # initialization of service
                    if service['initialized']:
                        self.set_service_variable(service['id'], initialized=False)
                        message['action'] = "Initialize"
                        message['service'] = service
                    

                    # service config has changed, send tasks
                    elif service['changed']:
                        message['action'] = 'Changed'
                        message['service'] = service
                        self.set_service_variable(service['id'], changed=False)
                    

                    elif service['status']:
                        message['action'] = 'Status'
                        message['service'] = service
                        self.set_service_variable(service['id'], status=False)

                    else:
                        message['action'] = "Continue"

                    # Send Data:
                    message = json.dumps(message)
                    sock.sendall(message.encode())

                    # Receive Data:
                    response = sock.recv(1024)
                    if not response:
                        break
                    response.decode()
                    response = json.loads(response)

                    # Update status number
                    self.set_service_variable(service['id'], status_number=response['status_number'])

                    if response['action'] == 'Status':
                        status = {
                            'service': service['id'],
                            'status': response['status_message']
                        }
                        self.status_messages.append(status)

                    elif response['action'] == 'Updated':
                        print(response['status_message'])

                    elif response['action'] == 'Continue':

                        for message in response['messages']:
                            print(f"[Service {service['id']}]: {message}")
                    
                    time.sleep(1)
                except socket.error as e:
                    print(f"Error while handling monitoring services: {e}")
                    break
        except Exception as e:
            print(e)
        finally:
            if not self.stop_flag:
                sock.close()
                self.reconnect(service)

    def command_line_handler(self):
        """
        Main function to handle user input and manage threads.
        Uses prompt-toolkit for handling user input with auto-completion and 
        ensures the prompt stays at the bottom of the terminal.
        """
        banner()

        # Command completer for auto-complete
        command_completer: WordCompleter = WordCompleter(
            ['exit', 'test', 'start', 'stop', 'config', 'set', 'delete', 'status'], ignore_case=True)

        # Create a prompt session
        session: PromptSession = PromptSession(completer=command_completer)

        while not self.stop_flag:
            with patch_stdout():
                try: 
                    # Using prompt-toolkit for input with auto-completion
                    user_input: str = session.prompt("Enter command: ")

                    match user_input:

                        case 'start':
                            self.start_service_workers()

                        case 'stop':
                            self.services_stop_flag = True
                            print("Service workers halted.")

                        case 'config':
                            print_service_list(self.monitoring_services_list, True)

                        case 'status':
                            self.get_services_status()

                        case 'set':
                            self.set_config_sequence()

                        case 'delete':
                            self.delete_monitoring_service()

                        case 'exit':
                            print("Exiting application...")
                            self.services_stop_flag = True
                            self.stop_flag = True
                            break
                        case _:
                            print("Invalid command.")
                            print_commands()
                except Exception as e:
                    print(f"Error with CLI: {e}")


    def start_worker(self, service):
        """
        Start and maintain connection with server.
        """

        server_address = service['ip_address']
        server_port = service['port']

        # Create a Socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((server_address, server_port))
            print(f"Connected to service {service['id']}")
            self.handle_monitoring_services(sock, service)
            
        except socket.error as e:
            print("Error with service worker.")
            print(e)
            self.reconnect(service)
        finally:
            if self.services_stop_flag:
                # Close the Connection:
                print(f"Service {service['id']} socket closed.")
                sock.close()

    
    def start_service_workers(self):
        """
        Start and maintain connection with server.
        """
        try:
            for service in self.monitoring_services_list:
                worker_thread: threading.Thread = threading.Thread(
                    target=self.start_worker, args=(service,))
                worker_thread.start()
            
        except Exception as e:
            print(e)


    def start_client(self):
        """
        """
        worker_thread: threading.Thread = threading.Thread(
            target=self.command_line_handler)
        worker_thread.start()


if __name__ == "__main__":
    na_manager = NA_Manager(config_file)
    na_manager.start_client()
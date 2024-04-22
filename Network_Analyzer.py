#!/usr/bin/env python3
import threading
import time
from Echo_Client import tcp_client
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.patch_stdout import patch_stdout
import subprocess
import sys
import os
import re
from applescript import tell
from timestamp_printing import timestamped_print
from network_monitoring_functions import ping, traceroute, check_server_http, check_server_https, check_ntp_server, check_dns_server_status, check_tcp_port, check_udp_port, check_echo_server

config_options = {
        "servers": {
            "ip_address": ["8.8.8.8", "23.41.4.216", "142.251.33.110"],
            "http": ['http://google.com', 'http://adobe.com', 'http://youtube.com'],
            "https": ['https://google.com', 'https://adobe.com', 'https://youtube.com'],
            "hostname": ["google.com", "adobe.com", "youtube.com"],
            "port": [200, 300, 400],
            'dns': [('Google DNS', '8.8.8.8'), ('Cloudfare DNS', '1.1.1.1'), ('Quad9DNS', '9.9.9.9'), ('OpenDNS', '208.67.222.222')],
            'dns_types': ['A', 'MX', 'AAAA', 'CNAME']
        },
        "services": ["HTTP", "HTTPS", "ICMP", "DNS", "NTP", "TCP", "UDP", "ECHO"]
    }


default_config = [{
        "service": config_options['services'][2],
        "server": config_options['servers']['ip_address'][0],
        "timeout": 1,
        "time": 2
    }, {
        "service": config_options["services"][1],
        "server": config_options["servers"]['https'][0],
        "timeout": 2,
        "time": 3
    }, {
        "service": config_options["services"][6],
        "server": config_options['servers']['ip_address'][2],
        "port": 200,
        "timeout": 4,
        "time": 5
    }, {
        "service": config_options["services"][7],
        "server": '127.0.0.1',
        "time": 5
    }]

global_config = default_config


def banner():
    banner = """
    =====================================================================
    _  _     _                  _       _             _                 
    | \\| |___| |___ __ _____ _ _| |__   /_\\  _ _  __ _| |_  _ ______ _ _ 
    | .` / -_|  _\\ V  V / _ | '_| / /  / _ \\| ' \\/ _` | | || |_ / -_| '_|
    |_|\\_\\___|\\__|\\_/\\_/\\___|_| |_\\_\\ /_/ \\_|_||_\\__,_|_|\\_, /__\\___|_|
                                                        |__/
    =====================================================================

    Analyze network address for response speeds. Run the default
    configuration, choose a different one, or add more.
    """
    print(banner)
    print_commands()


def print_commands():
    commands = """
    =====================================================================
    Commands:
    =====================================================================

        start: starts continious network tests using the current
               selected configuration
        stop: stops continous network tests
        config: display the current configuration
        delete: delete a service configuration
        set: start the sequence to add a new service configuration
        exit: exit the program
    """
    print(commands)


def set_config(service: str, server: str, time: int):
    """
        Sets the configuration details and returns the config object.
    """
    config = {
        "service": service,
        "server": server,
        "time": time,
    }
    return config


def set_time_interval(config):
    """
    Prompts user to enter a new time interval for each test.
    """
    # Get testing interval for the service
    time = 0
    while time < 1:
        time = input("Enter an interval amount in seconds: ")
        try:
            time = int(time)
            if time < 1:
                raise ValueError
        except ValueError:
            print('Invalid input.')

    config['time'] = time
    return config


def delete_config_option():
    print_selected_config()
    service = -1
    while service < 0 or service > len(global_config):
        service = input("Enter the service number to delete: ")
        try:
            service = int(service) - 1
        except ValueError:
            print("Invalid service number.")
    del global_config[service]
    print('Service deleted.')


def print_config_list(list: list, new=False):
    """
    Print list of options from the config list.

    :param list: list of options from the config object
    :param new: boolean that indicates to prompt to create a new option.
    """
    print('\n')
    for i in range(len(list)):
        print(f"\t\t\t{str(i+1)}. {list[i]}")

    if new:
        print(f"\t\t\t{len(list)+1}. Create new\n")


def print_selected_config():
    for i in range(len(global_config)):
        print(f"===== Service {i+1} =====")
        print(f"\nService to be tested: {global_config[i]['service']}")
        print(f"Target server: {global_config[i]["server"]}")
        if 'dns' in global_config[i]:
            print(f'Public DNS: {global_config[i]['dns']}')
            print(f'Domain record type: {global_config[i]['dns_type']}')
        if "port" in global_config[i]:
            print(f'Port number: {global_config[i]['port']}')
        if "timeout" in global_config[i]:
            print(f'Response timeout interval(seconds): {global_config[i]['timeout']}')
        print(f"Time interval(seconds): {global_config[i]["time"]}\n")


def set_config_sequence():
    config = {}

    # Get service index from user and check for valid input
    service = select_from_config_list(config_options['services'])

    config['service'] = service

    # Get server option from user and check for valid input
    match config['service']:

        case 'HTTP':
            config = select_HTTP(config)

        case 'HTTPS':
            config = select_HTTPS(config)

        case 'ICMP':
            config = select_ICMP(config)

        case 'DNS':
            config = select_DNS(config)

        case 'NTP':
            config = select_NTP(config)

        case 'TCP':
            config = select_TCP(config)

        case 'UDP':
            config = select_UDP(config)

        case 'ECHO':
            config = {
                "service": "ECHO",
                "server": '127.0.0.1'
            }

    config = set_time_interval(config)

    return config


def select_from_config_list(list, create_new=None, new_option=False):
    """
    Prints options to choose from and gets user input to select an option.

    :param list: list from config_options object
    :param create_new: function to create a new option
    :param new_option: boolean to indicate if a create new option should be
    printed to screen

    :return option: returns the option selected by the user
    """

    print_config_list(list, new_option)

    option = 0
    if new_option:
        while option < 1 or option > len(list)+1:
            try:
                option = int(input('Enter a number: '))
            except ValueError:
                print("Invalid inout.")
            if option < 1 or option > len(list)+1:
                print("Invalid input.")

    else:
        while option < 1 or option > len(list):
            try:
                option = int(input("Enter a number: "))
            except ValueError:
                print("Invalid input.")
            if option < 1 or option > len(list):
                print("Invalid input.")

    if option == len(list) + 1:
        option = create_new()
    else:
        option = list[option - 1]

    return option


def select_timeout():
    """
    Prompts user for response timeout interval and validates input.
    """
    # Get timeout interval from user for UDP function
    time = 0
    while time < 1:
        time = input("Enter response timeout interval(seconds): ")
        try:
            time = int(time)
            if time < 1:
                raise ValueError
        except ValueError:
            print('Invalid input.')
    return time


def select_TCP(config: object):
    """
    Prompts user to select TCP parameters or create new.

    :param config: Current config object to be updated by the selection.
    """
    config = select_IP(config)
    config = select_port(config)
    return config


def select_UDP(config: object):
    """
    Prompts user to select UDP parameters or create new.

    :param config: Current config object to be updated by the selection.
    """
    config = select_IP(config)
    config = select_port(config)
    config['timeout'] = select_timeout()

    return config


def select_NTP(config: object):
    """
    Prompts user to select NTP options or create new.

    :param config: Current config object to be updated by the selection.
    """
    print("""IP Address or hostname?

        1. IP Address
        2. Hostname

        """)

    target = 0
    while target < 1 or target > 2:
        target = int(input("Select a number: "))

        # Select IP Address
        if target == 1:
            config = select_IP(config)

        # Select Host Name
        if target == 2:
            config = select_hostname(config)

    return config


def select_DNS(config: object):
    """
    Prompts user to select DNS options or create new.

    :param config: Current config object to be updated by the selection.
    """
    # Select Host Name
    config = select_hostname(config)

    dns = config_options['servers']['dns']
    print("Select a DNS: ")
    config['dns'] = select_from_config_list(dns)

    dns_types = config_options['servers']['dns_types']
    print("Select a DNS type: ")
    config['dns_type'] = select_from_config_list(dns_types)

    return config


def select_ICMP(config: object):
    """
    Selects ICMP Parameters from config options or creates new options.
    :param config: Current config object to be updated by the selection.
    """

    print("""IP Address or hostname?

          1. IP Address
          2. Hostname

          """)

    target = 0
    while target < 1 or target > 2:
        target = int(input("Select a number: "))

        # Select IP Address
        if target == 1:
            config = select_IP(config)

        # Select Host Name
        if target == 2:
            config = select_hostname(config)

    config['timeout'] = select_timeout()
    return config


def select_hostname(config: object):
    """
    Prompts user to select a hostname or create a new one.

    :param config: Current config object to be updated by the selection.
    """
    # Print current hostname options and select new option
    print("Select a Hostname or create a new one: ")
    host_list = config_options['servers']['hostname']
    host = select_from_config_list(host_list, create_host, True)

    config['server'] = host
    return config


def select_IP(config: object):
    """
    Prompts user to select an IP address or create a new one.
    :param config: Current config object to be updated by the selection.
    """
    # Prints current IP options and option for new IP
    print("Select an IP Address or create a new one: ")
    ip_list = config_options['servers']['ip_address']
    ip = select_from_config_list(ip_list, create_ip, True)

    config['server'] = ip
    return config


def select_port(config: object):
    """
    Prompts user to select a port or create a new one.

    :param config: Current config object to be updated by the selection.
    """
    # Print current port options and create new option.
    print("Select a port or create a new one: ")
    port_list = config_options['servers']['port']
    port = select_from_config_list(port_list, create_port, True)

    config['port'] = port
    return config


def select_HTTP(config: object):
    """
    Prompts user to select URL or create a new one.
    :param config: Current config object to be updated by the selection.
    """
    # Print current HTTP List and ooption for new URL
    http_list = config_options['servers']['http']
    print("Choose an URL or create a new one:\n")
    url = select_from_config_list(http_list, create_HTTP, True)

    config['server'] = url
    return config


def select_HTTPS(config: object):
    """
    Prompts user to select URL or create a new one.
    :param config: Current config object to be updated by the selection.
    """
    # Print current HTTPS List and create new option
    https_list = config_options['servers']['https']
    print("Choose an url or create a new one:")
    url = select_from_config_list(https_list, create_HTTPS, True)

    config['server'] = url
    config['timeout'] = select_timeout()
    return config


def create_port():
    """
    Gets new port from user and validates for correct port range.
    """
    def is_valid_port_number(port):
        if port < 0 or port > 65535:
            return False
        return True

    port = -1
    while not is_valid_port_number(port):
        port = input("Enter a valid port number (0-65535): ")
        try:
            port = int(port)
        except ValueError:
            print("Invalid input.")
        if not is_valid_port_number(port):
            print("Invalid port number.")
    config_options['servers']['port'].append(port)
    return port


def create_HTTP():
    """
    Gets new URL from user and validates for HTTP format.
    """
    def is_http_url(url_str):
        # Regular expression for HTTP URL pattern
        http_url_pattern = r'^http://(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:/[^\s]*)?$'

        # Check if the string matches the HTTP URL pattern
        match = re.match(http_url_pattern, url_str)
        return bool(match)

    url = ''
    while not is_http_url(url):
        url = input("Enter URL (with 'http://'): ")
        if not is_http_url(url):
            print("Invalid HTTP URL.")

    config_options['servers']['HTTP'].append(url)
    return url


def create_HTTPS():
    """
    Gets new URL from user and validates for HTTPS format.
    """

    def is_https_url(url_str):
        # Regular expression for HTTP URL pattern
        http_url_pattern = r'^https://(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:/[^\s]*)?$'

        # Check if the string matches the HTTP URL pattern
        match = re.match(http_url_pattern, url_str)
        return bool(match)

    url = ''
    while not is_https_url(url):
        url = input("URL (with 'https://'): ")
        if not is_https_url(url):
            print("Invalid HTTPS URL.")

    config_options['servers']['HTTPS'].append(url)
    return url


def create_host():
    """
    Gets new hostname from user and prompts for valid format.
    """

    def is_valid_hostname(hostname):
        # Regular expression for valid hostname pattern
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'

        # Check if the string matches the hostname pattern
        match = re.match(hostname_pattern, hostname)
        return bool(match)

    host = ''
    while not is_valid_hostname(host):
        host = input("Enter a valid hostname: ")
        if not is_valid_hostname(host):
            print("Invalid input.")

    config_options['servers']['hostname'].append(host)
    return host


def create_ip():
    """
    Prompts user for valid IPv4 address and validates for IPv4 format.
    """

    def is_ipv4_address(ip_str):
        # Regular expression for IPv4 address pattern
        ipv4_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'

        # Check if the string matches the IPv4 pattern
        match = re.match(ipv4_pattern, ip_str)
        if match:
            # Check if each octet is in the valid range (0-255)
            for octet in match.groups():
                if not (0 <= int(octet) <= 255):
                    return False
            return True
        else:
            return False

    ip = ''
    while not is_ipv4_address(ip):
        ip = input('Enter an IPv4 address: ')
        if not is_ipv4_address(ip):
            print('Invalid IPv4 address.')

    config_options['servers']['ip_address'].append(ip)
    return ip


def start_server_in_new_terminal():
    """
    Starts the echo server in a new terminal.
    """

    # Command to start the echo server
    server_command = 'python Echo_Server.py'

    # Open a new terminal and run the the server
    if sys.platform.startswith('win'):  # For Windows
        subprocess.run(['start', 'cmd', '/k', server_command], shell=True)
    elif sys.platform.startswith('darwin'):  # For macOS
        dir_path = os.path.dirname(os.path.realpath(__file__))
        server_command = f'cd {dir_path} && source .venv/bin/activate && python Echo_Server.py'
        tell.app('Terminal', 'do script "' + server_command + '"')
    elif sys.platform.startswith('linux'):  # For Linux
        subprocess.run(['x-terminal-emulator', '-e', server_command])
    else:
        print("Unsupported platform.")


# Worker thread function
def worker(stop_event: threading.Event, config: object) -> None:
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
                    f"{service:<6}| {"PASS" if success else "FAIL"} - (server: {server} code: {code})")

            # Run HTTPS Tests
            case 'HTTPS':
                success, code, message = check_server_https(server, config['timeout'])
                timestamped_print(f"{service:<6}| {"PASS" if success else "FAIL"} - (server: {server} code: {code} message: {message})")

            # Run ICMP Tests
            case 'ICMP':
                reply_address, response_time = ping(config['server'], 64, config['timeout'])
                timestamped_print(f"{service:<6}| {"PASS" if response_time else "FAIL"} - (server: {server} reply-address: {reply_address} time: {response_time})")

            case 'DNS':
                status, results = check_dns_server_status(config['dns'][1], config['server'], config['dns_type'])
                timestamped_print(f"{service:<6}| {"PASS" if status else "FAIL"} - ({config['dns'][0]}[{config['dns_type']}]  query: {server} results: {results})")

            case 'NTP':
                status, _ = check_ntp_server(config['server'])
                timestamped_print(f"{service:<6}| {"PASS" if status else "FAIL"} - (server-status: {server} {"is up." if status else "is down."})")

            case 'TCP':
                status, message = check_tcp_port(config['server'], config['port'])
                timestamped_print(f"{service:<6}| {"PASS" if status else "FAIL"} - (response-description: {message})")
            case 'UDP':
                status, message = check_tcp_port(config['server'], config['port'])
                timestamped_print(f"{service:<6}| {"PASS" if status else "FAIL"} - (response-description: {message})")
            case 'ECHO':
                message = tcp_client('Echo test.')
                timestamped_print(f"{service:<6}| {"PASS" if message else "FAIL"} - (server-message: {message})")

        time.sleep(config['time'])
        pass


def main():
    """
    Main function to handle user input and manage threads.
    Uses prompt-toolkit for handling user input with auto-completion and 
    ensures the prompt stays at the bottom of the terminal.
    """

    start_server_in_new_terminal()

    banner()

    config = global_config

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
                        for service_config in global_config:
                            worker_thread: threading.Thread = threading.Thread(
                                target=worker, args=(stop_event, service_config))
                            worker_thread.start()

                    case 'stop':
                        if worker_thread.is_alive():
                            stop_event.set()
                            worker_thread.join()
                        else:
                            print("Network tests have not been started.")

                    case 'config':
                        print_selected_config()

                    case 'set':
                        global_config.append(set_config_sequence())

                    case 'delete':
                        delete_config_option()

                    case 'exit':
                        print("Exiting application...")
                        tcp_client('exit')
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


if __name__ == "__main__":
    main()
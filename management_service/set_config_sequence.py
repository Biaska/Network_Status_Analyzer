import re

def set_config_sequence(mgr):
    """
    Creates a new config object by getting user input. 
    """
    global config_options 
    config_options = mgr.config_options

    print("""
        Create or edit a service or task:
          
            1. Service
            2. Task
          
    """)
    option = 0
    option = input("Enter a number: ")
    while option < 1 or option > 2:
        try: 
            option = int(option)
        except ValueError:
            print("Invalid input.")
    if option == 1:
        service_config_sequence()
    else:
        task_config_sequence()


def service_config_sequence():
    """
    Starts input sequence to edit or create service monitor connections.
    """
    pass

def task_config_sequence():
    """
    Starts inpit sequence to edit or create sertvice tasks.
    """
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


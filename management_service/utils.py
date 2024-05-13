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


def print_service_tasks(service):
    tasks = service["tasks"]
    for i in range(len(tasks)):
        print(f"===== Service Task {i+1} =====")
        print(f"\nService to be tested: {tasks[i]["service"]}")
        print(f"Target server: {tasks[i]['server']}")
        if 'dns' in tasks[i]:
            print(f'Public DNS: {tasks[i]["dns"]}')
            print(f'Domain record type: {tasks[i]["dns_type"]}')
        if "port" in tasks[i]:
            print(f'Port number: {tasks[i]["port"]}')
        if "timeout" in tasks[i]:
            print(f'Response timeout interval(seconds): {tasks[i]["timeout"]}')
        print(f"Time interval(seconds): {tasks[i]['time']}\n")


def print_service_list(self, services, tasks=False):
    """
    Prints the current global config objects.
    """
    if self.no_of_services == 0:
        print("No monitoring services configured")
    else:
        for i in range(self.no_of_services):
            print(f"===== Monitor Service {services[i]["id"]} =====")
            print(f"IP Address: {services[i]["ip_address"]}")
            print(f"Port: {services[i]["port"]}")
            if tasks:
                print("===== Service Tasks List =====")
                print_service_tasks(services[i])



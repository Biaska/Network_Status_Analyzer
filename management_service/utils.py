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
        set: start the sequence to add a new service or task configuration
        status: get server monitor status from each running server
        exit: exit the program
    """
    print(commands)


def print_service_tasks(tasks):
    for i in range(len(tasks)):
        print(f"===== Service Task {i+1} =====")
        print(f"\nService to be tested: {tasks[i]['config']["service"]}")
        print(f"Target server: {tasks[i]['config']['server']}")
        if 'dns' in tasks[i]['config']:
            print(f'Public DNS: {tasks[i]['config']["dns"]}')
            print(f'Domain record type: {tasks[i]['config']["dns_type"]}')
        if "port" in tasks[i]['config']:
            print(f'Port number: {tasks[i]['config']["port"]}')
        if "timeout" in tasks[i]['config']:
            print(f'Response timeout interval(seconds): {tasks[i]['config']["timeout"]}')
        print(f"Time interval(seconds): {tasks[i]['config']['time']}\n")


def print_service_list(services, tasks=False):
    """
    Prints the current global config objects.
    """
    if len(services) == 0:
        print("No monitoring services configured")
    else:
        for i in range(len(services)):
            print(f"===== Monitor Service {i+1} =====\n")
            print(f"ID: {services[i]["id"]}")
            print(f"IP Address: {services[i]["ip_address"]}")
            print(f"Port: {services[i]["port"]}\n")
            if tasks:
                if len(services[i]['tasks']) == 0:
                    print("===== No Tasks Configured =====\n")
                else:    
                    print("===== Service Tasks List =====")
                    print_service_tasks(services[i]['tasks'])


def get_unrelated_services(services, id, only_ids=False):
    unrelated_services = []
    for i in range(len(services)):
        unrelated = True
        for j in range(len(services[i]['tasks'])):
            if services[i]['tasks'][j]["id"] == id:
                unrelated = False
        if unrelated:
            if only_ids:
                unrelated_services.append(services[i]['id'])
            else:
                unrelated_services.append(services[i])
    return unrelated_services


def get_unrelated_tasks(tasks, service):
    related_tasks = []
    unrelated = []
    for i in range(len(service['tasks'])):
        related_tasks.append(service['tasks'][i]['id'])
    for i in range(len(tasks)):
        if tasks[i]['id'] not in related_tasks:
            unrelated.append(tasks[i])
    return unrelated



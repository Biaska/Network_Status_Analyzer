# Network Analyzer CLI Application

## Installation and Startup

Install the directory and open a terminal in the directory.

Install the required packages(Recommended to install inside a virtual environment: 

`pip install -r requirements.txt`

Run the management service in one terminal:

`cd management_service`

`sudo python management_service.py`

Run the monitor service in another terminal and specify a server address, and port:

`cd monitoring_service`

`sudo python monitoring_service.py 127.0.0.1 12345`

## Start Screen

```
=====================================================================        

  _  _     _                  _       _             _                 
 | \| |___| |___ __ _____ _ _| |__   /_\  _ _  __ _| |_  _ ______ _ _ 
 | .` / -_)  _\ V  V / _ \ '_| / /  / _ \| ' \/ _` | | || |_ / -_) '_|
 |_|\_\___|\__|\_/\_/\___/_| |_\_\ /_/ \_\_||_\__,_|_|\_, /__\___|_|  
                                                      |__/                     

=====================================================================

Analyze network address for response speeds. Run the default
configuration, choose a different one, or add more.

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
```

## Commands

Run commands at any time, except when the set sequence
to create a new configuration object has been initiated.

## Configuration

Check the configuration with the `config` command. There is a default 
configuration with some randomly selected services and the echo server. New 
service configurations can be added with the `set` command which will start 
a sequence of prompts to choose a service and the appropriate parameters. 
Delete a service configuration from the global configuration using the 
`delete` command.

## Testing

Start continous test using the current global configuration objects with the
`start` command. Stop the tests at anytime with the `stop` command. 







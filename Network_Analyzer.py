#!/usr/bin/env python3
import threading
import time
from Echo_Client import tcp_client
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.patch_stdout import patch_stdout
import subprocess
import sys


def start_server_in_new_terminal():

    server_command = 'python Echo_Server.py'

    if sys.platform.startswith('win'):  # For Windows
        subprocess.run(['start', 'cmd', '/k', server_command], shell=True)
    elif sys.platform.startswith('darwin'):  # For macOS
        subprocess.run(['open', '-a', 'Terminal', server_command])
    elif sys.platform.startswith('linux'):  # For Linux
        subprocess.run(['x-terminal-emulator', '-e', server_command])
    else:
        print("Unsupported platform.")


# Worker thread function
def worker(stop_event: threading.Event) -> None:
    """
    Prints a message every 5 seconds until stop_event is set.
    """
    while not stop_event.is_set():
        print("Hello")
        time.sleep(5)
        # tcp_server()
        pass


def main():
    """
    Main function to handle user input and manage threads.
    Uses prompt-toolkit for handling user input with auto-completion and 
    ensures the prompt stays at the bottom of the terminal.
    """

    start_server_in_new_terminal()

    # Event to signal the worker thread to stop
    stop_event: threading.Event = threading.Event()

    # Create and start the worker thread
    worker_thread: threading.Thread = threading.Thread(
        target=worker, args=(stop_event,))
    worker_thread.start()

    # Command completer for auto-completion
    # This is where you will add new auto-complete commands
    command_completer: WordCompleter = WordCompleter(
        ['exit', 'test'], ignore_case=True)

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

                    case 'test':
                        tcp_client('hello')

                    case 'exit':
                        tcp_client('exit')
                        print("Exiting application...")
                        is_running = False

                # # This is where you create the actions for your commands
                # if user_input == "exit":
                #     print("Exiting application...")
                #     is_running = False
    
    except KeyboardInterrupt:
        tcp_client('exit')

    finally:
        # Signal the worker thread to stop and wait for its completion
        stop_event.set()
        worker_thread.join()


if __name__ == "__main__":
    main()
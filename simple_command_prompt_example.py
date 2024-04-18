import threading
from TCP_UDP_Client_Servers import tcp_server, tcp_client
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.patch_stdout import patch_stdout


# Worker thread function
def worker(stop_event: threading.Event) -> None:
    """
    Prints a message every 5 seconds until stop_event is set.
    """
    while not stop_event.is_set():
        # tcp_server()
        pass

# Main function
def main() -> None:
    """
    Main function to handle user input and manage threads.
    Uses prompt-toolkit for handling user input with auto-completion and 
    ensures the prompt stays at the bottom of the terminal.
    """
    # Event to signal the worker thread to stop
    stop_event: threading.Event = threading.Event()

    # Create and start the worker thread
    worker_thread: threading.Thread = threading.Thread(
        target=worker, args=(stop_event,))
    worker_thread.start()

    # Command completer for auto-completion
    # This is where you will add new auto-complete commands
    command_completer: WordCompleter = WordCompleter(
        ['exit'], ignore_case=True)

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
                        tcp_client()

                # This is where you create the actions for your commands
                if user_input == "exit":
                    print("Exiting application...")
                    is_running = False
    finally:
        # Signal the worker thread to stop and wait for its completion
        stop_event.set()
        worker_thread.join()


if __name__ == "__main__":
    main()

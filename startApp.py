import subprocess
import sys
import socket

IP = socket.gethostbyname(socket.gethostname())


def printError(*args):
    """Prints a message in red"""
    message = ""
    for i in args:
        message = message + str(i) + " "
    print(f"\033[91m{message}\033[0m")


def run_commands(commands):
    processes = []

    for command in commands:
        process = subprocess.Popen(
            ['start', 'cmd', '/K', command[0]], shell=True, cwd=command[1])
        processes.append(process)

    for process in processes:
        process.wait()

if __name__ == '__main__':
    location = sys.argv[1]
    if location == "home":
        i = r'C:\Users\spark\OneDrive\Desktop\Game Of Life'
    elif location == "laptop":
        i = r'C:\Users\spark\OneDrive\Desktop\Game Of Life'
    else:
        i = r'C:\Users\spark\OneDrive\Desktop\Game Of Life'
    commands = [
        ('python clientTest.py', i),
        ('python clientTest.py', i),
        ('python serverTest.py', i)
    ]
    print(commands)
    run_commands(commands)

"""
Writes text to the terminal with colour
"""

def printWarning(*args):
    """Prints a message in yellow"""
    message = ""
    for i in args:
        message = message + str(i) + " "
    print(f"\033[93m{message}\033[0m")


def printError(*args):
    """Prints a message in red"""
    message = ""
    for i in args:
        message = message + str(i) + " "
    print(f"\033[91m{message}\033[0m")


def printStatus(*args):
    """Prints a message in green"""
    message = ""
    for i in args:
        message = message + str(i) + " "
    print(f"\033[92m{message}\033[0m")

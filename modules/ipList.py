"""
Used to:
- Get the local IP address of the machine
- Get a list of stored IP addresses
- Add a new IP address to the list
"""
import socket

def getLocalIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        localIP = s.getsockname()[0]
    except Exception as e:
        localIP = "Unable to get local IP"
    finally:
        s.close()

    return localIP


def getIPList():
    listfile = open('modules/iplist', 'r')
    ipList = []
    for line in listfile:
        ipList.append(line.strip())
    listfile.close()
    return ipList


def addToIPList(ip):
    listfile = open('modules/iplist', 'a')
    listfile.write(ip + '\n')
    listfile.close()
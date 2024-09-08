import socket
import json
import threading
from time import sleep
import colouredText as ct
import snake

def socketListener():
    global gameID, gameHost, snakeInfo, gameStart, gameEnvironment, collision
    while True:
        try:
            data, addr = clientSocket.recvfrom(4096)
        except Exception as e:
            if type(e) == socket.timeout:
                continue
            elif type(e) == KeyboardInterrupt:
                return
            elif type(e) == WindowsError:
                ct.printError("Connection closed")
                return
            else:
                ct.printError(f"Error: {e}")
                continue

        try:
            #print(f"Received: {data}")
            data = json.loads(data)
            if data['type'] == 'disconnect':
                break
            elif data['type'] == 'createGame':
                ct.printStatus(f"Game created: {data['data']['id']}")
                gameID = data['data']['id']
                gameHost = True
            elif data['type'] == 'joinGame':
                ct.printStatus(f"Game joined: {data['data']['id']}")
                gameID = data['data']['id']
                gameHost = False
            elif data['type'] == 'startGameRes':
                if 'fail' in data['data']:
                    ct.printWarning(
                        f"Game start failed: {data['data']['message']}")
                else:
                    ct.printStatus(f"Game started: {data['data']['id']}")
                    snakeInfo = data['data']['snakeInfo']
            elif data['type'] == 'startGame':
                ct.printStatus(f"Game started: {data['data']['id']}")
                gameStart = True
            elif data['type'] == 'updateEnvironment':
                gameEnvironment = data['data']['environment']
                collision = data['data']['collision']
                if collision[0] and snakeGame is not None:
                    pass
                """
                    if collision[1] == 'wall':
                        snakeGame.quitProgram()
                        collision = (False, None, None)
                    elif collision[1] == 'food':
                        snakeGame.increaseSnakeLength()
                        collision = (False, None, None)
                    elif collision[1] == 'body':
                        snakeGame.quitProgram()
                        collision = (False, None, None)
                    elif collision[1] == 'self':
                        snakeGame.quitProgram()
                        collision = (False, None, None)"""
        except Exception as e:
            ct.printError(f"Error: {e}")
            break

def commandThread():
    while True:
        try:
            data = input('enter function: ')
            if data == 'disconnect':
                clientSocket.sendto(json.dumps({'type': 'disconnect', 'data': {'id': clientID}}).encode(), (SERVER_IP, 65432))
                break
            elif data == 'createGame':
                clientSocket.sendto(json.dumps({'type': 'createGame', 'data': {'id': clientID}}).encode(), (SERVER_IP, 65432))
            elif data == 'joinGame':
                userGameID = input('enter game id: ')
                clientSocket.sendto(json.dumps({'type': 'joinGame', 'data': {'id': clientID, 'gameID': userGameID}}).encode(), (SERVER_IP, 65432))
                return
            elif data == 'startGame':
                if gameHost and gameID is not None:
                    clientSocket.sendto(json.dumps({'type': 'startGameReq', 'data': {'id': clientID, 'gameID': gameID}}).encode(), (SERVER_IP, 65432))
                    return
            elif data == 'quick':
                clientSocket.sendto(json.dumps({'type': 'createGame', 'data': {'id': clientID}}).encode(), (SERVER_IP, 65432))
                sleep(0.5)
                clientSocket.sendto(json.dumps({'type': 'startGameReq', 'data': {'id': clientID, 'gameID': gameID}}).encode(), (SERVER_IP, 65432))
                return
            sleep(0.1)
        except KeyboardInterrupt:
            break

def getIPList():
    listfile = open('iplist', 'r')
    ipList = []
    for line in listfile:
        ipList.append(line.strip())
    listfile.close()
    return ipList

def addToIPList(ip):
    listfile = open('iplist', 'a')
    listfile.write(ip + '\n')
    listfile.close()

def attemptConnection(ipList):
    data, addr = None, None
    clientSocket.settimeout(0.3)
    for ip in ipList:
        try:
            clientSocket.sendto(json.dumps({'type': 'ping', 'data': {}}).encode(), (ip, 65432))
            data, addr = clientSocket.recvfrom(4096)
        except Exception as e:
            if type(e) == socket.timeout:
                print('bad ip')
            elif type(e) == KeyboardInterrupt:
                break
            elif type(e) == TimeoutError:
                break
            else:
                print("Error:", e)
                continue
        if data is not None:
            return ip
    return None

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

SERVER_IP = attemptConnection(getIPList())

if SERVER_IP is None:
    SERVER_IP = input('server could not be found. Enter ip: ')
    addToIPList(SERVER_IP)

name = input('enter name: ')
clientSocket.settimeout(0.1)
clientID = None
gameID = None
gameHost = False
snakeGame = None
gameStart = False
gameEnvironment = []
snakeInfo = []
collision = (False, None, None)

clientSocket.sendto(json.dumps({'type': 'connect', 'data': {'name': name}}).encode(), (SERVER_IP, 65432))

while clientID is None:
    try:
        data, addr = clientSocket.recvfrom(4096)
        print(f"Received: {data}")
        data = json.loads(data)
        
        if data['type'] == 'connect':
            clientID = data['data']['id']
    except Exception as e:
        if type(e) == socket.timeout:
            continue
        elif type(e) == KeyboardInterrupt:
            break
        else:
            print("Error:", e)
            continue


socketThread = threading.Thread(target=socketListener)
socketThread.start()

testThread = threading.Thread(target=commandThread, daemon=True)
testThread.start()

while not gameStart:
    try:
        sleep(0.1)
    except KeyboardInterrupt:
        break

testThread.join(timeout=0.1)

snakeGame = snake.snakeGame((800, 600), 40, snakeInfo)
snakeGame.startGame()

while snakeGame.running:
    try:
        snakeGame.processSnakeChange()
        if not snakeGame.running:
            break
        clientSnake = snakeGame.snake
        clientEnvironment = snakeGame.getSnakeAsEnvironment()

        clientSocket.sendto(json.dumps({'type': 'clientUpdate', 'data': {'id': clientID, 'snake':clientSnake, 'environment':clientEnvironment}}).encode(), (SERVER_IP, 65432))
        
        snakeGame.updateEnvironment(gameEnvironment)
        
        snakeGame.drawEnvironment()
        gameEnvironment = []

        snakeGame.playFrame()
        sleep(0.15)
    except KeyboardInterrupt:
        break

#need to work on clean exit
socketThread.join(timeout=0.1)

clientSocket.sendto(json.dumps({'type': 'disconnect', 'data': {'id': clientID}}).encode(), (SERVER_IP, 65432))
clientSocket.close()

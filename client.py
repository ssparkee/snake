import socket
import json
import threading
from time import sleep
import modules.colouredText as ct
import modules.snake as snake
import modules.ipList as ipList

def socketListener():
    global gameID, gameHost, snakeInfo, gameStart, gameEnvironment, collision, snakeGame
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
            data = json.loads(data)
            if data['type'] == 'disconnect':
                break
            elif data['type'] == 'createGame':
                ct.printStatus(f"Game created: {data['data']['code']}")
                gameID = data['data']['id']
                gameHost = True
            elif data['type'] == 'joinGame':
                ct.printStatus(f"Game joined: {data['data']['id']}")
                gameID = data['data']['id']
                gameHost = False
            elif data['type'] == 'getGames':
                ct.printStatus(f"Games: {data['data']['games']}")
            elif data['type'] == 'startGameRes':
                if 'fail' in data['data']:
                    ct.printWarning(
                        f"Game start failed: {data['data']['message']}")
                else:
                    ct.printStatus(f"Game starting soon: {data['data']['id']}")
                    snakeInfo = data['data']['snakeInfo']
                    gameStart = 1
            elif data['type'] == 'startGame':
                ct.printStatus(f"Game started: {data['data']['id']}")
                gameStart = 2
            elif data['type'] == 'updateEnvironment':
                gameEnvironment = data['data']['environment']
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
                userGameID = input('enter game code: ')
                clientSocket.sendto(json.dumps({'type': 'joinGame', 'data': {'id': clientID, 'code': userGameID}}).encode(), (SERVER_IP, 65432))
                return
            elif data == 'getGames':
                clientSocket.sendto(json.dumps({'type': 'getGames', 'data': {'id': clientID}}).encode(), (SERVER_IP, 65432))
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

def attemptConnection(ipList, testLocal=True):
    data, addr = None, None
    clientSocket.settimeout(0.3)
    for ip in ipList:
        try:
            clientSocket.sendto(json.dumps({'type': 'ping', 'data': {}}).encode(), (ip, 65432))
            data, addr = clientSocket.recvfrom(4096)
            if data is not None:
                print(data)
                return ip
        except Exception as e:
            if type(e) == socket.timeout:
                continue
            elif type(e) == KeyboardInterrupt:
                break
            elif type(e) == TimeoutError:
                continue
            else:
                print("Error:", e)
                continue
    if testLocal:
        try:
            ip = ipList.getLocalIP()
            clientSocket.sendto(json.dumps({'type': 'ping', 'data': {}}).encode(), (ip, 65432))
            data, addr = clientSocket.recvfrom(4096)
            if data is not None:
                ipList.addToIPList(ip)
                return ip
        except:
            return None
    return None

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

SERVER_IP = attemptConnection(ipList.getIPList())

if SERVER_IP is None:
    while SERVER_IP is None:
        i = input('server could not be found. Enter ip: ')
        SERVER_IP = attemptConnection([i], False)
    ipList.addToIPList(SERVER_IP)

name = input('enter name: ')
clientSocket.settimeout(0.1)
clientID = None
gameID = None
gameHost = False
snakeGame = None
gameStart = 0
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
        elif type(e) == WindowsError:
            continue
        else:
            print("Error:", e)
            continue

socketThread = threading.Thread(target=socketListener)
socketThread.start()

testThread = threading.Thread(target=commandThread, daemon=True)
testThread.start()

while gameStart == 0:
    try:
        if gameID is not None:
            clientSocket.sendto(json.dumps({'type': 'gameStatus', 'data': {'id': clientID}}).encode(), (SERVER_IP, 65432))
        sleep(0.1)
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(e)

testThread.join(timeout=0.1)
if len(snakeInfo) == 0:
    clientSocket.sendto(json.dumps({'type': 'disconnect', 'data': {
                        'id': clientID}}).encode(), (SERVER_IP, 65432))
    clientSocket.close()
    socketThread.join(timeout=0.1)
    quit()
snakeGame = snake.snakeGame((800, 600), 40, snakeInfo)
clientSocket.sendto(json.dumps({'type': 'clientUpdate', 'data': {'id': clientID, 'snake': snakeGame.snake}}).encode(), (SERVER_IP, 65432))
sleep(0.1)
while gameStart == 1:
    try:
        snakeGame.updateEnvironment(gameEnvironment)
        snakeGame.getMoveQueue()
        snakeGame.moveQueue = []
        snakeGame.playFrame()
        sleep(0.15)
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(e)

snakeGame.startGame()

while snakeGame.running:
    try:
        snakeGame.processSnakeChange()
        if not snakeGame.running:
            break
        clientSnake = snakeGame.snake

        clientSocket.sendto(json.dumps({'type': 'clientUpdate', 'data': {'id': clientID, 'snake':clientSnake}}).encode(), (SERVER_IP, 65432))
        
        snakeGame.updateEnvironment(gameEnvironment)

        snakeGame.playFrame()
        sleep(0.15)
    except KeyboardInterrupt:
        break

#need to work on clean exit
socketThread.join(timeout=0.1)

clientSocket.sendto(json.dumps({'type': 'disconnect', 'data': {'id': clientID}}).encode(), (SERVER_IP, 65432))
clientSocket.close()
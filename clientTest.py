import socket
import json
import threading
from time import sleep
import colouredText as ct
import snake

def socketListener():
    global gameID, gameHost, snakeGame, gameStart, gameEnvironment
    while True:
        try:
            data, addr = clientSocket.recvfrom(1024)
            print(f"Received: {data}")
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
                    snakeGame = snake.snakeGame((800, 600), 40, data['data']['snakeInfo'])
                    snakeGame.startGame()
            elif data['type'] == 'startGame':
                ct.printStatus(f"Game started: {data['data']['id']}")
                gameStart = True
            elif data['type'] == 'updateEnvironment':
                gameEnvironment = data['data']['environment']

        except socket.timeout:
            continue
        except KeyboardInterrupt:
            break
        except WindowsError:
            ct.printError("Connection closed")
            break
        except Exception as e:
            ct.printError(f"Error: {e}")
            break

def commandThread():
    while True:
        try:
            data = input('enter function: ')
            if data == 'disconnect':
                clientSocket.sendto(json.dumps({'type': 'disconnect', 'data': {'id': clientID}}).encode(), ('localhost', 65432))
                break
            elif data == 'createGame':
                clientSocket.sendto(json.dumps({'type': 'createGame', 'data': {'id': clientID}}).encode(), ('localhost', 65432))
            elif data == 'joinGame':
                userGameID = input('enter game id: ')
                clientSocket.sendto(json.dumps({'type': 'joinGame', 'data': {'id': clientID, 'gameID': userGameID}}).encode(), ('localhost', 65432))
            elif data == 'startGame':
                if gameHost and gameID is not None:
                    clientSocket.sendto(json.dumps({'type': 'startGameReq', 'data': {'id': clientID, 'gameID': gameID}}).encode(), ('localhost', 65432))
            sleep(0.1)
        except KeyboardInterrupt:
            break

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#clientSocket.sendto(b'Hello from client', ('localhost', 65432))
name = input('enter name: ')

clientSocket.sendto(json.dumps({'type': 'connect', 'data':{'name':name}}).encode(), ('localhost', 65432))
clientSocket.settimeout(0.1)

clientID = None
gameID = None
gameHost = False
snakeGame = None
gameStart = False
gameEnvironment = []
while clientID is None:
    try:
        data, addr = clientSocket.recvfrom(1024)
        print(f"Received: {data}")
        data = json.loads(data)
        
        if data['type'] == 'connect':
            clientID = data['data']['id']
    except socket.timeout:
        continue
    except KeyboardInterrupt:
        break


socketThread = threading.Thread(target=socketListener)
socketThread.start()

testThread = threading.Thread(target=commandThread, daemon=True)
testThread.start()

while not gameStart:
    try:
        pass
    except KeyboardInterrupt:
        break
while True:
    snakeGame.processSnakeChange()
    snakeGame.updateEnvironment(gameEnvironment)

    snakeGame.playFrame()
    sleep(0.15)

clientSocket.close()

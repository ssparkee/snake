import socket
from uuid import uuid4
import json
import pygame
import colouredText as ct
from random import randint
import threading
from time import sleep

class Client:
    def __init__(self, name, clientID, addr, gameID=None):
        self.id = clientID
        self.snake = {
            'head': (0, 0),
            'body': [(0, 0)],
            'direction': (0, 0),
            'last': (0, 0)
        }
        self.length = 3
        self.name = name
        self.addr = addr
        self.gameID = gameID
        self.environment = []

    def connectToGame(self, gameID):
        self.gameID = gameID


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

def getClientsInGame(gameID):
    return [client for client in clients.values() if client.gameID == gameID]

def newGame():
    gameID = str(uuid4())
    games[gameID] = {
        'id': gameID,
        'players': [],
        'state': 'waiting',
        'food': [],
        'board': []
    }
    return gameID


clients = {}
games = {}
gameThreads = []
GRIDWIDTHPX = 800
GRIDHEIGHTPX = 600
BLOCKSIZE = 40
GRIDWIDTH = GRIDWIDTHPX // BLOCKSIZE
GRIDHEIGHT = GRIDHEIGHTPX // BLOCKSIZE
FOODCOUNT = 3

gameExample = {
    'id': '1234',
    'players': ['1234', '5678'],
    'state': 'running',
    'food': [(1, 1), (2, 2), (3, 3)],
    'objects': [pygame.Rect(0,0,40,40)]
}

SERVER_IP = getLocalIP()
MINPLAYERS = 1

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((SERVER_IP, 65432))
serverSocket.settimeout(0.1)

ct.printStatus(f"UDP Server is listening, IP: {SERVER_IP}")

def sendToClient(clientID, data):
    serverSocket.sendto(json.dumps(data).encode(), clients[clientID].addr)


def getPlayerSnake(gameID, clientID):
    return clients[clientID].snake

def setPlayerSnake(gameID, clientID, snake):
    clients[clientID].snake = snake

def setPlayerEnvironment(gameID, clientID, environment):
    clients[clientID].environment = environment

def getPlayerEnvironment(clientID):
    return clients[clientID].environment

def getFoodSpawn(gameID):
    foodPos = (randint(0, GRIDWIDTH-1), randint(0, GRIDHEIGHT-1))
    while isOccupied(gameID, foodPos[0], foodPos[1])[0]:
        foodPos = (randint(0, GRIDWIDTH-1), randint(0, GRIDHEIGHT-1))
    print('food:', foodPos)
    return foodPos

def getEnvironmentExclusive(gameID, clientID):
    environment = []
    for client in getClientsInGame(gameID):
        if client.id != clientID:
            print('not same')
            for i in getPlayerEnvironment(client.id):
                environment.append(i)
    for food in games[gameID]['food']:
        environment.append({'type': 'food', 'pos': food})
    return environment

def isOccupied(gameID, x, y, clientID=''):
    for client in getClientsInGame(gameID):
        if client.id != clientID:
            for part in client.snake['body']:
                if part == [x, y]:
                    return (True, 'body', client.id)
        else:
            if int(client.snake['length']) > 3:
                for part in client.snake['body']:
                    if part == [x, y]:
                        return (True, 'self', client.id)
    if x < 0 or x >= GRIDWIDTH or y < 0 or y >= GRIDHEIGHT:
        return (True, 'wall', None)
    if (x, y) in games[gameID]['food']:
        games[gameID]['food'].remove((x, y))
        games[gameID]['food'].append(getFoodSpawn(gameID))
        return (True, 'food', None)
    return (False, None, None)

def createSnakeSpawn(gameID):
    headPos = (randint(0, 1) * (GRIDWIDTH-1), randint(0, GRIDHEIGHT-1))
    while isOccupied(gameID, headPos[0], headPos[1])[0]:
        headPos = (randint(0, 1) * (GRIDWIDTH-1), randint(0, GRIDHEIGHT-1))

    if headPos[0] == 0:
        direction = (1, 0)
    else:
        direction = (-1, 0)
    body = [headPos, headPos]
    return ({'length':3, 'head': headPos, 'body': body, 'direction': direction, 'last': (0, 0)}, direction[0])

def gameThread(gameID):
    sleep(1)
    gameClients = getClientsInGame(gameID)
    for client in gameClients:
        sendToClient(client.id, {
            'type': 'startGame',
            'data': {'id': gameID, 'start':'for real this time'}
        })
    while games[gameID]['state'] == 'running':
        for client in gameClients:
            try:
                sendToClient(client.id, {
                    'type': 'updateEnvironment',
                    'data': {'environment': getEnvironmentExclusive(gameID, client.id), 'collision': isOccupied(gameID, client.snake['head'][0], client.snake['head'][1], clientID=client.id)}
                })
            except KeyError:
                continue
            except RuntimeError:
                continue
        if len(gameClients) == 0:
            games[gameID]['state'] = 'over'
            return

while True:
    try:
        data, addr = serverSocket.recvfrom(4096)
    except Exception as e:
        if type(e) == socket.timeout:
            continue
        elif type(e) == KeyboardInterrupt:
            print("Closing server...")
            serverSocket.close()
            for thread in gameThreads:
                thread.close()
            quit()
            break
        elif type(e) == ConnectionResetError:
            continue
        else:
            print("Error:", e)
            continue

    try:
        data = json.loads(data)

        if data['type'] == 'connect':
            clientID = str(uuid4())
            clients[clientID] = Client(data['data']['name'], clientID, addr)

            sendToClient(clientID, {'type': 'connect', 'data': {'id': clientID}})
            ct.printStatus(f"Client connected: {clientID} / {clients[clientID].name}")

        elif data['type'] == 'disconnect':
            clientID = data['data']['id']
            sendToClient(clientID, {'type': 'disconnect', 'data': {'id': clientID}})
            ct.printStatus(f"Client disconnected: {clientID} / {clients[clientID].name}")
            for gameID in games:
                if clientID in games[gameID]['players']:
                    games[gameID]['players'].remove(clientID)
            del clients[clientID]

        elif data['type'] == 'ping':
            serverSocket.sendto(json.dumps({'type': 'ping', 'data': {}}).encode(), addr)
            ct.printStatus(f"Ping from IP {addr[0]}")

        elif data['type'] == 'createGame':
            gameID = newGame()
            clientID = data['data']['id']
            clients[clientID].connectToGame(gameID)
            games[gameID]['players'].append(clientID)

            sendToClient(clientID, {'type': 'createGame', 'data': {'id': gameID}})
            ct.printStatus(f"Game created: {gameID} with host {clientID} / {clients[clientID].name}")

        elif data['type'] == 'joinGame':
            gameID = data['data']['gameID']
            clientID = data['data']['id']
            clients[clientID].connectToGame(gameID)
            games[gameID]['players'].append(clientID)

            sendToClient(clientID, {'type': 'joinGame', 'data': {'id': gameID}})
            ct.printStatus(f"Game joined: {gameID} with player {clientID} / {clients[clientID].name}")

        elif data['type'] == 'startGameReq':
            gameID = data['data']['gameID']
            clientID = data['data']['id']

            if len(games[gameID]['players']) < MINPLAYERS:
                sendToClient(clientID, {'type': 'startGameRes', 'data': {'fail': True, 'message': 'Not enough players'}})
                continue
            else:
                games[gameID]['state'] = 'running'
                games[gameID]['food'] = [getFoodSpawn(gameID) for i in range(FOODCOUNT)]
                #sendToClient(clientID, {'type': 'startGame', 'data': {'id': gameID}})

                gameClients = getClientsInGame(gameID)
                for client in gameClients:
                    sendToClient(client.id, {
                        'type': 'startGameRes', 
                        'data': {
                            'id': gameID,
                            'snakeInfo': createSnakeSpawn(gameID), 
                            'players': [client.id for client in gameClients],
                            'gridpx': (GRIDWIDTHPX, GRIDHEIGHTPX),
                            'blocksize': BLOCKSIZE
                        }
                    })
                
                ct.printStatus(f"Game initialised: {gameID} with players {games[gameID]['players']}")

                gameThreads.append(threading.Thread(target=gameThread, args=(gameID,), daemon=True))
                gameThreads[-1].start()
        
        elif data['type'] == 'clientUpdate':
            clientID = data['data']['id']
            gameID = clients[clientID].gameID
            
            setPlayerSnake(gameID, clientID, data['data']['snake'])
            setPlayerEnvironment(gameID, clientID, data['data']['environment'])

    except Exception as e:
        if type(e) == json.decoder.JSONDecodeError:
            print("Invalid JSON received")
        elif type(e) == KeyError:
            print("Invalid data received")
        else:
            print("Invalid data received", e)
            continue
    
    
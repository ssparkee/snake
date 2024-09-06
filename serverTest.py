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
        self.name = name
        self.addr = addr
        self.gameID = gameID

    def connectToGame(self, gameID):
        self.gameID = gameID

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
GRIDWIDTHPX = 800
GRIDHEIGHTPX = 600
BLOCKSIZE = 40
GRIDWIDTH = GRIDWIDTHPX // BLOCKSIZE
GRIDHEIGHT = GRIDHEIGHTPX // BLOCKSIZE

gameExample = {
    'id': '1234',
    'players': ['1234', '5678'],
    'state': 'running',
    'food': [(1, 1), (2, 2), (3, 3)],
    'objects': [pygame.Rect(0,0,40,40)]
}

SERVER_IP = '127.0.0.1'

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((SERVER_IP, 65432))
serverSocket.settimeout(0.1)

ct.printStatus("UDP Server is listening...")

def sendToClient(clientID, data):
    serverSocket.sendto(json.dumps(data).encode(), clients[clientID].addr)


def getPlayerSnake(gameID, clientID):
    return clients[clientID].snake

def isOccupied(gameID, x, y):
    for client in getClientsInGame(gameID):
        for part in client.snake['body']:
            if part == (x, y):
                return (True, 'body', client.id)
    #add food check
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
    return
    while True:
        pass

while True:
    try:
        data, addr = serverSocket.recvfrom(1024)
    except socket.timeout:
        continue
    try:
        data = json.loads(data)
        print(f"Received: {data} from {addr}")


        if data['type'] == 'connect':
            clientID = str(uuid4())
            clients[clientID] = Client(data['data']['name'], clientID, addr)

            sendToClient(clientID, {'type': 'connect', 'data': {'id': clientID}})
            ct.printStatus(f"Client connected: {clientID} / {clients[clientID].name}")

        elif data['type'] == 'disconnect':
            clientID = data['data']['id']
            del clients[clientID]

            sendToClient(clientID, {'type': 'disconnect', 'data': {'id': clientID}})
            ct.printStatus(f"Client disconnected: {clientID} / {clients[clientID].name}")

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

            if len(games[gameID]['players']) < 2:
                sendToClient(clientID, {'type': 'startGameRes', 'data': {'fail': True, 'message': 'Not enough players'}})
                continue
            else:
                games[gameID]['state'] = 'running'

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

                threading.Thread(target=gameThread, args=(gameID,)).start()


    except Exception as e:
        print("Invalid data received", e)
        continue

    except KeyboardInterrupt:
        print("Closing server...")
        serverSocket.close()
        break
    
    
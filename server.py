import socket
from uuid import uuid4
import json
import pygame
import modules.colouredText as ct
from random import randint
import threading
from time import sleep, time


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
        self.lastMessageTimestamp = str(int(time()))

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
    global games
    gameCode = str(randint(1000, 9999))
    gameID = str(uuid4())
    games[gameID] = {
        'id': gameID,
        'code': gameCode,
        'players': [],
        'rules': {
            'GRIDWIDTHPX': GRIDWIDTHPX,
            'GRIDHEIGHTPX': GRIDHEIGHTPX,
            'BLOCKSIZE': BLOCKSIZE,
            'FOODCOUNT': FOODCOUNT,
        },
        'state': 'waiting',
        'public': True,
        'food': [],
        'board': [],
        'name': 'test name'
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

SERVER_IP = getLocalIP()
MINPLAYERS = 1
TIMEOUT = 8

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
    BLOCKSIZE = games[gameID]['rules']['BLOCKSIZE']
    GRIDWIDTH = games[gameID]['rules']['GRIDWIDTHPX'] // BLOCKSIZE
    GRIDHEIGHT = games[gameID]['rules']['GRIDHEIGHTPX'] // BLOCKSIZE
    foodPos = (randint(0, GRIDWIDTH-1), randint(0, GRIDHEIGHT-1))
    while isOccupied(gameID, foodPos[0], foodPos[1], removeFood=False)[0]:
        foodPos = (randint(0, GRIDWIDTH-1), randint(0, GRIDHEIGHT-1))
    print('food:', foodPos)
    return foodPos

def getEnvironmentExclusive(gameID, clientID):
    environment = []
    for client in getClientsInGame(gameID):
        if client.id != clientID:
            environment.append({'type':'snake', 'snake':getPlayerSnake(gameID, client.id)})
    for food in games[gameID]['food']:
        environment.append({'type': 'food', 'pos': food})
    return environment

def isOccupied(gameID, x, y, clientID='', removeFood=True):
    BLOCKSIZE = games[gameID]['rules']['BLOCKSIZE']
    GRIDWIDTH = games[gameID]['rules']['GRIDWIDTHPX'] // BLOCKSIZE
    GRIDHEIGHT = games[gameID]['rules']['GRIDHEIGHTPX'] // BLOCKSIZE

    for client in getClientsInGame(gameID):
        if client.id != clientID:
            for part in client.snake['body']:
                if part == [x, y]:
                    return (True, 'body', client.id)
            if tuple(client.snake['head']) == (x, y):
                return (True, 'head', client.id)
        else:
            if int(client.snake['length']) > 3:
                for part in client.snake['body']:
                    if part == [x, y]:
                        return (True, 'self', client.id)
    if x < 0 or x >= GRIDWIDTH or y < 0 or y >= GRIDHEIGHT:
        return (True, 'wall', None)
    if (x, y) in games[gameID]['food']:
        if removeFood:
            games[gameID]['food'].remove((x, y))
            games[gameID]['food'].append(getFoodSpawn(gameID))
        return (True, 'food', None)
    return (False, None, None)

def checkFood(x, y, gameID):
    if (x, y) in games[gameID]['food']:
        games[gameID]['food'].remove((x, y))
        games[gameID]['food'].append(getFoodSpawn(gameID))

def createSnakeSpawn(gameID):
    BLOCKSIZE = games[gameID]['rules']['BLOCKSIZE']
    GRIDWIDTH = games[gameID]['rules']['GRIDWIDTHPX'] // BLOCKSIZE
    GRIDHEIGHT = games[gameID]['rules']['GRIDHEIGHTPX'] // BLOCKSIZE

    headPos = (randint(0, 1) * (GRIDWIDTH-1), randint(0, GRIDHEIGHT-1))
    while isOccupied(gameID, headPos[0], headPos[1])[0] or isOccupied(gameID, headPos[0], headPos[1]+1)[0] or isOccupied(gameID, headPos[0], headPos[1]-1)[0]:
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
            'type': 'updateEnvironment',
            'data': {'environment': getEnvironmentExclusive(gameID, client.id)}
        })
    sleep(2)
    gameClients = getClientsInGame(gameID)
    for client in gameClients:
        sendToClient(client.id, {
            'type': 'startGame',
            'data': {'id': gameID, 'start':'for real this time'}
        })
    while games[gameID]['state'] == 'running':
        gameClients = getClientsInGame(gameID)
        for client in gameClients:
            try:
                if int(time()) - int(clients[client.id].lastMessageTimestamp) > TIMEOUT:
                    ct.printWarning(f"Client {client.id} timed out!")
                    if client.id in games[gameID]['players']:
                        games[gameID]['players'].remove(client.id)
                        del clients[client.id]
                else:
                    checkFood(client.snake['head'][0], client.snake['head'][1], gameID)
                    sendToClient(client.id, {
                        'type': 'updateEnvironment',
                        'data': {
                            'environment': getEnvironmentExclusive(gameID, client.id), 
                        }
                    })
            except KeyError:
                continue
            except RuntimeError:
                continue
        if len(getClientsInGame(gameID)) == 0:
            ct.printStatus(f"Game {games[gameID]['code']} has no players, ending game")
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

        if data['type'] != 'ping' and data['type'] != 'connect':
            clients[data['data']['id']].lastMessageTimestamp = str(int(time()))

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
            serverSocket.sendto(json.dumps({'type': 'ping', 'data': {'blank':'blank'}}).encode(), addr)
            ct.printStatus(f"Ping from IP {addr[0]}")

        elif data['type'] == 'createGame':
            gameID = newGame()
            clientID = data['data']['id']
            clients[clientID].connectToGame(gameID)
            games[gameID]['players'].append(clientID)

            sendToClient(clientID, {'type': 'createGame', 'data': {'id': gameID, 'code': games[gameID]['code']}})
            ct.printStatus(f"Game created: {gameID} with host {clientID} / {clients[clientID].name}")

        elif data['type'] == 'getGames':
            gameList = []
            print(games)
            for game in games.values():
                print(game)
                if game['state'] == 'waiting' and game['public']:
                    gameList.append({
                        'id': game['id'],
                        'code': game['code'],
                        'numPlayers': len(game['players']),
                        'hostName': clients[game['players'][0]].name,
                        'name': game['name']
                    })
            gameList = sorted(gameList, key=lambda x: x['numPlayers'], reverse=True)
            
            sendToClient(data['data']['id'], {'type': 'getGames', 'data': {'games': gameList}})

        elif data['type'] == 'joinGame':
            gameCode = data['data']['code']
            for i in games:
                if games[i]['code'] == gameCode:
                    gameID = gameID
                    break
            clientID = data['data']['id']
            clients[clientID].connectToGame(gameID)
            games[gameID]['players'].append(clientID)

            sendToClient(clientID, {'type': 'joinGame', 'data': {'id': gameID}})
            ct.printStatus(f"Game joined: {gameID} with player {clientID} / {clients[clientID].name}")

        elif data['type'] == 'leaveGame':
            gameID = data['data']['gameID']
            clientID = data['data']['id']
            games[gameID]['players'].remove(clientID)
            clients[clientID].gameID = None
            ct.printStatus(f"Player {clientID} / {clients[clientID].name} left game {gameID}")

        elif data['type'] == 'gameStatus':
            clientID = data['data']['id']
            gameID = clients[clientID].gameID
            sendToClient(clientID, {'type': 'gameStatus', 'data': {'state': games[gameID]['state'], 'players': games[gameID]['players']}})

        elif data['type'] == 'startGameReq':
            gameID = data['data']['gameID']
            clientID = data['data']['id']

            if len(games[gameID]['players']) < MINPLAYERS:
                sendToClient(clientID, {'type': 'startGameRes', 'data': {'fail': True, 'message': 'Not enough players'}})
                continue
            else:
                games[gameID]['state'] = 'running'
                games[gameID]['food'] = [getFoodSpawn(gameID) for i in range(games[gameID]['rules']['FOODCOUNT'])]

                gameClients = getClientsInGame(gameID)
                for client in gameClients:
                    sendToClient(client.id, {
                        'type': 'startGameRes', 
                        'data': {
                            'id': gameID,
                            'snakeInfo': createSnakeSpawn(gameID), 
                            'players': [client.id for client in gameClients],
                            'gridpx': (games[gameID]['rules']['GRIDWIDTHPX'], games[gameID]['rules']['GRIDHEIGHTPX']),
                            'blocksize': games[gameID]['rules']['BLOCKSIZE']
                        }
                    })
                
                ct.printStatus(f"Game initialised: {gameID} with players {games[gameID]['players']}")

                gameThreads.append(threading.Thread(target=gameThread, args=(gameID,), daemon=True))
                gameThreads[-1].start()
        
        elif data['type'] == 'clientUpdate':
            clientID = data['data']['id']
            gameID = clients[clientID].gameID
            
            setPlayerSnake(gameID, clientID, data['data']['snake'])
            #setPlayerEnvironment(gameID, clientID, data['data']['environment'])

    except Exception as e:
        if type(e) == json.decoder.JSONDecodeError:
            print("Invalid JSON received")
        elif type(e) == KeyError:
            print("Invalid data received", e)
        else:
            print("Error", e)
            continue
    
    
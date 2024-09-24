"""Python inbuilt modules"""
import socket
from uuid import uuid4
import json
import threading
from time import sleep, time
from random import randint
import os

"""Change the working directory to the current file's directory"""
os.chdir(os.path.dirname(os.path.abspath(__file__)))

"""Small utility modules"""
import modules.colouredText as ct
from modules.ipList import getLocalIP

class Client: 
    """Class for client information"""
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

def getClientsInGame(gameID):
    """Returns a list of clients in a game"""
    return [client for client in clients.values() if client.gameID == gameID]

def newGame(public=True, name='test name'):
    """Creates a new game and returns the gameID"""
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
        'public': public,
        'food': [],
        'board': [],
        'name': name
    }
    return gameID

def sendToClient(clientID, data):
    """Sends data to a the matching address of a client"""
    try:
        serverSocket.sendto(json.dumps(data).encode(), clients[clientID].addr)
    except TimeoutError:
        ct.printWarning(f'Timeout error sending to client {clientID} / {clients[clientID].addr}!')
        pass

def getPlayerSnake(gameID, clientID):
    """Gets the snake of a player"""
    return clients[clientID].snake

def setPlayerSnake(gameID, clientID, snake):
    """Sets the snake of a player"""
    clients[clientID].snake = snake

def setPlayerEnvironment(gameID, clientID, environment):
    """Sets the environment of a player"""
    clients[clientID].environment = environment

def getPlayerEnvironment(clientID):
    """Gets the environment of a player"""
    return clients[clientID].environment

def getFoodSpawn(gameID):
    """Gets a random spawn location for food"""
    BLOCKSIZE = games[gameID]['rules']['BLOCKSIZE']
    GRIDWIDTH = games[gameID]['rules']['GRIDWIDTHPX'] // BLOCKSIZE
    GRIDHEIGHT = games[gameID]['rules']['GRIDHEIGHTPX'] // BLOCKSIZE
    foodPos = (randint(0, GRIDWIDTH-1), randint(0, GRIDHEIGHT-1))

    while isOccupied(gameID, foodPos[0], foodPos[1], removeFood=False)[0]: #Get a new spawn location until it is not occupied
        foodPos = (randint(0, GRIDWIDTH-1), randint(0, GRIDHEIGHT-1))

    return foodPos

def isOccupied(gameID, x, y, clientID='', removeFood=True):
    """Checks if a position is occupied by a snake, wall, or food"""
    BLOCKSIZE = games[gameID]['rules']['BLOCKSIZE']
    GRIDWIDTH = games[gameID]['rules']['GRIDWIDTHPX'] // BLOCKSIZE
    GRIDHEIGHT = games[gameID]['rules']['GRIDHEIGHTPX'] // BLOCKSIZE

    for client in getClientsInGame(gameID): #Check if the position is occupied by a snake
        if client.id != clientID:
            for part in client.snake['body']: #Check for body parts
                if part == [x, y]:
                    return (True, 'body', client.id)
            if tuple(client.snake['head']) == (x, y): #Check for the head
                return (True, 'head', client.id)
        else:
            if int(client.snake['length']) > 3: 
                #Check for the tail. If the tail is less than 3, it is not a collision, as at the start of the game the tail is spawned in the same place as the head
                for part in client.snake['body']:
                    if part == [x, y]:
                        return (True, 'self', client.id)

    if x < 0 or x >= GRIDWIDTH or y < 0 or y >= GRIDHEIGHT: #Check if the position is outside the grid
        return (True, 'wall', None)

    if (x, y) in games[gameID]['food']: #Check if the position is occupied by food
        if removeFood:
            games[gameID]['food'].remove((x, y)) #Remove the food and spawn a new one
            games[gameID]['food'].append(getFoodSpawn(gameID))
        return (True, 'food', None)

    return (False, None, None) #No collision

def checkFood(x, y, gameID):
    """Checks if a snake has collided with food and spawns a new piece of food"""
    if (x, y) in games[gameID]['food']:
        games[gameID]['food'].remove((x, y))
        games[gameID]['food'].append(getFoodSpawn(gameID))


def getEnvironmentExclusive(gameID, clientID):
    """Gets the environment of a player, excluding their own snake"""
    environment = []
    for client in getClientsInGame(gameID):
        if client.id != clientID:  # If the client is not the player, add their snake to the environment
            environment.append(
                {'type': 'snake', 'snake': getPlayerSnake(gameID, client.id)})

    for food in games[gameID]['food']:  # Add food to the environment
        environment.append({'type': 'food', 'pos': food})

    return environment

def createSnakeSpawn(gameID, currentSpawns):
    """Creates a spawn location for a snake"""
    BLOCKSIZE = games[gameID]['rules']['BLOCKSIZE']
    GRIDWIDTH = games[gameID]['rules']['GRIDWIDTHPX'] // BLOCKSIZE
    GRIDHEIGHT = games[gameID]['rules']['GRIDHEIGHTPX'] // BLOCKSIZE

    """Code to spawn the snake in a random location.
    This location is:
    - Not occupied by another snake
    - Does not have another snake's head within 1 block
    - On either the left or right side of the grid
    - On a random row, but not the top or bottom row
    """
    headPos = (randint(0, 1) * (GRIDWIDTH-1), randint(0, GRIDHEIGHT-1))
    while isOccupied(gameID, headPos[0], headPos[1])[0] or isOccupied(gameID, headPos[0], headPos[1]+1)[0] or isOccupied(gameID, headPos[0], headPos[1]-1)[0] or headPos in currentSpawns:
        headPos = (randint(0, 1) * (GRIDWIDTH-1), randint(0, GRIDHEIGHT-1))

    #Set the direction of the snake based on the spawn location
    if headPos[0] == 0:
        direction = (1, 0)
    else:
        direction = (-1, 0)
    body = [headPos, headPos] #Set the two body parts of the snake in the same location as the head

    return ({'length':3, 'head': headPos, 'body': body, 'direction': direction, 'last': (0, 0)}, direction[0])

def gameThread(gameID):
    """Thread for running a game. Each game instance runs in its own thread"""
    
    #Give the clients a chance to load the game, then send the environment
    sleep(0.5)
    gameClients = getClientsInGame(gameID)
    for client in gameClients:
        sendToClient(client.id, {
            'type': 'updateEnvironment',
            'data': {'environment': getEnvironmentExclusive(gameID, client.id)}
        })
    
    #Start the game after 2 seconds
    sleep(2)
    gameClients = getClientsInGame(gameID)
    for client in gameClients:
        sendToClient(client.id, {
            'type': 'startGame',
            'data': {'id': gameID, 'start':'for real this time'}
        })

    #Game loop
    while games[gameID]['state'] == 'running':
        gameClients = getClientsInGame(gameID)
        for client in gameClients:
            try:
                if int(time()) - int(clients[client.id].lastMessageTimestamp) > TIMEOUT:
                    #Check if the client has timed out
                    ct.printWarning(f"Client {getShortID(client.id)} timed out!")
                    if client.id in games[gameID]['players']:
                        games[gameID]['players'].remove(client.id)
                        del clients[client.id]
                else:
                    #Check if the client has collided with food and update their environment. 
                    #Most collision detection is done client-side.
                    #The only collision done server-side is to find a new spawn location for food.
                    #This is probably prone to exploitation however
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

        if len(getClientsInGame(gameID)) == 0: #No players in the game, end the game and stop the thread
            ct.printWarning(f"Game {games[gameID]['code']} has no players, ending game")
            games[gameID]['state'] = 'over'
            return

def checkClientTimeout(clientID):
    """Check if a client has timed out and remove them from their game and the client list"""
    if int(time()) - int(clients[clientID].lastMessageTimestamp) > TIMEOUT + 1:
        ct.printWarning(f"Client {clientID} timed out!")
        i = 0
        while True:
            if i >= len(games):
                break
            gameID = list(games.keys())[i]
            if clientID in games[gameID]['players']:
                games[gameID]['players'].remove(clientID)
                if len(games[gameID]['players']) == 0 and games[gameID]['state'] == 'waiting':
                    del games[gameID]
                    i -= 1
            i += 1
        del clients[clientID]
        return True
    return False

def getLobbyList(gameID, clientID=None):
    """Get a list of players in a game to display to the host"""
    temp = []
    for i in games[gameID]['players']:
        if i == clientID:
            temp.append({'name': f"{clients[i].name} (you)", 'id': i})
        else:
            temp.append({'name': clients[i].name, 'id': i})
    return temp

def getShortID(i):
    """Gets a shortened version of an ID for server logging"""
    return i[0:7]

def isClientId(clientID):
    """Check if a client ID is valid"""
    return clientID in clients.keys()

def doesTypeRequireID(data):
    """Check if a message type requires a client ID"""
    return data['type'] in ['disconnect', 'createGame', 'getGames', 'joinGame', 'leaveGame', 'gameStatus', 'startGameReq', 'clientUpdate', 'kickPlayer']

"""Initialise variables"""
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

"""Start the server"""
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    serverSocket.bind((SERVER_IP, 65432))
except OSError:
    #An error occurs when the server is already running and a second instance is started, i did this a lot lol
    ct.printError("Server could not bind to the specified IP address, meaning it is probably already running...")
    quit()
serverSocket.settimeout(0.1)

ct.printStatus(f"Snake server is listening, IP: {SERVER_IP}")

while True:
    #Check for client timeouts
    i = 0
    while True:
        if i >= len(clients):
            break
        if not checkClientTimeout(list(clients.keys())[i]):
            i += 1


    try:
        data, addr = serverSocket.recvfrom(4096) 
        #Receive data from all clients. 
        #This current method on both the client and server side is not perfect, as any messages sent while the server is processing a message will be lost, and messages are not properly acnowledged.
    except Exception as e:
        if type(e) == socket.timeout:
            continue
        elif type(e) == KeyboardInterrupt:
            ct.printError("Closing server...")
            serverSocket.close()
            for thread in gameThreads:
                thread.close()
            quit()
            break
        elif type(e) == ConnectionResetError:
            continue
        else:
            ct.printError(f"Error while recieving data: {e}")
            continue
    try:
        data = json.loads(data)

        validID = False
        try:
            clientID = data['data']['id']
        except KeyError:
            clientID = ''
            pass

        if doesTypeRequireID(data):
            if isClientId(clientID):
                validID = True

                # Update the last message timestamp of the client
                clients[data['data']['id']].lastMessageTimestamp = str(int(time()))
            else:
                ct.printWarning(f"Client {getShortID(clientID)} attempted to send a message without a valid client ID")
        else:
            #The message type does not require a client ID, therefore it is valid
            validID = True

        if validID:
            match data['type']:
                case 'ping': #Client is attempting to find the server, provide a response
                    serverSocket.sendto(json.dumps({'type': 'ping', 'data': {'blank':'blank'}}).encode(), addr)
                    ct.printStatus(f"Ping from IP {addr[0]}")

                case 'connect': #Client is attempting to connect to the server, generate a client instance and respond with their client ID
                    clientID = str(uuid4())
                    clients[clientID] = Client(data['data']['name'], clientID, addr)

                    sendToClient(clientID, {'type': 'connect', 'data': {'id': clientID}})
                    ct.printStatus(f"Client connected: {getShortID(clientID)} / {clients[clientID].name}")

                case 'disconnect': #Client is disconnecting from the server, remove them from the client list and any games they are in
                    sendToClient(clientID, {'type': 'disconnect', 'data': {'id': clientID}})
                    ct.printStatus(f"Client disconnected: {getShortID(clientID)} / {clients[clientID].name}")
                    i = 0
                    while True: #This style of loop is used to avoid issues with modifying the dictionary while iterating over it
                        if i >= len(games):
                            break
                        gameID = list(games.keys())[i]
                        if clientID in games[gameID]['players']:
                            games[gameID]['players'].remove(clientID)
                            if len(games[gameID]['players']) == 0 and games[gameID]['state'] == 'waiting':
                                del games[gameID]
                                i -= 1
                        i += 1
                    del clients[clientID]

                case 'createGame': #Client is creating a new game, generate a game ID and add them to the game list
                    gameID = newGame(data['data']['public'], data['data']['name'])
                    clients[clientID].connectToGame(gameID)
                    games[gameID]['players'].append(clientID)

                    sendToClient(clientID, {'type': 'createGame', 'data': {'id': gameID, 'code': games[gameID]['code']}})
                    ct.printStatus(f"Game created: {getShortID(gameID)} with host {getShortID(clientID)} / {clients[clientID].name}")

                case 'getGames': #Client is requesting a list of games, send a list of games that are public and waiting
                    gameList = []
                    i = 0
                    while True:
                        if i >= len(games.values()):
                            break
                        game = list(games.values())[i]
                        if game['state'] == 'waiting' and game['public']:
                            gameList.append({
                                'id': game['id'],
                                'code': game['code'],
                                'numPlayers': len(game['players']),
                                'hostName': clients[game['players'][0]].name,
                                'name': game['name']
                            })
                        i += 1
                    if len(gameList) > 0:
                        gameList = sorted(gameList, key=lambda x: x['numPlayers'], reverse=True)

                    sendToClient(data['data']['id'], {'type': 'getGames', 'data': {'games': gameList}})

                case 'joinGame': #Client is joining a game, add them to the game's player list
                    gameCode = data['data']['code']

                    gameID = None
                    for i in games:
                        #Find the game with the matching code
                        if games[i]['code'] == gameCode:
                            gameID = i
                            break
                    
                    if gameID is not None:
                        if len(games[gameID]['players']) > 6: #Check if the game is full
                            break
                        
                        clients[clientID].connectToGame(gameID)
                        games[gameID]['players'].append(clientID)

                        sendToClient(clientID, {'type': 'joinGame', 'data': {'id': gameID, 'success':True}})

                        sendToClient(games[gameID]['players'][0], {'type': 'lobbyStatus', 'data': {'state': games[gameID]['state'], 'players': getLobbyList(gameID, games[gameID]['players'][0])}})
                        ct.printStatus(f"Game joined: {getShortID(gameID)} with player {getShortID(clientID)} / {clients[clientID].name}")
                    else:
                        sendToClient(clientID, {'type': 'joinGame', 'data': {'id': None, 'success':False}})
                        ct.printWarning(f"Client {getShortID(clientID)} / {clients[clientID].name} could not join game with provided code: {gameCode}")

                case 'leaveGame': #Client is leaving a game, remove them from the game's player list
                    gameID = data['data']['gameID']
                    games[gameID]['players'].remove(clientID)
                    clients[clientID].gameID = None
                    ct.printStatus(f"Player {getShortID(clientID)} / {clients[clientID].name} left game {getShortID(gameID)}")

                case 'gameStatus': #Client (host) is requesting the status of a game, send the state and player list
                    gameID = clients[clientID].gameID
                    sendToClient(clientID, {'type': 'gameStatus', 'data': {'state': games[gameID]['state'], 'players': games[gameID]['players']}})

                case 'startGameReq': #Client (host) is requesting to start a game, check if there are enough players and start the game
                    gameID = data['data']['gameID']

                    if len(games[gameID]['players']) < MINPLAYERS: #Check if there are enough players. Currently minimum is 1, but can be increased if desired
                        sendToClient(clientID, {'type': 'startGameRes', 'data': {'fail': True, 'message': 'Not enough players'}})
                    else:
                        games[gameID]['state'] = 'running'

                        #Initialise the game board and spawn food. Food count is set in the game rules (default 3)
                        games[gameID]['food'] = [getFoodSpawn(gameID) for i in range(games[gameID]['rules']['FOODCOUNT'])]

                        gameClients = getClientsInGame(gameID)
                        currentSpanws = []
                        for client in gameClients: #Send the game start message to all players
                            spawn = createSnakeSpawn(gameID, currentSpanws)
                            currentSpanws.append(spawn[0]['head'])
                            sendToClient(client.id, {
                                'type': 'startGameRes', 
                                'data': {
                                    'id': gameID,
                                    'snakeInfo': spawn, 
                                    'players': [client.id for client in gameClients],
                                    'gridpx': (games[gameID]['rules']['GRIDWIDTHPX'], games[gameID]['rules']['GRIDHEIGHTPX']),
                                    'blocksize': games[gameID]['rules']['BLOCKSIZE']
                                }
                            })
                        
                        ct.printStatus(f"Game initialised: {getShortID(gameID)} with {len(games[gameID]['players'])} players")

                        #Initialise and start a game thread
                        gameThreads.append(threading.Thread(target=gameThread, args=(gameID,), daemon=True))
                        gameThreads[-1].start()

                case 'clientUpdate': #Client is updating their snake, update the server's copy of the snake
                    gameID = clients[clientID].gameID

                    setPlayerSnake(gameID, clientID, data['data']['snake'])

                case 'kickPlayer': #Client (host) is kicking a player from the game, remove them from the player list
                    playerID = data['data']['playerID']
                    gameID = data['data']['gameID']
                    games[gameID]['players'].remove(playerID)
                    clients[playerID].gameID = None
                    sendToClient(playerID, {'type': 'kickPlayer', 'data': {'id': game}})
                    sendToClient(clientID, {'type': 'lobbyStatus', 'data': {'state': games[gameID]['state'], 'players': getLobbyList(gameID, clientID)}})
                    ct.printStatus(f"Player {getShortID(clientID)} / {clients[playerID].name} kicked from game {getShortID(gameID)}")


    except Exception as e:
        if type(e) == json.decoder.JSONDecodeError:
            ct.printError("Invalid JSON received")
        elif type(e) == KeyError:
            ct.printError(f"Key error while processing client message: {e}")
        else:
            ct.printError(f"Error while processing client message: {e}")
            continue
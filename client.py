"""Python inbuilt modules"""
import socket
import json
import time
import threading
from random import randint
from time import sleep
import os

"""Change the working directory to the current file's directory"""
os.chdir(os.path.dirname(os.path.abspath(__file__)))

"""Elements of the pygame window"""
import modules.loadingSnake as ls
import modules.submitDialog as sd
import modules.lobbiesList as ll
import modules.lobbyDialog as ld
import modules.lobbyMembersList

"""Main snake game module"""
import modules.snake as snake

"""Small utility modules"""
from modules.colours import *
import modules.colouredText as ct
import modules.ipList as ipList

"""Pygame modules"""
import pygame
from pygame.locals import *

WIDTH, HEIGHT = 600, 600
SERVER_IP = None

def sendToServer(message, ip=None):
    """Send a message to the server"""

    if ip is None: #Check if optional IP isn't provided
        if SERVER_IP is None: #Check if global IP has been set yet
            return
        ip = SERVER_IP
    clientSocket.sendto(json.dumps(message).encode(), (ip, 65432))

def quitProgram():
    """Quit the program"""
    pygame.quit()
    socketThread.join(timeout=0.1)
    if clientID is not None:
        sendToServer({'type': 'disconnect', 'data': {'id': clientID}})
        clientSocket.close()

def fakeGamesList():
    """Fake games list for testing (not used)"""
    gamesList = []
    for i in range(randint(1, 10)):
        gamesList.append({'id': 'ak1jk1fjkl1j1908-fjajl', 'id':'a' + str(randint(1000, 9999)), 'hostName': 'Adam', 'name': f'Lobby {i}', 'numPlayers': randint(1, 4)})
    return gamesList

def socketListener():
    """Function to read messages from the server. Runs on a separate thread"""
    global gameID, clientID, gameHost, snakeInfo, gameStart, gameEnvironment, gamesList, windowIndex, activeWindow, gameCode
    while True:
        try:
            data, addr = clientSocket.recvfrom(4096)
        except Exception as e: #Catch any exceptions when receiving data from the server
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

            match data['type']:
                case 'disconnect':
                    break
                case 'connect': #Connection successful, get client ID and add it to the lobby member list (used later if the client is a lobby host)
                    ct.printStatus(f"Connected to server, id: {data['data']['id']}")
                    clientID = data['data']['id']
                    lobbyMembersWindow.clientID = clientID
                    lobbyMembersWindow.updateMembersList([{'id': clientID, 'name': f"{name} (you)"}], clientID)

                case 'kickPlayer': #If the client is kicked from the lobby, return to the lobby list
                    ct.printStatus(f"You were kicked :(")
                    returnToLobbyList()

                case 'createGame': #Game creation sucessful, get the game ID and code
                    ct.printStatus(f"Game created: {data['data']['code']}")
                    gameID = data['data']['id']
                    gameCode = data['data']['code']
                    gameHost = True
                    activeWindow = lobbyMembersWindow
                    windowIndex = 6

                case 'lobbyStatus': #The lobby members have changed, update the list
                    ct.printStatus(f"Current game members: {data['data']['players']}")
                    lobbyMembersWindow.updateMembersList(data['data']['players'], clientID)

                case 'joinGame': #Join game successful, get the game ID and display the 'waiting for host' screen
                    ct.printStatus(f"Game joined: {data['data']['id']}")
                    gameID = data['data']['id']
                    gameHost = False
                    activeWindow = None
                    windowIndex = 7

                case 'getGames': #Response from the server with the active games list
                    ct.printStatus(f"Games: {data['data']['games']}")
                    gamesList = data['data']['games']
                    if len(gamesList) == 0:
                        ct.printStatus("No active games")
                        gamesList = []

                case 'startGameRes': #Response from the server regarding starting the game
                    if 'fail' in data['data']: #Check if game start was unsuccessful
                        ct.printWarning(f"Game start failed: {data['data']['message']}")
                    else: #Game start successful, display the main game screen
                        ct.printStatus(f"Game starting soon: {data['data']['id']}") 
                        snakeInfo = data['data']['snakeInfo']
                        gameStart = 1
                        windowIndex = 10

                case 'startGame': #Game start message from the server, start moving the snake
                    ct.printStatus(f"Game started: {data['data']['id']}")
                    gameStart = 2

                case 'updateEnvironment': #Update the game environment
                    gameEnvironment = data['data']['environment']

        except Exception as e:
            ct.printError(f"Error: {e}")
            break

def autoConnectThread():
    """Try to automatically connect to the server based on a list of previous addresses of the server. Runs on a seperate thread"""
    global connectionAttemptState, SERVER_IP
    connectionAttemptState = 1
    for i in ipList.getIPList(): #Try to connect with addresses from the 'iplist' file
        ip = attemptConnection(i)
        if ip is not None:
            SERVER_IP = ip
            connectionAttemptState = 3
            return
    ip = attemptConnection(ipList.getLocalIP()) #Addresses in the file failed, attempt to connect to the local IP. Works most times (in testing) as the server is usually running on the same machine
    if ip is not None:
        ipList.addToIPList(ip) #If the connection was successful, add the IP to the list
        SERVER_IP = ip
        connectionAttemptState = 3
        return
    connectionAttemptState = 2

def manualConnectThread(manualIP):
    """Auto connection failed, try to connect to the server using a manually entered IP from the user. Runs on a seperate thread"""
    global connectionAttemptState, SERVER_IP
    ip = attemptConnection(manualIP)
    if ip is not None:
        SERVER_IP = ip
        connectionAttemptState = 3
        return
    connectionAttemptState = 2

def attemptConnection(ip, testLocal=True):
    """Attempt to connect to the server using a given IP"""
    data, addr = None, None
    clientSocket.settimeout(0.5)
    try:
        sendToServer({'type': 'ping', 'data': {}}, ip) #Send a ping message to the server then wait for a response
        time.sleep(0.1)
        data, addr = clientSocket.recvfrom(4096)
        print(data, addr)
        if data is not None:
            print(data)
            return ip
    except Exception as e: #Catch any exceptions when trying to connect to the server
        if type(e) == socket.timeout:
            return None
        elif type(e) == KeyboardInterrupt:
            return None
        elif type(e) == TimeoutError:
            return None
        else:
            print("Error:", e)
            print(type(e))
            return None

def joinLobby(lobbyCode):
    """Join a lobby with the given code"""
    ct.printStatus(f"Joining lobby {lobbyCode}")
    if lobbyCode[0] == 'a':
        return
    sendToServer({'type': 'joinGame', 'data': {'id': clientID, 'code': lobbyCode}})

def refreshLobbies():
    """Refresh the active lobbies list (run when the 'refresh' button is clicked)"""
    ct.printStatus("Refreshing lobbies")
    sendToServer({'type': 'getGames', 'data': {'id': clientID}})

def createLobby():
    """Open the lobby creation dialog (run when the 'create lobby' button is clicked)"""
    ct.printStatus("Creating lobby")
    game_modes = ["Last Man Standing"] #, "Time Trial"]
    dialog = ld.LobbyDialog(game_modes, createLobbySubmit, marginLeft=25, width=300, height=500)
    dialog.run_dialog()

def joinPrivate():
    """Open the private lobby join dialog (run when the 'join private' button is clicked)"""
    global windowIndex
    ct.printStatus("Joining private lobby")
    windowIndex = 5

def createLobbySubmit(lobbyInfo):
    """Create a lobby with the given information (run when the user completes the lobby creation dialog)"""
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    print(lobbyInfo)
    sendToServer({'type': 'createGame', 'data': {'id': clientID, 'name': lobbyInfo['lobby'], 'public': lobbyInfo['public'], 'mode': lobbyInfo['mode']}})

def kickPlayer(playerID):
    """Kick a player from the lobby (run when the host clicks the 'X' in the lobby member list)"""
    sendToServer({'type': 'kickPlayer', 'data': {'id': clientID, 'playerID': playerID, 'gameID': gameID}})

def returnToLobbyList():
    """Big function to clear all game data and return to the active lobbies list"""
    global snakeText, windowIndex, gamesList, startLoadTime, getGamesSent, screen, gameEnvironment, connectionAttemptState, gamesList, gameID, gameEnvironment
    #lots of globals, probably not the best way to do this but it works

    snakeText = connectionFont.render('Getting active lobbies...', True, WHITE)
    gamesList = None
    startLoadTime = time.time()
    getGamesSent = False
    snakeGame.snake = None
    gameEnvironment = []
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    windowIndex = 3
    connectionAttemptState = 3
    gamesList = []
    gameID = None
    gameEnvironment = []
    lobbyMembersWindow.updateMembersList([{'id': clientID, 'name': f"{name} (you)"}], clientID)

"""Initialise variables"""
active, gameHost = False, False
gameID, snakeInfo, clientID, gamesList, gameCode = None, None, None, None, None
gameEnvironment = []
gameStart, windowIndex, frameNum, connectionAttemptState = 0, 0, 0, 0
ips = ipList.getIPList()

clock = pygame.time.Clock()
startLoadTime = time.time() 
#Start load time is used to make a minimum delay between loading screens. Not necessary but allows me to show off the cool spinning snake loading screen

"""Initialise the socket connection and server listener thread"""
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.settimeout(0.1)
socketThread = threading.Thread(target=socketListener, daemon=True)

"""Initialise the pygame window"""
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Adam's Snake")
pygame.mouse.set_cursor(*pygame.cursors.diamond)

"""Initialise variables for the pygame windows"""
ls.init(WIDTH, HEIGHT)

snakeImg = pygame.image.load('snake.png')

connectionFont = pygame.font.Font(None, 36)
snakeText = connectionFont.render('Connecting to server...', True, WHITE)
text_rect = snakeText.get_rect(center=(WIDTH // 2, HEIGHT // 6-30))

cfWindow = sd.submitDialog(WIDTH, HEIGHT, screen, "Could not automatically connect to the server", "Enter server IP:", charLimit=20)
nameWindow = sd.submitDialog(WIDTH, HEIGHT, screen, "Welcome to Adam's Snake!", "Enter your name:", charLimit=12)
privateWindow = sd.submitDialog(WIDTH, HEIGHT, screen, "Join private lobby", "Enter the lobby code:", charLimit=4)

lobbiesWindow = ll.lobbiesList(WIDTH, HEIGHT, screen, [], refreshLobbies, createLobby, joinPrivate, joinLobby)

lobbyMembersWindow = modules.lobbyMembersList.LobbyMembersList(WIDTH, HEIGHT, screen, 0, [])
startRectCol = DGREY

textBoxWindows = [cfWindow, nameWindow, privateWindow]
activeWindow = nameWindow

while True:
    screen.fill(BLACK)

    """Every 25 frames, send a ping to the server. If this is not sent, the server will disconnect the client after a couple of seconds of inactivity"""
    frameNum += 1
    if frameNum % 25 == 0 and clientID is not None:
        sendToServer({'type': 'clientCheck', 'data': {'id':clientID}})

    """Check for user input"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quitProgram()
            
        elif event.type == KEYDOWN:
            if activeWindow in textBoxWindows: #Check if the active window has a text input
                if event.key == K_RETURN:
                    if activeWindow == nameWindow: #User has entered their name, move to the next screen
                        name = activeWindow.input_text
                        startLoadTime = time.time()
                        windowIndex = 1

                    elif activeWindow == cfWindow: #User has manually entered the server IP, try to connect to the server again
                        ip = activeWindow.input_text

                    elif activeWindow == privateWindow: #User has entered a private lobby code, try to join the lobby
                        joinLobby(activeWindow.input_text)

                    

                    activeWindow.input_text = '' #Clear the text input
                elif event.key == K_BACKSPACE:
                    activeWindow.input_text = activeWindow.input_text[:-1]
                else:
                    if len(activeWindow.input_text) < activeWindow.charLimit: #Add the key press to the text input unless the character limit is reached
                        activeWindow.input_text += event.unicode

        elif event.type == MOUSEBUTTONDOWN: #Check for mouse clicks
            if activeWindow == lobbiesWindow: #Handle clicks on the active lobbies list
                lobbiesWindow.handleMouseClick(pygame.mouse.get_pos())
            
            elif activeWindow == lobbyMembersWindow: #Handle clicks on the lobby member list
                memberID = lobbyMembersWindow.handleMouseClick(pygame.mouse.get_pos())
                if memberID is not None:  # If the user clicks the 'X' next to a player, kick them from the lobby
                    kickPlayer(memberID) 
                elif startRect.collidepoint(event.pos): #If the user clicks the 'start' button, start the game
                    sendToServer({'type': 'startGameReq', 'data': {'id': clientID, 'gameID': gameID}})
            
            elif activeWindow in textBoxWindows: #Handle clicks on the text input boxes

                if activeWindow.input_box.collidepoint(event.pos): #Set the input box to active if the user clicks on it
                    activeWindow.inputActive = not activeWindow.inputActive
                else:
                    activeWindow.inputActive = False

                if activeWindow.buttonRect.collidepoint(event.pos): #Same as pressing enter, submit the text
                    if activeWindow == nameWindow: 
                        name = activeWindow.input_text
                        startLoadTime = time.time()
                        windowIndex = 1
                    elif activeWindow == cfWindow:
                        ip = activeWindow.input_text
                    elif activeWindow == privateWindow:
                        joinLobby(activeWindow.input_text)
                    activeWindow.input_text = ''

    """Window index is used to determine which screen to display"""
    match windowIndex:
        case 0: #Initial screen, get the user's name
            activeWindow = nameWindow
            nameWindow.setHighlights(pygame.mouse.get_pos())
            nameWindow.displayWindow()
            screen.blit(snakeImg, ((WIDTH - snakeImg.get_width()) // 2, 50))

        case 1: #Loading screen, attempt to connect to the server
            screen.blit(snakeText, text_rect)
            ls.drawLoadingSnake(clock, screen, moveSegments=(frameNum % 3 == 0)) #To slow down the snake animation, only move the segments every 3 frames
            if connectionAttemptState == 0:
                if len(ips) == 1:
                    manualConnect = threading.Thread(target=manualConnectThread, args=(ips[0],), daemon=True)
                    manualConnect.start()
                else:
                    autoConnect = threading.Thread(target=autoConnectThread, daemon=True)
                    autoConnect.start()
            elif connectionAttemptState == 1:
                pass
            elif connectionAttemptState == 2 and time.time() - startLoadTime > 1: #Like mentioned before, the loading screen is displayed for at least 1 second because its cool
                ip = None
                windowIndex = 2
            elif connectionAttemptState == 3 and time.time() - startLoadTime > 1: #Connection successful, start the socket listener thread
                socketThread.start()
                sendToServer({'type': 'connect', 'data': {'name': name}})
                startLoadTime = time.time()
                snakeText = connectionFont.render('Getting active lobbies...', True, WHITE)
                getGamesSent = False
                windowIndex = 3

        case 2: #Connection failed, ask the user to manually enter the server IP
            activeWindow = cfWindow
            cfWindow.setHighlights(pygame.mouse.get_pos())
            cfWindow.displayWindow()
            if ip is not None:
                ips = [str(ip)]
                print(ips)
                startLoadTime = time.time()
                windowIndex = 1
                connectionAttemptState = 0

        case 3: #Loading screen, get the active lobbies list
            screen.blit(snakeText, text_rect)
            ls.init(WIDTH, HEIGHT)
            ls.drawLoadingSnake(clock, screen, moveSegments=(frameNum % 3 == 0))
            if time.time() - startLoadTime > 1:
                if clientID is not None and gamesList is None and not getGamesSent:
                    getGamesSent = True
                    sendToServer({'type': 'getGames', 'data': {'id': clientID}})
                if gamesList is not None:
                    lobbiesWindow.lobbies = gamesList
                    windowIndex = 4

        case 4: #Active lobbies list screen
            activeWindow = lobbiesWindow
            lobbiesWindow.lobbies = gamesList
            lobbiesWindow.setHighlights(pygame.mouse.get_pos())
            lobbiesWindow.displayWindow()

        case 5: #Join private lobby screen
            activeWindow = privateWindow
            privateWindow.setHighlights(pygame.mouse.get_pos())
            privateWindow.displayWindow()

        case 6: #Lobby screen (host)
            readyText = connectionFont.render('Press start when ready!', True, WHITE)
            readyRect = readyText.get_rect(center=(WIDTH // 2, HEIGHT // 6 - 30))

            codeText = connectionFont.render(f'Code: {gameCode}', True, WHITE)
            codeRect = codeText.get_rect(center=(WIDTH // 2, HEIGHT // 6))

            startText = pygame.font.Font(None, 64).render('Start', True, BLACK)
            startRect = pygame.Rect((WIDTH - 300) // 2, HEIGHT - 100, 300, 50)

            screen.blit(codeText, codeRect)
            screen.blit(readyText, readyRect)

            startRectCol = DGREY
            if startRect.collidepoint(pygame.mouse.get_pos()):
                startRectCol = HIGHLIGHT_COLOUR
            pygame.draw.rect(screen, startRectCol, startRect)
            screen.blit(startText, (startRect.centerx - startText.get_width() // 2, startRect.y + 5))

            lobbyMembersWindow.setHighlights(pygame.mouse.get_pos())
            lobbyMembersWindow.drawList()

        case 7: #Lobby screen (not host)
            snakeText = connectionFont.render('Waiting for host to start...', True, WHITE)
            screen.blit(snakeText, text_rect)
            ls.init(WIDTH, HEIGHT)
            ls.drawLoadingSnake(clock, screen, moveSegments=(frameNum % 3 == 0))

        case 10: #Game screen
            if len(snakeInfo) == 0 or snakeInfo is None: #If the snake info is not received, something has gone wrong.
                socketThread.join(timeout=0.1)
                sendToServer({'type': 'disconnect', 'data': {'id': clientID}})
                clientSocket.close()
                quit()

            screen = pygame.display.set_mode((800, 600))
            snakeGame = snake.snakeGame(screen, (800, 600), 40, snakeInfo)
            sendToServer({'type': 'clientUpdate', 'data': {'id': clientID, 'snake': snakeGame.snake}}) #Send the initial snake position to the server

            sleep(0.1)

            while gameStart == 1: #Wait for the server to start the game. gameStart variable is controlled by the server communication thread
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

            snakeGame.startGame() #Server has started the game, start the game loop

            while snakeGame.running: #Main game loop
                try:
                    snakeGame.processSnakeChange()
                    if not snakeGame.running: #If the game is over, return to the lobby list. This is temporaty, the game should probably have a 'game over' screen or a 'respawn' screen depending on game mode
                        print("Game over")
                        break

                    sendToServer({'type': 'clientUpdate', 'data': {'id': clientID, 'snake': snakeGame.snake}}) #Send the updated snake position to the server

                    snakeGame.updateEnvironment(gameEnvironment) #Update the game environment based on the server response

                    snakeGame.playFrame()
                    sleep(0.15)
                except KeyboardInterrupt:
                    break

            sendToServer({'type': 'leaveGame', 'data': {'id': clientID, 'gameID': gameID}}) #Game is over, leave the game and return to the lobby list
            returnToLobbyList()

    pygame.display.flip()
    clock.tick(15)

socketThread.join(timeout=0.1)
sendToServer({'type': 'disconnect', 'data': {'id': clientID}})
clientSocket.close()
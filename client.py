"""Python inbuilt modules"""
import modules.lobbyDialog as lobbyDialog
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
import modules.loadingSnake as loadingSnake
import modules.submitDialog as submitDialog
import modules.lobbiesList as lobbiesList
import modules.confirmDialog as confirmDialog
import modules.lobbyMembersList as lobbyMembersList

"""Main snake game module"""
import modules.snake as snake

"""Small utility modules"""
from modules.colours import *
from modules.colouredText import *
import modules.ipList as ipList

"""Pygame modules"""
import pygame
from pygame.locals import *

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
    try:
        socketThread.join(timeout=0.1)
    except RuntimeError:
        pass
    if clientID is not None:
        try:
            sendToServer({'type': 'disconnect', 'data': {'id': clientID}})
            clientSocket.close()
        except Exception as e:
            printError(f"Error while tyring to close socket: {e}")
            return

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
                printError("Connection closed")
                return
            else:
                printError(f"Error: {e}")
                continue
        try:
            data = json.loads(data)

            match data['type']:
                case 'disconnect':
                    break
                case 'connect': #Connection successful, get client ID and add it to the lobby member list (used later if the client is a lobby host)
                    printStatus(f"Connected to server, id: {data['data']['id']}")
                    clientID = data['data']['id']
                    lobbyMembersWindow.clientID = clientID
                    lobbyMembersWindow.updateMembersList([{'id': clientID, 'name': f"{name} (you)"}], clientID)

                case 'kickPlayer': #If the client is kicked from the lobby, return to the lobby list
                    printStatus(f"You were kicked :(")
                    activeWindow = kickWindow
                    windowIndex = 12

                case 'createGame': #Game creation sucessful, get the game ID and code
                    printStatus(f"Game created: {data['data']['code']}")
                    gameID = data['data']['id']
                    gameCode = data['data']['code']
                    gameHost = True
                    activeWindow = lobbyMembersWindow
                    windowIndex = 6

                case 'lobbyStatus': #The lobby members have changed, update the list
                    printStatus(f"Current game members: {data['data']['players']}")
                    lobbyMembersWindow.updateMembersList(data['data']['players'], clientID)

                case 'joinGame': #Join game successful, get the game ID and display the 'waiting for host' screen
                    if data['data']['success']:
                        printStatus(f"Game joined: {data['data']['id']}")
                        gameID = data['data']['id']
                        gameHost = False
                        activeWindow = None
                        windowIndex = 7
                    else:
                        printWarning("Failed to join lobby")
                        activeWindow = joinFail
                        windowIndex = 13

                case 'getGames': #Response from the server with the active games list
                    printStatus(f"Games: {data['data']['games']}")
                    gamesList = data['data']['games']
                    if len(gamesList) == 0:
                        printStatus("No active games")
                        gamesList = []

                case 'startGameRes': #Response from the server regarding starting the game
                    if 'fail' in data['data']: #Check if game start was unsuccessful
                        printWarning(f"Game start failed: {data['data']['message']}")
                    else: #Game start successful, display the main game screen
                        printStatus(f"Game starting soon: {data['data']['id']}") 
                        snakeInfo = data['data']['snakeInfo']
                        gameStart = 1
                        windowIndex = 10

                case 'startGame': #Game start message from the server, start moving the snake
                    printStatus(f"Game started: {data['data']['id']}")
                    gameStart = 2

                case 'updateEnvironment': #Update the game environment
                    gameEnvironment = data['data']['environment']

        except Exception as e:
            printError(f"Error: {e}")
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
        if data is not None:
            return ip
    except Exception as e: #Catch any exceptions when trying to connect to the server
        if type(e) == socket.timeout:
            return None
        elif type(e) == KeyboardInterrupt:
            return None
        elif type(e) == TimeoutError:
            return None
        else:
            printError(f"Error while trying to connect to {ip}: {e}")
            return None

def joinLobby(lobbyCode):
    """Join a lobby with the given code"""
    global windowIndex, activeWindow
    printStatus(f"Joining lobby {lobbyCode}")
    if len(lobbyCode) != 4: #Check if the code is the correct length
        printWarning("Invalid lobby code")
        windowIndex = 13
        activeWindow = joinFail
        return
    sendToServer({'type': 'joinGame', 'data': {'id': clientID, 'code': lobbyCode}})

def refreshLobbies():
    """Refresh the active lobbies list (run when the 'refresh' button is clicked)"""
    printStatus("Refreshing lobbies")
    sendToServer({'type': 'getGames', 'data': {'id': clientID}})

def createLobby():
    """Open the lobby creation dialog (run when the 'create lobby' button is clicked)"""
    printStatus("Creating lobby")
    game_modes = ["Last Man Standing"] #, "Time Trial"]
    dialog = lobbyDialog.LobbyDialog(game_modes, createLobbySubmit, marginLeft=25, width=300, height=500)
    dialog.run_dialog()

def joinPrivate():
    """Open the private lobby join dialog (run when the 'join private' button is clicked)"""
    global windowIndex
    printStatus("Joining private lobby")
    windowIndex = 5

def createLobbySubmit(lobbyInfo):
    """Create a lobby with the given information (run when the user completes the lobby creation dialog)"""
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    sendToServer({'type': 'createGame', 'data': {'id': clientID, 'name': lobbyInfo['lobby'], 'public': lobbyInfo['public'], 'mode': lobbyInfo['mode']}})

def kickPlayer(playerID):
    """Kick a player from the lobby (run when the host clicks the 'X' in the lobby member list)"""
    sendToServer({'type': 'kickPlayer', 'data': {'id': clientID, 'playerID': playerID, 'gameID': gameID}})

def returnToLobbyList(changeScreen=True):
    """Big function to clear all game data and return to the active lobbies list"""
    global snakeText, windowIndex, gamesList, startLoadTime, getGamesSent, screen, gameEnvironment, connectionAttemptState, gamesList, gameID, gameEnvironment
    #lots of globals, probably not the best way to do this but it works
    try:
        snakeText = connectionFont.render('Getting active lobbies...', True, WHITE)
        gamesList = None
        startLoadTime = time.time()
        getGamesSent = False
        gameEnvironment = []
        if changeScreen:
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
        gamesList = []
        gameID = None
        gameEnvironment = []
        lobbyMembersWindow.updateMembersList([{'id': clientID, 'name': f"{name} (you)"}], clientID)
        try:
            snakeGame.snake = None
        except:
            pass
        connectionAttemptState = 3
        refreshLobbies()
        windowIndex = 3
    except Exception as e:
        printError(f'Error returning to lobby: {e}')
    printStatus("Returning to lobby!")

"""Initialise variables"""
WIDTH, HEIGHT = 600, 600
SERVER_IP = None
MIN_LOAD_TIME = 1
active, gameHost = False, False
gameID, snakeInfo, clientID, gamesList, gameCode = None, None, None, None, None
gameEnvironment = []
gameStart, windowIndex, frameNum, connectionAttemptState = 0, 0, 0, 0
ips = ipList.getIPList()

clock = pygame.time.Clock()
startLoadTime = time.time() 
#Start load time is used to make a minimum delay between loading screens. Not necessary but allows me to show off the cool spinning snake loading screen.
#If you to change this, you can change the MIN_LOAD_TIME variable.

"""Initialise the socket connection and server listener thread"""
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.settimeout(0.1)
socketThread = threading.Thread(target=socketListener, daemon=True)

"""Initialise the pygame window"""
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Slither Royale")
pygame.mouse.set_cursor(*pygame.cursors.diamond)

"""Initialise variables for the pygame windows"""
loadingSnake.init(WIDTH, HEIGHT)

snakeImg = pygame.image.load('snake.png')

connectionFont = pygame.font.Font(None, 36)
snakeText = connectionFont.render('Connecting to server...', True, WHITE)
text_rect = snakeText.get_rect(center=(WIDTH // 2, HEIGHT // 6-30))

cfWindow = submitDialog.SubmitDialog(WIDTH, HEIGHT, screen, "Could not automatically connect to the server", "Enter server IP:", charLimit=20)
nameWindow = submitDialog.SubmitDialog(WIDTH, HEIGHT, screen, "Welcome to Slither Royale!", "Enter your name:", charLimit=10)
privateWindow = submitDialog.SubmitDialog(WIDTH, HEIGHT, screen, "Join private lobby", "Enter the lobby code:", charLimit=4)

deathWindow = confirmDialog.ConfirmDialog(WIDTH, HEIGHT, screen, "You died!", "Better luck next time :)", returnToLobbyList, "Return to lobby")
kickWindow = confirmDialog.ConfirmDialog(WIDTH, HEIGHT, screen, "You were kicked!", "", returnToLobbyList, "Return to lobby")
joinFail = confirmDialog.ConfirmDialog(WIDTH, HEIGHT, screen, "Failed to join lobby", "The lobby may be full or the code is incorrect.", returnToLobbyList, "Return to Menu")

lobbiesWindow = lobbiesList.LobbiesList(WIDTH, HEIGHT, screen, [], refreshLobbies, createLobby, joinPrivate, joinLobby)

lobbyMembersWindow = lobbyMembersList.LobbyMembersList(WIDTH, HEIGHT, screen, 0, [])
startRectCol = DGREY

textBoxWindows = [cfWindow, nameWindow, privateWindow]
confirmWindows = [deathWindow, kickWindow, joinFail]
activeWindow = nameWindow

while True:
    try:
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
                        if activeWindow == nameWindow and len(activeWindow.input_text) > 0: #User has entered their name, move to the next screen
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
                
                elif activeWindow in confirmWindows: #Handle clicks on the confirmation dialogs
                    if activeWindow.confirmButtonRect.collidepoint(event.pos):
                        activeWindow.confirmFunc()

                elif activeWindow in textBoxWindows: #Handle clicks on the text input boxes

                    if activeWindow.input_box.collidepoint(event.pos): #Set the input box to active if the user clicks on it
                        activeWindow.inputActive = not activeWindow.inputActive
                    else:
                        activeWindow.inputActive = False

                    if activeWindow.buttonRect.collidepoint(event.pos): #Same as pressing enter, submit the text
                        if activeWindow == nameWindow and len(activeWindow.input_text) > 0:
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
                loadingSnake.drawLoadingSnake(clock, screen, moveSegments=(frameNum % 3 == 0)) #To slow down the snake animation, only move the segments every 3 frames
                if connectionAttemptState == 0:
                    if len(ips) == 1:
                        manualConnect = threading.Thread(target=manualConnectThread, args=(ips[0],), daemon=True)
                        manualConnect.start()
                    else:
                        autoConnect = threading.Thread(target=autoConnectThread, daemon=True)
                        autoConnect.start()
                elif connectionAttemptState == 1:
                    pass
                elif connectionAttemptState == 2 and time.time() - startLoadTime > MIN_LOAD_TIME: 
                    #Like mentioned before, the loading screen is displayed for at least 1 second because its cool
                    ip = None
                    windowIndex = 2
                elif connectionAttemptState == 3 and time.time() - startLoadTime > MIN_LOAD_TIME: 
                    #Connection successful, start the socket listener thread
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
                    printStatus(f"Checking IP List: {ips}")
                    startLoadTime = time.time()
                    windowIndex = 1
                    connectionAttemptState = 0

            case 3: #Loading screen, get the active lobbies list
                screen.blit(snakeText, text_rect)
                loadingSnake.init(WIDTH, HEIGHT)
                loadingSnake.drawLoadingSnake(clock, screen, moveSegments=(frameNum % 3 == 0))
                if time.time() - startLoadTime > MIN_LOAD_TIME:
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
                loadingSnake.init(WIDTH, HEIGHT)
                loadingSnake.drawLoadingSnake(clock, screen, moveSegments=(frameNum % 3 == 0))

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
                        printError(f"Error before game start: {e}")

                snakeGame.startGame() #Server has started the game, start the game loop

                while snakeGame.running: #Main game loop
                    try:
                        snakeGame.processSnakeChange()
                        if not snakeGame.running: #If the game is over, return to the lobby list. This is temporaty, the game should probably have a 'game over' screen or a 'respawn' screen depending on game mode
                            printWarning("Game over!")
                            break

                        sendToServer({'type': 'clientUpdate', 'data': {'id': clientID, 'snake': snakeGame.snake}}) #Send the updated snake position to the server

                        snakeGame.updateEnvironment(gameEnvironment) #Update the game environment based on the server response

                        snakeGame.playFrame()
                        sleep(0.15)
                    except KeyboardInterrupt:
                        break

                sendToServer({'type': 'leaveGame', 'data': {'id': clientID, 'gameID': gameID}}) #Game is over, leave the game and return to the lobby list
                #returnToLobbyList()
                screen = pygame.display.set_mode((WIDTH, HEIGHT))
                activeWindow = deathWindow
                windowIndex = 11
            
            case 11: #Game over screen
                deathWindow.displayWindow()
                deathWindow.setHighlights(pygame.mouse.get_pos())

            case 12: #Kicked screen
                kickWindow.displayWindow()
                kickWindow.setHighlights(pygame.mouse.get_pos())

            case 13: #Failed to join lobby screen
                joinFail.displayWindow()
                joinFail.setHighlights(pygame.mouse.get_pos())

        pygame.display.flip()
        clock.tick(15)
    except KeyboardInterrupt:
        break
    except pygame.error as e:
        printError(f"Pygame error: {e}")
        break

quitProgram()
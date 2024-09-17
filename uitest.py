import modules.loadingSnake as ls
import modules.submitDialog as sd
import modules.colouredText as ct
import modules.lobbiesList as ll
import modules.ipList as ipList
import modules.snake as snake
import pygame
from pygame.locals import *
import socket
import json
import time
import threading
from random import randint
from time import sleep

pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WIDTH, HEIGHT = 600, 600
SERVER_IP = None
ls.init(WIDTH, HEIGHT)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("UI Test")

connectionFont = pygame.font.Font(None, 36)
snakeText = connectionFont.render('Connecting to server...', True, WHITE)
text_rect = snakeText.get_rect(center=(WIDTH // 2, HEIGHT // 6-30))

active = False
gameID, snakeInfo, gameEnvironment, clientID, gamesList = None, None, None, None, None
gameHost = False
gameStart = 0

clock = pygame.time.Clock()
windowIndex = 0
startLoadTime = time.time()

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.settimeout(0.1)

def quitProgram():
    pygame.quit()
    socketThread.join(timeout=0.1)
    if clientID is not None:
        clientSocket.sendto(json.dumps({'type': 'disconnect', 'data': {'id': clientID}}).encode(), (SERVER_IP, 65432))
        clientSocket.close()

def fakeGamesList():
    gamesList = []
    for i in range(randint(1, 10)):
        gamesList.append({'id': 'ak1jk1fjkl1j1908-fjajl', 'id':'a' + str(randint(1000, 9999)), 'hostName': 'Adam', 'name': f'Lobby {i}', 'numPlayers': randint(1, 4)})
    return gamesList

def socketListener():
    global gameID, clientID, gameHost, snakeInfo, gameStart, gameEnvironment, gamesList, windowIndex
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
            elif data['type'] == 'connect':
                ct.printStatus(f"Connected to server, id: {data['data']['id']}")
                clientID = data['data']['id']
            elif data['type'] == 'createGame':
                ct.printStatus(f"Game created: {data['data']['code']}")
                gameID = data['data']['id']
                gameHost = True
            elif data['type'] == 'joinGame':
                ct.printStatus(f"Game joined: {data['data']['id']}")
                gameID = data['data']['id']
                gameHost = False
                windowIndex = 5
            elif data['type'] == 'getGames':
                ct.printStatus(f"Games: {data['data']['games']}")
                gamesList = data['data']['games']
                if len(gamesList) == 0:
                    ct.printStatus("No active games")
                    gamesList = fakeGamesList()
            elif data['type'] == 'startGameRes':
                if 'fail' in data['data']:
                    ct.printWarning(
                        f"Game start failed: {data['data']['message']}")
                else:
                    ct.printStatus(f"Game starting soon: {data['data']['id']}")
                    snakeInfo = data['data']['snakeInfo']
                    gameStart = 1
                    windowIndex = 6
            elif data['type'] == 'startGame':
                ct.printStatus(f"Game started: {data['data']['id']}")
                gameStart = 2
            elif data['type'] == 'updateEnvironment':
                gameEnvironment = data['data']['environment']
        except Exception as e:
            ct.printError(f"Error: {e}")
            break

def autoConnectThread():
    global connectionAttemptState, SERVER_IP
    connectionAttemptState = 1
    for i in ipList.getIPList():
        ip = attemptConnection(i)
        if ip is not None:
            SERVER_IP = ip
            connectionAttemptState = 3
            return
    ip = attemptConnection(ipList.getLocalIP())
    if ip is not None:
        ipList.addToIPList(ip)
        SERVER_IP = ip
        connectionAttemptState = 3
        return
    connectionAttemptState = 2

def manualConnectThread(manualIP):
    global connectionAttemptState, SERVER_IP
    ip = attemptConnection(manualIP)
    if ip is not None:
        SERVER_IP = ip
        connectionAttemptState = 3
        return
    connectionAttemptState = 2

def attemptConnection(ip, testLocal=True):
    data, addr = None, None
    clientSocket.settimeout(0.5)
    try:
        clientSocket.sendto(json.dumps({'type': 'ping', 'data': {}}).encode(), (ip, 65432))
        time.sleep(0.1)
        data, addr = clientSocket.recvfrom(4096)
        print(data, addr)
        if data is not None:
            print(data)
            return ip
    except Exception as e:
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

def refreshLobbies():
    ct.printStatus("Refreshing lobbies")
    clientSocket.sendto(json.dumps({'type': 'getGames', 'data': {'id': clientID}}).encode(), (SERVER_IP, 65432))

def createLobby():
    ct.printStatus("Creating lobby")

def joinPrivate():
    ct.printStatus("Joining private lobby")

def joinLobby(lobbyCode):
    ct.printStatus(f"Joining lobby {lobbyCode}")
    if lobbyCode[0] == 'a':
        return
    clientSocket.sendto(json.dumps({'type': 'joinGame', 'data': {'id': clientID, 'code': lobbyCode}}).encode(), (SERVER_IP, 65432))

def returnToLobbyList():
    global snakeText, windowIndex, gamesList, startLoadTime, getGamesSent, clientSnake, screen
    snakeText = connectionFont.render('Getting active lobbies...', True, WHITE)
    gamesList = None
    startLoadTime = time.time()
    getGamesSent = False
    clientSnake = None
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    windowIndex = 3

cfWindow = sd.submitDialog(WIDTH, HEIGHT, screen, "Could not automatically connect to the server", "Enter server IP:")
nameWindow = sd.submitDialog(WIDTH, HEIGHT, screen, "Welcome to Adam's Snake!", "Enter your name:")

lobbiesWindow = ll.lobbiesList(WIDTH, HEIGHT, screen, [], refreshLobbies, createLobby, joinPrivate, joinLobby)

textBoxWindows = [cfWindow, nameWindow]

activeWindow = nameWindow


socketThread = threading.Thread(target=socketListener, daemon=True)
#socketThread.start()

ips = ipList.getIPList()
frameNum = 0
connectionAttemptState = 0
pygame.mouse.set_cursor(*pygame.cursors.diamond)
while True:
    frameNum += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quitProgram()
        elif event.type == KEYDOWN:
            if activeWindow in textBoxWindows:
                if event.key == K_RETURN:
                    print(activeWindow.input_text)
                    ip = activeWindow.input_text
                    activeWindow.input_text = ''
                elif event.key == K_BACKSPACE:
                    activeWindow.input_text = activeWindow.input_text[:-1]
                else:
                    activeWindow.input_text += event.unicode
        elif event.type == MOUSEBUTTONDOWN:
            if activeWindow == lobbiesWindow:
                lobbiesWindow.handleMouseClick(pygame.mouse.get_pos())

            elif activeWindow in textBoxWindows:
                if activeWindow.input_box.collidepoint(event.pos):
                    activeWindow.inputActive = not activeWindow.inputActive
                else:
                    activeWindow.inputActive = False
                if activeWindow.buttonRect.collidepoint(event.pos):
                    if activeWindow == nameWindow:
                        name = activeWindow.input_text
                        startLoadTime = time.time()
                        windowIndex = 1
                    elif activeWindow == cfWindow:
                        ip = activeWindow.input_text
                    activeWindow.input_text = ''

    screen.fill(BLACK)

    if windowIndex == 0:
        activeWindow = nameWindow
        nameWindow.setHighlights(pygame.mouse.get_pos())
        nameWindow.displayWindow()

    elif windowIndex == 1:
        screen.blit(snakeText, text_rect)
        ls.drawLoadingSnake(clock, screen, moveSegments=(frameNum % 3 == 0)) #make it so the snake gets bigger!!
        if connectionAttemptState == 0:
            if len(ips) == 1:
                manualConnect = threading.Thread(target=manualConnectThread, args=(ips[0],), daemon=True)
                manualConnect.start()
            else:
                autoConnect = threading.Thread(target=autoConnectThread, daemon=True)
                autoConnect.start()
        if connectionAttemptState == 1:
            pass
        if connectionAttemptState == 2 and time.time() - startLoadTime > 1:
            ip = None
            windowIndex = 2
        if connectionAttemptState == 3 and time.time() - startLoadTime > 1:
            socketThread.start()
            clientSocket.sendto(json.dumps({'type': 'connect', 'data': {'name': name}}).encode(), (SERVER_IP, 65432))
            startLoadTime = time.time()
            snakeText = connectionFont.render('Getting active lobbies...', True, WHITE)
            getGamesSent = False
            windowIndex = 3

    elif windowIndex == 2:
        activeWindow = cfWindow
        cfWindow.setHighlights(pygame.mouse.get_pos())
        cfWindow.displayWindow()
        if ip is not None:
            ips = [str(ip)]
            startLoadTime = time.time()
            windowIndex = 1

    elif windowIndex == 3:
        screen.blit(snakeText, text_rect)
        ls.drawLoadingSnake(clock, screen, moveSegments=(frameNum % 3 == 0))
        if clientID is not None and gamesList is None and time.time() - startLoadTime > 1 and not getGamesSent:
            getGamesSent = True
            clientSocket.sendto(json.dumps({'type': 'getGames', 'data': {'id': clientID}}).encode(), (SERVER_IP, 65432))
        if gamesList is not None:
            lobbiesWindow.lobbies = gamesList
            windowIndex = 4

    elif windowIndex == 4:
        activeWindow = lobbiesWindow
        lobbiesWindow.lobbies = gamesList
        lobbiesWindow.displayWindow()
        lobbiesWindow.setHighlights(pygame.mouse.get_pos())

    elif windowIndex == 5:
        snakeText = connectionFont.render('Waiting for host to start...', True, WHITE)
        screen.blit(snakeText, text_rect)
        ls.drawLoadingSnake(clock, screen, moveSegments=(frameNum % 3 == 0))

    elif windowIndex == 6:
        if len(snakeInfo) == 0:
            socketThread.join(timeout=0.1)
            clientSocket.sendto(json.dumps({'type': 'disconnect', 'data': {
                                'id': clientID}}).encode(), (SERVER_IP, 65432))
            clientSocket.close()
            quit()

        screen = pygame.display.set_mode((800, 600))
        snakeGame = snake.snakeGame(screen, (800, 600), 40, snakeInfo)
        clientSocket.sendto(json.dumps({'type': 'clientUpdate', 'data': {
                            'id': clientID, 'snake': snakeGame.snake}}).encode(), (SERVER_IP, 65432))
        
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
                    print("Game over")
                    break
                clientSnake = snakeGame.snake

                clientSocket.sendto(json.dumps({'type': 'clientUpdate', 'data': {
                                    'id': clientID, 'snake': clientSnake}}).encode(), (SERVER_IP, 65432))

                snakeGame.updateEnvironment(gameEnvironment)

                snakeGame.playFrame()
                sleep(0.15)
            except KeyboardInterrupt:
                break

        clientSocket.sendto(json.dumps({'type': 'leaveGame', 'data': {'id': clientID, 'gameID':gameID}}).encode(), (SERVER_IP, 65432))
        returnToLobbyList()

    pygame.display.flip()

    clock.tick(15)

socketThread.join(timeout=0.1)
clientSocket.sendto(json.dumps({'type': 'disconnect', 'data': {
                    'id': clientID}}).encode(), (SERVER_IP, 65432))
clientSocket.close()

import pygame
from random import randint

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_a,
    K_d,
    K_s,
    K_w,
    KEYDOWN,
    QUIT
)
def quitProgram():
    pygame.quit()
    quit()

moveKeys = {
    'up': [pygame.K_UP, pygame.K_w],
    'down': [pygame.K_DOWN, pygame.K_s],
    'left': [pygame.K_LEFT, pygame.K_a],
    'right': [pygame.K_RIGHT, pygame.K_d]
}

def isKeyInMoveKeys(key):
    for keys in moveKeys.values():
        if key in keys:
            return True
    return False

def getRandApplePos(snake, gridWidth=20, gridHeight=15):
    randPos = (
        (randint(1, gridWidth-1)),
        (randint(1, gridHeight-1))
    )
    while randPos in snake['body']:
        randPos = (
            (randint(1, gridWidth-1)),
            (randint(1, gridHeight-1))
        )
    return randPos

SCREENWIDTH = 800
SCREENHEIGHT = 700
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class snakeGame:
    def __init__(self, gridPX, blockSize, snakeInfo):
        self.GRIDWIDTHPX = gridPX[0]
        self.GRIDHEIGHTPX = gridPX[1]
        self.BLOCKSIZE = blockSize
        self.GRIDWIDTH = gridPX[0] // blockSize
        self.GRIDHEIGHT = gridPX[1] // blockSize
        self.snake = snakeInfo[0]
        self.x_change = snakeInfo[1]
        self.y_change = 0
        self.velocity = 1
        self.environment = []

    def startGame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.gameOver = False

    def drawGrid(self):
        gridSize = (self.GRIDWIDTH, self.GRIDHEIGHT)
        for x in range(gridSize[0]):
            for y in range(gridSize[1]):
                rect = pygame.Rect(x*self.BLOCKSIZE, y*self.BLOCKSIZE, self.BLOCKSIZE, self.BLOCKSIZE)
                pygame.draw.rect(self.screen, WHITE, rect, 1)
    
    def updateEnvironment(self, environment):
        self.environment = environment

    def drawEnvironment(self):
        for element in self.environment:
            if element['type'] == 'food':
                self.drawApple(element['pos'])
            elif element['type'] == 'rect':
                pygame.draw.rect(self.screen, element['colour'], element['rect'])
            elif element['type'] == 'circle':
                pygame.draw.circle(self.screen, element['colour'], element['pos'], element['radius'])

    def drawSnake(self):
        for i in self.snake['body']:
            bodyRect = pygame.Rect(i[0]*self.BLOCKSIZE, i[1]*self.BLOCKSIZE, self.BLOCKSIZE, self.BLOCKSIZE)
            pygame.draw.rect(self.screen, (50, 125, 0), bodyRect)
        
        headRect = pygame.Rect(self.snake['head'][0]*self.BLOCKSIZE, self.snake['head'][1]*self.BLOCKSIZE, self.BLOCKSIZE, self.BLOCKSIZE)
        pygame.draw.rect(self.screen, (180, 20, 0), headRect)

        eyeSize = self.BLOCKSIZE // 8
        eyeOffset = self.BLOCKSIZE // 8

        eye1Pos, eye2Pos = self.getEyes(eyeOffset, self.snake['direction'], headRect)

        pygame.draw.circle(self.screen, (255, 255, 255), eye1Pos, eyeSize)
        pygame.draw.circle(self.screen, (255, 255, 255), eye2Pos, eyeSize)
    
    def getEyes(self, offset, direction, headRect):
        if direction == (0, -self.velocity):
            eye1Pos = (headRect.left + offset, headRect.top + offset)
            eye2Pos = (headRect.right - offset * 2, headRect.top + offset)
        elif direction == (0, self.velocity):
            eye1Pos = (headRect.left + offset, headRect.bottom - offset * 2)
            eye2Pos = (headRect.right - offset * 2, headRect.bottom - offset * 2)
        elif direction == (-self.velocity, 0):
            eye1Pos = (headRect.left + offset, headRect.top + offset)
            eye2Pos = (headRect.left + offset, headRect.bottom - offset * 2)
        elif direction == (self.velocity, 0):
            eye1Pos = (headRect.right - offset * 2, headRect.top + offset)
            eye2Pos = (headRect.right - offset * 2, headRect.bottom - offset * 2)
        
        return eye1Pos, eye2Pos
    
    def drawApple(self, applePos):
        pygame.draw.circle(self.screen, 
                            (255, 0, 0),
                            (applePos[0]*self.BLOCKSIZE + (self.BLOCKSIZE/2), applePos[1]*self.BLOCKSIZE + (self.BLOCKSIZE/2)), 
                            self.BLOCKSIZE/2.3)

    def increaseSnakeLength(self):
        self.snake['body'].insert(0, self.snake['last'])
        self.snake['length'] += 1

    def processSnakeChange(self):
        moveQueue = []
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    quitProgram()
                else:
                    if isKeyInMoveKeys(event.key) and len(moveQueue) < 6:
                        moveQueue.append(event.key)
            elif event.type == QUIT:
                quitProgram()

        if len(moveQueue) > 0:
            movementOccured = True
            while True:
                if len(moveQueue) == 0:
                    break
                key = moveQueue.pop(0)
                if key in moveKeys['up'] and self.y_change == 0:
                    self.x_change = 0
                    self.y_change = -self.velocity
                elif key in moveKeys['down'] and self.y_change == 0:
                    self.x_change = 0
                    self.y_change = self.velocity
                elif key in moveKeys['left'] and self.x_change == 0:
                    self.x_change = -self.velocity
                    self.y_change = 0
                elif key in moveKeys['right'] and self.x_change == 0:
                    self.x_change = self.velocity
                    self.y_change = 0
                else:
                    movementOccured = False
                if movementOccured:
                    break

        self.snake['direction'] = (self.x_change, self.y_change)
        if self.x_change != 0 or self.y_change != 0:
            self.snake['last'] = self.snake['body'][1]
            self.snake['body'].append(self.snake['head'])
            self.snake['body'] = self.snake['body'][1:]

        self.snake['head'] = (self.snake['head'][0] + self.x_change, self.snake['head'][1] + self.y_change)

    def playFrame(self):
        self.screen.fill(BLACK)
        self.drawGrid()
        self.drawEnvironment()

        self.drawSnake()
        pygame.display.update()

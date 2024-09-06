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

def drawGrid(gridWidth=20, gridHeight=15):
    gridSize = (gridWidth, gridHeight)
    for x in range(gridSize[0]):
        for y in range(gridSize[1]):
            rect = pygame.Rect(x*BLOCKSIZE, y*BLOCKSIZE, BLOCKSIZE, BLOCKSIZE)
            pygame.draw.rect(screen, WHITE, rect, 1)

    return gridSize


def drawSnake(snake):
    for i in snake['body']:
        bodyRect = pygame.Rect(i[0]*BLOCKSIZE, i[1]*BLOCKSIZE, BLOCKSIZE, BLOCKSIZE)
        pygame.draw.rect(screen, (50, 125, 0), bodyRect)

    headRect = pygame.Rect(
        snake['head'][0]*BLOCKSIZE, snake['head'][1]*BLOCKSIZE, BLOCKSIZE, BLOCKSIZE)
    pygame.draw.rect(screen, (180, 20, 0), headRect)

    eyeSize = BLOCKSIZE // 8
    eyeOffset = BLOCKSIZE // 8

    eye1Pos, eye2Pos = getEyes(eyeOffset, snake['direction'], headRect)

    pygame.draw.circle(screen, (255, 255, 255), eye1Pos, eyeSize)
    pygame.draw.circle(screen, (255, 255, 255), eye2Pos, eyeSize)

def getEyes(offset, direction, headRect):
    if direction == (0, -velocity):
        eye1Pos = (headRect.left + offset, headRect.top + offset)
        eye2Pos = (headRect.right - offset * 2, headRect.top + offset)
    elif direction == (0, velocity):
        eye1Pos = (headRect.left + offset,
                    headRect.bottom - offset * 2)
        eye2Pos = (headRect.right - offset * 2,
                    headRect.bottom - offset * 2)
    elif direction == (-velocity, 0):
        eye1Pos = (headRect.left + offset, headRect.top + offset)
        eye2Pos = (headRect.left + offset,
                    headRect.bottom - offset * 2)
    elif direction == (velocity, 0):
        eye1Pos = (headRect.right - offset * 2, headRect.top + offset)
        eye2Pos = (headRect.right - offset * 2,
                   headRect.bottom - offset * 2)
    else:
        eye1Pos = (headRect.left + offset,
                   headRect.bottom - offset * 2)
        eye2Pos = (headRect.right - offset * 2,
                   headRect.bottom - offset * 2)
    return eye1Pos, eye2Pos

def drawApple(applePos):
    #bodyRect = pygame.Rect(applePos[0], applePos[1], BLOCKSIZE, BLOCKSIZE)
    pygame.draw.circle(screen, 
                        (255, 0, 0),
                        (applePos[0]*BLOCKSIZE + (BLOCKSIZE/2), applePos[1]*BLOCKSIZE + (BLOCKSIZE/2)), 
                        BLOCKSIZE/2.3)


def getRandApplePos(gridWidth=20, gridHeight=15):
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

def processSnakeChange(snake, x_change, y_change):
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
            if len(moveQueue) < 1:
                break
            key = moveQueue[0]
            moveQueue = moveQueue[1:]
            if key in moveKeys['up']:
                if y_change != velocity:
                    y_change = -velocity
                    x_change = 0
            elif key in moveKeys['down']:
                if y_change != -velocity:
                    y_change = velocity
                    x_change = 0
            elif key in moveKeys['left']:
                if x_change != velocity:
                    x_change = -velocity
                    y_change = 0
            elif key in moveKeys['right']:
                if x_change != -velocity:
                    x_change = velocity
                    y_change = 0
            else:
                movementOccured = False
            if movementOccured:
                break

    snake['direction'] = (x_change, y_change)
    if x_change != 0 or y_change != 0:
        snake['last'] = snake['body'][1]
        snake['body'].append(snake['head'])
        snake['body'] = snake['body'][1:]

    snake['head'] = (snake['head'][0] + x_change, snake['head'][1] + y_change)

    return snake, x_change, y_change

pygame.init()

SCREENWIDTH = 800
SCREENHEIGHT = 700
GRIDWIDTHPX = 800
GRIDHEIGHTPX = 600
BLOCKSIZE = 40
GRIDWIDTH = GRIDWIDTHPX // BLOCKSIZE
GRIDHEIGHT = GRIDHEIGHTPX // BLOCKSIZE
BLACK = (0,0,0)
WHITE = (255, 255, 255)
objectCenter = lambda object : (
    (SCREENWIDTH-object.get_width())/2,
    (SCREENHEIGHT-object.get_height())/2,
)
snake = {'length': 3, 'head': (0, 3), 'body': [(
    0, 1), (0, 2)], 'last': (0, 0), 'direction': (0, 0)
}

screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
screen.fill(BLACK)
CLOCK = pygame.time.Clock()

velocity = 1
x_change = 0
y_change = 0
applePos = getRandApplePos()
moveQueue = []
running = True


def createSnake():
    headPos = (randint(0, 1) * (GRIDWIDTH-1), randint(0, GRIDHEIGHT-1))

    if headPos[0] == 0:
        direction = (velocity, 0)
    else:
        direction = (-velocity, 0)
    body = [headPos, headPos]
    return ({'length': 3, 'head': headPos, 'body': body, 'direction': direction, 'last': (0, 0)}, direction[0])

snake, x_change = createSnake()
while True:
    screen.fill(BLACK)
    drawGrid(GRIDWIDTH, GRIDHEIGHT)

    snake, x_change, y_change = processSnakeChange(snake, x_change, y_change)    

    if snake['head'] == applePos:
        applePos = getRandApplePos()
        snake['body'].insert(0, snake['last'])
        snake['length'] += 1

    if snake['head'] in snake['body'] and snake['length'] > 3:
        print('game over')
        running = False

    if snake['head'][0] >= GRIDWIDTH or snake['head'][1] >= GRIDHEIGHT or snake['head'][0] < 0 or snake['head'][1] < 0:
        print('game over')
        running = False
    if not running:
        break

    drawSnake(snake)
    drawApple(applePos)

    pygame.display.update()
    CLOCK.tick(5)                
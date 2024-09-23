import pygame
from random import randint
import ctypes
from time import sleep
from modules.colours import *

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

# Define the keys for movement. Both arrow keys and WASD are supported.
moveKeys = {
    'up': [pygame.K_UP, pygame.K_w],
    'down': [pygame.K_DOWN, pygame.K_s],
    'left': [pygame.K_LEFT, pygame.K_a],
    'right': [pygame.K_RIGHT, pygame.K_d]
}

def isKeyInMoveKeys(key):
    # Check if the key is in the moveKeys dictionary
    for keys in moveKeys.values():
        if key in keys:
            return True
    return False

class snakeGame:
    """Initial Variables"""
    velocity = 1
    environment = []
    running = False
    moveQueue = []
    y_change = 0

    def __init__(self, screen, gridPX, blockSize, snakeInfo):
        self.GRIDWIDTHPX = gridPX[0]
        self.GRIDHEIGHTPX = gridPX[1]
        self.BLOCKSIZE = blockSize
        self.GRIDWIDTH = gridPX[0] // blockSize
        self.GRIDHEIGHT = gridPX[1] // blockSize
        self.snake = snakeInfo[0]
        self.x_change = snakeInfo[1]
        self.snake['direction'] = (self.x_change, self.y_change)

        #Set up the screen
        self.screen = screen
        self.clock = pygame.time.Clock()
        sleep(0.1)
        
        try: #Bring the window to the front (a bit janky)
            user32 = ctypes.windll.user32
            user32.SetForegroundWindow(pygame.display.get_wm_info()['window'])
        except:
            pass

        #Draw the grid and snake
        self.screen.fill(BLACK)
        self.drawGrid()
        self.drawSnake(self.snake)
        pygame.display.update()

    def startGame(self):
        """Start the game"""
        self.running = True
        self.gameOver = False

    def quitProgram(self):
        """Quit the game"""
        self.running = False

    def drawGrid(self):
        """Draw the grid"""
        gridSize = (self.GRIDWIDTH, self.GRIDHEIGHT)

        for x in range(gridSize[0]):
            for y in range(gridSize[1]):
                rect = pygame.Rect(x*self.BLOCKSIZE, y*self.BLOCKSIZE, self.BLOCKSIZE, self.BLOCKSIZE)
                pygame.draw.rect(self.screen, WHITE, rect, 1)
    
    def updateEnvironment(self, environment):
        """Get the environment. This function used to be more complicated, but the envrionment system was simplified. This function is probably not needed anymore."""
        self.environment = environment

    def getSnakeAsEnvironment(self):
        """Get the snake as an environment element. Same story as the updateEnvironment function."""
        return self.snake

    def drawEnvironment(self):
        """Draw the environment"""

        for element in self.environment:
            match element['type']:
                case 'food':
                    self.drawApple(element['pos'])
                case 'snake':
                    self.drawSnake(element['snake'], headColour=(0, 0, 255))

    def getEyes(self, offset, direction, headRect):
        """Get the position of the eyes based on the direction of the snake"""
        eye1Pos, eye2Pos = (0, 0), (0, 0)
        if direction == (0, -self.velocity):
            eye1Pos = (headRect.left + offset, headRect.top + offset)
            eye2Pos = (headRect.right - offset * 2, headRect.top + offset)
        elif direction == (0, self.velocity):
            eye1Pos = (headRect.left + offset, headRect.bottom - offset * 2)
            eye2Pos = (headRect.right - offset * 2,
                       headRect.bottom - offset * 2)
        elif direction == (-self.velocity, 0):
            eye1Pos = (headRect.left + offset, headRect.top + offset)
            eye2Pos = (headRect.left + offset, headRect.bottom - offset * 2)
        elif direction == (self.velocity, 0):
            eye1Pos = (headRect.right - offset * 2, headRect.top + offset)
            eye2Pos = (headRect.right - offset * 2,
                       headRect.bottom - offset * 2)

        return (eye1Pos, eye2Pos)

    def drawEyes(self, snake):
        """Draw the eyes of the snake"""
        eyeSize = self.BLOCKSIZE // 8
        eyeOffset = self.BLOCKSIZE // 8
        headRect = pygame.Rect(snake['head'][0]*self.BLOCKSIZE, snake['head'][1]*self.BLOCKSIZE, self.BLOCKSIZE, self.BLOCKSIZE)

        eye1Pos, eye2Pos = self.getEyes(eyeOffset, tuple(snake['direction']), headRect)

        pygame.draw.circle(self.screen, (255, 255, 255), eye1Pos, eyeSize)
        pygame.draw.circle(self.screen, (255, 255, 255), eye2Pos, eyeSize)

    def drawSnake(self, snake, headColour=(180, 20, 0)):
        """Draw the snake"""
        for i in snake['body']:
            bodyRect = pygame.Rect(i[0]*self.BLOCKSIZE, i[1]*self.BLOCKSIZE, self.BLOCKSIZE, self.BLOCKSIZE)
            pygame.draw.rect(self.screen, (50, 125, 0), bodyRect)
        
        headRect = pygame.Rect(snake['head'][0]*self.BLOCKSIZE, snake['head'][1]*self.BLOCKSIZE, self.BLOCKSIZE, self.BLOCKSIZE)
        pygame.draw.rect(self.screen, headColour, headRect)

        self.drawEyes(snake)

    def drawScore(self):
        """Draw the score"""
        score = pygame.font.Font('freesansbold.ttf', 32).render(f'Score: {self.snake["length"]}', True, WHITE)
        textRect = score.get_rect()
        textRect.center = (textRect.width/2 + 10, self.GRIDHEIGHTPX - 20)
        self.screen.blit(score, textRect)
    
    def drawApple(self, applePos):
        """Draw the apple"""
        pygame.draw.circle(self.screen, (255, 0, 0), (applePos[0]*self.BLOCKSIZE + (self.BLOCKSIZE/2), applePos[1]*self.BLOCKSIZE + (self.BLOCKSIZE/2)), self.BLOCKSIZE/2.3)

    def increaseSnakeLength(self):
        """Increase the length of the snake by one"""
        self.snake['body'].insert(0, self.snake['last'])
        self.snake['length'] += 1

    def checkLocalCollision(self, headPos):
        """Check for collision, return its type"""
        snake = self.snake
        if headPos in snake['body'] and snake['length'] > 3:
            return 'self'
        if headPos[0] < 0 or headPos[0] >= self.GRIDWIDTH or headPos[1] < 0 or headPos[1] >= self.GRIDHEIGHT: #Check if the snake is out of bounds
            return 'wall'
        for element in self.environment:
            match element['type']:
                case 'rect':
                    if tuple(headPos) == tuple(element['pos']):
                        return 'snake'
                case 'food':
                    if tuple(headPos) == tuple(element['pos']):
                        return 'food'
                case 'snake':
                    if list(headPos) in element['snake']['body']:
                        return 'snake'
                    if tuple(headPos) == tuple(element['snake']['head']):
                        return 'head'

    def getMoveQueue(self):
        """
        Get the move queue.
        As the client can press multiple keys within a single frame, the move queue is used to store the keys that are pressed.
        Every frame, one of these keys is popped from the queue and the snake moves in that direction.
        This makes the game much more responsive, and is pretty essential as otherwise movement feels really clunky.
        """
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.quitProgram()
                else:
                    if isKeyInMoveKeys(event.key) and len(self.moveQueue) < 6: #Limit the amount of keys in the queue
                        self.moveQueue.append(event.key)
            elif event.type == QUIT:
                self.quitProgram()

    def processSnakeChange(self):
        """Process the snake movement"""
        self.getMoveQueue()

        if len(self.moveQueue) > 0:
            movementOccured = True
            while True:
                #Pop the first key from the queue and attempt to move the snake.
                #If it is not a valid move, try the next key in the queue.
                if len(self.moveQueue) == 0:
                    break
                key = self.moveQueue.pop(0)
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
                    #If movement happened, chaange the direction of the snake and draw the eyes accordingly.
                    self.snake['direction'] = (self.x_change, self.y_change)
                    self.drawEyes(self.snake)
                    break

        #Check for collision
        collision = self.checkLocalCollision((self.snake['head'][0] + self.x_change, self.snake['head'][1] + self.y_change))
        match collision:
            #Currently these are all the same but could be different, for instance if the the walls are an instant death or similar to the walls in pacman that teleport you to the other side.
            case 'wall':
                self.playFrame()
                sleep(0.1)
                self.quitProgram()
            case 'self':
                self.playFrame()
                sleep(0.1)
                self.quitProgram()
            case 'snake':
                self.playFrame()
                sleep(0.1)
                self.quitProgram()
            case 'head':
                self.playFrame()
                sleep(0.1)
                self.quitProgram()

        #Move the snake. This must be done after the collision check but before the snake length is increased.
        if self.x_change != 0 or self.y_change != 0:
            self.snake['last'] = self.snake['body'][1]
            self.snake['body'].append(self.snake['head'])
            self.snake['body'] = self.snake['body'][1:]

        #Move the head of the snake
        self.snake['head'] = (self.snake['head'][0] + self.x_change, self.snake['head'][1] + self.y_change)

        #Finally, check if the snake has eaten food
        if collision == 'food':
            self.increaseSnakeLength()

    def playFrame(self, drawEnvironment=True):
        """Play a frame of the game"""
        self.screen.fill(BLACK)
        self.drawGrid()
        if drawEnvironment:
            self.drawEnvironment()

        self.drawSnake(self.snake)
        self.drawScore()
        pygame.display.update()

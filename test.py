import snake
from time import sleep
import pygame

snakeInfo = [{"length": 3, "head": [0, 3], "body": [[0, 3], [0, 3]], "direction": [1, 0], "last": [0, 0]}, 1]

snakeGame = snake.snakeGame((800, 600), 40, snakeInfo)
snakeGame.startGame()
food = {'type': 'food', 'pos': snake.getRandApplePos(snakeInfo[0])}
while True:
    snakeGame.processSnakeChange()
    snakeGame.updateEnvironment([food, {'type': 'rect', 'colour': (255, 0, 0), 'rect': pygame.Rect(0, 0, 40, 40)}])

    snakeObj = snakeGame.snake
    if snakeObj['head'] == food['pos']:
        food['pos'] = snake.getRandApplePos(snakeGame.snake)
        snakeGame.increaseSnakeLength()

    if snakeObj['head'] in snakeObj['body'] and snakeObj['length'] > 3:
        print("Game Over")
        break

    if snakeObj['head'][0] > snakeGame.GRIDWIDTH-1 or snakeObj['head'][0] < 0 or snakeObj['head'][1] > snakeGame.GRIDHEIGHT-1 or snakeObj['head'][1] < 0:
        print("Game Over")
        break

    snakeGame.playFrame()

    sleep(0.15)


import modules.loadingSnake as ls
import modules.connectionFailed as cf
import pygame
from pygame.locals import *

pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WIDTH, HEIGHT = 600, 600
ls.init(WIDTH, HEIGHT)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("UI Test")

connectionFont = pygame.font.Font(None, 36)
text = connectionFont.render('Connecting to server...', True, WHITE)
text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 6-30))


active = False

cfWindow = cf.connectionFailed(WIDTH, HEIGHT, screen)

clock = pygame.time.Clock()
serverConnection = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == KEYDOWN:
            if not cfWindow.inputActive:
                if event.key == K_1:
                    serverConnection = 1
                elif event.key == K_2:
                    serverConnection = 2
            else:
                if event.key == K_RETURN:
                    print(cfWindow.input_text)
                    cfWindow.input_text = ''
                elif event.key == K_BACKSPACE:
                    cfWindow.input_text = cfWindow.input_text[:-1]
                else:
                    cfWindow.input_text += event.unicode
        elif event.type == MOUSEBUTTONDOWN:
            if cfWindow.input_box.collidepoint(event.pos):
                cfWindow.inputActive = not cfWindow.inputActive
            else:
                cfWindow.inputActive = False
            if cfWindow.buttonRect.collidepoint(event.pos):
                print(cfWindow.input_text)
                cfWindow.input_text = ''

    screen.fill(BLACK)

    if serverConnection == 0:
        screen.blit(text, text_rect)
        ls.drawLoadingSnake(clock, screen) #make it so the snake gets bigger!!
    elif serverConnection == 1:
        cfWindow.setHighlights(pygame.mouse.get_pos())

        cfWindow.displayWindow()

    pygame.display.flip()

    clock.tick(5)

# Quit Pygame
pygame.quit()

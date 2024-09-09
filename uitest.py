from loadingSnake import drawLoadingSnake, setScreenDimensions
import pygame
from pygame.locals import *
# Initialize Pygame
pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WIDTH, HEIGHT = 600, 600
setScreenDimensions(WIDTH, HEIGHT)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("UI Test")

font = pygame.font.Font(None, 36)
text = font.render('Connecting to server...', True, WHITE)
text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 6-30))

popup_font = pygame.font.Font(None, 28)
popup_text1 = popup_font.render("Could not automatically connect to the server", True, WHITE)
popup_rect1 = popup_text1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
popup_text2 = popup_font.render("Enter server IP:", True, WHITE)
popup_rect2 = popup_text2.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))

input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 36)
input_text = ''
active = False

clock = pygame.time.Clock()
serverConnection = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == KEYDOWN:
            if not active:
                if event.key == K_1:
                    serverConnection = 1
                elif event.key == K_2:
                    serverConnection = 2
            else:
                if event.key == K_RETURN:
                    print(input_text)
                    input_text = ''
                elif event.key == K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode
        elif event.type == MOUSEBUTTONDOWN:
            if input_box.collidepoint(event.pos):
                active = not active
            else:
                active = False

    screen.fill(BLACK)

    if serverConnection == 0:
        screen.blit(text, text_rect)
        drawLoadingSnake(clock, screen)
    elif serverConnection == 1:
        screen.blit(popup_text1, popup_rect1)
        screen.blit(popup_text2, popup_rect2)

        # Draw the input box
        pygame.draw.rect(screen, WHITE, input_box, 2)

        # Render the text inside the input box
        ip_surface = font.render(input_text, True, WHITE)
        screen.blit(ip_surface, (input_box.x + 5, input_box.y + 5))

        # Adjust the width of the input box based on the length of the text
        input_box.w = max(200, ip_surface.get_width() + 10)

    pygame.display.flip()

    clock.tick(5)

# Quit Pygame
pygame.quit()

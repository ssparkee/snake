import pygame
try:
    from modules.colours import *
except ImportError:
    from colours import *

class ConfirmDialog():
    buttonColour = WHITE

    def __init__(self, width, height, screen, firstline, secondline, confirmFunc, confirmText="Return to Lobby"):
        self.WIDTH = width
        self.HEIGHT = height
        self.screen = screen
        self.confirmFunc = confirmFunc

        self.dialogFont = pygame.font.Font(None, 36)
        self.confirmFont = pygame.font.Font(None, 42)

        self.line1 = self.dialogFont.render(firstline, True, WHITE)
        self.line2 = self.dialogFont.render(secondline, True, WHITE)
        self.rect1 = self.line1.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 80))
        self.rect2 = self.line2.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 20))

        self.confirmButtonText = self.confirmFont.render(confirmText, True, BLACK)
        self.confirmButtonTextRect = self.confirmButtonText.get_rect(center=(self.WIDTH // 2, self.HEIGHT -100))
        self.confirmButtonRect = pygame.Rect((self.WIDTH - self.confirmButtonTextRect.width - 40) // 2, self.HEIGHT - 100, self.confirmButtonTextRect.width + 40, 40)

    def setHighlights(self, mousePos):
        if self.confirmButtonRect.collidepoint(mousePos):
            self.buttonColour = HIGHLIGHT_COLOUR
        else:
            self.buttonColour = WHITE

    def displayWindow(self):
        self.screen.blit(self.line1, self.rect1)
        self.screen.blit(self.line2, self.rect2)

        pygame.draw.rect(self.screen, self.buttonColour, self.confirmButtonRect)
        self.screen.blit(self.confirmButtonText, (self.confirmButtonRect.x + self.confirmButtonRect.width // 2 - self.confirmButtonTextRect.width // 2, self.confirmButtonRect.y + self.confirmButtonRect.height // 2 - self.confirmButtonTextRect.height // 2))

def test():
    print("Confirmed")

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    dialog = ConfirmDialog(800, 600, screen, "Are you sure?", "This action cannot be undone.", test)
    running = True
    while running:
        screen.fill(BLACK)
        dialog.setHighlights(pygame.mouse.get_pos())
        dialog.displayWindow()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if dialog.confirmButtonRect.collidepoint(pygame.mouse.get_pos()):
                    dialog.confirmFunc()
        pygame.display.flip()
    pygame.quit()
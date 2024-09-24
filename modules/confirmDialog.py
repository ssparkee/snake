from modules.colours import *
import pygame

class ConfirmDialog():
    dialogFont = pygame.font.Font(None, 28)
    confirmFont = pygame.font.Font(None, 36)
    buttonSurface = pygame.Surface((150, 30))

    def __init__(self, width, height, screen, firstline, secondline, confirmFunc, confirmText="Confirm"):
        self.WIDTH = width
        self.HEIGHT = height
        self.screen = screen

        self.line1 = self.dialogFont.render(firstline, True, WHITE)
        self.line2 = self.dialogFont.render(secondline, True, WHITE)
        self.rect1 = self.line1.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 50))
        self.rect2 = self.line2.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 20))

        self.confirmButtonText = self.confirmFont.render("Submit", True, BLACK)

    def setHighlights(self):
        pass

    def displayWindow(self):
        pass
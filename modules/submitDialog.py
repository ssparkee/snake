import pygame
from time import time
from modules.colours import *

class submitDialog():
    def __init__(self, width, height, screen, firstline, secondline, charLimit=12):
        self.WIDTH = width
        self.HEIGHT = height
        self.screen = screen
        self.charLimit = charLimit
        self.input_box = pygame.Rect(self.WIDTH // 2 - 100, self.HEIGHT // 2, 200, 36)
        
        self.popup_font = pygame.font.Font(None, 28)
        self.popup_text1 = self.popup_font.render(firstline, True, WHITE)
        self.popup_text2 = self.popup_font.render(secondline, True, WHITE)
        self.popup_rect1 = self.popup_text1.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 50))
        self.popup_rect2 = self.popup_text2.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 20))
        self.input_text = ''
        self.inputActive = False
        self.submitButtonFont = pygame.font.Font(None, 36)
        self.buttonSurface = pygame.Surface((150, 30))

        self.submitButtonText = self.submitButtonFont.render("Submit", True, BLACK)

        self.submitButtonTextRect = self.submitButtonText.get_rect(center=(self.buttonSurface.get_width()/2, self.buttonSurface.get_height()/2))
        self.buttonRect = pygame.Rect(self.WIDTH // 2 - (self.buttonSurface.get_width() // 2), self.HEIGHT // 2 + 50, self.buttonSurface.get_width(), self.buttonSurface.get_height())
        
        self.cursor_visible = True
        self.cursor_last_blink = time()

    def setHighlights(self, mousePos):
        if self.buttonRect.collidepoint(mousePos):
            pygame.draw.rect(self.buttonSurface, (127, 255, 212), (1, 1, self.buttonSurface.get_width()-2, self.buttonSurface.get_height()-2))
            
        else:
            pygame.draw.rect(self.buttonSurface, (0, 0, 0), (0, 0, self.buttonSurface.get_width(), self.buttonSurface.get_height()))
            pygame.draw.rect(self.buttonSurface, (255, 255, 255), (1, 1, self.buttonSurface.get_width()-2, self.buttonSurface.get_height()-2))
            pygame.draw.rect(self.buttonSurface, (0, 0, 0), (1, 1, self.buttonSurface.get_width()-2, 1), 2)
            pygame.draw.rect(self.buttonSurface, (0, 100, 0), (1, self.buttonSurface.get_height()-2, self.buttonSurface.get_width()-2, 10), 2)
            
        if self.input_box.collidepoint(mousePos):
            pygame.draw.rect(self.screen, (127, 255, 212), self.input_box, 2)
        else:
            pygame.draw.rect(self.screen, WHITE, self.input_box, 2)

    def displayWindow(self):
        self.screen.blit(self.popup_text1, self.popup_rect1)
        self.screen.blit(self.popup_text2, self.popup_rect2)

        self.ip_surface = self.submitButtonFont.render(self.input_text, True, WHITE)
        self.screen.blit(self.ip_surface, (self.input_box.x + 5, self.input_box.y + 5))
        self.input_box.w = max(200, self.ip_surface.get_width() + 10)

        current_time = time()
        if current_time - self.cursor_last_blink >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_last_blink = current_time
        
        if self.inputActive and self.cursor_visible:
            cursor_x = self.input_box.x + 5 + self.ip_surface.get_width() + 2
            cursor_y = self.input_box.y + 5
            pygame.draw.line(self.screen, WHITE, (cursor_x, cursor_y), (cursor_x, cursor_y + 26), 2)

        self.buttonSurface.blit(self.submitButtonText, self.submitButtonTextRect)
        self.screen.blit(self.buttonSurface, (self.buttonRect.x, self.buttonRect.y))
    

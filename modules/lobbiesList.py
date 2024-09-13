import pygame
from time import time

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
HIGHLIGHT_COLOR = (127, 255, 212)


class lobbiesList():
    def __init__(self, width, height, screen, lobbies):
        self.WIDTH = width
        self.HEIGHT = height
        self.screen = screen
        self.lobbies = lobbies
        self.lobbyRects = []
        self.highlightRect = None

        self.containerWidth = int(self.WIDTH * 0.9)
        self.containerHeight = 60
        self.containerMargin = 20

        self.buttonWidth = int(self.WIDTH * 0.4)
        self.buttonHeight = 30
        self.createColour = GRAY
        self.refreshColour = GRAY

    def displayWindow(self):
        self.screen.fill(BLACK)

        self.lobbyRects.clear()
        self.updateLobbies()
        for rect, lobby in self.lobbyRects:
            startY = (self.HEIGHT - (len(self.lobbies) * (self.containerHeight + self.containerMargin))) // 2
            containerX = (self.WIDTH - self.containerWidth) // 2
            containerY = startY + self.lobbyRects.index((rect, lobby)) * (self.containerHeight + self.containerMargin)

            if self.highlightRect == rect:
                rectColour = HIGHLIGHT_COLOR
            else:
                rectColour = GRAY
            pygame.draw.rect(self.screen, rectColour, rect)

            font = pygame.font.Font(None, 42)
            hostFont = pygame.font.Font(None, 26)
            hostText = hostFont.render(f"Host: {lobby['hostName']}", True, BLACK)
            nameText = font.render(f"{lobby['name']}", True, BLACK)
            playerText = hostFont.render(f"Players: {lobby['numPlayers']}", True, BLACK)

            self.screen.blit(hostText, (containerX + 10, containerY + self.containerHeight - 20))
            self.screen.blit(nameText, (containerX + 10, containerY + 10))
            self.screen.blit(playerText, (containerX + self.containerWidth - 120, containerY + self.containerHeight - 20))

        createX = 30
        createY = (self.HEIGHT - (self.buttonHeight + 20))
        self.createRect = pygame.Rect(createX, createY, self.buttonWidth, self.buttonHeight)
        pygame.draw.rect(self.screen, self.createColour, self.createRect)

        self.refreshRect = pygame.Rect(self.WIDTH - 30 - self.buttonWidth, createY, self.buttonWidth, self.buttonHeight)
        pygame.draw.rect(self.screen, self.refreshColour, self.refreshRect)

        createFont = pygame.font.Font(None, 26)
        createText = createFont.render("Create Lobby", True, BLACK)
        self.screen.blit(createText, (createX + (self.buttonWidth // 2) - (createText.get_width() // 2), createY + 6))

        refreshText = createFont.render("Refresh", True, BLACK)
        self.screen.blit(refreshText, (self.WIDTH - self.buttonWidth + (createText.get_width() // 2), createY + 6))

        pygame.display.flip()

    def updateLobbies(self):
        startY = (self.HEIGHT - (len(self.lobbies) * (self.containerHeight + self.containerMargin))) // 2
        for i, lobby in enumerate(self.lobbies):
            containerX = (self.WIDTH - self.containerWidth) // 2
            containerY = startY + i * (self.containerHeight + self.containerMargin)

            rect = pygame.Rect(containerX, containerY, self.containerWidth, self.containerHeight)
            self.lobbyRects.append((rect, lobby))

    def setHighlights(self, mousePos):
        self.highlightRect = None
        for rect, lobby in self.lobbyRects:
            if rect.collidepoint(mousePos):
                self.highlightRect = rect
                return True
        if self.createRect.collidepoint(mousePos):
            self.createColour = HIGHLIGHT_COLOR
            return True
        else:
            self.createColour = GRAY
        if self.refreshRect.collidepoint(mousePos):
            self.refreshColour = HIGHLIGHT_COLOR
            return True
        else:
            self.refreshColour = GRAY
        return False

    def handleMouseClick(self, mousePos):
        for rect, lobby in self.lobbyRects:
            if rect.collidepoint(mousePos):
                print(f"Lobby ID: {lobby['id']}")
                return True

        if self.createRect.collidepoint(mousePos):
            print("Create Lobby")
            return True

        if self.refreshRect.collidepoint(mousePos):
            print("Refresh Lobby")
            return True

        return False

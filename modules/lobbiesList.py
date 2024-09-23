"""
This module contains the lobbiesList class which is used to display the list of lobbies available to join.
"""
import pygame
from time import time
from modules.colours import *


class lobbiesList():
    """
    Class to display the list of lobbies available to join.
    """
    def __init__(self, width, height, screen, lobbies, refreshLobbies, createLobby, joinPrivate, joinLobby):
        self.WIDTH = width
        self.HEIGHT = height
        self.screen = screen
        self.lobbies = lobbies
        self.lobbyRects = []
        self.highlightRect = None
        self.buttonColls = []

        self.containerWidth = int(self.WIDTH * 0.9)
        self.containerHeight = 60
        self.containerMargin = 20
        self.startY = 60

        self.buttonWidth = int(self.WIDTH * 0.4)
        self.buttonHeight = 30

        self.refreshLobbies = refreshLobbies
        self.createLobby = createLobby
        self.joinPrivate = joinPrivate
        self.joinLobby = joinLobby

    def getRectColour(self, rect):
        if rect == self.highlightRect:
            return HIGHLIGHT_COLOUR
        else:
            return LGREY

    def displayWindow(self):
        self.screen.fill(BLACK)

        self.lobbyRects.clear()
        self.updateLobbies()

        if len(self.lobbyRects) == 0:
            containerX = (self.WIDTH - self.containerWidth) // 2
            containerY = self.startY
            rect = pygame.Rect(containerX, containerY, self.containerWidth, self.containerHeight)
            pygame.draw.rect(self.screen, LGREY, rect)
            font = pygame.font.Font(None, 42)
            text = font.render("No lobbies available :(", True, BLACK)
            self.screen.blit(text, (containerX + 10, containerY + 10))

        for rect, lobby in self.lobbyRects:            
            containerX = (self.WIDTH - self.containerWidth) // 2
            containerY = self.startY + self.lobbyRects.index((rect, lobby)) * (self.containerHeight + self.containerMargin)

            if self.highlightRect == rect:
                rectColour = HIGHLIGHT_COLOUR
            else:
                rectColour = LGREY
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
        pygame.draw.rect(self.screen, self.getRectColour(self.createRect), self.createRect)
        self.buttonColls.append((self.createRect, self.createLobby))

        self.privateRect = pygame.Rect(self.WIDTH - 30 - self.buttonWidth, createY, self.buttonWidth, self.buttonHeight)
        pygame.draw.rect(self.screen, self.getRectColour(self.privateRect), self.privateRect)
        self.buttonColls.append((self.privateRect, self.joinPrivate))

        self.refreshRect = pygame.Rect(self.WIDTH - 30 - self.buttonWidth, 12, self.buttonWidth, self.buttonHeight)
        pygame.draw.rect(self.screen, self.getRectColour(self.refreshRect), self.refreshRect)
        self.buttonColls.append((self.refreshRect, self.refreshLobbies))

        createFont = pygame.font.Font(None, 26)
        createText = createFont.render("Create Lobby", True, BLACK)
        self.screen.blit(createText, (createX + (self.buttonWidth // 2) - (createText.get_width() // 2), createY + 6))

        privateText = createFont.render("Join Private Lobby", True, BLACK)
        self.screen.blit(privateText, (self.WIDTH - 30 - self.buttonWidth + (self.buttonWidth // 2) - (privateText.get_width() // 2), createY + 6))

        refreshText = createFont.render("Refresh", True, BLACK)
        self.screen.blit(refreshText, (self.WIDTH - 30 - self.buttonWidth + (self.buttonWidth // 2) - (refreshText.get_width() // 2), self.refreshRect.y + 6))

        pygame.display.flip()

    def updateLobbies(self):
        startY = self.startY
        for i, lobby in enumerate(self.lobbies):
            if i > 5:
                break

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
        
        for rect, func in self.buttonColls:
            if rect.collidepoint(mousePos):
                self.highlightRect = rect
                return True
        return False

    def handleMouseClick(self, mousePos):
        for rect, lobby in self.lobbyRects:
            if rect.collidepoint(mousePos):
                print(f"Lobby ID: {lobby['code']}")
                self.joinLobby(lobby['code'])
                return True

        for rect, func in self.buttonColls:
            if rect.collidepoint(mousePos):
                func()
                return True

        return False

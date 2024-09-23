"""
This module contains the class LobbyMembersList which is used to display the list of members in the lobby to the host.
"""
import pygame
from modules.colours import *

class LobbyMembersList:
    """
    Class to display the list of members in the lobby to the host.
    """
    membersList = []
    lobbyRects = []
    highlightRect = None
    def __init__(self, width, height, screen, clientID, members=[], startY=140):
        self.WIDTH = width
        self.HEIGHT = height
        self.screen = screen
        self.startY = startY
        self.clientID = clientID
        self.updateMembersList(members, clientID)

    def updateMembersList(self, members, clientID=None):
        self.membersList = []
        self.lobbyRects = []
        for i, member in enumerate(members):
            self.membersList.append(member)

            containerX = (self.WIDTH - 300) // 2
            containerY = self.startY + i * 60
            self.lobbyRects.append(pygame.Rect(containerX, containerY, 300, 50))

    def drawList(self):
        if len(self.membersList) == 1:
            tempRect = pygame.Rect(
                (self.WIDTH - 300) // 2,
                self.startY + 60,
                300,
                50
            )
            pygame.draw.rect(self.screen, DGREY, tempRect)
            font = pygame.font.Font(None, 42)
            text = font.render('No other players :(', True, (0,0,0))
            self.screen.blit(text, (tempRect.x + 10, tempRect.y + 10))
        for i, member in enumerate(self.membersList):
            memberRect = self.lobbyRects[i]
            if memberRect == self.highlightRect:
                pygame.draw.rect(self.screen, HIGHLIGHT_COLOUR, memberRect)
                if member['id'] != self.clientID:
                    self.drawX(memberRect)
            else:
                pygame.draw.rect(self.screen, DGREY, memberRect)
            font = pygame.font.Font(None, 42)
            text = font.render(member['name'], True, (0, 0, 0))
            self.screen.blit(text, (memberRect.x + 10, memberRect.y + 10))

    def setHighlights(self, mousePos):
        self.highlightRect = None
        for i, rect in enumerate(self.lobbyRects):
            if rect.collidepoint(mousePos):
                self.highlightRect = rect
                return True

    def handleMouseClick(self, mousePos):
        for i, rect in enumerate(self.lobbyRects):
            if rect.collidepoint(mousePos) and self.membersList[i]['id'] != self.clientID:
                return self.membersList[i]['id']
        return None

    def drawX(self, memberRect):
        # Define the position and size for the "X"
        offset_x = memberRect.width - 40
        offset_y = memberRect.height - 38
        line_length = 24
        line_width = 6

        # Calculate the start and end points for the "X"
        start_pos_1 = (memberRect.x + offset_x, memberRect.y + offset_y)
        end_pos_1 = (memberRect.x + offset_x + line_length,
                     memberRect.y + offset_y + line_length)

        start_pos_2 = (memberRect.x + offset_x,
                       memberRect.y + offset_y + line_length)
        end_pos_2 = (memberRect.x + offset_x +
                     line_length, memberRect.y + offset_y)

        # Draw the red "X"
        pygame.draw.line(self.screen, (255, 0, 0),
                         start_pos_1, end_pos_1, line_width)  # Red color
        pygame.draw.line(self.screen, (255, 0, 0),
                         start_pos_2, end_pos_2, line_width)
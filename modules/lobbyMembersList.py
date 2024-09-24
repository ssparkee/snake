"""
This module contains the class LobbyMembersList which is used to display the list of members in the lobby to the host.
"""
import pygame
try:
    from modules.colours import *
except ImportError:
    from colours import *

class LobbyMembersList:
    """
    Class to display the list of members in the lobby to the host.
    """
    membersList = []
    lobbyRects = []
    highlightRect = None
    def __init__(self, width, height, screen, clientID, members=[], startY=140, textIndent=50):
        self.WIDTH = width
        self.HEIGHT = height
        self.screen = screen
        self.startY = startY
        self.textIndent = textIndent
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
            self.screen.blit(text, (tempRect.x + 10, tempRect.y + 12))
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
            self.screen.blit(text, (memberRect.x + self.textIndent, memberRect.y + 12))

            if member['id'] == self.clientID:
                headColour = RED
            else:
                headColour = BLUE

            headRect = pygame.Rect(memberRect.x + 10, memberRect.y + 10, 30, 30)
            pygame.draw.rect(self.screen, headColour, headRect)

            eye1Rect = pygame.Rect(headRect.right - 8, headRect.bottom - 10, 5, 5)
            eye2Rect = pygame.Rect(headRect.right - 8, headRect.top + 6, 5, 5)
            pygame.draw.rect(self.screen, WHITE, eye1Rect)
            pygame.draw.rect(self.screen, WHITE, eye2Rect)

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
        offset_x = memberRect.width - 40
        offset_y = memberRect.height - 38
        line_length = 24
        line_width = 6

        start_pos_1 = (memberRect.x + offset_x, memberRect.y + offset_y)
        end_pos_1 = (memberRect.x + offset_x + line_length, memberRect.y + offset_y + line_length)

        start_pos_2 = (memberRect.x + offset_x, memberRect.y + offset_y + line_length)
        end_pos_2 = (memberRect.x + offset_x + line_length, memberRect.y + offset_y)

        pygame.draw.line(self.screen, (255, 0, 0), start_pos_1, end_pos_1, line_width)
        pygame.draw.line(self.screen, (255, 0, 0), start_pos_2, end_pos_2, line_width)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    members = [
        {'name': 'Player 1', 'id': 1},
        {'name': 'Player 2', 'id': 2},
        {'name': 'Player 3', 'id': 3},
        {'name': 'Player 4', 'id': 4},
        {'name': 'Player 5', 'id': 5},
    ]
    lobby = LobbyMembersList(800, 600, screen, 1, members, textIndent=50)
    running = True
    while running:
        screen.fill(BLACK)
        lobby.setHighlights(pygame.mouse.get_pos())
        lobby.drawList()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                print(lobby.handleMouseClick(pygame.mouse.get_pos()))
import pygame
if __name__ == "__main__":
    from colours import *
else:
    from modules.colours import *

class LobbyMembersList:
    membersList = []
    lobbyRects = []
    highlightRect = None
    def __init__(self, width, height, screen, clientID, members=[], startY=80):
        self.WIDTH = width
        self.HEIGHT = height
        self.screen = screen
        self.startY = startY
        self.updateMembersList(members, clientID)

    def updateMembersList(self, members, clientID=None):
        for i, member in enumerate(members):
            if member['id'] != clientID:
                self.membersList.append(member)

                containerX = (self.WIDTH - 200) // 2
                containerY = self.startY + i * 60
                self.lobbyRects.append(pygame.Rect(containerX, containerY, 200, 50))

    def drawList(self):
        if len(self.membersList) < 1:
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
            return
        for i, member in enumerate(self.membersList):
            memberRect = self.lobbyRects[i]
            if memberRect == self.highlightRect:
                pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, memberRect)
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
            if rect.collidepoint(mousePos):
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


if __name__ == '__main__':
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((800, 600))
    memberslist = [{'name': 'test1', 'id': 1}, {'name': 'test2', 'id': 2}, {'name': 'test3', 'id': 3}]
    members = LobbyMembersList(800, 600, screen, 0, memberslist)
    memberslist.append({'name': '12345678', 'id': 4})
    members.updateMembersList(memberslist)
    print(members.membersList)
    while True:
        screen.fill((0, 0, 0))
        members.setHighlights(pygame.mouse.get_pos())
        members.drawList()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        clock.tick(60)
    pygame.quit()
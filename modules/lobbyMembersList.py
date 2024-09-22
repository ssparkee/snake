import pygame

membersList = []
hasInit = False
def initList(width, height, screen_, clientID, members=[], startY=60):
    global membersList, WIDTH, HEIGHT, screen, STARTY, hasInit
    membersList = members
    WIDTH = width
    HEIGHT = height
    screen = screen_
    STARTY = startY
    for i in members:
        if i['id'] != clientID:
            membersList.append(i)

    hasInit = True

def addToList(member):
    if not hasInit:
        return
    membersList.append(member)

def drawList():
    if not hasInit:
        return
    for i, member in enumerate(membersList):
        containerX = (WIDTH - 200) // 2
        containerY = STARTY + i * 60
        pygame.draw.rect(screen, (150, 150, 150), (containerX, containerY, 200, 50))
        font = pygame.font.Font(None, 42)
        text = font.render(member['name'], True, (0, 0, 0))
        screen.blit(text, (containerX + 10, containerY + 10))

if __name__ == '__main__':
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((800, 600))
    members = [{'name': 'test1', 'id': 1}, {'name': 'test2', 'id': 2}, {'name': 'test3', 'id': 3}]
    initList(800, 600, screen, 0, members)
    addToList({'name': 'test4', 'id': 4})
    while True:
        screen.fill((0, 0, 0))
        drawList()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            self.handle_events(event)
        clock.tick(60)
    pygame.quit()
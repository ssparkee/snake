import tkinter as tk
from tkinter.filedialog import asksaveasfile, askopenfile
from tkinter.simpledialog import askinteger
from tkinter.messagebox import Message
from tkinter import colorchooser
import json

class cell:
    def __init__(self, claimed=False, population=-1, team=-1):
        self.claimed = claimed
        self.population = population
        self.team = team

    def setClaimed(self, team, population=1):
        if self.claimed:
            teams[self.team].population -= self.population
        self.claimed = True
        self.team = team
        self.population = population
        teams[team].population += population

    def save(self):
        return {
            "claimed": self.claimed,
            "population": self.population,
            "team": self.team
        }

    @staticmethod
    def load(data):
        return cell(data["claimed"], data["population"], data["team"])

class team:
    def __init__(self, population, colour, teamNumber):
        self.population = population
        self.colour = colour
        self.teamNumber = teamNumber
    def save(self, teamNumber):
        return {
            "team number": teamNumber,
            "population": self.population,
            "colour": self.colour
        }
    @staticmethod
    def load(data):
        return teamStates(data["population"], data["colour"], data["team number"])

def createButtons():
    global buttons
    buttons = []
    for row in range(GRIDSIZE):
        buttonRow = []
        for col in range(GRIDSIZE):
            button = tk.Button(root,
                               text=f"",
                               width=10, height=3,
                               bg="lightGray",
                               command=lambda r=row, c=col: handleCellClick(r, c))
            button.grid(row=row, column=col, padx=0, pady=0)
            buttonRow.append(button)
        buttons.append(buttonRow)

def createPGrid():
    global pGrid
    pGrid = [[cell() for _ in range(GRIDSIZE)] for _ in range(GRIDSIZE)]

def clamp(value, minVal, maxVal):
    return max(min(value, maxVal), minVal)

def createTeams(numTeams=2):
    global teams
    defaultColours = ["blue", "red", "green", "yellow", "purple", "orange", "pink", "brown"]
    numTeams = clamp(numTeams, 2, len(defaultColours))
    teams = [team(0, defaultColours[i], i) for i in range(numTeams)]

def handleCellClick(row, col):
    global pGrid
    if gameState[0] == 1:
        if not pGrid[row][col].claimed:
            pGrid[row][col].setClaimed(gameState[1])
            buttons[row][col].config(bg=teams[gameState[1]].colour)

def simGeneration():
    pass

def resetCommand():
    pass

def saveCommand():
    pass

def loadCommand():
    pass

def quitCommand():
    print("Quitting")
    root.quit()
    quit()

def changeGameState():
    global gameState
    gameState = (1, 1)

GRIDSIZE = 15
generation = 0
pGrid = []
teams = []
buttons = []
#gameState[0]
#-1 => game not started
#0 => game in progress
#1 => game paused, waiting for user input
#2 => game paused, waiting for next generation start
#3 => game paused, manual pause
#gameState[1]
#-1 => no team selected
#other values => index of team selected
gameState = (-1, -1)

root = tk.Tk()
root.option_add('*tearOff', False)
root.title("Adam's Game of Life")
menu = tk.Menu(root, tearoff=0)
root.config(menu=menu)

fileMenu = tk.Menu(menu)
menu.add_cascade(label='File', menu=fileMenu)
fileMenu.add_command(label='Reset', command=resetCommand, accelerator="Ctrl+R", underline=0)
fileMenu.add_separator()
fileMenu.add_command(label='Save', command=saveCommand, accelerator="Ctrl+S", underline=0)
fileMenu.add_command(label='Load', command=loadCommand, accelerator="Ctrl+L", underline=0)
fileMenu.add_separator()
fileMenu.add_command(label='Exit', command=quitCommand, accelerator="Ctrl+Q", underline=0)
fileMenu.add_command(label='hello', command=changeGameState)


createTeams()
createPGrid()
createButtons()
root.mainloop()

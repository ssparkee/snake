import tkinter as tk
from tkinter.filedialog import asksaveasfile, askopenfile
from tkinter.simpledialog import askinteger
from tkinter.messagebox import Message
from tkinter import colorchooser
import json

class cell:
    def __init__(self, cellState=0, cellType="city", cellPopulation=0, importData=None):
        if importData is None:
            self.state = cellState
            self.type = cellType
            self.population = cellPopulation
        else:
            self.copyData(importData)

    def copyData(self, data):
        self.state = data['cellState']
        self.type = data['cellType']
        self.population = data['cellPopulation']
    
    def exportData(self):
        return {
            'cellState': self.state,
            'cellType': self.type,
            'cellPopulation': self.population
        }

    def updateState(self):
        if self.state != 3 and self.type == "city":
            if self.population <= 0:
                self.population = 0
                self.state = 0
            else:
                self.state = 1


class cellsClass:
    def __init__(self, gridSize= 15):
        self.gridSize = gridSize
        self.cellGrid = [[cell() for _ in range(gridSize)] for _ in range(gridSize)]
        self.cellsLeft = False
    
    def load(self, saveDict):
        self.gridSize = saveDict['gridSize']
        self.cellGrid = [[cell(importData=saveDict['cellState'][row][col]) for row in range(self.gridSize)] for col in range(self.gridSize)]

    def save(self):
        return {'gridSize': self.gridSize, 'cellState': [[self.cellGrid[row][col].exportData() for row in range(self.gridSize)] for col in range(self.gridSize)]}

    def __str__(self):
        return str(self.save())

    def setCell(self, row, col, newState=None, overload=(False, 0, "city", 1)):
        cell = self.cellGrid[row][col]
        state = cell.state
        population = cell.population
        if cell.type == "city":
            if newState is None:
                if state == 1:
                    state = 0
                    population = 0
                else:
                    state = 1
                    population = 1
            else:
                if overload[0]:
                    state = overload[1]
                    cell.type = overload[2]
                    population = overload[3]
                else:
                    if (state == 0) or (state == 1):
                        state = newState
        if state == 1:
            bgCol = enabledColour
        else:
            bgCol = 'lightGray'
        cell.state = state
        cell.population = population
        self.cellGrid[row][col] = cell
        buttons[row][col].config(bg=bgCol, text=str(cell.population))

    def getGridAsBool(self):
        temp = [[False for _ in range(self.gridSize)]for _ in range(self.gridSize)]
        for row in range(self.gridSize):
            for col in range(self.gridSize):
                if self.cellGrid[row][col].state == 1:
                    temp[row][col] = True
        return temp

    def getCellNeighbors(self, row, col):         
        neighbors = 0
        maxSize = self.gridSize - 1
        cells = self.getGridAsBool()

        if row != maxSize:
            if cells[row+1][col]:
                neighbors += 1
            if col != 0:
                if cells[row+1][col-1]:
                    neighbors += 1
            if col != maxSize:
                if cells[row+1][col+1]:
                    neighbors += 1
        if row != 0:
            if cells[row-1][col]:
                neighbors += 1
            if col != 0:
                if cells[row-1][col-1]:
                    neighbors += 1
            if col != maxSize:
                if cells[row-1][col+1]:
                    neighbors += 1
        if col != maxSize:
            if cells[row][col+1]:
                neighbors += 1
        if col != 0:
            if cells[row][col-1]:
                neighbors += 1

        return neighbors

    def simGeneration(self, updateButtons=True):
        cells = self.getGridAsBool()
        activeCells = 0
        newGrid = [[cell() for _ in range(self.gridSize)] for _ in range(self.gridSize)]
        for row in range(self.gridSize):
            for col in range(self.gridSize):
                neighbors = self.getCellNeighbors(row, col)
                newGrid[row][col].copyData(self.cellGrid[row][col].exportData())
                if cells[row][col]:
                    activeCells += 1

                    if neighbors < 2:
                        newGrid[row][col].population += -1
                        activeCells += -1
                    if neighbors > 3:
                        newGrid[row][col].population += -1
                        activeCells += -1
                elif neighbors > 2:
                    newGrid[row][col].population += 1
                    activeCells += 1                 

                newGrid[row][col].updateState()   

                if updateButtons:                        
                    if newGrid[row][col].population > 0:
                        newGrid[row][col].state = 1
                        bgCol = enabledColour
                        buttons[row][col].config(text=str(newGrid[row][col].population))
                    else:
                        bgCol = 'lightGray'
                        newGrid[row][col].state = 0
                        buttons[row][col].config(text="")
                    buttons[row][col].config(bg=bgCol)
        root.update_idletasks()
        self.cellGrid = newGrid
        return activeCells

    def updateAllButtons(self):
        for row in range(self.gridSize):
            for col in range(self.gridSize):
                newCells = self.getGridAsBool()
                if newCells[row][col]:
                    bgCol = enabledColour
                    buttons[row][col].config(text=str(self.cellGrid[row][col].population))
                else:
                    bgCol = 'lightGray'
                buttons[row][col].config(bg=bgCol)

def createButtons():
    buttons = []
    for row in range(cells.gridSize):
        buttonRow = []
        for col in range(cells.gridSize):
            button = tk.Button(root, 
                            text=f"", 
                            width=10, height=3,
                            bg="lightGray",
                            command=lambda r=row, c=col: cellClick(r, c))
            button.grid(row=row, column=col, padx=0, pady=0)
            buttonRow.append(button)
        buttons.append(buttonRow)
    return buttons

def cellClick(row, col):
    print(f"Cell clicked: {row}, {col}")
    cells.setCell(row, col)
    setStartText(running, True)

def simGeneration(updateButtons=False):
    global generation, running
    generation += 1
    updateGenerationLabel(generation)
    activeCells = cells.simGeneration(updateButtons=updateButtons)
    if activeCells == 0:
        running = False
        cells.cellsLeft = False
        setStartText(False, False)
        if simUntil[0]:
            print("Set sim ended early, no more cells left!")
            Message(message=f"The sim stopped early at generation {generation} as there are no more cells left", icon='warning', title='Simulation Ended Early').show()
        else:
            print("Sim ended, no more cells!")
            Message(message=f"The sim stopped at generation {generation} as there are no more cells left", icon='info', title='Simulation Ended').show()
    else:
        cells.cellsLeft = True

def runSimulation():
    global running, cells, generation, simUntil
    if running:
        if simUntil[0]:
            if generation < simUntil[1]:
                simGeneration(updateButtons=True)
                root.after(simSpeed.get(), runSimulation)
            else:
                running = False
                simUntil = (False, 0)
                setStartText(False, cells.cellsLeft)
                simSpeed.set(startSpeed)
                print("Sim stopped, reached max generation")
                Message(message=f"The sim stopped at generation {generation} as it reached the maximum generation", icon='info', title='Simulation Ended').show()
        else:
            simGeneration(updateButtons=True)
            root.after(simSpeed.get(), runSimulation)

def singleSimCommand():
    simGeneration(updateButtons=True)

def updateGenerationLabel(generation):
    global generationLabel
    generationLabel.config(text=f"Generation: {generation}")

def setStartText(isRunning, cellsLeft):
    if isRunning:
        controlsMenu.entryconfigure(0, label="Stop")
        menu.entryconfigure(3, label="Stop")
        thirdStartButton.config(text="Stop")
    else:
        controlsMenu.entryconfigure(0, label="Start")
        menu.entryconfigure(3, label="Start")
        thirdStartButton.config(text="Start")

    if cellsLeft:
        simOneGenButton.config(state=tk.ACTIVE)
        thirdStartButton.config(state=tk.ACTIVE)
        controlsMenu.entryconfigure(0, state=tk.ACTIVE)
        menu.entryconfigure(3, state=tk.ACTIVE)
        controlsMenu.entryconfigure(3, state=tk.ACTIVE)
        controlsMenu.entryconfigure(4, state=tk.ACTIVE)
    else:
        simOneGenButton.config(state=tk.DISABLED)
        thirdStartButton.config(state=tk.DISABLED)
        controlsMenu.entryconfigure(0, state=tk.DISABLED)
        menu.entryconfigure(3, state=tk.DISABLED)
        controlsMenu.entryconfigure(3, state=tk.DISABLED)
        controlsMenu.entryconfigure(4, state=tk.DISABLED)

def startCommand():
    global running
    running = True
    setStartText(running, cells.cellsLeft)
    runSimulation()

def stopCommand():
    global running
    running = False
    setStartText(running, cells.cellsLeft)

def toggleSimCommand(event=None):
    global running
    running = not running
    setStartText(running, cells.cellsLeft)
    if running:
        runSimulation()

def quitCommand(event=None):
    print("Quitting")
    root.quit()
    quit()

def resetCommand(event=None):
    global GRIDSIZE, simSpeed, cells, generation, enabledColour, simUntil
    stopCommand()
    cells = cellsClass(gridSize=GRIDSIZE)
    generation = 0
    simUntil = (False, 0)
    enabledColour = 'green'
    updateGenerationLabel(generation)
    simSpeed.set(STARTSPEED)
    middle = round((cells.gridSize-1)/2)
    cells.setCell(middle, middle)
    cells.updateAllButtons()

def saveCommand(event=None):
    stopCommand()
    saveData = {
        'generation': generation,
        'cellState': cells.save(),
        'enabledColour': enabledColour
    }
    jsonSave = json.dumps(saveData, indent=4)
    f = asksaveasfile(initialfile=f'Generation {generation}.agl',
                      defaultextension=".agl", 
                      filetypes=[("All Files", "*.*"), ("Adam's Game Of Life Save", "*.agl")])
    if f is None:
        return
    f.write(jsonSave)
    f.close()

def loadCommand(event=None):
    global generation, GRIDSIZE, enabledColour
    stopCommand()
    f = askopenfile(mode='r', filetypes=[("Adam's Game Of Life Save", "*.agl"), ("All Files", "*.*")])
    if f is None:
        return
    saveContent = f.read()
    print(f'loaded file {f.name}')
    try:
        jsonSave = json.loads(saveContent)
        generation = jsonSave['generation']
        cells.load(jsonSave['cellState'])
        GRIDSIZE = cells.gridSize
        enabledColour = jsonSave['enabledColour']
        updateGenerationLabel(generation)
        cells.updateAllButtons()
    except Exception as e:
        print(e)
        Message(message=f"There was an unexpected error loading the save file.", icon='error', title='Load Failed!').show()
        resetCommand()

    f.close()
    
def changeColourCommand(event=None):
    global enabledColour
    enabledColour = colorchooser.askcolor(title="Choose Colour")[-1]
    cells.updateAllButtons() 

def getMaxSimsCommand(event=None):
    global simUntil
    def clamp(n, min, max):
        if n < min:
            return min
        elif n > max:
            return max
        else:
            return n

    maxSims = clamp(askinteger("Choose Generation", "What generation do you want the simulation to stop at?"), generation+1, 1000+generation)
    simUntil = (True, maxSims)
    simSpeed.set(STARTSPEED/2)
    startCommand()

GRIDSIZE = 15
STARTSPEED = 500
generation = 0
cells = cellsClass(gridSize=GRIDSIZE)
enabledColour = 'green'
running = False
simUntil = (False, 0)

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

controlsMenu = tk.Menu(menu)
menu.add_cascade(label='Controls', menu=controlsMenu)
controlsMenu.add_command(label='Start', command=toggleSimCommand)
controlsMenu.add_command(label='Reset', command=resetCommand, accelerator="Ctrl+R", underline=0)

controlsMenu.add_separator()

controlsMenu.add_command(label='Simulate One Generation', command=singleSimCommand)
controlsMenu.add_command(label="Simulate Until Generation", command=getMaxSimsCommand)

controlsMenu.add_separator()

speedMenu = tk.Menu(menu)
controlsMenu.add_cascade(label='Change Speed', menu=speedMenu)
simSpeed = tk.IntVar(value=STARTSPEED)
speedMenu.add_radiobutton(label='0.25x', variable=simSpeed, value=STARTSPEED*4)
speedMenu.add_radiobutton(label='0.5x', variable=simSpeed, value=STARTSPEED*2)
speedMenu.add_radiobutton(label='1x', variable=simSpeed, value=STARTSPEED)
speedMenu.add_radiobutton(label='2x', variable=simSpeed, value=STARTSPEED/2)

controlsMenu.add_command(label='Change Colour', command=changeColourCommand)


helpMenu = tk.Menu(menu)
menu.add_cascade(label='Help', menu=helpMenu)
helpMenu.add_command(label='About')

startButton = menu.add_command(label='Start', command=toggleSimCommand, accelerator='Space')

buttons = createButtons()
middle = round((cells.gridSize-1)/2)
cells.setCell(middle, middle)

generationLabel = tk.Label(root, text="Generation: 0", font=("Arial", 16), justify=tk.LEFT)
generationLabel.grid(row=cells.gridSize, column=0, sticky="w", columnspan=5, pady=(10, 0), padx=(5,0))

thirdStartButton = tk.Button(root, text="Start", font=("Arial", 16), justify=tk.RIGHT, command=toggleSimCommand)
thirdStartButton.grid(row=cells.gridSize, column=cells.gridSize-4, sticky="e", columnspan=2, pady=(5, 5), padx=(0, 5))

simOneGenButton = tk.Button(root, text="Next", font=("Arial", 16), justify=tk.RIGHT, command=singleSimCommand)
simOneGenButton.grid(row=cells.gridSize, column=cells.gridSize-3, sticky="e", columnspan=2, pady=(5, 5), padx=(0, 5))

clearButton = tk.Button(root, text="Clear", font=("Arial", 16), justify=tk.RIGHT, command=resetCommand)
clearButton.grid(row=cells.gridSize, column=cells.gridSize-2, sticky="e", columnspan=2, pady=(5, 5), padx=(0, 5))

root.bind_all('<space>', toggleSimCommand)
root.bind_all('<Control-q>', quitCommand)
root.bind_all('<Control-r>', resetCommand)
root.bind_all('<Control-s>', saveCommand)
root.bind_all('<Control-l>', loadCommand)
root.mainloop()
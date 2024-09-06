def nextGen(state):
    newState = list(state)
    for i in range(len(state)):
        if state[i] == "#":
            newState[i] = "_"
            newState[i+1] = "#"
    return ''.join(newState)

state = "#______________________#_________________________"

generations = int(input("how many: "))
for i in range(generations):
    print("Gen", i+1, state)
    state = nextGen(state)
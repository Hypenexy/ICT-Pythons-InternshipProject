gameArea = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

def render():
    print(gameArea)

def renderEmptySpace(height):
    n = 0
    while(n < height):
        print("\n")
        n += 1
def welcome_title():
    renderEmptySpace(6)
    print("\nTIC TAC TOE")
    print("\nVersion 1.0 by Georgi Murlev")
    renderEmptySpace(2)

def main_menu():
    welcome_title()
    print("\n1. Play")
    print("\n2. Play Vs CPU")
    print("\n3. Settings")
    print("\n4. Exit")
    renderEmptySpace(2)
    # Maybe use arrow selections like in a linux cmd script install
    choice = input("")
    if(choice == 2):
        sub_menu("playcpu")
    if(choice == 3):
        sub_menu("settings")

def sub_menu(menu):
    if(menu == "playcpu"):
        welcome_title()
        print("\nDifficulty")
        print("\n1. Easy")
        print("\n2. Medium")
        print("\n3. Impossible")
        renderEmptySpace(1)
        print("\n4. Back")
        renderEmptySpace(2)

def checkWin():
    for row in gameArea:
        for item in row:
            sum # placeholders for now
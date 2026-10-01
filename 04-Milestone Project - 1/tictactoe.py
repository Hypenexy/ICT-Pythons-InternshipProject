from pprint import pprint
import inquirer

gameArea = [[1, 0, -1], [0, 0, 0], [-1, 0, 0]]

options = {
    "dark_mode": True,
    "horizontal_lines": True
}
# 1 represents X
# -1 represents O
# so 3 is win for X
# and -3 is win for O
def render():
    for row in gameArea:
        rowCharacters = []
        for symbol in row:
            char = " "
            if(symbol == 1):
                char = "X"
            if(symbol == -1):
                char = "O"
            rowCharacters.append(char)
        rowStylised = " | ".join(rowCharacters)
        if(options["horizontal_lines"]):
            print("---------")
        print(rowStylised)
    
    if(options["horizontal_lines"]):
        print("---------")
    

def start_game():
    render()

def renderEmptySpace(height):
    n = 0
    while(n < height):
        print("\n")
        n += 1

def welcome_title():
    renderEmptySpace(6)
    print("TIC TAC TOE")
    print("Version 1.0 by Georgi Murlev")
    renderEmptySpace(1)

def main_menu():
    welcome_title()
    # print("1. Play")
    # print("2. Play Vs CPU")
    # print("3. Settings")
    # print("4. Exit")
    # renderEmptySpace(2)
    # # Maybe use arrow selections like in a linux cmd script install
    # choice = 0
    # while choice < 1 or choice > 4:
    #     choice = int(input(""))
    #     sub_menu("playcpu")
    # if(choice == 3):
    #     sub_menu("settings")
    questions = [
        inquirer.List(
            "submenu",
            message="What will it be today?",
            choices=["Play", "Play Vs CPU", "Settings", "Exit"],
        ),
    ]

    answers = inquirer.prompt(questions)
    if(answers["submenu"] == "Play"):
        start_game()
    elif(answers["submenu"] == "Exit"):
        # Gracefully exit
        pass
    else:
        sub_menu(answers["submenu"])

def sub_menu(menu):
    print(menu)
    if(menu == "Play Vs CPU"):
        # welcome_title()
        # print("Difficulty")
        # print("1. Easy")
        # print("2. Medium")
        # print("3. Impossible")
        # renderEmptySpace(1)
        # print("4. Back")
        # renderEmptySpace(2)
        questions = [
            inquirer.List(
                "difficulty",
                message="Select your difficulty",
                choices=["1. Easy", "2. Medium", "3. Impossible", "Back to Main Menu"],
            ),
        ]
    
        answers = inquirer.prompt(questions)
        if(answers["difficulty"] == "Back to Main Menu"):
            main_menu()
        else:
            # Bot game logic here... function call of course
            # sub_menu(answers["submenu"])
            pass
    if(menu == "Settings"):
        # print("1. Theme: Dark")
        # print("2. Horizontal lines grid: On")
        # renderEmptySpace(1)
        # print("4. Back")
        questions = [
            inquirer.List(
                "setting",
                message="Press Enter to toggle settings",
                choices=[
                    f"Theme: {"Dark" if options['dark_mode'] else "Light"}",
                    f"Horizontal lines grid: {"On" if options['horizontal_lines'] else "Off"}",
                    "Back to Main Menu"
                ]
                #, default=f"Horizontal lines grid: {"On" if options['horizontal_lines'] else "Off"}"
            ),
        ]
    
        answers = inquirer.prompt(questions)
        if(answers["setting"] == "Back to Main Menu"):
            main_menu()
        else:
            if(answers["setting"] == "Theme: Dark"):
                options["dark_mode"] = False
            if(answers["setting"] == "Theme: Light"):
                options["dark_mode"] = True
            if(answers["setting"] == "Horizontal lines grid: On"):
                options["horizontal_lines"] = False
            if(answers["setting"] == "Horizontal lines grid: Off"):
                options["horizontal_lines"] = True
            renderEmptySpace(2)
            sub_menu("Settings")
    
def checkWin():
    for row in gameArea:
        for item in row:
            sum # placeholders for now

main_menu()
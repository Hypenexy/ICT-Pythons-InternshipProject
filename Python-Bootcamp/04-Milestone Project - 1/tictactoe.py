from pprint import pprint
import inquirer
import curses
import numpy as np

gameArea = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

options = {
    "dark_mode": True,
    "horizontal_lines": True
}
# 1 represents X
# -1 represents O
# so 3 is win for X
# and -3 is win for O
def render(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)

    gameArea[:] = [[0, 0, 0] for _ in range(3)]
    c_row, c_col = 0, 0
    current_player = "X"

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Arrow keys: move | Enter: select | q: quit")
        stdscr.addstr(2, 0, f"Turn: {current_player}")

        board_top = 4
        row_spacing = 2 if options["horizontal_lines"] else 1
        for row_index, row in enumerate(gameArea):
            screen_row = board_top + row_index * row_spacing
            for col_index, value in enumerate(row):
                char = "X" if value == 1 else "O" if value == -1 else " "
                if row_index == c_row and col_index == c_col:
                    stdscr.addstr(screen_row, 1 + col_index * 4, f" {char} ", curses.A_REVERSE)
                else:
                    stdscr.addstr(screen_row, 1 + col_index * 4, f" {char} ")
                if col_index < 2:
                    stdscr.addstr(screen_row, 4 + col_index * 4, "|")

            if options["horizontal_lines"] and row_index < 2:
                stdscr.addstr(screen_row + 1, 1, "---+---+---")

        winner = checkWin()
        is_draw = winner is None and all(cell != 0 for row in gameArea for cell in row)
        if winner is not None or is_draw:
            stdscr.clear()
            stdscr.refresh()
            return winner.upper() if winner else "draw"

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and c_row > 0:
            c_row -= 1
        elif key == curses.KEY_DOWN and c_row < 2:
            c_row += 1
        elif key == curses.KEY_LEFT and c_col > 0:
            c_col -= 1
        elif key == curses.KEY_RIGHT and c_col < 2:
            c_col += 1
        elif key in (10, 13, curses.KEY_ENTER):
            if gameArea[c_row][c_col] == 0:
                gameArea[c_row][c_col] = 1 if current_player == "X" else -1
                current_player = "O" if current_player == "X" else "X"
        elif key in (ord("q"), ord("Q")):
            stdscr.clear()
            stdscr.refresh()
            return None

def start_game():
    while True:
        result = curses.wrapper(render)
        if result is None:
            return

        message = "It's a draw!" if result == "draw" else f"{result} wins!"
        print(message)
        questions = [
            inquirer.List(
                "next_action",
                message="What would you like to do?",
                choices=["Play Again", "Exit"],
            ),
        ]
        answers = inquirer.prompt(questions)
        if answers is None or answers["next_action"] != "Play Again":
            return

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
    diagonal = np.asarray(gameArea)
    if(np.trace(diagonal) == 3):
        return 'x'
    if(np.trace(diagonal) == -3):
        return 'o'
    
    anti_diagonal = np.fliplr(diagonal)
    if(np.trace(anti_diagonal) == 3):
        return 'x'
    if(np.trace(anti_diagonal) == -3):
        return 'o'

    for totals in (np.sum(diagonal, axis=1), np.sum(diagonal, axis=0)):
        if np.any(totals == 3):
            return 'x'
        if np.any(totals == -3):
            return 'o'

    
    
    return None
            
main_menu()
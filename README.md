SNAKE GAME WITHOUT "CURSES" MODULE
==================================

Supported Operating System (OS)
-------------------------------
`Windows` OS supports the `keyboard` and `msvcrt.getch` module packages.
But operations other than the Windows environment are most likely not supported,
especially on the library `keyboard`.

Required Modules
----------------
Install the packages or modules needed to run the game!
`asciiTUI` and `keyboard`

How to Run the Game?
--------------------
To run the game, follow the code below:
```pycon
game = Snake()
game.play()
```
Or just directly execute the WinSnake.py file.

The code above uses the default game rules. If you want to change it go to the
topic "Settings the Game"

Settings the Game
-----------------
Installation parameters in Snake():

`width`: Set the width (X) length on the game board [default: terminal width]

`height`: Set the height (Y) length on the game board [default: terminal height]

`fps`: Set the frames per second (FPS) as well as set the speed of the snake [default: 9]

`lots_of_apples`: Regulate how many apples there are in the game [default: 20]

`generate_new_apple`: Set whether an apple will appear or not every time the snake eats an apple [default: True]

`game_over`: Set whether the game can be game over [default: True]

`save_high_score`: Set save the highscore in the file "SNAKE-SCORE.hi" [default: True]

Exit Codes
----------
-2: Not yet installed the required packages

-1: If the OS used is other than Windows.

0: Exit the game (pressing Q)

1: Force quit the game (pressing Ctrl+C)

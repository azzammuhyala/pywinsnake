import os, random, time
if os.name == 'nt':
    try:
        from asciiTUI import terminal_size as tsize
        from asciiTUI import rgb
        from asciiTUI import remove_ansi as rmansi
        from asciiTUI import justify
        from keyboard import is_pressed as ispress
        from msvcrt import getch
    except Exception as e:
        type_error = type(e).__name__
        if type_error == 'ModuleNotFoundError':
            print(f'Please install packages:\n  asciiTUI `pip install asciiTUI`\n  keyboard `pip install keyboard`\n{type_error}: {e}')
        else:
            print(f'WinSnake ERROR: {type_error}: {e}')
        exit(-2)
else:
    print('\033[31mERROR\033[0m - THIS SOFTWARE ONLY WORKS IN A WINDOWS ENVIRONMENT')
    print('Exit - Exit code: -1')
    exit(-1)

class Snake:
    """
SNAKE GAME WITHOUT "CURSES" MODULE
==================================

Supported Operating System (OS)
-------------------------------
`Windows` OS supports the `keyboard` and `msvcrt.getch` module packages.
But operations other than the Windows environment are most likely not supported,
especially on the library `keyboard`.

Required Modules
----------------
Install the packages or modules needed to run the game.
`asciiTUI` and `keyboard`

How to Run the Game?
--------------------
To run the game, follow the code below:

>>> game = Snake()
>>> game.play()

Or just directly execute the "WinSnake.py" file.

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
`show_score_board`: Set to display the scoreboard [default: True]

Exit Codes
----------
-2: Not yet installed the required packages
-1: If the OS used is other than Windows.
0: Exit the game (pressing Q)
1: Force quit the game (pressing Ctrl+C)
    """
    def __init__(self,
                width:int=tsize('x'),
                height:int=tsize('y'),
                fps:int=9,
                lots_of_apples:int=20,
                generate_new_apple:bool=True,
                game_over:bool=True,
                save_high_score:bool=True,
                show_score_board:bool=True
        ) -> None:
        if not all(isinstance(args, int) for args in (width, height, fps, lots_of_apples)):
            raise TypeError('Type arguments (width:{}, height:{}, fps:{}, lots_of_apples:{}) are all not int'.format(
                type(width).__name__, type(height).__name__, type(fps).__name__, type(lots_of_apples).__name__
            ))
        if (250 > width < 60) or (100 > height < 20) or (90 > fps < 2) or (1150 > lots_of_apples < 1):
            raise ValueError(f'The value given is out of bounds.\nMIN, MAX:\n  width: 60, 250 - [got {width}]\n  height: 20, 100 - [got {height}]\n  fps: 2, 90 - [got {fps}]\n  lots_of_apples : 1, 1150 - [got {lots_of_apples}]')

        self.WIDTH = width # width of display
        self.HEIGHT = height # height of display
        self.FPS = fps # frame per seconds
        self.LOA = lots_of_apples # the number of apples in the game
        self.GNA = bool(generate_new_apple) # produces a new apple every time you eat one if the value is True
        self.GO = bool(game_over) # showing game over if the value is True
        self.SHC = bool(save_high_score) # saves the highscore if the value is True
        self.SSB = bool(show_score_board)

        # this function is used to set the size of the coordinates which can change depending on the value of self.SSB
        self.SSBs = lambda SSB_T, SSB_F: SSB_T if self.SSB else SSB_F

        self.exit_code = 0
        self.running = True
        self.ASCII = [f'{rgb(0,200,255)}$\033[0m', f'{rgb(0,200,0)}#\033[0m', f'{rgb(200,0,0)}@\033[0m', ' '] # ascii characters on snake board
        self.__game_over = False # Declares whether it is game over or not
        self.__ASCII_DISPLAY = [] # This is part of the main screen on the snake board
        # snake position
        self.__posX_snake = (self.WIDTH-2) // 2
        self.__posY_snake = (self.HEIGHT-self.SSBs(4, 3)) // 2
        # change of snake coordinates
        self.__deltaX = 0
        self.__deltaY = 0
        self.__moveSnake = '' # the direction the snake walks
        # data section snake coordinates, snake length, and highest score
        self.__snakeList = []
        self.__lenSnake = 1
        self.__hiScore = self.__highscore() if self.SHC else '-'
        self.__posApples = [self.__rdmPosApples() for _ in range(self.LOA)] # apple coordinate data section
        self.__current_time4FPS = '-' # get the delay time and convert it to FPS in real time

    def cls(self) -> None:
        os.system('cls') # This function is used to clean the screen

    def __sleepFPS(self) -> None:
        # Sleep time in FPS form
        current_time = time.time()
        while True:
            self.__control_event()
            if current_time+(1/self.FPS) <= time.time():
                break

    def __highscore(self, new_hi_score:None|int=None) -> None|int:
        # This function is used to get or change the highest score value in the SNAKE-SCORE.hi file
        try:
            with open('SNAKE-SCORE.hi', 'r+', encoding='utf8') as hi:
                if new_hi_score == None:
                    score = hi.read()
                else:
                    hi.write(new_hi_score)
            return int(score) if score.isdigit() else self.__highscore(0)
        except:
            try:
                with open('SNAKE-SCORE.hi', 'w', encoding='utf8') as hie:
                    hie.write(str(new_hi_score))
            finally:
                return new_hi_score

    def __rdmPosApples(self) -> tuple[int]:
        # This function is used to provide random coordinates of where the apple is located
        return (random.randint(0, self.WIDTH-3), random.randint(0, self.HEIGHT-self.SSBs(5, 4)))

    def __showQuit(self, exit_code:int=0) -> None:
        # displays or asks if you want to exit the game
        print()
        while True:
            quit_user = input('Are you sure want to Quit? [Y/n]: ').lower()
            match quit_user:
                case 'y':
                    self.running = False
                    self.exit_code = exit_code
                    break
                case 'n':
                    break

    def __showGameOver(self, message:str) -> None:
        # Displays game over on the screen
        self.__snakeList.clear()
        self.__posX_snake, self.__posY_snake, self.__deltaX, self.__deltaY, self.__lenSnake, self.__posApples, self.__moveSnake, self.__game_over = (self.WIDTH-2) // 2, (self.HEIGHT-self.SSBs(4, 3)) // 2, 0, 0, 1, [self.__rdmPosApples() for _ in range(self.LOA)], '', True
        def showinfo():
            self.cls()
            self.__showDisplay(showControl=False)
            print(f"\n(Enter 'c' to continue) \033[31mGAME OVER\033[0m - \033[33m{message}\033[0m...", end='')
        showinfo()
        while True:
            game_over_user = getch().decode('utf-8').lower()
            match game_over_user:
                case 'c':
                    self.__game_over = False
                    break
                case 'q':
                    self.__showQuit()
                    showinfo()

    def __showDisplay(self, showControl:bool=True) -> None:
        # Displays the score bar and snake board on the screen
        lensnk, fps, loa, hiscr, ct_appl = map(str, [self.__lenSnake-1, self.FPS, self.LOA, self.__hiScore, len(list(set(self.__posApples)))])
        hiscr = '-' if hiscr == 'False' else hiscr
        real_fps = f'{1/(time.time()-self.__current_time4FPS):.1f}' if isinstance(self.__current_time4FPS, (int, float)) else '-'
        print(
            (rgb()+'SCORE: '+rgb(20,225,100)+lensnk+rgb()
            +'  FPS: '+rgb(127,127,127)+f'{real_fps}/{fps}'+rgb()
            +'  APPLES: '+rgb(200,0,0)+f'{ct_appl}/{loa}'+rgb()
            +' '*(self.WIDTH-36-len(ct_appl+lensnk+fps+loa+hiscr+real_fps))
            +'HI SCORE: '+rgb(225,100,20)+hiscr+'\033[0m\n' if self.SSB else '')
            +'\u250f'+'\u2501'*(self.WIDTH-2)+'\u2513\n'
            +'\n'.join([row for row in self.__ASCII_DISPLAY])
            +'\n\u2517'+'\u2501'*(self.WIDTH-2)+'\u251b'
            +('\n'+justify("[w]:\033[35mUp\033[0m  [s]:\033[35mDown\033[0m  [a]:\033[35mLeft\033[0m  [d]:\033[35mRight\033[0m  [p]:\033[35mPause\033[0m  [q]:\033[35mQuit\033[0m", self.WIDTH, wrap=False) if self.SSB and showControl else '')
        ,end='')

    def __control_event(self) -> None:
        # get user keyboard input
        if ispress('w'):
            self.__moveSnake = 'w'
        elif ispress('a'):
            self.__moveSnake = 'a'
        elif ispress('s'):
            self.__moveSnake = 's'
        elif ispress('d'):
            self.__moveSnake = 'd'
        elif ispress('p'):
            # pause loop
            def showinfo():
                self.cls()
                self.__showDisplay(showControl=False)
                print("\n(Enter 'c' to continue) \033[33mGAME PAUSE\033[0m...", end='')
            showinfo()
            while True:
                pause_user = getch().decode('utf-8').lower()
                match pause_user:
                    case 'c':
                        self.__moveSnake = ''
                        break
                    case 'q':
                        self.__showQuit()
                        if self.running == False:
                            break
                        else:
                            showinfo()

        elif ispress('q'):
            self.__showQuit()

    def play(self) -> int:
        # check length and type of self.ASCII
        if len(self.ASCII) != 4:
            raise ValueError(f'Requires at least 4 characters in the ASCII attribute, not {len(self.ASCII)}')
        if not isinstance(self.ASCII, list):
            raise TypeError(f'ASCII attribute type is list, not {type(self.ASCII).__name__}')
        for char in self.ASCII:
            if len(rmansi(char)) != 1:
                raise ValueError(f'Requires at least 1 ASCII character, not {len(rmansi(char))}')
        # changes all value on self.ASCII to str
        self.ASCII = [str(char) for char in self.ASCII]
        # title
        os.system('title Snake Game')
        while self.running:
            try:
                # delete the position of the apple that was in the snake the first time it was there
                if self.__lenSnake == 1:
                    for _ in range(self.__posApples.count(((self.WIDTH-2) // 2, (self.HEIGHT-self.SSBs(4, 3)) // 2))):
                        self.__posApples.remove(((self.WIDTH-2) // 2, (self.HEIGHT-self.SSBs(4, 3)) // 2))
                # Check whether the position of the snake is the same as the position of one of the apples. If so, it will delete the coordinates of the apple eaten by the snake and add 1 apple randomly if self.GNA is True value..
                if (self.__posX_snake, self.__posY_snake) in self.__posApples:
                    self.__posApples.remove((self.__posX_snake, self.__posY_snake))
                    if self.GNA:
                        self.__posApples.append(self.__rdmPosApples())
                    self.__lenSnake += 1

                self.__posX_snake += self.__deltaX
                self.__posY_snake += self.__deltaY
                # check whether the position of the snake is outside the limits of the snake board. If yes then game over
                if self.__posX_snake < -1 or self.__posX_snake > self.WIDTH-2 or self.__posY_snake < -1 or self.__posY_snake > self.HEIGHT-self.SSBs(4, 3):
                    if not self.GO:
                        self.__posX_snake = (self.__posX_snake + self.WIDTH-1) % (self.WIDTH-1)
                        self.__posY_snake = (self.__posY_snake + self.HEIGHT-self.SSBs(3, 2)) % (self.HEIGHT-self.SSBs(3, 2))
                    else:
                        self.__showGameOver("BOARD EXIT")
                # clear all objects display
                if not self.__game_over:
                    self.__ASCII_DISPLAY.clear()

                snakeHead = (self.__posX_snake, self.__posY_snake)
                self.__snakeList.append(snakeHead)
                # Remove the tail from the snake so it looks as if the snake is moving
                if len(self.__snakeList) > self.__lenSnake:
                    del self.__snakeList[0]
                # Snake board rendering process
                for row in range(self.HEIGHT-self.SSBs(4, 3)):
                    colchard = '\u2503'
                    for col in range(self.WIDTH-2):
                        if (col, row) in self.__snakeList:
                            colchard += self.ASCII[0] if (col, row) == self.__snakeList[-1] else self.ASCII[1]
                        elif (col, row) in self.__posApples:
                            colchard += self.ASCII[2]
                        else:
                            colchard += self.ASCII[3]
                    colchard += '\u2503'
                    self.__ASCII_DISPLAY.append(colchard)
                # update high score
                if self.SHC:
                    self.__hiScore = self.__highscore()
                # check whether the snake's position hits any part of the snake's body. If yes then game over
                if snakeHead in self.__snakeList[:-1] and self.GO:
                    self.__showGameOver("CRASHING")
                # Checks whether the score is greater than the high score
                hiscore = self.__highscore()
                if (hiscore if hiscore != None else 0) < self.__lenSnake-1 and self.SHC:
                    self.__hiScore = self.__highscore(self.__lenSnake-1)
                del hiscore
                # TUI display and control section
                self.cls()
                self.__showDisplay()

                self.__control_event()
                # snake movement selection process
                delta_move = {'w': (0, -1), 'a': (-1, 0), 's': (0, 1), 'd': (1, 0)}
                if self.__moveSnake in delta_move:
                    self.__deltaX, self.__deltaY = delta_move[self.__moveSnake]
                self.__current_time4FPS = time.time()
                # sleep
                self.__sleepFPS()

            except (KeyboardInterrupt, EOFError):
                self.exit_code = 1
                self.running = False
        self.cls()
        print('Exit - Exit code: {}'.format(self.exit_code))
        return self.exit_code

if __name__ == '__main__':
    while True:
        print(
            "=" * 60
            +"\n\033[36mWin\033[32mSn\033[31ma\033[32mke\033[0m Game!\n"+
            "=" * 60
        )
        try:
            w   = input('Width: ')
            h   = input('Height: ')
            fps = input('FPS: ')
            loa = input('Many lots of Apples: ')
            gna = input('Generate new apple: ')
            go  = input('Game Over mode: ')
            shc = input('Save hight score: ')
            ssb = input('Show score board: ')
            game_snake = Snake(width              = int(w) if w.isdigit() else tsize('x'),
                               height             = int(h) if h.isdigit() else tsize('y'),
                               fps                = int(fps) if fps.isdigit() else 9,
                               lots_of_apples     = int(loa) if loa.isdigit() else 20,
                               generate_new_apple = gna,
                               game_over          = go,
                               save_high_score    = shc,
                               show_score_board   = ssb
                            )
            game_snake.play()
            del w, h, fps, loa, gna, go, shc, ssb, game_snake
        except (KeyboardInterrupt, EOFError):
            print('\nExit...',end='')
            getch()
            break
        except Exception as e:
            print(f"\033[31m{type(e).__name__}\033[0m: {e}")
            continue

"""
Copyright (C) 2024
AzzamMuhyala - https://github.com/azzammuhyala
"""
import os, random, time, math
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
            print(f'WinSnake ERROR: \033[31m{type_error}\033[0m: {e}')
        exit(-2)
else:
    print('\033[31mERROR\033[0m - THIS SOFTWARE ONLY WORKS IN A WINDOWS ENVIRONMENT')
    print('Exit - Exit code: \033[31m-1\033[0m')
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
`asciiTUI` and `keyboard`.

How to Run the Game?
--------------------
To run the game, follow the code below:

>>> game = Snake()
>>> game.play()

Or just directly execute the "WinSnake.py" file.

The code above uses the default game rules. If you want to change it go to the
topic "Settings the Game".

Settings the Game
-----------------
Installation parameters in Snake():
`width`: Set the width (X) length on the game board [default: terminal width].
`height`: Set the height (Y) length on the game board [default: terminal height].
`fps`: Set the frames per second (FPS) as well as set the speed of the snake [default: 9].
`lots_of_apples`: Regulate how many apples there are in the game [default: 20].
`generate_new_apple`: Set whether an apple will appear or not every time the snake eats an apple [default: True].
`game_over`: Set whether the game can be game over [default: True].
`save_high_score`: Set save the highscore in the file "SNAKE-SCORE.hi" [default: True].
`show_score_board`: Set to display the scoreboard [default: True].
`bot_mode`: Set to bot mode [default: False].
`bot_move_type`: Set bot algorithm type [default: 'neat'].
`bot_move_info_type`: Set to change the display type of move snake on the bottom screen [default: 'wasd'].

Types of `bot_move_type`:
  - 'neat': Make bot lanes organized and neat.
  - 'algorithm': Using an algorithm system.

Types of `bot_move_info_type`:
  - `wasd`: Only show ['w', 'a', 's', 'd', ''].
  - `ulds`: Only show ['Up', 'Left', 'Down', 'Right', 'Stop'].

Exit Codes
----------
-2: Not yet installed the required packages
-1: If the OS used is other than Windows.
0: Exit the game (pressing Q).
1: Force quit the game (pressing Ctrl + (C or D)).
~: Orders.
    """
    def __init__(self,
                width             :int  = tsize('x'),
                height            :int  = tsize('y'),
                fps               :int  = 9,
                lots_of_apples    :int  = 20,
                len_snake         :int  = 1,
                generate_new_apple:bool = True,
                game_over         :bool = True,
                save_high_score   :bool = True,
                show_score_board  :bool = True,
                bot_mode          :bool = False,
                bot_move_type     :str  = 'neat',
                bot_move_info_type:str  = 'wasd'
        ) -> None:
        if not all(isinstance(args, int) for args in (width, height, fps, lots_of_apples, len_snake)):
            raise TypeError('Type arguments (width:{}, height:{}, fps:{}, lots_of_apples:{}, len_snake:{}) are all not int'.format(
                type(width).__name__, type(height).__name__, type(fps).__name__, type(lots_of_apples).__name__, type(len_snake).__name__
            ))
        if (250 > width < 60) or (100 > height < 20) or (90 > fps < 2) or (1150 > lots_of_apples < 1) or (width*height-5 > len_snake < 1):
            raise ValueError(f'The value given is out of bounds.\nMIN, MAX:\n  width: 60, 250 - [got {width}]\n  height: 20, 100 - [got {height}]\n  fps: 2, 90 - [got {fps}]\n  lots_of_apples: 1, 1150 - [got {lots_of_apples}]\n  len_snake: 1, {width*height-5} - [got {len_snake}]')
        if not bot_move_type in ('neat', 'algorithm'):
            raise TypeError(f"No bot mode with type '{bot_move_type}'!")
        if not bot_move_info_type in ('wasd', 'ulds'):
            raise TypeError(f"No bot move info type with type '{bot_move_info_type}'!")

        self.WIDTH = width # width of display
        self.HEIGHT = height # height of display
        self.FPS = fps # frame per seconds
        self.LOA = lots_of_apples # the number of apples in the game
        self.LS = len_snake # snake length for the first time
        self.GNA = bool(generate_new_apple) # produces a new apple every time you eat one if the value is True
        self.GO = bool(game_over) # showing game over if the value is True
        self.SHC = bool(save_high_score) # saves the highscore if the value is True
        self.SSB = bool(show_score_board) # display scoreboard setting
        self.BM = bool(bot_mode) # game with bot moves
        self.BMT = bot_move_type # types bot moving
        self.BMIT = bot_move_info_type # bot move info display type

        # this function is used to set the size of the coordinates which can change depending on the value of self.SSB
        self._SSBs = lambda SSB_T, SSB_F: SSB_T if self.SSB else SSB_F

        self.exit_code = 0
        self.running = True
        self.ASCII = [f'{rgb(0,200,255)}$\033[0m', f'{rgb(0,200,0)}#\033[0m', f'{rgb(200,0,0)}@\033[0m', ' '] # ascii characters on snake board
        self._message_exit = '' # showing messages exit
        self._botMovesInfo = {'w': 'Up', 'a': 'Left', 's': 'Down', 'd': 'Right', '': 'Stop'}
        self._game_over = False # Declares whether it is game over or not
        self._ASCII_DISPLAY = [] # This is part of the main screen on the snake board
        # snake position
        self._posX_snake = (self.WIDTH-2) // 2
        self._posY_snake = (self.HEIGHT-self._SSBs(4, 3)) // 2
        # change of snake coordinates
        self._deltaX = 0
        self._deltaY = 0
        self._moveSnake = '' # the direction the snake walks
        # data section snake coordinates, snake length, and highest score
        self._snakeList = []
        self._lenSnake = len_snake
        self._rmCountApple = 0
        self._hiScore = self._highscore() if self.SHC else '-'
        self._posApples = [self._rdmPosApples() for _ in range(self.LOA)] # apple coordinate data section
        self._getRealTime = '-' # get the delay time and convert it to FPS in real time
        self._getDelayFPS = time.time()

    def cls(self) -> None:
        os.system('cls') # This function is used to clean the screen

    def _sleepFPS(self) -> None:
        # Sleep time in FPS form
        current = time.time() + (1 / self.FPS - (time.time() - self._getDelayFPS))
        while True:
            self._move_event()
            if current <= time.time():
                break

    def _highscore(self, new_hi_score:None|int=None) -> None|int:
        # This function is used to get or change the highest score value in the SNAKE-SCORE.hi file
        try:
            with open('SNAKE-SCORE.hi', 'r+', encoding='utf8') as hi:
                if new_hi_score == None:
                    score = hi.read()
                else:
                    hi.write(new_hi_score)
            return int(score) if score.isdigit() else self._highscore(0)
        except:
            try:
                with open('SNAKE-SCORE.hi', 'w', encoding='utf8') as hie:
                    hie.write(str(new_hi_score))
            finally:
                return new_hi_score

    def _rdmPosApples(self) -> tuple[int]:
        # This function is used to provide random coordinates of where the apple is located
        return (random.randint(1, self.WIDTH-2), random.randint(1, self.HEIGHT-self._SSBs(4, 3)))

    def _showQuit(self) -> None:
        # displays or asks if you want to exit the game
        print()
        while True:
            quit_user = input('Are you sure want to Quit? [Y/n]: ').lower()
            match quit_user:
                case 'y':
                    self.running = False
                    self.exit_code = 0
                    self._message_exit = 'You Quit the game. Bye, see you later.. :)'
                    break
                case 'n':
                    break

    def _showGameOver(self, message:str) -> None:
        # Displays game over on the screen
        self._game_over = True
        def showinfo():
            self.cls()
            self._showDisplay(showControl=False)
            print(f"\n(Enter 'c' to continue) \033[31mGAME OVER\033[0m - \033[33m{message}\033[0m...", end='')
        showinfo()
        while True:
            game_over_user = getch().decode('utf-8').lower()
            match game_over_user:
                case 'c':
                    self._snakeList.clear()
                    self._posX_snake, self._posY_snake, self._deltaX, self._deltaY, self._lenSnake, self._posApples, self._moveSnake = (self.WIDTH-2) // 2, (self.HEIGHT-self._SSBs(4, 3)) // 2, 0, 0, self.LS, [self._rdmPosApples() for _ in range(self.LOA)], ''
                    self._game_over = False
                    break
                case 'q':
                    self._showQuit()
                    if self.running == False: break
                    else: showinfo()

    def _showDisplay(self, showControl:bool=True) -> None:
        # Displays the score bar and snake board on the screen
        lensnk, fps, loa, hiscr, ct_appl = map(str, [self._lenSnake-1, self.FPS, self.LOA-self._rmCountApple, self._hiScore, len(list(set(self._posApples)))])
        hiscr = '-' if hiscr == 'False' else hiscr
        real_fps = f'{1/(time.time()-self._getRealTime):.1f}' if isinstance(self._getRealTime, (int, float)) else '-'
        print(
            (rgb()+'SCORE: '+rgb(20,225,100)+lensnk+rgb()
            +'  FPS: '+rgb(127,127,127)+f'{real_fps}/{fps}'+rgb()
            +'  APPLES: '+rgb(200,0,0)+f'{ct_appl}/{loa}'+rgb()
            +' '*(self.WIDTH-36-len(ct_appl+lensnk+fps+loa+hiscr+real_fps))
            +'HI SCORE: '+rgb(225,100,20)+hiscr+'\033[0m\n' if self.SSB else '')
            +'\n'.join([row for row in self._ASCII_DISPLAY])
            +('\n'+justify(f"{'[w]:\033[35mUp\033[0m  [s]:\033[35mDown\033[0m  [a]:\033[35mLeft\033[0m  [d]:\033[35mRight\033[0m' if not self.BM else f'Bot move: [\033[32m{self._moveSnake if self.BMIT == 'wasd' else self._botMovesInfo[self._moveSnake]}\033[0m]'}  [p]:\033[35mPause\033[0m  [q]:\033[35mQuit\033[0m", self.WIDTH, wrap=False) if self.SSB and showControl else '')
        ,end='')

    def _move_event(self) -> None:
        # get user keyboard input
        if not self.BM:
            if ispress('w'):
                self._moveSnake = 'w'
            elif ispress('a'):
                self._moveSnake = 'a'
            elif ispress('s'):
                self._moveSnake = 's'
            elif ispress('d'):
                self._moveSnake = 'd'
        if ispress('p'):
            def showinfo():
                self.cls()
                self._showDisplay(showControl=False)
                print("\n(Enter 'c' to continue) \033[33mGAME PAUSE\033[0m...", end='')
            showinfo()
            # pause loop
            while True:
                pause_user = getch().decode('utf-8').lower()
                match pause_user:
                    case 'c':
                        self._moveSnake = ''
                        break
                    case 'q':
                        self._showQuit()
                        if self.running == False: break
                        else: showinfo()

        elif ispress('q'):
            self._showQuit()

    def _play_bot(self):
        """ BOT algorithm for playing snake """
        if self.GO:
            # Algorithm for game over mode
            errmes = 'We apologize, currently our bot still supports non-game over mode.'
            input(f'\n{errmes}\n[Press ENTER to continue] OK...')
            self.running = False
            self.exit_code = 2
            self._message_exit = errmes

        else:
            # Algorithm for no game over mode
            def find_nearest_apple() -> tuple[int]:
                """ Find the nearest apple coordinates using Euclidean distance """
                min_distance = float('inf')
                nearest_apple = None
                for apple in self._posApples:
                    distance = math.sqrt((self._posX_snake - apple[0])**2 + (self._posY_snake - apple[1])**2)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_apple = apple
                return nearest_apple

            match self.BMT:
                case 'neat':
                    if self._posApples:
                        if self._moveSnake in ('w', 'a', 's', '') and self._posX_snake < self.WIDTH-2: self._moveSnake = 'd'
                        if self._posX_snake == self.WIDTH-2:
                            if self._moveSnake == 'w': self._moveSnake = 'd'
                            else: self._moveSnake = 'w'
                    else:
                        self._moveSnake = ''

                case 'algorithm':
                    near_apple = find_nearest_apple()
                    if near_apple:
                        if near_apple[0] < self._posX_snake: self._moveSnake = 'a'
                        elif near_apple[0] > self._posX_snake: self._moveSnake = 'd'
                        elif near_apple[1] < self._posY_snake: self._moveSnake = 'w'
                        elif near_apple[1] > self._posY_snake: self._moveSnake = 's'
                    else:
                        self._moveSnake = ''

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
                self._getDelayFPS = time.time()
                # delete the position of the apple that was in the snake the first time it was there
                if self._lenSnake == 1 and self.GO:
                    for _ in range(self._posApples.count(((self.WIDTH-2) // 2, (self.HEIGHT-self._SSBs(3, 2)) // 2))):
                        self._rmCountApple += 1
                        self._posApples.remove(((self.WIDTH-2) // 2, (self.HEIGHT-self._SSBs(3, 2)) // 2))
                # Check whether the position of the snake is the same as the position of one of the apples. If so, it will delete the coordinates of the apple eaten by the snake and add 1 apple randomly if self.GNA is True value..
                if (self._posX_snake, self._posY_snake) in self._posApples:
                    self._posApples.remove((self._posX_snake, self._posY_snake))
                    if self.GNA:
                        self._posApples.append(self._rdmPosApples())
                    self._lenSnake += 1

                self._posX_snake += self._deltaX
                self._posY_snake += self._deltaY
                # check whether the position of the snake is outside the limits of the snake board. If yes then game over
                if self._posX_snake < 0 or self._posX_snake > self.WIDTH-1 or self._posY_snake < 0 or self._posY_snake > self.HEIGHT-self._SSBs(4, 3):
                    if not self.GO:
                        self._posX_snake = (self._posX_snake + self.WIDTH) % (self.WIDTH)
                        self._posY_snake = (self._posY_snake + self.HEIGHT-self._SSBs(2, 1)) % (self.HEIGHT-self._SSBs(2, 1))
                    else:
                        self._showGameOver("BOARD EXIT")
                # clear all objects display
                if not self._game_over:
                    self._ASCII_DISPLAY.clear()

                snakeHead = (self._posX_snake, self._posY_snake)
                self._snakeList.append(snakeHead)
                # Remove the tail from the snake so it looks as if the snake is moving
                if len(self._snakeList) > self._lenSnake:
                    del self._snakeList[0]
                # Snake board rendering process
                for row in range(self.HEIGHT-self._SSBs(2, 1)):
                    colchard = ''
                    for col in range(self.WIDTH):
                        coordinat = (col, row)
                        if coordinat in self._snakeList:
                            colchard += self.ASCII[0] if coordinat == self._snakeList[-1] else self.ASCII[1]
                        elif coordinat in self._posApples:
                            colchard += self.ASCII[2]
                        elif coordinat == (0, 0):
                            colchard += '\u250f'
                        elif coordinat == (self.WIDTH-1, 0):
                            colchard += '\u2513'
                        elif coordinat == (0, self.HEIGHT-self._SSBs(3, 2)):
                            colchard += '\u2517'
                        elif coordinat == (self.WIDTH-1, self.HEIGHT-self._SSBs(3, 2)):
                            colchard += '\u251b'
                        elif coordinat in [(0, row), (self.WIDTH-1, row)]:
                            colchard += '\u2503'
                        elif coordinat in [(col, 0), (col, self.HEIGHT-self._SSBs(3, 2))]:
                            colchard += '\u2501'
                        else:
                            colchard += self.ASCII[3]
                    self._ASCII_DISPLAY.append(colchard)
                # update high score
                if self.SHC:
                    self._hiScore = self._highscore()
                # check whether the snake's position hits any part of the snake's body. If yes then game over
                if snakeHead in self._snakeList[:-1] and len(self._snakeList) > self.LS and self.GO:
                    self._showGameOver("CRASHING")
                # Checks whether the score is greater than the high score
                hiscore = self._highscore()
                if (hiscore if hiscore != None else 0) < self._lenSnake-1 and self.SHC:
                    self._hiScore = self._highscore(self._lenSnake-1)
                del hiscore
                # TUI display and control section
                self.cls()
                self._showDisplay()
                if self.BM:
                    self._play_bot()
                self._move_event()
                # snake movement selection process
                delta_move = {'w': (0, -1), 'a': (-1, 0), 's': (0, 1), 'd': (1, 0)}
                if self._moveSnake in delta_move:
                    self._deltaX, self._deltaY = delta_move[self._moveSnake]
                elif self._moveSnake == '' and self.BM:
                    self._deltaX, self._deltaY = (0, 0)
                self._getRealTime = time.time()
                # sleep
                self._sleepFPS()

            except (KeyboardInterrupt, EOFError):
                self.exit_code = 1
                self._message_exit = 'You pressing Ctrl + (C or Z)..'
                self.running = False
        self.cls()
        print('\033[0mExit - Exit code: \033[33m{}\033[0m\nWinSnake: \033[36m{}\033[0m'.format(self.exit_code, self._message_exit))
        return self.exit_code

if __name__ == '__main__':
    os.system('cls')
    while True:
        print(
            "=" * 60
            +"\n\033[36mWin\033[32mSn\033[31ma\033[32mke\033[0m Game!\n"+
            "=" * 60
        )
        try:
            w    = input('Width               (\033[32mint\033[0m): ')
            h    = input('Height              (\033[32mint\033[0m): ')
            fps  = input('FPS                 (\033[32mint\033[0m): ')
            loa  = input('Many lots of apples (\033[32mint\033[0m): ')
            ls   = input('Length snake        (\033[32mint\033[0m): ')
            gna  = input('Generate new apple (\033[32mbool\033[0m): ')
            go   = input('Game over mode     (\033[32mbool\033[0m): ')
            shc  = input('Save hight score   (\033[32mbool\033[0m): ')
            ssb  = input('Show score board   (\033[32mbool\033[0m): ')
            bm   = input('Bot mode           (\033[32mbool\033[0m): ')
            if bm:
                bmit = input('\nType moving bot show:\n  1: wasd\n  2: ulds\n[\033[36mCHOOSE\033[0m] > ')
                bmt  = input('\nBot move type:\n  1: neat\n  2: algorithm\n[\033[36mCHOOSE\033[0m] > ')
            game_snake = Snake(width              = int(w) if w.isdigit() else tsize('x'),
                               height             = int(h) if h.isdigit() else tsize('y'),
                               fps                = int(fps) if fps.isdigit() else 9,
                               lots_of_apples     = int(loa) if loa.isdigit() else 20,
                               len_snake          = int(ls) if ls.isdigit() else 1,
                               generate_new_apple = gna,
                               game_over          = go,
                               save_high_score    = shc,
                               show_score_board   = ssb,
                               bot_mode           = bm,
                               bot_move_info_type = bmit
                                                        .replace('1', 'wasd')
                                                        .replace('2', 'ulds') if bmit in ('1', '2') else 'wasd',
                               bot_move_type      = bmt
                                                       .replace('1', 'neat')
                                                       .replace('2', 'algorithm') if bmt in ('1', '2') else 'neat'
                            )
            game_snake.play()
            del w, h, fps, loa, gna, go, shc, ssb, bm, bmt, game_snake
        except (KeyboardInterrupt, EOFError):
            print('\n\033[33mExit [Any] or Reset config [R]...\033[0m',end='')
            keyexit = getch().decode('utf-8').lower()
            if keyexit == 'r':
                print()
                continue
            del keyexit
            exit()
        except Exception as e:
            print(f"\n\033[31m{type(e).__name__}\033[0m: {e}")
            del e
            continue

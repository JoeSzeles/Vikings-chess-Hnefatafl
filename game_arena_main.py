import os
import sys
import pygame as pg
import time
import random
import glob
import openai
import re
import json
from urllib import request, parse
import requests
from spritecutter import split_image_into_frames
from itertools import cycle  # Import cycle from itertools

import pygame as pg
from itertools import cycle  # Import cycle from itertools
from spritecutter import split_image_into_frames


WINDOW_HEIGHT =1000
WINDOW_WIDTH = 1600
GAME_NAME = TITLE = "VIKINGS_CHESS"
GAME_ICON = pg.image.load("king2.png")
MAIN_MENU_TOP_BUTTON_x = 400
MAIN_MENU_TOP_BUTTON_y = 400
BOARD_TOP = 150
BOARD_LEFT = 100
CELL_WIDTH = 60
CELL_HEIGHT = 60
PIECE_RADIUS = 30
VALID_MOVE_INDICATOR_RADIUS = 10
SETTINGS_TEXT_GAP_VERTICAL = 0
SETTINGS_TEXT_GAP_HORIZONTAL = 0

bg = (222, 222, 0)
bg2 = (30, 30, 30)# Game window color
red = (255, 0, 0)
black = (0, 0, 0)
yellow = (255, 255, 1)
golden = (155, 125, 0)
white = (255, 255, 255)
pink_fuchsia = (255, 0, 255)
green_neon = (15, 255, 80)
green_dark = (2, 48, 32)
green_teal = (0, 128, 128)
blue_indigo = (63, 0, 255)
blue_zaffre = (8, 24, 168)

ATTACKER_PIECE_COLOR = pink_fuchsia
DEFENDER_PIECE_COLOR = green_teal
KING_PIECE_COLOR = golden
VALID_MOVE_INDICATOR_COLOR = green_neon
BORDER_COLOR = golden

GAME_ICON_resized = pg.image.load("king2.png")
BACKGROUND_IMAGE = pg.image.load("game3.png")

click_snd = os.path.join("sounds", "click_1.wav")
move_snd_1 = os.path.join("sounds", "move_1.mp3")
kill_snd_1 = os.path.join("sounds", "kill_1.mp3")
win_snd_1 = os.path.join("sounds", "win_1.wav")
lose_snd_1 = os.path.join("sounds", "lose_1.wav")

clicked = False



def update_sprite_positions(chessboard, sprite_frames):
    if not sprite_frames:
        return []

    sprite_frame_size = sprite_frames[0].get_size()
    board_x, board_y, board_width, board_height = chessboard.get_dimensions()

    # Calculate the position for each sprite so its center aligns with each point
    sprite_positions = [
        (board_x - sprite_frame_size[0] // 2, board_y - sprite_frame_size[1] // 2),  # Top-left corner
        (board_x + board_width - sprite_frame_size[0]  // 2, board_y - sprite_frame_size[1]  // 2),  # Top-right corner
        (board_x - sprite_frame_size[0] // 2, board_y + board_height - sprite_frame_size[1] // 2),  # Bottom-left corner
        (board_x + board_width - sprite_frame_size[0]// 2, board_y + board_height - sprite_frame_size[1] // 2),  # Bottom-right corner
        (board_x + board_width // 2 - sprite_frame_size[0] // 2, board_y + board_height // 2 - sprite_frame_size[1] // 2)  # Center
    ]

    return sprite_positions



def draw_mini_map(screen, board_status, top_left, cell_size, piece_size):
    # Define colors for different pieces
    attacker_color = pg.Color('red')
    defender_color = pg.Color('blue')
    king_color = pg.Color('yellow')
    empty_color = pg.Color('white')
    restricted_color = pg.Color('grey')
    
    # Loop through the board status and draw each cell
    for row_index, row in enumerate(board_status):
        for col_index, col in enumerate(row):
            # Calculate the position and draw the cell
            cell_rect = pg.Rect(
                top_left[0] + col_index * cell_size,
                top_left[1] + row_index * cell_size,
                cell_size,
                cell_size
            )
            pg.draw.rect(screen, empty_color, cell_rect, 1)  # Draw cell border
            
            # Draw the piece in the cell
            piece_pos = (cell_rect.centerx, cell_rect.centery)
            if col == 'a':  # Attacker
                pg.draw.circle(screen, attacker_color, piece_pos, piece_size)
            elif col == 'd':  # Defender
                pg.draw.circle(screen, defender_color, piece_pos, piece_size)
            elif col == 'k':  # King
                pg.draw.circle(screen, king_color, piece_pos, piece_size)
            elif col == 'x':  # Restricted cell
                pg.draw.circle(screen, restricted_color, piece_pos, piece_size)

def write_text(text, screen, position, color, font, new_window=True):
    '''
    This function writes the given text at the given position on given surface applying th e given color and font.

    Parameters
    ----------
    text : string
        This string will be #printed.
    screen : a pygame display or surface
        The text wiil be written on this suface.
    position : a pair of values e.g. (x,y)
        The text wiil be written at this position.
    color : rgb coolor code e.g. (255,255,255)
        The text wiil be written in this color.
    font : a pygame font (pg.font.SysFont)
        The text wiil be written in this font.
    new_window : a boolean value, optional
        This parameter will determine whether the text wil be #printed in a new window or current window. 
        If the former, all current text and graphics on this surface will be overwritten with background color.
        The default is True.

    Returns
    -------
    None.

    '''

    if new_window:
        screen.fill(bg2)
    txtobj = font.render(text, True, (255, 255, 255))
    txtrect = txtobj.get_rect()
    txtrect.topleft = position
    screen.blit(txtobj, txtrect)

class BackgroundLayer:
    def __init__(self, screen, image_path, window_size):
        self.screen = screen
        self.image_path = image_path
        self.window_size = window_size
        self.load_image()

    def load_image(self):
        # Load the image and scale it to fill the entire window
        self.image = pg.image.load(self.image_path)
        self.image = pg.transform.scale(self.image, self.window_size)

    def draw(self):
        # Draw the scaled image onto the screen
        self.screen.blit(self.image, (0, 0))


class Custom_button:

    '''
    This class holds the ncessary part of a custom button operation.


    '''

    button_col = (111, 111, 111) #main button background color
    hover_col = red
    click_col = (50, 150, 255)
    text_col = black

    def __init__(self, x, y, text, screen, font, width=200, height=70):
        self.x = x
        self.y = y
        self.text = text
        self.screen = screen
        self.font = font
        self.width = width
        self.height = height
        self.button_image = pg.image.load('button4.png')
        self.button_image = pg.transform.scale(self.button_image, (width, height))

    def draw_button(self):
        global clicked
        action = False

        # Get mouse position
        pos = pg.mouse.get_pos()

        # Create pg.Rect object for the button
        button_rect = pg.Rect(self.x, self.y, self.width, self.height)

        # Check mouseover and clicked conditions
        if button_rect.collidepoint(pos):
            if pg.mouse.get_pressed()[0] == 1:
                clicked = True
            elif pg.mouse.get_pressed()[0] == 0 and clicked:
                clicked = False
                action = True

        # Draw the button background
        self.screen.blit(self.button_image, button_rect.topleft)

        # Add text to button
        text_img = self.font.render(self.text, True, self.text_col)
        text_len = text_img.get_width()
        self.screen.blit(text_img, (self.x + int(self.width / 2) - int(text_len / 2), self.y + 15))
        return action


class ChessBoard:
    '''
    This class contains all properties of a chess board.

    Properties:

        1. initial_pattern: this parameter holds the position of pieces at the start of the match.
        2. rows: n(rows) on board
        3. columns: n(columns) on board
        4. cell_width: width of each cell on surface
        5. cell_height: height of each cell on surface
        6. screen: where the board will be #printed
        7. restricted_cell: holds the (row, column) value of restricted cells

    Methods:

        1. draw_empty_board(): this method draws an empty board with no piece on given surface
        2. initiate_board_pieces(): this method initiates all the sprite instances of different types of pieces

    '''

    def __init__(self, screen, board_size="large"):


        self.cell_width = CELL_WIDTH
        self.cell_height = CELL_HEIGHT

        # MAPS 

        self.initial_pattern11 = ["x..aaaaa..x",
                                  ".....a.....",
                                  "...........",
                                  "a....d....a",
                                  "a...ddd...a",
                                  "aa.ddcdd.aa",
                                  "a...ddd...a",
                                  "a....d....a",
                                  "...........",
                                  ".....a.....",
                                  "x..aaaaa..x"]

        self.initial_pattern9 = ["x..aaa..x",
                                 "..d.a..d.",
                                 "..k...k..",
                                 "a.......a",
                                 "aa.aca.aa",
                                 "a..aad..a",
                                 "...gbg...",
                                 "....g....",
                                 "x..aaa..x"]
        

                # custom map 
                # a: attacker, d: defender, c : king, k: attacker king, g:defender commander, w : wall
        self.initial_pattern12 = ["........d.d.d.d.d.d........",
                                  "www......d.d.c.d.d......www",
                                  "..........d.d.d.d..........",
                                  "...........d.g.d...........",
                                  "............d.d............",
                                  "............................",
                                  "...........................",
                                  "...........................",
                                  "............a.a............",
                                  "...........a.a.a...........",
                                  "www.......a.a.a.a.......www",
                                  "........xa.a.b.a.ax........",
                                  ".......xa.a.a.a.a.ax......."]
        # Define cell_width and cell_height
                # custom map
        self.initial_pattern13 = ["x...aaaaa...x",
                                  ".....aaa.....",
                                  "......a......",
                                  "......g......",
                                  "a...d.d.d...a",
                                  "aa...ddd...aa",
                                  "aaa.ddcdd.aaa",
                                  "aa...ddd...aa",
                                  "a...d.d.d...a",
                                  ".............",
                                  "......a......",
                                  ".....aaa.....",
                                  "x...aaaaa...x"]


        if board_size == "large":
            self.initial_pattern = self.initial_pattern11
        elif board_size == "custom":
         self.initial_pattern = self.initial_pattern12
        elif board_size == "XL":
         self.initial_pattern = self.initial_pattern13
        else:
            self.initial_pattern = self.initial_pattern9

        self.rows = len(self.initial_pattern)
        self.columns = len(self.initial_pattern[0])

        # Calculate the total width and height of the chessboard
        self.total_width = self.columns * self.cell_width
        self.total_height = self.rows * self.cell_height

        self.game_image = pg.image.load('background.png')
        self.game_image= pg.transform.scale(self.game_image, (1600 , 1000))
        self.board_size = board_size

        # Load and scale the chessboard-specific background image########################################################################################
        ################################################################################################################################################


        # Define file name patterns for different board sizes
        file_patterns = {
            "small": "maps_small*.png",  # pattern for 9x9 board maps
            "large": "maps_large*.png",  # pattern for 11x11 board maps
            "XL": "maps_xl*.png" ,        # pattern for 13x13 board maps
            "custom": "maps_custom*.png"         # pattern for 13x13 board maps
        }

        # Get the pattern for the current board size
        pattern = file_patterns.get(board_size, "maps_large*.png")  # Default to large if not specified

        # List all files matching the pattern
        map_files = glob.glob(pattern)

        # Randomly select a map file from the filtered list
        if map_files:
            selected_map_file = random.choice(map_files)
            self.background_image = pg.image.load(selected_map_file)
            self.background_image = pg.transform.scale(self.background_image, (self.total_width, self.total_height))
        if not map_files:
            print(f"No map files found for pattern {pattern}")
            # Load a default background image or set a default color
            self.background_image = None  # Or set a default imaged color
        # Position variables for the chessboard
        self.board_left = BOARD_LEFT
        self.board_top = BOARD_TOP
        self.screen = screen

        self.restricted_cells = [(0, 0), (0, self.columns-1), (int(self.rows/2), int(
        self.columns/2)), (self.rows-1, 0), (self.rows-1, self.columns-1)]

    def draw_empty_board(self):
        '''
        This method draws an empty board with no piece on given surface

        Returns
        -------
        None.

        '''

        border_top = pg.Rect(BOARD_LEFT - 10, BOARD_TOP -
                             10, self.columns*CELL_WIDTH + 20, 10)
        pg.draw.rect(self.screen, BORDER_COLOR, border_top)
        border_down = pg.Rect(BOARD_LEFT - 10, BOARD_TOP +
                              self.rows*CELL_HEIGHT, self.columns*CELL_WIDTH + 20, 10)
        pg.draw.rect(self.screen, BORDER_COLOR, border_down)
        border_left = pg.Rect(BOARD_LEFT - 10, BOARD_TOP -
                              10, 10, self.rows*CELL_HEIGHT + 10)
        pg.draw.rect(self.screen, BORDER_COLOR, border_left)
        border_right = pg.Rect(BOARD_LEFT+self.columns*CELL_WIDTH,
                               BOARD_TOP - 10, 10, self.rows*CELL_HEIGHT + 10)
        pg.draw.rect(self.screen, BORDER_COLOR, border_right)

        color_flag = True
        for row in range(self.rows):
            write_text(str(row), self.screen, (BOARD_LEFT - 30, BOARD_TOP + row*CELL_HEIGHT +
                       PIECE_RADIUS), (255, 255, 255), pg.font.SysFont("franklingothicmedium", 15), False)
            write_text(str(row), self.screen, (BOARD_LEFT + row*CELL_WIDTH +
                       PIECE_RADIUS, BOARD_TOP - 30), (255, 255, 255), pg.font.SysFont("franklingothicmedium", 15), False)
            for column in range(self.columns):

                cell_rect = pg.Rect(BOARD_LEFT + column * self.cell_width, BOARD_TOP +
                                    row * self.cell_height, self.cell_width, self.cell_height)

                if (row == 0 or row == self.rows-1) and (column == 0 or column == self.columns-1):
                    pg.draw.rect(self.screen, red, cell_rect)
                elif row == int(self.rows / 2) and column == int(self.columns / 2):
                    pg.draw.rect(self.screen, blue_indigo, cell_rect)
                elif color_flag:
                    pg.draw.rect(self.screen, white, cell_rect)
                else:
                    pg.draw.rect(self.screen, black, cell_rect)


                color_flag = not color_flag
        if self.background_image:
            self.screen.blit(self.background_image, (self.board_left, self.board_top))
        else:
            # If no background image, fill with a default color or draw a placeholder
            self.screen.fill((0, 0, 0))  # Example: Fill with black color


       ############################ ADD UNITS


    def initiate_board_pieces(self):
        '''
        This method initiates all the sprite instances of different types of pieces

        Returns
        -------
        None.

        '''

        att_cnt, def_cnt = 1, 1
        # for more effective use, this dict maps piece ids and pieces -> {pid : piece}
        global piece_pid_map
        piece_pid_map = {}

        for row in range(self.rows):
            for column in range(self.columns):
                if self.initial_pattern[row][column] == 'a':
                    pid = "a" + str(att_cnt)
                    AttackerPiece(pid, row, column)
                    att_cnt += 1
                elif self.initial_pattern[row][column] == 'd':
                    pid = "d" + str(def_cnt)
                    DefenderPiece(pid, row, column)
                    def_cnt += 1
                elif self.initial_pattern[row][column] == 'c':
                    pid = "k"
                    KingPiece(pid, row, column)
                    def_cnt += 1
                elif self.initial_pattern[row][column] == 'b' :
                    pid = "b"  + str(att_cnt)
                    AttackerKingPiece(pid, row, column)
                    att_cnt += 1

                elif self.initial_pattern[row][column] == 'g' :
                    pid = "g"  # golem
                    GolemPiece(pid, row, column)
                    def_cnt += 1
                elif self.initial_pattern[row][column] == 'w' :
                    pid = "w"  
                    Wall(pid, row, column)
  
                else:
                    pass

        for piece in All_pieces:
            piece_pid_map[piece.pid] = piece

    def get_dimensions(self):
        '''
        Returns the top-left position, width, and height of the chessboard.
        '''
        return (self.board_left, self.board_top, self.total_width, self.total_height)

#########################################################################################################################################


class ChessPiece(pg.sprite.Sprite):
    '''
    This class contains information about each piece.

    Properties:
        1. pid: holds a unique id for currnet piece instance
        2. row: holds the row index of current piece instance
        3. column: holds the column index of current piece instance
        4. center: center position of corresponding piece instance

    Methods:
        1. update_piece_position(row, column): if the corresponding piece instance is moved, this method updates row and column value of that piece.

    '''

    def __init__(self, pid, row, column):

        pg.sprite.Sprite.__init__(self, self.groups)
        self.pid = pid
        self.row, self.column = (row, column)
        self.center = (BOARD_LEFT + int(CELL_WIDTH / 2) + self.column*CELL_WIDTH,
                       BOARD_TOP + int(CELL_HEIGHT / 2) + self.row*CELL_HEIGHT)

    def draw_piece(self, screen):
        '''
        Draws a piece on board.

        Parameters
        ----------
        screen : surface

        Returns
        -------
        None.

        '''

        pg.draw.circle(screen, self.color, self.center, PIECE_RADIUS)

    def update_piece_position(self, row, column):
        '''
        This updates the position of all pieces on board.

        Parameters
        ----------
        row : row number
        column : column number

        Returns
        -------
        None.

        '''

        self.row, self.column = (row, column)
        self.center = (BOARD_LEFT + int(CELL_WIDTH / 2) + self.column*CELL_WIDTH,
                       BOARD_TOP + int(CELL_HEIGHT / 2) + self.row*CELL_HEIGHT)
        
# SAVE map lyaut
       
def save_board_layout(board_layout):
    # Convert the board layout (2D list) to a formatted string
    board_text = "\n".join([" ".join(row) for row in board_layout])

    # Print to the output
    print("Board Layout:")
    print(board_text)

    # Save to a file called 'map.txt'
    with open("map.txt", "w") as file:
        file.write(board_text)

############## Player

class AttackerPiece(ChessPiece):
    def __init__(self, pid, row, column):
        super().__init__(pid, row, column)
        self.ptype = "a"

        # Load the sprite sheet and split into frames
        self.animation_frames = split_image_into_frames('attacker6.png', grid_size=3, crop_size=0, scale_factor=0.3)
        self.frame_cycle = cycle(self.animation_frames)  # Create an iterator to cycle through the frames
        self.current_frame = next(self.frame_cycle)  # Set the initial frame

        # Animation control
        self.animation_interval = 100  # Milliseconds between frames
        self.last_update = pg.time.get_ticks()

    def update_animation(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.animation_interval:
            self.last_update = now
            self.current_frame = next(self.frame_cycle)  # Move to the next frame

    def draw_piece(self, screen):
        # Update the animation
        self.update_animation()

        # Draw the current frame of the animation
        screen.blit(self.current_frame, (self.center[0] - CELL_WIDTH / 2, self.center[1] - CELL_HEIGHT / 2))





class DefenderPiece(ChessPiece):
    def __init__(self, pid, row, column):
        ChessPiece.__init__(self, pid, row, column)
        pg.sprite.Sprite.__init__(self, self.groups)
        self.color = DEFENDER_PIECE_COLOR
        self.permit_to_res_sp = False
        self.ptype = "d"

        # Load the sprite sheet and split into frames
        self.animation_frames = split_image_into_frames('defender4.png', grid_size=3, crop_size=0, scale_factor=0.3)
        self.frame_cycle = cycle(self.animation_frames)  # Create an iterator to cycle through the frames
        self.current_frame = next(self.frame_cycle)  # Set the initial frame

        # Animation control
        self.animation_interval = 100  # Milliseconds between frames
        self.last_update = pg.time.get_ticks()

    def update_animation(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.animation_interval:
            self.last_update = now
            self.current_frame = next(self.frame_cycle)  # Move to the next frame

    def draw_piece(self, screen):
        # Update the animation
        self.update_animation()

        # Draw the current frame of the animation
        screen.blit(self.current_frame, (self.center[0] - CELL_WIDTH / 2, self.center[1] - CELL_HEIGHT / 2))



class AttackerKingPiece(ChessPiece):
    def __init__(self, pid, row, column):
        super().__init__(pid, row, column)
        self.ptype = "a"  # Identifier for Attacker King

        # Load the sprite sheet and split into frames
        self.animation_frames = split_image_into_frames('animation4.png', grid_size=3, crop_size=0, scale_factor=0.28)
        self.frame_cycle = cycle(self.animation_frames)  # Create an iterator to cycle through the frames
        self.current_frame = next(self.frame_cycle)  # Set the initial frame

        # Animation control
        self.animation_interval = 100  # Milliseconds between frames
        self.last_update = pg.time.get_ticks()

    def update_animation(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.animation_interval:
            self.last_update = now
            self.current_frame = next(self.frame_cycle)  # Move to the next frame

    def draw_piece(self, screen):
        # Update the animation
        self.update_animation()

        # Draw the current frame of the animation
        screen.blit(self.current_frame, (self.center[0] - CELL_WIDTH / 2, self.center[1] - CELL_HEIGHT / 2))

class GolemPiece(ChessPiece):
    def __init__(self, pid, row, column):
        super().__init__(pid, row, column)
        self.ptype = "d"  # Identifier for Attacker King

        # Load the sprite sheet and split into frames
        self.animation_frames = split_image_into_frames('king4.png', grid_size=3, crop_size=0, scale_factor=0.28)
        self.frame_cycle = cycle(self.animation_frames)  # Create an iterator to cycle through the frames
        self.current_frame = next(self.frame_cycle)  # Set the initial frame

        # Animation control
        self.animation_interval = 100  # Milliseconds between frames
        self.last_update = pg.time.get_ticks()

    def update_animation(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.animation_interval:
            self.last_update = now
            self.current_frame = next(self.frame_cycle)  # Move to the next frame

    def draw_piece(self, screen):
        # Update the animation
        self.update_animation()

        # Draw the current frame of the animation
        screen.blit(self.current_frame, (self.center[0] - CELL_WIDTH / 2, self.center[1] - CELL_HEIGHT / 2))
 


class KingPiece(DefenderPiece):
    '''
    This class holds information about the king piece. It's a child of DefenderPiece class.

    Properties:
        1. color: a rgb color code. e.g. (255,255,255)
            color of the king piece that will be drawn on board.
        2. ptype: type of piece. "k" means king.
        3. permit_to_res_sp: a boolean value.
            tells whether the king piece is allowed on a restricted cell or not. here it's true.
    '''

    def __init__(self, pid, row, column):
        DefenderPiece.__init__(self, pid, row, column)
        self.color = KING_PIECE_COLOR
        self.permit_to_res_sp = True
        self.ptype = "k"

        # Load the sprite sheet for king and split into frames
        self.animation_frames = split_image_into_frames('king3.png', grid_size=3, crop_size=0, scale_factor=0.3)
        self.frame_cycle = cycle(self.animation_frames)  # Create an iterator to cycle through the frames
        self.current_frame = next(self.frame_cycle)  # Set the initial frame

        # Animation control
        self.animation_interval = 100  # Milliseconds between frames
        self.last_update = pg.time.get_ticks()

    def update_animation(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.animation_interval:
            self.last_update = now
            self.current_frame = next(self.frame_cycle)  # Move to the next frame

    def draw_piece(self, screen):
        # Update the animation
        self.update_animation()

        # Draw the current frame of the animation
        screen.blit(self.current_frame, (self.center[0] - CELL_WIDTH / 2, self.center[1] - CELL_HEIGHT / 2))

class Wall(ChessPiece):
    def __init__(self, pid, row, column):
        super().__init__(pid, row, column)
        # Load and scale the image for attackers
        self.ptype = "w" 
        self.image = pg.image.load('wall1.png')
        self.image = pg.transform.scale(self.image, (CELL_WIDTH, CELL_HEIGHT))

    def draw_piece(self, screen):
        screen.blit(self.image, (self.center[0] - CELL_WIDTH / 2, 
                                 self.center[1] - CELL_HEIGHT / 2))


def match_specific_global_data():
    '''
    This function declares and initiates all sprite groups. 

    Global Properties:
        1. All_pieces: a srpite group containing all pieces.
        2. Attacker_pieces: a srpite group containing all attacker pieces.
        3. Defender_pieces: a srpite group containing all defender pieces.
        4. King_pieces: a srpite group containing all king piece.

    Returns
    -------
    None.

    '''

    global All_pieces, Attacker_pieces, Defender_pieces, King_pieces

    All_pieces = pg.sprite.Group()
    Attacker_pieces = pg.sprite.Group()
    Defender_pieces = pg.sprite.Group()
    King_pieces = pg.sprite.Group()

    ChessPiece.groups = All_pieces
    AttackerPiece.groups = All_pieces, Attacker_pieces
    DefenderPiece.groups = All_pieces, Defender_pieces
    KingPiece.groups = All_pieces, Defender_pieces, King_pieces

################################################################################################
class Game_manager:
    '''
    This class handles all the events within the game.

    Properties:

        1. screen: a pygame display or surface.
            holds the current screen where the game is played on.
        2. board: a ChessBoard object.
            this board is used in current game.
        3. turn: a boolean value. default is True.
            this value decides whose turn it is - attackers' or defenders'.
        4. king_escape: a boolean value. dafult is false.
            this variable tells whether the king is captured or not.
        5. king_captured: a boolean value. default is false.
            this variable tells whether the king escaped or not.
        6. all_attackers_killed: a boolean value. default is false.
            this variable tells if all attackers are killed or not.
        7. finish: a boolean value. default is false.
            this variable tells whether a match finishing condition is reached or not.
        8. already_selected: a ChessPiece object, or any of it's child class object.
            this varaible holds currenlty selected piece.
        9. is_selected: a boolean value. default is false.
            this variable tells whether any piece is selected or not.
        10. valid_moves: a list of pair. 
            this list contains all the valid move indices- (row, column) of currently selected piece.
        11. valid_moves_positions: a list of pair. 
                this list contains all the valid move pixel positions- (x_pos, y_pos) of currently selected piece.
        12. current_board_status: a list of lists. 
                this holds current positions of all pieces i.e. current board pattern.
        13. current_board_status_with_border: a list of lists. 
                this holds current positions of all pieces i.e. current board pattern along with border index. 
                (this is redundent I know, but, it's needed for avoiding complexity)
        14. mode: 0 means p-vs-p, 1 means p-vs-ai
                this variable holds game mode.
        15. last_move: pair of pairs of indecies - ((prev_row, prev_col), (curr_row, curr_col))
                this variable holds the 'from' and 'to' of last move.
        16. board_size: "large" means 11x11, "small" means 9x9, default is "large"
                this variable holds board sizes.

    Methods:

        1. select_piece(selected_piece): 
            to select a piece.
        2. find_valid_moves(): 
            finds valid moves of selected piece.
        3. show_valid_moves(): 
            draws the indicator of valid moves on board.
        4. deselect(): 
            deselects currently selected piece.
        5. update_board_status(): 
            updates board status after each move.
        6. capture_check(): 
            contains capture related logics.
        7. king_capture_check(): 
            contains caturing-king related logics.
        8. escape_check(): 
            contains king-escape related logics.
        9. attackers_count_check(): 
            counts currently unkilled attacker pieces.
        10. match_finished(): 
                performs necessary tasks when match ends.
        11. mouse_click_analyzer(msx, msy): 
                analyzes current mouse click action and performs necessary functionalites.
        12. turn_msg(): 
                displays info about whose turn it is. 
        13. ai_move_manager(piece, row, column):
                handles ai moves

    '''

    def __init__(self, screen, board, mode, board_size="large"):
        self.screen = screen
        self.board = board
        self.turn = True
        self.king_escaped = False
        self.king_captured = False
        self.all_attackers_killed = False
        self.finish = False
        self.already_selected = None
        self.is_selected = False
        self.valid_moves = []
        self.valid_moves_positions = []
        self.current_board_status = []
        self.current_board_status_with_border = []
        self.mode = mode
        self.last_move = None
        self.board_size = board_size
        self.player_score = 0
        self.bot_score = 0
        self.player_moves = 0    # Tracks number of moves made by Player 1
        self.bot_moves = 0       # Tracks number of moves made by Player 2/Bot
        self.player_units = 0    # Tracks number of units Player 1 has on the board
        self.bot_units = 0       # Tracks number of units Player 2/Bot has on the board
        self.player_knockouts = 0 # Tracks number of units Player 1 has knocked out
        self.bot_knockouts = 0    # Tracks number of units Player 2/Bot has knocked out
        self.player_wins = 0     # Tracks number of wins for Player 1
        self.player_losses = 0   # Tracks number of losses for Player 1
        self.bot_wins = 0        # Tracks number of wins for Player 2/Bot
        self.bot_losses = 0      # Tracks number of losses for Player 2/Bot
        self.last_move_time = pg.time.get_ticks()
        self.current_move_time = 0

        # initiating current_board_status and current_board_status_with_border.
        # initially board is in initial_pattern
        # appending top border row
        border = []
        for column in range(self.board.columns + 2):
            border.append("=")
        self.current_board_status_with_border.append(border)

        # appending according to initial_pattern
        for row in self.board.initial_pattern:
            bordered_row = ["="]  # to add a left border
            one_row = []
            for column in row:
                one_row.append(column)
                bordered_row.append(column)
            self.current_board_status.append(one_row)
            bordered_row.append("=")  # to add a right border
            self.current_board_status_with_border.append(bordered_row)

        # appending bottom border row
        self.current_board_status_with_border.append(border)

    def select_piece(self, selected_piece):
        '''
        This method selects a piece.

        Parameters
        ----------
        selected_piece : a ChessPiece or it's child class object.
            assigns this piece to already_selected variable.

        Returns
        -------
        None.

        '''

        self.is_selected = True
        self.already_selected = selected_piece
        self.find_valid_moves()

    def find_valid_moves(self):
        '''
        This method finds valid moves of the selected piece and ensures that no piece can move through or capture a wall.

        Returns
        -------
        None.
        '''
        self.valid_moves = []
        start_row = self.already_selected.row
        start_col = self.already_selected.column

        # Directions to check (up, down, left, right)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for row_offset, col_offset in directions:
            tempr, tempc = start_row, start_col
            # Move in each direction until a blocking object or board edge is encountered
            while True:
                tempr += row_offset
                tempc += col_offset

                if not (0 <= tempr < self.board.rows and 0 <= tempc < self.board.columns):
                    break  # Break if it goes out of board boundaries
                
                thispos = self.current_board_status[tempr][tempc]

                # Stop at the first wall or piece encountered; walls are not capturable or passable
                if thispos == "w" or thispos in ["a", "d", "k"]:  # Assuming 'a', 'd', 'k' are other piece types
                    break
                
                # Add valid move and check if it's the king with limited movement
                if self.already_selected.ptype == "k":
                    self.valid_moves.append((tempr, tempc))
                    break  # King can only move one step
                
                self.valid_moves.append((tempr, tempc))

        # Convert board indices to screen positions for rendering valid moves
        self.valid_moves_positions = [
            (BOARD_LEFT + int(CELL_WIDTH / 2) + pos[1] * CELL_WIDTH,
             BOARD_TOP + int(CELL_HEIGHT / 2) + pos[0] * CELL_HEIGHT)
            for pos in self.valid_moves
        ]



    def show_valid_moves(self):
        '''
        This method draws the indicator of valid moves on board.

        Returns
        -------
        None.

        '''

        # Size of the square, you can adjust this as needed
        square_side_length = 2 * VALID_MOVE_INDICATOR_RADIUS

        # iterating over valid moves positions and drawing them on board
        for index in self.valid_moves_positions:
            # Calculate the top-left corner of the square
            square_rect = pg.Rect(index[0] - CELL_WIDTH // 2, index[1] - CELL_WIDTH // 2, CELL_WIDTH, CELL_WIDTH)

            # Draw the square
            pg.draw.rect(self.screen, pink_fuchsia, square_rect, width=4)  # width=2 for outline, adjust as neede

    def deselect(self):
        '''
        This method deselects currently selected piece.

        Returns
        -------
        None.

        '''

        self.is_selected = False
        self.already_selected = None
        self.valid_moves = []
        self.valid_moves_positions = []

    def update_board_status(self):
        '''
        This method updates board status after each move.

        Returns
        -------
        None.

        '''
        
        self.current_board_status = []
        self.current_board_status_with_border = []

        # adding top border row
        border = []
        for column in range(self.board.columns + 2):
            border.append("=")
        self.current_board_status_with_border.append(border)

        # first setting all cells as empty cells, then making changes where necessary
        for row in range(self.board.rows):
            bordered_row = ["="]  # left border
            one_row = []
            for column in range(self.board.columns):
                one_row.append(".")
                bordered_row.append(".")

            if row == 0 or row == self.board.rows - 1:
                one_row[0] = "x"
                one_row[self.board.columns-1] = "x"
                bordered_row[1] = "x"
                bordered_row[self.board.columns] = "x"
            self.current_board_status.append(one_row)
            bordered_row.append("=")  # right border
            self.current_board_status_with_border.append(bordered_row)

        # adding bottom border
        self.current_board_status_with_border.append(border)

        # according to each piece's positions, updating corresponding (row, column) value
        for piece in All_pieces:
            self.current_board_status[piece.row][piece.column] = piece.ptype
            # adding an extra 1 because 0th row and 0th column is border
            self.current_board_status_with_border[piece.row +
                                                  1][piece.column+1] = piece.ptype

        # initial pattern set middle cell as empty cell. but, if it is actually an restricted cell.
        # if it doesn't contain king, it's marked as "x'.
        if self.current_board_status[int(self.board.rows/2)][int(self.board.columns/2)] != "k":
            self.current_board_status[int(
                self.board.rows/2)][int(self.board.columns/2)] = "x"
            self.current_board_status_with_border[int(
                self.board.rows/2)+1][int(self.board.columns/2)+1] = "x"
   

   

    def capture_check(self):
        ptype, prow, pcol = self.already_selected.ptype, self.already_selected.row + 1, self.already_selected.column + 1
        sorroundings = [(prow, pcol + 1), (prow, pcol - 1), (prow - 1, pcol), (prow + 1, pcol)]
        two_hop_away = [(prow, pcol + 2), (prow, pcol - 2), (prow - 2, pcol), (prow + 2, pcol)]

        for pos, item in enumerate(sorroundings):
            opp = self.current_board_status_with_border[item[0]][item[1]]
            try:
                opp2 = self.current_board_status_with_border[two_hop_away[pos][0]][two_hop_away[pos][1]]
            except:
                opp2 = "."

            if ptype == opp or ptype == "x" or ptype == "=" or opp == "." or opp2 == ".":
                continue

            elif opp == "k":
                self.king_capture_check(item[0], item[1])
                if self.king_captured:
                    self.finish = True  # Ending the game if the king is captured
                    if self.turn:  # Player captures the king
                        self.player_score += 1000  # Incrementing player's score
                    else:  # Bot captures the king
                        self.bot_score += 1000  # Incrementing bot's score
                    break  # Stop checking other pieces once the king is captured

                print(self.king_captured)
                

            elif ptype != opp:
                # neghbour cell's piece is of different type
                if ptype == "a" and (ptype == opp2 or opp2 == "x"):
                    # a-d-a or a-d-res_cell situation
                    for piece in All_pieces:
                        if piece.ptype == opp and piece.row == sorroundings[pos][0]-1 and piece.column == sorroundings[pos][1]-1:
                            pg.mixer.Sound.play(pg.mixer.Sound(kill_snd_1))
                            piece.kill()
                            self.update_board_status()
                            break

                elif ptype != "a" and opp2 != "a" and opp2 != "=" and opp == "a":
                    # d-a-d or k-a-d or d-a-k or d-a-res_cell or k-a-res_cell situation
                    for piece in All_pieces:
                        if piece.ptype == opp and piece.row == sorroundings[pos][0]-1 and piece.column == sorroundings[pos][1]-1:
                            pg.mixer.Sound.play(pg.mixer.Sound(kill_snd_1))
                            piece.kill()
                            self.update_board_status()
                            break
        if self.king_captured:
            self.finish = True
            pg.mixer.Sound.play(pg.mixer.Sound(lose_snd_1))





    def king_capture_check(self, kingr, kingc):
        front = self.current_board_status_with_border[kingr][kingc + 1]
        back = self.current_board_status_with_border[kingr][kingc - 1]
        up = self.current_board_status_with_border[kingr - 1][kingc]
        down = self.current_board_status_with_border[kingr + 1][kingc]

        if front == "x" or back == "x" or up == "x" or down == "x":
            return

        elif front == "d" or back == "d" or up == "d" or down == "d":
            return

        elif front == "." or back == "." or up == "." or down == ".":
            return

        else:
            self.king_captured = True

    def escape_check(self):
        if self.current_board_status[0][0] == "k" or self.current_board_status[0][self.board.columns-1] == "k" or self.current_board_status[self.board.rows-1][0] == "k" or self.current_board_status[self.board.rows-1][self.board.columns-1] == "k":
            self.king_escaped = True
            self.finish = True
            pg.mixer.Sound.play(pg.mixer.Sound(win_snd_1))
            self.player_score += 1000  # King escapes

        else:
            self.king_escaped = False
 

 #DRAW SCORES########################################################################################

    def draw_scores(self, x, y):

        # Load the custom font; specify the path to the font file and the font size
        font_path = "IMPACT.TTF"  # Adjust the path if the font file is in a subfolder
        font_size = 30
        font = pg.font.Font(font_path, font_size)
    
        # Render the text
        player_score_text = font.render(f"Player 1 Score: {self.player_score}", True, (66, 255, 0))
        self.screen.blit(player_score_text, (x, y))
        y += 40

        player_moves_text = font.render(f"Move Number: {self.player_moves}", True, (66, 255, 0))
        self.screen.blit(player_moves_text, (x, y))
        y += 40

        bot_score_text = font.render(f"Player 2 Score: {self.bot_score}", True, (255, 0, 66))
        self.screen.blit(bot_score_text, (x, y ))  # Slight offset for the second line
        y += 40  # Adjust y position for the next line of text


    def attackers_count_check(self):
        '''
        This method checks if all attackers are killed or not.

        Returns
        -------
        None.

        '''
        # only way attackers would win is by capturing king, so it's not necessary to check defenders' count
        # Attacker_pieces sprite group holds all attackers
        if len(Attacker_pieces) == 0:
            self.all_attackers_killed = True
            self.finish = True
            pg.mixer.Sound.play(pg.mixer.Sound(win_snd_1))


    def match_finished(self):
        '''
        This method displays necessary messages when the match finishes.

        Returns
        -------
        None.

        '''
        consolas = pg.font.SysFont("consolas", 22)
        if self.king_captured:
            if self.mode == 0:
                write_text(">>> KING CAPTURED !! ATTACKERS WIN !!", self.screen, (20, BOARD_TOP - 80), white,
                           consolas, False)
            else:
                write_text(">>> KING CAPTURED !! AI WINS !!", self.screen, (20, BOARD_TOP - 80), white,
                           consolas, False)

        elif self.king_escaped:
            write_text(">>> KING ESCAPED !! DEFENDERS WIN !!", self.screen, (20, BOARD_TOP - 80), white,
                       consolas, False)
            

        elif self.all_attackers_killed:
            write_text(">>> ALL ATTACKERS DEAD !! DEFENDERS WIN !!", self.screen, (20, BOARD_TOP - 80), white,
                       consolas, False)
            

        else:
            pass

    def mouse_click_analyzer(self, msx, msy):
        '''
        Analyzes a mouse click event to determine the action based on the position clicked.

        Parameters
        ----------
        msx : integer
            X-coordinate of the mouse click.
        msy : integer
            Y-coordinate of the mouse click.

        Returns
        -------
        None.
        '''
        if not self.is_selected:
            for piece in All_pieces:
                if (msx >= piece.center[0] - PIECE_RADIUS) and (msx < piece.center[0] + PIECE_RADIUS) and \
                   (msy >= piece.center[1] - PIECE_RADIUS) and (msy < piece.center[1] + PIECE_RADIUS):
                    if piece.ptype == 'w':  # Skip if the piece is a wall
                        continue
                    if (piece.ptype == "a" and self.turn) or (piece.ptype != "a" and not self.turn):
                        self.select_piece(piece)
                        break
        else:
            piece = self.already_selected
            if (msx >= piece.center[0] - PIECE_RADIUS) and (msx < piece.center[0] + PIECE_RADIUS) and \
               (msy >= piece.center[1] - PIECE_RADIUS) and (msy < piece.center[1] + PIECE_RADIUS):
                # Deselect if the same piece or a wall is clicked
                self.deselect()
            else:
                # Handle move if a valid position is clicked
                for ind, pos in enumerate(self.valid_moves_positions):
                    if (msx >= pos[0] - PIECE_RADIUS) and (msx < pos[0] + PIECE_RADIUS) and \
                       (msy >= pos[1] - PIECE_RADIUS) and (msy < pos[1] + PIECE_RADIUS):
                        self.move_piece(ind)
                        break
                self.deselect()

    def move_piece(self, index):
        '''
        Moves the selected piece to a new position based on valid moves.

        Parameters
        ----------
        index : int
            Index of the valid move in the valid_moves list.

        Returns
        -------
        None.
        '''
        # Update the piece's position
        new_pos = self.valid_moves[index]
        prev_pos = (self.already_selected.row, self.already_selected.column)
        self.already_selected.update_piece_position(new_pos[0], new_pos[1])
        self.update_board_status()
        self.capture_check()
        if self.already_selected.ptype == "k":
            self.escape_check()
        if self.already_selected.ptype != "a":
            self.attackers_count_check()
        self.turn = not self.turn  # Change turn
        pg.mixer.Sound.play(pg.mixer.Sound(move_snd_1))
        self.last_move = (prev_pos, new_pos)  # Save the move as a tuple of tuples





    def ai_move_manager(self, piece, row, column):
        '''
        This function handles functionalities after AI chooses which piece to move

        Parameters
        ----------
        piece : AI's choosen piece
        row : row index
        column : column index

        Returns
        -------
        None.

        '''

        # updating piece's position
        self.already_selected = piece
        prev = (self.already_selected.row, self.already_selected.column)
        self.already_selected.update_piece_position(row-1, column-1)
        curr = (row-1, column-1)
        self.last_move = (prev, curr)
        # updating board status
        self.update_board_status()
        # playing a sound effect
        pg.mixer.Sound.play(pg.mixer.Sound(move_snd_1))
        # self.already_selected = self.ai_selected
        # checking if any opponent piece was captured or not
        self.capture_check()
        # checking if selected piece is king or not
        # if it is, then checking if it's escaped or not
        if self.already_selected.ptype == "k":
            self.escape_check()
        # if it was defender's turn, checking if all of the attackers are captured or not
        if self.already_selected.ptype != "a":
            self.attackers_count_check()
        # altering turn; a to d or d to a
        self.turn = not self.turn
        self.deselect()
        self.bot_moves += 1
        self.current_move_time = pg.time.get_ticks()
        self.last_move_time = self.current_move_time   




    def display_elapsed_time(self):
        elapsed_time = (pg.time.get_ticks() - self.last_move_time) // 1000  # Convert milliseconds to seconds
        elapsed_time_text = f"Time since last move: {elapsed_time} seconds"
        font = pg.font.Font(None, 36)  # Adjust the font and size as needed
        text_surface = font.render(elapsed_time_text, True, (56, 220, 56))  # White color
        self.screen.blit(text_surface, (600, 80))  # Adjust the position as needed

    def turn_msg(self, game_started):
        '''
        This method shows message saying whose turn it is now.

        Returns
        -------
        None.

        '''
        consolas = pg.font.SysFont("consolas", 22)
        if not game_started:
            if self.mode == 0:
                write_text(">>> Click 'New Game' to start a new game.", self.screen,
                           (30, BOARD_TOP - 80), red, consolas, False)
            else:
                write_text(">>> Click 'New Game' to start a new game. AI is attacker and you are defender.", self.screen,
                           (30, BOARD_TOP - 80), red, consolas, False)

        elif self.mode == 0 and self.turn:
            write_text(">>> Attacker's Turn", self.screen, (30, BOARD_TOP - 80), red,
                       consolas, False)

        elif self.mode == 1 and self.turn:
            write_text(">>> AI is thinking...", self.screen, (30, BOARD_TOP - 80), blue_indigo,
                       consolas, False)

        else:
            write_text(">>> Defender's Turn", self.screen, (30, BOARD_TOP - 80), blue_indigo,
                       consolas, False)


class AI_manager:

    def __init__(self, manager, screen):

        self.manager = manager
        self.screen = screen

    def move(self):
        '''
        AI uses this function to move a piece.

        Returns
        -------
        None.

        '''

        current_board = []
        rows = self.manager.board.rows
        columns = self.manager.board.columns
        self.rows = rows
        self.columns = columns
        
        # creating pattern such as
        # [['x', '.', '.', 'a1', 'a2', 'a3', 'a4', 'a5', '.', '.', 'x'], 
        #  ['.', '.', '.', '.', '.', 'a6', '.', '.', '.', '.', '.'], 
        #  ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'], 
        #  ['a7', '.', '.', '.', '.', 'd1', '.', '.', '.', '.', 'a8'],
        #  ['a9', '.', '.', '.', 'd2', 'd3', 'd4', '.', '.', '.', 'a10'], 
        #  ['a11', 'a12', '.', 'd5', 'd6', 'k', 'd7', 'd8', '.', 'a13', 'a14'],
        #  ['a15', '.', '.', '.', 'd9', 'd10', 'd11', '.', '.', '.', 'a16'], 
        #  ['a17', '.', '.', '.', '.', 'd12', '.', '.', '.', '.', 'a18'],
        #  ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'], 
        #  ['.', '.', '.', '.', '.', 'a19', '.', '.', '.', '.', '.'], 
        #  ['x', '.', '.', 'a20', 'a21', 'a22', 'a23', 'a24', '.', '.', 'x']]        

        current_board = []

        border_row = []
        for column in range(columns+2):
            border_row.append("=")
        current_board.append(border_row)

        for row in range(rows):
            one_row = ["="]
            for column in range(columns):
                one_row.append('.')
            one_row.append("=")
            current_board.append(one_row)

        current_board.append(border_row)

        for piece in All_pieces:
            current_board[piece.row+1][piece.column+1] = piece.pid

        current_board[1][1] = current_board[1][rows] = current_board[rows][1] = current_board[rows][columns] = 'x'
        if current_board[int((self.rows+1)/2)][int((self.columns+1)/2)] != 'k':
            current_board[int((self.rows+1)/2)][int((self.columns+1)/2)] = 'x'

        # find all possible valid move and return -> list[piece, (pair of indices)]
        piece, best_move = self.find_best_move(current_board)
        row, col = best_move

        # Increment the bot's move counter
        self.manager.bot_moves += 1
        # perform the move
        self.manager.ai_move_manager(piece, row, col)

    def find_all_possible_valid_moves(self, board_status_at_this_state, fake_turn):
        '''
        AI uses this fucntion to finds out all valid moves of all pieces of a type.

        Parameters
        ----------
        board_status_at_this_state : a 2d matrix
            at any state of evaluation, ai feeds that state's board status here to calculate moves
        fake_turn : boolean
            True - attackers' turn, False - defenders' turn

        Returns
        -------
        valid_moves : a list of pairs - [(str, (int, int))]
            (piece_pid, (row, column))

        '''

        valid_moves = []
        piece_pos_this_state = {}
        for row_ind, row in enumerate(board_status_at_this_state):
            for col_ind, column in enumerate(row):
                if column != "." and column != "x" and column != "=":
                    piece_pos_this_state[column] = (row_ind, col_ind)

        for each in piece_pos_this_state.keys():
            piece = each[0]

            # find moves for a side only if it's their turn
            if (fake_turn and not piece[0] == "a") or (not fake_turn and piece[0] == "a"):
                continue

            tempr = piece_pos_this_state[each][0]
            tempc = piece_pos_this_state[each][1]

            # finding valid moves in upwards direction
            tempr -= 1
            while tempr >= 0:
                # stores current row and column
                thispos = board_status_at_this_state[tempr][tempc][0]
                # if finds any piece, no move left in this direction anymore
                if thispos == "a" or thispos == "d" or thispos == "k" or thispos == "=" or (thispos == "x" and piece != "k"):
                    break
                else:
                    # this part is commented out because so far ai is only attacker and this part checks both 'a' or 'd'
                    # # if selected piece is king, only one move per direction is allowed
                    if piece == "k":
                        if tempr < piece_pos_this_state[each][0] - 1 or tempr > piece_pos_this_state[each][0] + 1:
                            break
                        valid_moves.append(
                            (piece_pid_map[each], (tempr, tempc)))
                    else:
                        # "." means empty cell
                        if thispos == ".":
                            valid_moves.append(
                                (piece_pid_map[each], (tempr, tempc)))

                tempr -= 1

            tempr = piece_pos_this_state[each][0]
            tempc = piece_pos_this_state[each][1]

            # finding valid moves in downwards direction
            tempr += 1
            while tempr < self.manager.board.rows+2:
                # stores current row and column
                thispos = board_status_at_this_state[tempr][tempc][0]
                # if finds any piece, no move left in this direction anymore
                if thispos == "a" or thispos == "d" or thispos == "k" or thispos == "=" or (thispos == "x" and piece != "k"):
                    break
                else:
                    # # if selected piece is king, only one move per direction is allowed
                    if piece == "k":
                        if tempr < piece_pos_this_state[each][0] - 1 or tempr > piece_pos_this_state[each][0] + 1:
                            break
                        valid_moves.append(
                            (piece_pid_map[each], (tempr, tempc)))
                    else:
                        # "." means empty cell
                        if thispos == ".":
                            valid_moves.append(
                                (piece_pid_map[each], (tempr, tempc)))

                tempr += 1

            tempr = piece_pos_this_state[each][0]
            tempc = piece_pos_this_state[each][1]

            # finding valid moves in left direction
            tempc -= 1
            while tempc >= 0:
                # stores current row and column
                thispos = board_status_at_this_state[tempr][tempc][0]
                # if finds any piece, no move left in this direction anymore
                if thispos == "a" or thispos == "d" or thispos == "k" or thispos == "=" or (thispos == "x" and piece != "k"):
                    break
                else:
                    # # if selected piece is king, only one move per direction is allowed
                    if piece == "k":
                        if tempc < piece_pos_this_state[each][1] - 1 or tempc > piece_pos_this_state[each][1] + 1:
                            break
                        valid_moves.append(
                            (piece_pid_map[each], (tempr, tempc)))
                    else:
                        # "." means empty cell
                        if thispos == ".":
                            valid_moves.append(
                                (piece_pid_map[each], (tempr, tempc)))

                tempc -= 1

            tempr = piece_pos_this_state[each][0]
            tempc = piece_pos_this_state[each][1]

            # finding valid moves in right direction
            tempc += 1
            while tempc < self.manager.board.columns+2:
                # stores current row and column
                thispos = board_status_at_this_state[tempr][tempc][0]
                # if finds any piece, no move left in this direction anymore
                if thispos == "a" or thispos == "d" or thispos == "k" or thispos == "=" or (thispos == "x" and piece != "k"):
                    break
                else:
                    # # if selected piece is king, only one move per direction is allowed
                    if piece == "k":
                        if tempc < piece_pos_this_state[each][1] - 1 or tempc > piece_pos_this_state[each][1] + 1:
                            break
                        valid_moves.append(
                            (piece_pid_map[each], (tempr, tempc)))
                    else:
                        # "." means empty cell
                        if thispos == ".":
                            valid_moves.append(
                                (piece_pid_map[each], (tempr, tempc)))

                tempc += 1
                

        return valid_moves
  
    def king_mobility(self, fake_board, r, c):
        '''
        THis function checks how many cells can king move at current state

        Parameters
        ----------
        fake_board : board status at that state            
        r : row of king            
        c : column of king            

        Returns
        -------
        score : number of cells king can move to            

        '''
        score = 0
        i = c-1
        while(i != '='):
            if fake_board[r][i] == '.' or fake_board[r][i] == 'x':
                score += 1
            else:
                break
            i -= 1

        i = c+1
        while(i != '='):
            if fake_board[r][i] == '.' or fake_board[r][i] == 'x':
                score += 1
            else:
                break

            i += 1

        i = r-1
        while(i != '='):
            if fake_board[i][c] == '.' or fake_board[i][c] == 'x':
                score += 1
            else:
                break

            i -= 1

        i = r+1
        while(i != '='):
            if fake_board[i][c] == '.' or fake_board[i][c] == 'x':
                score += 1
            else:
                break

            i += 1

        return score

    def king_sorrounded(self, fake_board, r, c):
        '''
        Finds out how many attacekrs are sorrounding king at current board state.

        Parameters
        ----------
        fake_board : board status at that state            
        r : row of king            
        c : column of king   

        Returns
        -------
        score : number of sorrounding attackers.

        '''
        score = 0
        if fake_board[r][c+1][0] == 'a':
            score += 1

        if fake_board[r][c-1][0] == 'a':
            score += 1

        if fake_board[r-1][c][0] == 'a':
            score += 1

        if fake_board[r+1][c][0] == 'a':
            score += 1

        return score

    def evaluate(self, fake_board):
        '''
        This function evaluates current board state using a predefined heuristic value. Heart of AI...

        Parameters
        ----------
        fake_board : current board state.

        Returns
        -------
        score : calculated cost/value of this state.

        '''
        # heuristic values
        weight_pos = 5
        # for 11x11 board
        weight_king_pos_11 = [[10000, 10000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 10000, 10000],
                              [10000, 500, 500, 500, 500, 500,
                              500, 500, 500, 500, 10000],
                              [1000, 500, 200, 200, 200, 200,
                              200, 200, 200, 500, 1000],
                              [1000, 500, 200, 50, 50, 50, 50, 50, 200, 500, 1000],
                              [1000, 500, 200, 50, 10, 10, 10, 50, 200, 500, 1000],
                              [1000, 500, 200, 50, 10, 0, 10, 50, 200, 500, 1000],
                              [1000, 500, 200, 50, 10, 10, 10, 50, 200, 500, 1000],
                              [1000, 500, 200, 50, 50, 50, 50, 50, 200, 500, 1000],
                              [1000, 500, 200, 200, 200, 200,
                              200, 200, 200, 500, 1000],
                              [10000, 500, 500, 500, 500, 500,
                              500, 500, 500, 500, 10000],
                              [10000, 10000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 10000, 10000]]

        # for 9x9 board
        weight_king_pos_9 = [[10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000],
                            [10000, 500, 500, 500, 500, 500, 500, 500, 10000],
                            [10000, 500, 150, 150, 150, 150, 150, 500, 10000],
                            [10000, 500, 150, 30, 30, 30, 150, 500, 10000],
                            [10000, 500, 150, 30, 0, 30, 150, 500, 10000],
                            [10000, 500, 150, 30, 30, 30, 150, 500, 10000],
                            [10000, 500, 150, 150, 150, 150, 150, 500, 10000],
                            [10000, 500, 500, 500, 500, 500, 500, 500, 10000],
                            [10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000]]

        if self.manager.board_size == "large":
            weight_king_pos = weight_king_pos_11
            weight_attacker = 12  # weight is given because inequal number of attacker and defender
            weight_defender = 24
            weight_king_sorrounded = 50000
        else:
            weight_king_pos = weight_king_pos_9
            weight_attacker = 8  # weight is given because inequal number of attacker and defender
            weight_defender = 12
            weight_king_sorrounded = 10000

        #weight_king_sorrounded = 50000


        attacker = 0  # attacker count

        defender = 0  # defender count

        score = 0

        if self.fake_gameOver(fake_board) == 1:  # if 1 then winner is attacker
            print("c")
            score += 10000000
            return score

        elif self.fake_gameOver(fake_board) == 2:  # if 1 then winner is defender
            score -= 10000000
            return score

        # finding number of attackers and defenders currently on board
        # searching king position
        for row_index, row in enumerate(fake_board):
            for col_index, col in enumerate(row):
                if(col == 'k'):
                    r = row_index
                    c = col_index
                elif(col[0] == 'a'):
                    attacker += 1
                elif(col[0] == 'd'):
                    defender += 1

        # making dynamic heuristic evaluation to prioritize on restricting movement of king when he is close to corner cells
        if r-3 <= 1 and c-3 <= 1:
            if fake_board[1][2][0] == 'a':
                score += 1000
            if fake_board[2][1][0] == 'a':
                score += 1000
        elif r-3 <= 1 and c+3 >=(self.columns):
            if fake_board[1][self.columns-1][0] == 'a':
                score += 1000
            if fake_board[2][self.columns][0] == 'a':
                score += 1000

        elif r+3 >= (self.rows) and c-3 <= 1:
            if fake_board[self.rows-1][1][0] == 'a':
                score += 1000
            if fake_board[self.rows][2][0] == 'a':
                score += 1000

        elif r+3 >=(self.rows) and c+3 >=(self.columns):
            if fake_board[self.rows][self.columns-1][0] == 'a':
                score += 1000
            if fake_board[self.rows-1][self.columns][0] == 'a':
                score += 1000

        score += (attacker*weight_attacker)
        score -= (defender*weight_defender)
        score -= (weight_pos*weight_king_pos[r-1][c-1])
        score += (weight_king_sorrounded *
                  self.king_sorrounded(fake_board, r, c))

        return score

    def fake_move(self, fake_board, commited_move):
        '''
        This function performs a fake move - AI's imaginative move in alpha-beta pruning

        Parameters
        ----------
        fake_board : this state's board status
        commited_move : which and where to move - (piece.pid, (row, column))

        Returns
        -------
        current_board : board status after commiting that move
        diff : difference of number of uncaptured pieces on both sides        

        '''
        # fake board = current state fake board, commited move=the move to be executed
        # (piece, (where to))
        current_board = []
        for row in range(len(fake_board)):
            one_row = []
            for column in range(len(fake_board[0])):
                one_row.append(".")
            current_board.append(one_row)

        for row_index, row in enumerate(fake_board):
            for col_index, column in enumerate(row):
                current_board[row_index][col_index] = column

        for row_index, row in enumerate(current_board):
            f = True
            for column_index, col in enumerate(row):
                if(commited_move[0].pid == col):
                    current_board[row_index][column_index] = "."
                    f = False
                    break

            if not f:
                break

        # row = int((self.rows+1)/2)
        # column = int((self.columns+1)/2)
        if current_board[int((self.rows+1)/2)][int((self.columns+1)/2)] == ".":
            current_board[int((self.rows+1)/2)][int((self.columns+1)/2)] = 'x'
        current_board[commited_move[1][0]][commited_move[1]
                                           [1]] = commited_move[0].pid

        current_board, king_captured = self.fake_capture_check(
            current_board, commited_move)

        attacker = 0
        defender = 0
        for row_index, row in enumerate(current_board):
            for col_index, col in enumerate(row):
                if(col[0] == 'a'):
                    attacker += 1
                elif(col[0] == 'd'):
                    defender += 1

        if current_board[int((self.rows+1)/2)][int((self.columns+1)/2)] == ".":
            current_board[int((self.rows+1)/2)][int((self.columns+1)/2)] = 'x'

        return current_board, attacker-defender

    def minimax(self, fake_board, alpha, beta, max_depth, turn):
        '''
        Implementation of minimax algorithm.

        Parameters
        ----------
        fake_board : current fake state's board
        alpha : integer
        beta : integer
        max_depth : number of step to dive into the tree
        turn : True for attackers, False for defenders

        Returns
        -------
        bestvalue: the best value evaluated

        '''

        bestvalue = -10000000000
        moves = self.find_all_possible_valid_moves(
            fake_board, turn)  # True attacker ,False Defender

        if max_depth <= 0 or self.fake_gameOver(fake_board) == 1 or self.fake_gameOver(fake_board) == 2:
            return self.evaluate(fake_board)

        # fake board is copied into current board
        current_board = []
        for row in range(len(fake_board)):
            one_row = []
            for column in range(len(fake_board[0])):
                one_row.append(".")
            current_board.append(one_row)

        for row_index, row in enumerate(fake_board):
            for col_index, column in enumerate(row):
                current_board[row_index][col_index] = column

        # commit a move from valid moves list -> evaluate -> pick bestvalue -> alpha-beta computing
        if(turn == True):  # attacker maximizer
            bestvalue = -1000000000000000000
            for i in moves:
                tmp_fake_board, diff = self.fake_move(current_board, i)
                value = self.minimax(tmp_fake_board, alpha,
                                     beta, max_depth-1, False)
                bestvalue = max(value, bestvalue)
                alpha = max(alpha, bestvalue)
                if(beta <= alpha):
                    break

        else:  # defender minimizer
            bestvalue = 1000000000000000000
            for i in moves:
                tmp_fake_board, diff = self.fake_move(current_board, i)
                value = self.minimax(tmp_fake_board, alpha,
                                     beta, max_depth-1, True)
                bestvalue = min(value, bestvalue)
                beta = min(beta, bestvalue)
                if(beta <= alpha):
                    break

        return bestvalue

    def strategy(self, current_board):
        '''
        Brain of AI...

        Parameters
        ----------
        current_board : current state's board

        Returns
        -------
        bestmove : best move for this state to be committed by AI

        '''
        # value to calcaute the move with best minimax value
        bestvalue = -1000000000000000000
        max_depth = 3
        # True attacker,False Defender  
        # moves = (piece_object,(row,col))
        moves = self.find_all_possible_valid_moves(current_board, True)
        c = 0
        diffs = {}
        for i in moves:   # iterate all possible valid moves and their corersponding min max value
            c += 1
            fake_board, diff = self.fake_move(current_board, i)
            value = self.minimax(fake_board, -1000000000000000000,
                                 1000000000000000000, max_depth-1, False)
            print(value, i[1], diff)
            if(value > bestvalue):
                bestmove = i
                bestvalue = value
                diffs[value] = diff

            elif(value == bestvalue and diff > diffs[value]):
                bestmove = i
                bestvalue = value
                diffs[value] = diff

            if(value == bestvalue and (i[1] == (1, 2) or i[1] == (2, 1) or i[1] == (1, self.columns-1) or i[1] == (2, self.columns) or i[1] == (self.rows-1, 1) or i[1] == (self.rows, 2) or i[1] == (self.rows-1, self.columns) or i[1] == (self.rows, self.columns-1))):
                bestmove = i

        return bestmove

    def find_best_move(self, current_board):
        '''
        Calls algoritm.

        Parameters
        ----------
        current_board : current state's board

        Returns
        -------
        best_move : best move for this state to be committed by AI
        
        '''

        best_move = self.strategy(current_board)

        return best_move

    def fake_gameOver(self, fake_board):
        '''
        Check AI's minimax tree traversing has reached game over condition or not.

        Parameters
        ----------
        fake_board : current fake state's board

        Returns
        -------
        int
            1 attacker win, 2 defender win, 3 none win

        '''
        # 1 attacker win,2 defender win,3 none win        
        if self.fake_king_capture_check(fake_board):
            return 1
        elif self.fake_king_escape(fake_board) or self.fake_attacker_cnt(fake_board):
            return 2
        else:
            return 3

    def fake_capture_check(self, fake_board_with_border, move):
        '''
        This method contains capture related logics at any fake state.

        Parameters
        ----------
        fake_board_with_border : current fake state's board
        move : for which move the capture event might happen

        Returns
        -------
        fake_board_with_border : current fake state's board
        king_captured : whether the king is captured or not - True or False

        '''
        # storing current piece's type and index
        ptype, prow, pcol = move[0].pid[0], move[1][0], move[1][1]

        # indices of sorrounding one hop cells and two hops cells.
        sorroundings = [(prow, pcol+1), (prow, pcol-1),
                        (prow-1, pcol), (prow+1, pcol)]
        two_hop_away = [(prow, pcol+2), (prow, pcol-2),
                        (prow-2, pcol), (prow+2, pcol)]
        
        # iterating over each neighbour cells and finding out if the piece of this cell is captured or not
        for pos, item in enumerate(sorroundings):

            king_captured = False
            # currently selected cell's piece, if any
            opp = fake_board_with_border[item[0]][item[1]][0]            
            # if index is 1, which means it's right beside border, which means there's no two-hop cell in thi direction
            # it may overflow the list index, so it will be set as empty cell instead to avoid error
            try:
                opp2 = fake_board_with_border[two_hop_away[pos]
                                              [0]][two_hop_away[pos][1]][0]
            except:
                opp2 = "."

            # if next cell is empty or has same type of piece or has border, no capturing is possible
            # if two hop cell is empty, then also no capturing is possible
            if ptype == opp or ptype == "x" or ptype == "=" or opp == "." or opp2 == ".":
                continue

            elif opp == "k":
                # king needs 4 enemies on 4 cardinal points to be captured. so, handled in another function.
                king_captured = self.fake_king_capture_check(
                    fake_board_with_border)                

            elif ptype != opp:
                # neghbour cell's piece is of different type
                if ptype == "a" and (ptype == opp2 or opp2 == "x"):
                    # a-d-a or a-d-res_cell situation
                    fake_board_with_border[item[0]][item[1]] = '.'                    

                elif ptype != "a" and opp2 != "a" and opp2 != "=" and opp == "a":
                    # d-a-d or k-a-d or d-a-k or d-a-res_cell or k-a-res_cell situation
                    fake_board_with_border[item[0]][item[1]] = '.'                    

        return fake_board_with_border, king_captured
        

    def fake_king_capture_check(self, fake_board_with_border):
        '''
        This method contains caturing-king related logics.

        Parameters
        ----------
        fake_board_with_border : current fake state's board

        Returns
        -------
        bool
            True if captured, False if not.

        '''
        # store all four neighbor cells' pieces             
        for row_index, row in enumerate(fake_board_with_border):
            for col_index, col in enumerate(row):
                if col == "k":                    
                    kingr = row_index
                    kingc = col_index
                    break
        
        front = fake_board_with_border[kingr][kingc+1][0]
        back = fake_board_with_border[kingr][kingc-1][0]
        up = fake_board_with_border[kingr-1][kingc][0]
        down = fake_board_with_border[kingr+1][kingc][0]

        # if all four sides has attackers or a 3-attackers-one-bordercell situation occurs, king is captured
        # all other possible combos are discarded
        if front == "x" or back == "x" or up == "x" or down == "x":
            return False

        elif front == "d" or back == "d" or up == "d" or down == "d":
            return False

        elif front == "." or back == "." or up == "." or down == ".":
            return False

        else:
            return True

    def fake_king_escape(self, fake_board):
        '''
        Checks whether king has escaped in this fake state or not.

        Parameters
        ----------
        fake_board : current fake state's board

        Returns
        -------
        bool
            True if escaped, False if not.

        '''
        r = self.manager.board.rows
        c = self.manager.board.columns
        if fake_board[1][1] == 'k' or fake_board[1][c] == 'k' or fake_board[r][1] == 'k' or fake_board[r][c] == 'k':
            return True

    def fake_attacker_cnt(self, fake_board):
        '''
        Checks whether all attacekrs are captured in this fake state or not.

        Parameters
        ----------
        fake_board : current fake state's board

        Returns
        -------
        bool
            True if all are captured, False if not.

        '''

        for row_index, row in enumerate(fake_board):
            for col_ind, col in enumerate(row):
                if col[0] == "a":
                    return False
        return True

########################################
#########################################
###########################################

def game_window(screen, mode):
    # Initialize necessary instances
    match_specific_global_data()

    # Initialize other necessary components
    chessboard = ChessBoard(screen)
    chessboard.initiate_board_pieces()
    manager = Game_manager(screen, chessboard, mode)
    if mode == 1:
        bot = AI_manager(manager, screen)

    # Load and scale the background image
    background_image = pg.image.load("game_bg_2.png")
    background_image = pg.transform.scale(background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
    mode_btn = Custom_button(600, 0, "Switch Mode", screen, pg.font.SysFont("franklingothicmedium", 30))

    # Load the sprite frames
    sprite_frames = split_image_into_frames('flash5.png')  # Use your sprite cutter function
    if sprite_frames:
        sprite_frame_size = sprite_frames[0].get_size()  # Assuming all frames are the same size
    else:
        sprite_frame_size = (0, 0)  # Default size if frames couldn't be loaded

    sprite_index = 0  # For cycling through sprite frames

    # Get chessboard dimensions
    board_x, board_y, board_width, board_height = chessboard.get_dimensions()



    # Main game loop
    game_started = False
    tafle = True
    bot = AI_manager(manager, screen) if mode == 1 else None

    # Calculate the mini-map position and draw the mini-map
    # Initialize the mini-map cell size and piece size
    mini_map_cell_size = 10  # Define the cell size of the mini-map
    mini_map_piece_size = 4  # Define the piece size on the mini-map6

    # Calculate the mini-map position and draw the mini-map
    mini_map_width = 11 * mini_map_cell_size  # Adjust for your board size
    mini_map_margin = 50  # Margin from the right edge of the window
    mini_map_top_left_x = WINDOW_WIDTH - mini_map_width - mini_map_margin
    mini_map_top_left_y = 80  # Margin from the top of the window
    mini_map_top_left = (mini_map_top_left_x, mini_map_top_left_y)
    
    game_started = False
    tafle = True
    bot = AI_manager(manager, screen) if mode == 1 else None

    # Position for the score display (adjust these as needed)
    score_x = WINDOW_WIDTH-500  
    score_y = 100 
    sprite_positions = []  # Initialize with an empty list


########## MAIN GAME ELEMENTS 
    while tafle:
        # fire sprite :
    # Calculate sprite positions
# Calculate sprite positions

        chessboard.draw_empty_board()  # Draw the chessboard
        manager.draw_scores(score_x, score_y)  # Draw scores
        manager.display_elapsed_time()  # Display elapsed time





        # New button for loading a specific map
        load_map_btn = Custom_button(200, 0, "Random map", screen, pg.font.SysFont("franklingothicmedium", 30))


        size9by9btn = Custom_button(WINDOW_WIDTH-150, 0, "9x9", screen,
                                    pg.font.SysFont("franklingothicmedium", 20), width=150, height=80)

        size11by11btn = Custom_button(WINDOW_WIDTH-300, 0, "11x11", screen,
                                      pg.font.SysFont("franklingothicmedium", 20), width=150, height=80)

        size12by12btn = Custom_button(WINDOW_WIDTH-450, 0, "Custom", screen,
                                      pg.font.SysFont("franklingothicmedium", 20), width=150, height=80)
        size12by13btn = Custom_button(WINDOW_WIDTH-600, 0, "13x13", screen,
                                      pg.font.SysFont("franklingothicmedium", 20), width=150, height=80)

        backbtn = Custom_button(0, 0, "Back", screen,
                                pg.font.SysFont("franklingothicmedium", 30))
        write_text("Hnefatafl - Play Vikings Chess", screen, (500, 20), (255, 255, 255),
                   pg.font.SysFont("franklingothicmedium", 40))

        write_text("Game Settings", screen, (300, 40), (255, 255, 255),
                   pg.font.SysFont("franklingothicmedium", 40), False)

        write_text("Board Size:", screen, (500, 40), (255, 255, 255),
                   pg.font.SysFont("franklingothicmedium", 40), False)

        screen.blit(background_image, (0, 0))


        
        # Draw mode button and handle its action
        # Switch mode logic
        if mode_btn.draw_button():

            pg.mixer.Sound.play(pg.mixer.Sound(click_snd))
            mode = (mode + 1) % 3  # Cycles through 0, 1, 2
            print(f"Switched to Mode {mode}")
            game_started = False  # Reset game_started state
            chessboard.initiate_board_pieces()  # Reinitialize board pieces
            manager = Game_manager(screen, chessboard, mode)  # Reinitialize game manager
            bot = AI_manager(manager, screen) if mode == 1 else None

        if game_started:
            manager.draw_scores(score_x, score_y)  # Draw the scores

        else:
            txt = 'New Game'

        newgamebtn = Custom_button(
            400, 0, txt, screen, pg.font.SysFont("franklingothicmedium", 30))

        if backbtn.draw_button():
            pg.mixer.Sound.play(pg.mixer.Sound(click_snd))
            main()

        if size9by9btn.draw_button():
            pg.mixer.Sound.play(pg.mixer.Sound(click_snd))
            game_started = False
            match_specific_global_data()
            chessboard = ChessBoard(screen, "small")
            chessboard.draw_empty_board()
            chessboard.initiate_board_pieces()
            manager = Game_manager(screen, chessboard, mode, "small")
            if mode == 1:
                bot = AI_manager(manager, screen)
            # Update sprite positions
            sprite_positions = update_sprite_positions(chessboard, sprite_frames)

        if size11by11btn.draw_button():
            pg.mixer.Sound.play(pg.mixer.Sound(click_snd))
            game_started = False
            match_specific_global_data()
            chessboard = ChessBoard(screen, "large")
            chessboard.draw_empty_board()
            chessboard.initiate_board_pieces()
            manager = Game_manager(screen, chessboard, mode, "large")
            if mode == 1:
                bot = AI_manager(manager, screen)
            # Update sprite positions
            sprite_positions = update_sprite_positions(chessboard, sprite_frames)

        if size12by12btn.draw_button():
            pg.mixer.Sound.play(pg.mixer.Sound(click_snd))
            game_started = False
            match_specific_global_data()
            chessboard = ChessBoard(screen, "custom")
            chessboard.draw_empty_board()
            chessboard.initiate_board_pieces()
            manager = Game_manager(screen, chessboard, mode, "custom")
            if mode == 1:
                bot = AI_manager(manager, screen)
            # Update sprite positions
            sprite_positions = update_sprite_positions(chessboard, sprite_frames)

        if size12by13btn.draw_button():
            pg.mixer.Sound.play(pg.mixer.Sound(click_snd))
            game_started = False
            match_specific_global_data()
            chessboard = ChessBoard(screen, "XL")
            chessboard.draw_empty_board()
            chessboard.initiate_board_pieces()
            manager = Game_manager(screen, chessboard, mode, "XL")
            if mode == 1:
                bot = AI_manager(manager, screen)
            # Update sprite positions
            sprite_positions = update_sprite_positions(chessboard, sprite_frames)


        if newgamebtn.draw_button():
            last_board = manager.board_size
            game_started = True
            match_specific_global_data()
            chessboard = ChessBoard(screen, last_board)
            chessboard.draw_empty_board()
            chessboard.initiate_board_pieces()
            manager = Game_manager(screen, chessboard, mode, last_board)
            if mode == 1:
                bot = AI_manager(manager, screen)
            # Update sprite positions
            sprite_positions = update_sprite_positions(chessboard, sprite_frames)

        chessboard.draw_empty_board()
        draw_mini_map(screen, manager.current_board_status, mini_map_top_left, mini_map_cell_size, mini_map_piece_size)
        manager.draw_scores(score_x, score_y)

        # Handle events and possible state changes
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    tafle = False
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                msx, msy = pg.mouse.get_pos()
                if not manager.finish:
                    if mode == 0 or (mode == 1 and not manager.turn):
                        manager.mouse_click_analyzer(msx, msy)
                        # After processing the click, draw the last move
                        if manager.last_move:
                            prev_pos, new_pos = manager.last_move
                            pg.draw.circle(screen, red, (BOARD_LEFT + (prev_pos[1] * CELL_WIDTH) + (CELL_WIDTH / 2), BOARD_TOP + (prev_pos[0] * CELL_HEIGHT) + (CELL_HEIGHT / 2)), 5)
                            pg.draw.circle(screen, white, (BOARD_LEFT + (new_pos[1] * CELL_WIDTH) + (CELL_WIDTH / 2), BOARD_TOP + (new_pos[0] * CELL_HEIGHT) + (CELL_HEIGHT / 2)), 5)


                    #ANIMATED SPRITES  ####################################################################

        for pos in sprite_positions:
            screen.blit(sprite_frames[sprite_index], pos)  # Draw each sprite frame at its position

        # Update sprite frame index
        sprite_index = (sprite_index + 1) % len(sprite_frames)





        if game_started and mode == 1 and manager.turn and not manager.finish:
            
            chessboard.draw_empty_board()
            for piece in All_pieces:
                piece.draw_piece(screen)
            if manager.finish:
                manager.match_finished()
            else:
                manager.turn_msg(game_started)
            if manager.last_move is not None:
                pg.draw.circle(screen, red, (BOARD_LEFT+(manager.last_move[0][1]*CELL_WIDTH)+(CELL_WIDTH/2), BOARD_TOP+(
                    manager.last_move[0][0]*CELL_HEIGHT)+(CELL_HEIGHT/2)), 5)
                pg.draw.circle(screen, white, (BOARD_LEFT+(manager.last_move[1][1]*CELL_WIDTH)+(CELL_WIDTH/2), BOARD_TOP+(
                    manager.last_move[1][0]*CELL_HEIGHT)+(CELL_HEIGHT/2)), 5)
            pg.display.update()
            print("c")
            bot.move()
        for piece in All_pieces:
            piece.draw_piece(screen)        

        manager.show_valid_moves()
        if manager.finish:
            manager.match_finished()
        else:
            manager.turn_msg(game_started)
       
        if manager.last_move is not None:
            pg.draw.circle(screen, red, (BOARD_LEFT+(manager.last_move[0][1]*CELL_WIDTH)+(CELL_WIDTH/2), BOARD_TOP+(
                manager.last_move[0][0]*CELL_HEIGHT)+(CELL_HEIGHT/2)), 5)
            pg.draw.circle(screen, white, (BOARD_LEFT+(manager.last_move[1][1]*CELL_WIDTH)+(CELL_WIDTH/2), BOARD_TOP+(
                manager.last_move[1][0]*CELL_HEIGHT)+(CELL_HEIGHT/2)), 5)

        # Draw the Load Map button and check for clicks
        map_files = glob.glob('map*.png')
        if load_map_btn.draw_button():
            pg.mixer.Sound.play(pg.mixer.Sound(click_snd))
            # Load the specific map file here
            specific_map_file = random.choice(map_files)
            #specific_map_file = 'map1.png'
            chessboard.background_image = pg.image.load(specific_map_file)
            chessboard.background_image = pg.transform.scale(chessboard.background_image, (chessboard.total_width, chessboard.total_height))
        manager.display_elapsed_time()
        pg.display.update()


        # Initialize Pygame if not already initialized
        if pg.get_init() is None:
            pg.init()

        # Update the display
        pg.display.update()

        
        

def rules(screen):
    tafle = True
    while tafle:
        write_text("Rules of Viking Chess", screen, (20, 20), (255, 255, 255),
                   pg.font.SysFont("franklingothicmedium", 40))
        backbtn = Custom_button(750, 20, "Back", screen,
                                pg.font.SysFont("franklingothicmedium", 30))

        if backbtn.draw_button():
            pg.mixer.Sound.play(pg.mixer.Sound(click_snd))
            main()
        
        msgs = []
        msgs.append("> Turn based board game.")
        msgs.append("> Two board sizes: 'large' - 11x11 and 'small' - 9x9.")
        msgs.append("> Center cell and four corner cells are called restricted cells.")
        msgs.append("> Excluding king, a-d count is 24-12 on large board and 16-8 on small board.")
        msgs.append("> All pieces except king can move any number of cells horizontally or vertically.")
        msgs.append("> King can move only one cell at a time.")
        msgs.append("> Only king can move to any of the restricted cells.")
        msgs.append("> Pieces, except king, can be captured by sandwitching them from both sides.")
        msgs.append("> Restricted cells can be used to sandwitch opponent.")
        msgs.append("> Only one opponent piece can be captured in single line with single move.")
        msgs.append("> Multiple pieces can be captured with a single move on cardinal points.")
        msgs.append("> To capture king, attackers need to sorround him on all four cardinal points.")
        msgs.append("> If king is captured, attackers win.")
        msgs.append("> If king escapes to any of the four corner cells, defenders win.")
        msgs.append("> If all attackers are captured, defenders win.")
        
        consolas = pg.font.SysFont("consolas", 20)
        cnt = 0
        for msg in msgs:
            write_text(msg, screen, (20, BOARD_TOP - 80 + 40*cnt), white, consolas, False)
            cnt += 1        

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    tafle = False
        pg.display.update()

def history(screen):
    tafle = True
    while tafle:
        write_text("History", screen, (20, 20), (255, 255, 255),
                   pg.font.SysFont("franklingothicmedium", 40))
        backbtn = Custom_button(750, 20, "Back", screen,
                                pg.font.SysFont("franklingothicmedium", 30))

        if backbtn.draw_button():
            pg.mixer.Sound.play(pg.mixer.Sound(click_snd))
            main()
            
        msgs = []
        msgs.append("> Originated in Scandinavia.")
        msgs.append("> Developed from a Roman game called Ludus Latrunculorum.")
        msgs.append("> This game flourished until the arrival of chess.")
        msgs.append("> This game was revived back in nineteenth century.")
        
        
        consolas = pg.font.SysFont("consolas", 20)
        cnt = 0
        for msg in msgs:
            write_text(msg, screen, (20, BOARD_TOP - 80 + 40*cnt), white, consolas, False)
            cnt += 1        

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    tafle = False
        pg.display.update()


def main():
    # Initialization code...
    pg.init()
    screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pg.display.set_caption(GAME_NAME)
    pg.display.set_icon(GAME_ICON)

    ###Background music
    # Initialize Pygame and its mixer
    pg.init()
    pg.init()

    # List all MP3 files in the 'music' folder
    music_files = glob.glob('music/*.mp3')

    # Choose a random music file from the list
    random_music_file = random.choice(music_files)

    # Load and play the randomly chosen music file
    pg.mixer.music.load(random_music_file)
    pg.mixer.music.play(-1)  # -1 makes the music loop indefinitely




    #####################################################################
    icon_rect = GAME_ICON_resized.get_rect(
        center=(500, MAIN_MENU_TOP_BUTTON_y-150))
    
    # Load and scale the background image
    menu_background = pg.image.load("game5.png")
    menu_background = pg.transform.scale(menu_background, (WINDOW_WIDTH, WINDOW_HEIGHT))

    game_on = True

    while game_on:    
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_on = False
                pg.quit()

 
        write_text("Welcome To Vikings Chess!", screen, (250, 20),
                   (255, 255, 255), pg.font.SysFont("franklingothicmedium", 50))

        btn_font = pg.font.SysFont("franklingothicmedium", 28)
        gamebtn_1 = Custom_button(
            MAIN_MENU_TOP_BUTTON_x - 110, MAIN_MENU_TOP_BUTTON_y, "2 player", screen, btn_font)
        gamebtn_2 = Custom_button(
            MAIN_MENU_TOP_BUTTON_x + 110, MAIN_MENU_TOP_BUTTON_y, "Player vs Bot", screen, btn_font)
        rulesbtn = Custom_button(
            MAIN_MENU_TOP_BUTTON_x, MAIN_MENU_TOP_BUTTON_y + 100, "Rules", screen, btn_font)
        historybtn = Custom_button(
            MAIN_MENU_TOP_BUTTON_x, MAIN_MENU_TOP_BUTTON_y + 200, "History", screen, btn_font)
        exitbtn = Custom_button(
            MAIN_MENU_TOP_BUTTON_x, MAIN_MENU_TOP_BUTTON_y + 300, "Exit", screen, btn_font)
        
        screen.blit(menu_background, (0, 0)) #draw menu background
        screen.blit(GAME_ICON_resized, (icon_rect))
        if gamebtn_1.draw_button():
            pg.mixer.Sound.play(pg.mixer.Sound(click_snd))
            game_window(screen, mode=0)

        if gamebtn_2.draw_button():
            pg.mixer.Sound.play(pg.mixer.Sound(click_snd))
            game_window(screen, mode=1)

        if rulesbtn.draw_button():
            pg.mixer.Sound.play(pg.mixer.Sound(click_snd))
            rules(screen)

        if historybtn.draw_button():
            pg.mixer.Sound.play(pg.mixer.Sound(click_snd))
            history(screen)

        if exitbtn.draw_button():
            pg.mixer.Sound.play(pg.mixer.Sound(click_snd))
            game_on = False
            pg.quit()        

     
        pg.display.update()


if __name__ == "__main__":
    main()

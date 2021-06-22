#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 22:46:06 2021

@author: jonas
"""

# Used for coordinates
import numpy as np
# Used to generate random coordinates
from random import randint

# Create macros to make controlling the snake with absolute directions easier
NORTH, EAST, SOUTH, WEST = np.array([0,-1]), np.array([1,0]), np.array([0,1]), np.array([-1,0])
# Create macros to make controlling the snake with relative directions easier (realtive to the moving direction of the snake)
LEFT, FORWARD, RIGHT = -1, 0, 1


class Snake:
    """
    TODO: DOCSTRING
    
    This class is gonna control the snake and the gameboard. Each turn you call a method and tell the class where to move the snake. This class shall take care of collision detection, the game board, the position of the snake, spawning the apple and keeping track of the score. It should do everything except run the game loop, check the user input and render the game. This function should only run the backend. A seperate script shall collect the user input, render the game to the screen and implement the while loop to run the game.
    """
    
    # Set in __init__. Tupel with width and height of the game board.
    BOARD_SIZE = ()
    # Set in __init__ and changed during the game. Position of the body of the snake. List of tupels. Every np.array ist one point on the board. The first element is the head. The last element is the tail.
    position_snake_body = []
    # Set in _spawm_apple. Holds a numpy vector with the position of the apple on the game board.
    position_apple = np.array([])
    
    def __init__(self, board_width:int=32, board_height:int=18, initial_length:int=3):
        #
        #   TODO: DOCSTRING, Initialise game score
        #
        
        #   SET BOARD SIZE
        # 
        # Check the requested size of the board
        if not (board_width > 0 and board_height > 0):
            raise ValueError("The board width and height must be bigger than 0!")
        # Set the size of the board
        self.BOARD_SIZE = (board_width, board_height)
        
        #   INITIALISE SNAKE
        #
        # Set the initial size and position of the snake
        # The snake may not be shorter than 2. If it's to short, moving with relative directions doesn't work anymore.
        if not initial_length >= 2:
            raise ValueError("The snake must have a length of at least 1.")
        # Initialise position and length of the snake
        # The snake head will be placed in the middle of the first row. The body will be placed of screen.
        self.position_snake_body = [ np.array([self._get_max_x()//2, i]) for i in range(0, -initial_length, -1) ]
        
        #   PLACE THE FIRST APPLE
        self._spawn_apple()
        
    def _get_max_x(self):
        """
        This function returns the x-coordinate of the point with the biggest x-coordinate on the game board.

        Returns
        -------
        int
            x-coordinate of the point with the biggest x-coordinate on the game board.

        """
        return self.BOARD_SIZE[0]-1
    
    def _get_max_y(self):
        """
        This function returns the y-coordinate of the point with the biggest y-coordinate on the game board.

        Returns
        -------
        int
            y-coordinate of the point with the biggest x-coordinate on the game board.

        """
        return self.BOARD_SIZE[1]-1
    
    def _is_array_in_list(self, array:np.ndarray, array_list:list):
        """
        Check if a np.ndarray is part of a list of np.ndarrays.

        Parameters
        ----------
        array : np.ndarray
            DESCRIPTION.
        array_list : list of np.ndarrays
            DESCRIPTION.

        Returns
        -------
        BOOLEAN
            True if array is an element of array_list. False if array is not an element of array_list.

        """
        return np.any([ (array == i).all() for i in array_list ])
        
    def _spawn_apple(self):
        """
        This function will position the apple at a random position on the game board. Positions occupied by the snakes body will be avoided.

        Returns
        -------
        None.

        """
        # Generate random positions on the game board until one is found, that is not occupied by the snake
        while True:
            # Generate a random position on the game board
            new_position_x = randint(0, self._get_max_x())
            new_position_y = randint(0, self._get_max_y())
            # Convert random position to numpy array
            new_position = np.array([new_position_x, new_position_y])
            
            # Check if the random position is part of the list position_snake_body (all positions occupied by the snake). If it is not, break the loop.
            if not self._is_array_in_list(new_position, self.position_snake_body):
                break
        
        # Overwrite the current position of the apple with the new position
        self.position_apple = new_position
        
    def _detect_collision_withObstacle(self):
        # TODO: DOCSTRING, Check collision detection with walls and snake body
        pass
    
    def _detect_collision_withApple(self, relative_direction:int):
        # TODO: DOCSTRING, will the snake collide with the apple in when it's gonna move? If yes, update score, spawn a new apple and update tell move() to lengthen the tail of the snake.
        pass
    
    def move(self, direction:"NORTH, EAST, SOUTH, WEST, LEFT, FORWARD, RIGHT"):
        # TODO: DOCSTRING, Move one step, call collision detection, check if apple was eaten, enlarge snake if necessary, increase score if necessary, Return True if the snake lives and False if it dies.
        #
        #   CHECK IF INPUT IS A VALID DIRECTION
        #   CONVERT RELATIVE DIRECTIONS INTO ABSOLUTE DIRECTIONS
        #
        # Check if the parameter direction is a valid relative direction. Valid relative directions are the ints LEFT, FORWARD and RIGHT (defined above the class Snake.)
        if type(direction) is int and direction in [LEFT, FORWARD, RIGHT]:
            #
            # CONVERT RELATIVE DIRECTIONS TO ABSOLUTE DIRECTIONS
            #
            # Get current direction by subtraction the second and the first element of the snake body.
            current_direction = self.position_snake_body[1]-self.position_snake_body[0]
            # Define a rotation angle based on the relative direction (-90°, 0°, +90°)
            rotation_angle = direction*np.pi/2
            # Rotate the current absolute direction with a rotation matrix. Matrix will rotate the current_direction by rotation_angle radians.
            direction = current_direction @ np.array([ [ int(np.cos(rotation_angle)), -int(np.sin(rotation_angle))], 
                                                       [ int(np.sin(rotation_angle)),  int(np.cos(rotation_angle))] ])
            # CONVERSION TO ABSOLUTE DIRECTION DONE
            
        # Check if the parameter direction is a valid absolute direction. Valid absolute directions are the np.ndarrays NORTH, EAST, SOUTH and WEST (defined above the class Snake.)
        elif not isinstance(direction, np.ndarray) or not self._is_array_in_list(direction, [NORTH, EAST, SOUTH, WEST]):
            # Parameter direction is neither relative nor absolute direction. Raise ValueError
            raise ValueError("Wrong value passed for parameter 'direction'. Snake.Snake.move() expects the directions Snake.NORTH, Snake.EAST, Snake.SOUTH and Snake.WEST or Snake.LEFT, Snake.FORWARD and Snake.RIGHT.")
            
        # TODO: move snake, collision detection with wall, snake and apple.
    
    def get_game_state(self):
        # TODO: DOCSTRING, Return the current state of the game. Where is the snake? Where is the apple? Where are the walls? This is the interface for the AI and the GUI
        pass
    
    
if __name__ == "__main__":
    #
    #   Implement the while-loop, user input detection and rendering here. Maybe create a new class or some functions for that.
    #
    snake = Snake()
    
    snake.move(LEFT)
    snake.move(FORWARD)
    snake.move(RIGHT)
    snake.move(NORTH)
    snake.move(SOUTH)
    snake.move(EAST)
    snake.move(WEST)
    
    #snake.move([WEST, EAST])
    #snake.move(90)
    #snake.move(NORTH+10)
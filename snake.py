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
# Create macros so the output of the class is easier to understand.
FLOOR, SNAKE, APPLE = 0, 1, 2


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
    # Variable to keep track of the status of the game. False means the snake lives and the game can go on. True means the snake is dead and the game is over.    
    _snake_dead = False
    # Integer keeping track of the players points
    score = 0
    # Step counter. Integer keeping track of how many steps the player needed to get the apple. Used for score computation
    step_counter = 0
    
    def __init__(self, board_width:int=32, board_height:int=18, initial_length:int=3, max_score_per_apple:int=50, min_score_per_apple:int=10, max_step_to_apple:int=20):
        #
        #   TODO: DOCSTRING, Initialise game score
        #
        
        #   SET BOARD SIZE
        # 
        # Check the requested size of the board
        if not isinstance(board_width, int) or not isinstance(board_height, int): raise ValueError("Height and width of the game board must be integer!")
        if not (board_width > 1 and board_height > 1): raise ValueError("The board width and height must be bigger than 1!")
        # Set the size of the board
        self.BOARD_SIZE = (board_width, board_height)
        
        #   INITIALISE SNAKE
        #
        # Set the initial size and position of the snake
        # The snake may not be shorter than 2. If it's to short, moving with relative directions doesn't work anymore.
        if not isinstance(initial_length, int) or not initial_length >= 2: raise ValueError("The snake must have a length of at least 1 (only integer values allowed).")
        # Initialise position and length of the snake
        # The snake head will be placed in the middle of the first row. The body will be placed of screen.
        self.position_snake_body = [ np.array([self._get_max_x()//2, i]) for i in range(0, -initial_length, -1) ]
        
        #   PLACE THE FIRST APPLE
        self._spawn_apple()
        
        #   INITIALISE CONSTANTS FOR COMPUTING THE SCORE
        #
        # Check input for type
        if not isinstance(max_score_per_apple, int) or not isinstance(min_score_per_apple, int) or not isinstance(max_step_to_apple, int): 
            raise ValueError("max_score_per_apple, min_score_per_apple and max_step_to_apple must be integers!")
        # Check if input makes sense
        if min_score_per_apple < 1: raise ValueError("min_score_per_apple can't be smaller than 1.")
        if max_score_per_apple < min_score_per_apple: raise ValueError("max_score_per_apple must be equal or bigger than min_score_per_apple!")
        if max_step_to_apple < 1: raise ValueError("max_step_to_apple must be at least 1.")
        # Maximal score player can get for an apple. The longer it takes to get the apple, the less points he gets.
        self.MAXIMAL_SCORE_PER_APPLE = max_score_per_apple
        # Minimal score a player can get for an apple. The faster he gets to the apple, the more points he gets.
        self.MINIMAL_SCORE_PER_APPLE = min_score_per_apple
        # The more steps the player needs to get the apple, the less points he makes. If he makes more than 20, he will get the MINIMAL_SCORE_PER_APPLE
        self.MAXIMAL_STEP_COUNT      = max_step_to_apple
        
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
    
    def _update_score(self):
        """
        Compute new score and update the score attribute. The longer the player needs to get to the apple, the less points he gets for the apple.
        There is a maximal and a minimal number of points the player can get for one apple.

        Returns
        -------
        None.

        """
        # Compute the number of points the player should get. This formula makes sure that the number of points decreases with the step counter and that there is a minimal and a maximal possible point value
        points = (self.MAXIMAL_SCORE_PER_APPLE-self.MINIMAL_SCORE_PER_APPLE) * np.exp(-(self.step_counter-1)/self.MAXIMAL_STEP_COUNT) + self.MINIMAL_SCORE_PER_APPLE
        # Round the points to the neares multiple of 5.
        points = 5 * round(points/5)
        # Update score count
        self.score += points
        # Reset step counter
        self.step_counter = 0
        
    def move(self, direction:"NORTH, EAST, SOUTH, WEST, LEFT, FORWARD, RIGHT"):
        """
        TODO

        Parameters
        ----------
        direction : NORTH, EAST, SOUTH, WEST, LEFT, FORWARD, RIGHT
            DESCRIPTION.

        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        # >>>> CHECK IF INPUT IS A VALID DIRECTION
        #
        # Check if the parameter direction is a valid relative direction. Valid relative directions are the integerss LEFT, FORWARD and RIGHT (defined above the class Snake.)
        if not isinstance(direction, int) or not direction in [LEFT, FORWARD, RIGHT]:
            # Check if the parameter direction is a valid absolute direction. Valid absolute directions are the np.ndarrays NORTH, EAST, SOUTH and WEST (defined above the class Snake.)
            if not isinstance(direction, np.ndarray) or not self._is_array_in_list(direction, [NORTH, EAST, SOUTH, WEST]):
                # Parameter direction is neither relative nor absolute direction. Raise ValueError
                raise ValueError("Wrong value passed for parameter 'direction'. Snake.Snake.move() expects the directions Snake.NORTH, Snake.EAST, Snake.SOUTH and Snake.WEST or Snake.LEFT, Snake.FORWARD and Snake.RIGHT.")
          
        # CHECK IF ABSOLUTE DIRECTION POINTS AGAINST CURRENT MOVING DIRECTION
        #
        # Get current direction by subtraction the second and the first element of the snake body.
        current_direction = self.position_snake_body[0]-self.position_snake_body[1]
        # Is the passed direction an absolute direction?
        if isinstance(direction, np.ndarray) or self._is_array_in_list(direction, [NORTH, EAST, SOUTH, WEST]):
            # Is the passed direction opposite to the current direction? If so ignore the user input and move the snake one step FORWARD.
            if (direction==-1*current_direction).all() == True: direction = FORWARD
        #    
        # <<<< CHECK INPUT
        
        #   IS THE GAME OVER?
        #
        # Check if the snake died in the previous round. If it's dead, do nothing and return the status of the snake: True=GameOver, False=Snake is alive and well.
        if self._snake_dead==True:
            return self._snake_dead
            
        # >>>> MOVE SNAKE AND DETECT APPLE
        #
        # 1. CONVERT RELATIVE DIRECTIONS INTO ABSOLUTE DIRECTIONS
        #
        # Check if the parameter direction is a valid relative direction. Valid relative directions are the ints LEFT, FORWARD and RIGHT (defined above the class Snake.)
        if type(direction) is int and direction in [LEFT, FORWARD, RIGHT]:
            #
            # CONVERT RELATIVE DIRECTIONS TO ABSOLUTE DIRECTIONS
            #
            # Define a rotation angle based on the relative direction (-90°, 0°, +90°)
            rotation_angle = direction*np.pi/2
            # Rotate the current absolute direction with a rotation matrix. Matrix will rotate the current_direction by rotation_angle radians.
            direction = current_direction @ np.array([ [  int(np.cos(rotation_angle)), int(np.sin(rotation_angle))], 
                                                       [ -int(np.sin(rotation_angle)), int(np.cos(rotation_angle))] ])
            # CONVERSION TO ABSOLUTE DIRECTION DONE
            
        # Check if the parameter direction is a valid absolute direction. Valid absolute directions are the np.ndarrays NORTH, EAST, SOUTH and WEST (defined above the class Snake.)
        elif not isinstance(direction, np.ndarray) or not self._is_array_in_list(direction, [NORTH, EAST, SOUTH, WEST]):
            # Parameter direction is neither relative nor absolute direction. Raise ValueError
            raise ValueError("Wrong value passed for parameter 'direction'. Snake.Snake.move() expects the directions Snake.NORTH, Snake.EAST, Snake.SOUTH and Snake.WEST or Snake.LEFT, Snake.FORWARD and Snake.RIGHT.")

        # 2. MOVE THE SNAKE AND DETECT APPLE
        #
        # Increase the step counter by one. This is used for the score computation. The faster the player gets the apple, the more points he gets.
        self.step_counter += 1
        
        # Compute the future position of the snakes head
        future_snake_head_position = self.position_snake_body[0] + direction
        # Add a new element at the beginning of the list for the new position of the snakes head
        self.position_snake_body.insert(0, future_snake_head_position)
        
        # Check if the snake has reached the apple
        collision_with_apple = (future_snake_head_position == self.position_apple).all()
        
        if collision_with_apple == True:
            # Spawn a new apple if the snake has reached the apple
            # Do not delete the tail of the snake. The snake will become longe because of that
            self._spawn_apple()
            self._update_score()
        else:
            # Delete the tail of the snake if the apple was not reached. This will make the snake move and keep their length, because the head of the snake was already moved.
            del self.position_snake_body[-1]
        #
        # <<<< MOVE SNAKE AND DETECT APPLE
            
        # >>>> COLLISION DETECTION WALL AND SNAKE
        #
        # Check if the snake is hitting the wall or itself and update self._snake_dead
        # Get the position of the snakes head
        snake_head = self.position_snake_body[0]
        # COLLISION WIHT WALL: Check if head of snake is outside of the board game.
        if (snake_head >= np.array(self.BOARD_SIZE) ).any() or ( snake_head < np.zeros(2) ).any() == True:
            self._snake_dead = True
        # COLLISION WIHT SNAKE: Check if the head of the snake matches the position of any other part of the snake.
        elif self._is_array_in_list(snake_head, self.position_snake_body[1:]) == True:
            self._snake_dead = True
        #
        # <<<< COLLISTION DETECTION
        
        # Return the status of the snake: True=GameOver, False=Snake is alive and well.
        return self._snake_dead

    def get_game_state(self):
        # TODO: DOCSTRING, Return the current state of the game. Where is the snake? Where is the apple? Where are the walls? This is the interface for the AI and the GUI
        gameBoard = [ [ FLOOR for j in range(0, self.BOARD_SIZE[0]) ] for i in range(0, self.BOARD_SIZE[1]) ]
        for snakeBody in self.position_snake_body:
            if ( snakeBody >= 0 ).all() and ( snakeBody < np.array(self.BOARD_SIZE) ).all():
                gameBoard[snakeBody[1]][snakeBody[0]] = SNAKE
            
        gameBoard[self.position_apple[1]][self.position_apple[0]] = APPLE
        
        return {"gameover"  : self._snake_dead,
                "score"     : self.score,
                "snakeBody" : self.position_snake_body,
                "apple"     : self.position_apple,
                "width"     : self.BOARD_SIZE[0],
                "height"    : self.BOARD_SIZE[1],
                "board"     : gameBoard}
    
    def print_game_state(self):
        # Get the state of the game
        game_state = self.get_game_state()
        # PINT THE CURRENT GAME BOARD
        # Create a mapping so the programm knows what ascii characters it should use to print the game.
        graphics = {FLOOR: " ", SNAKE: "▇", APPLE: "◼"}
        # Print board
        print("┌"+"".join([ "─" for i in range(0, game_state["width"]) ])+"┐")
        for row in game_state["board"]:
            output = ""
            for col in row:
                output += graphics[col]
            print("│"+output+"│")
        print("└"+"".join([ "─" for i in range(0, game_state["width"]) ])+"┘")
        # Print score and if your dead
        print(f"game over={game_state['gameover']}; score={game_state['score']}")
#        
#
#   END OF CLASS SNAKE
#
#   
    
def run_snake():
    #
    #   Implement the while-loop, user input detection and rendering-
    #
    
    # >>>> DEFINE MACROS (COLOR, SCREEN SIZE, ...)
    #
    
    # Color
    BACKGROUND_COLOR = (85,102,0)
    APPLE_COLOR = (102,17,0)
    SNAKE_COLOR = (51,51,0)
    
    # Screen and game board size
    SCREEN_SIZE = (800,450)
    BOX_SIZE = 20
    SNAKE_MARGIN = 1
    SNAKE_BORDER_RADIUS = 2
    APPLE_MARGIN = 4
    APPLE_BORDER_RADIUS = 2
    BOARD_WIDTH, BOARD_HEIGHT = [ int(i/BOX_SIZE) for i in SCREEN_SIZE ]
    
    # Frame Rate
    FPS = 15
    
    #
    # <<<< DEFINE MACROS
    
    # >>>> SETUP GAME
    #
    # Setup the game clock
    frame_rate = pygame.time.Clock()
    
    # Setup green 800x450 display
    SCREEN = pygame.display.set_mode(SCREEN_SIZE)
    SCREEN.fill(BACKGROUND_COLOR)
    
    # Get an instance of the snake game
    snake_controller = Snake( board_width=BOARD_WIDTH, board_height=BOARD_HEIGHT )
    #
    # <<<< SETUP GAME
    
    
    # >>>> START GAME LOOP
    running = True
    while running:
        
        # Clear the screen
        SCREEN.fill(BACKGROUND_COLOR)
        
        # Reset walking direction
        direction = FORWARD
        
        # >>>> HANDLE EVENTS AND KEY PRESSES
        #
        for event in pygame.event.get():
            
            # Quit if the user closes the gui.
            if event.type == pygame.locals.QUIT:
                running = False
                break
        
        # Change the walking direction if a key is pressed
        key_input = pygame.key.get_pressed()
        if key_input[pygame.K_UP]:      
            direction = NORTH
        elif key_input[pygame.K_RIGHT]:   
            direction = EAST
        elif key_input[pygame.K_DOWN]:    
            direction = SOUTH
        elif key_input[pygame.K_LEFT]:    
            direction = WEST
        #
        # <<<< HANDLE EVENTS AND KEY PRESSES
        
        # Move the snake by one step
        snake_controller.move(direction)
        
        # Get the current state of the game
        game_state = snake_controller.get_game_state()
        
        # >>>> RENDER SNAKE AND APPLE
        #
        # Draw the apple
        position_apple = tuple(game_state["apple"]*BOX_SIZE+APPLE_MARGIN)
        apple = pygame.Rect(position_apple, (BOX_SIZE-2*APPLE_MARGIN, BOX_SIZE-2*APPLE_MARGIN))
        pygame.draw.rect(SCREEN, APPLE_COLOR, apple, border_radius=APPLE_BORDER_RADIUS)
        
        # Draw the snake
        for snake_element in game_state["snakeBody"]:
            position_snake = tuple(snake_element*BOX_SIZE+SNAKE_MARGIN)
            snake = pygame.Rect(position_snake, (BOX_SIZE-2*SNAKE_MARGIN, BOX_SIZE-2*SNAKE_MARGIN))
            pygame.draw.rect(SCREEN, SNAKE_COLOR, snake, border_radius=SNAKE_BORDER_RADIUS)
        
        # So far the body of the snake is a bunch of unconnected boxes. This loop connects them together by drawing new boxes between the segments of the snake.
        for snake_current, snake_next in zip(game_state["snakeBody"][:-1], game_state["snakeBody"][1:]):
            direction_snake_tail = (snake_next-snake_current)
            snake_tail_connector = pygame.Rect((0,0), (BOX_SIZE-2*SNAKE_MARGIN, BOX_SIZE-2*SNAKE_MARGIN))
            snake_tail_connector.center = snake_current*BOX_SIZE + BOX_SIZE/2 + direction_snake_tail*BOX_SIZE/2
            pygame.draw.rect(SCREEN, SNAKE_COLOR, snake_tail_connector)
        #
        # <<<< RENDER SNAKE AND APPLE
        
        # Set the caption of the display window with the current game score
        pygame.display.set_caption(f"Snake - Score: {game_state['score']}")
        
        # Update display
        pygame.display.update()
        # Tick the clock
        frame_rate.tick(FPS)
    #
    # <<<< END GAME LOOP
    
    
if __name__ == "__main__":
    
    # Import game engine pygame
    import pygame
    import pygame.locals    
    # Initialise game engine
    pygame.init()
    
    try:
        # Run the game
        run_snake()
    except Exception as e:
        # Catch any errors, close the game and reraise the exception
        print("The Game crashed!")
        pygame.quit()
        raise e
    
    # Exit the game
    pygame.quit()
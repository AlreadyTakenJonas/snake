#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 22:46:06 2021

@author: jonas
"""

# Used for coordinates
import numpy as np
# Used to generate random coordinates
import random

from pathlib import Path
import yaml

# Import some helpful code snippets
import snake.utilities as util

# Import game engine pygame
import pygame
import pygame.locals    
    

# Create macros to make controlling the snake with absolute directions easier
# Do not change these values. They are important for converting between relative and absolute directions
NORTH, EAST, SOUTH, WEST = np.array([0,-1]), np.array([1,0]), np.array([0,1]), np.array([-1,0])
# Create macros to make controlling the snake with relative directions easier (realtive to the moving direction of the snake)
# Do not change these values. They are important for converting between relative and absolute directions
LEFT, FORWARD, RIGHT = -1, 0, 1
# Create macros so the output of the class is easier to understand.
FLOOR, SNAKE, APPLE = 0, 1, 2


class GameEngine:
    """
    TODO: DOCSTRING
    
    This class is gonna control the snake and the gameboard. Each turn you call a method and tell the class where to move the snake. This class shall take care of collision detection, the game board, the position of the snake, spawning the apple and keeping track of the score. It should do everything except run the game loop, check the user input and render the game. This function should only run the backend. A seperate script shall collect the user input, render the game to the screen and implement the while loop to run the game.
    """
    
    # Define colors for graphics
    BACKGROUND_COLOR = (85,102,0)
    APPLE_COLOR = (102,17,0)
    SNAKE_COLOR = (51,51,0)
    
    # Define pixel size of graphics
    BOX_SIZE = 40
    SNAKE_MARGIN = 1
    SNAKE_BORDER_RADIUS = 2
    APPLE_MARGIN = 4
    APPLE_BORDER_RADIUS = 2
    
    # Where to store the high score list?
    HIGHSCORE_FILE = Path("data/highscores.yml")
        
    def __init__(self, board_width:int=32, board_height:int=18, initial_length:int=3, 
                 max_score_per_apple:int=50, min_score_per_apple:int=10, 
                 max_step_to_apple:int=20):
        #
        #   TODO: DOCSTRING, Initialise game score
        #
        
        # Remember all parameters given on initialisation. Can be used to reset the gameEngine to its initial state.
        self.initParameterList = {
            "board_width": board_width,
            "board_height": board_height, 
            "initial_length": initial_length, 
            "max_score_per_apple": max_score_per_apple, 
            "min_score_per_apple": min_score_per_apple, 
            "max_step_to_apple": max_step_to_apple
        }
        
        #   SET BOARD SIZE
        # 
        # Check the requested size of the board
        if not isinstance(board_width, int) or not isinstance(board_height, int): raise ValueError("Height and width of the game board must be integer!")
        if not (board_width > 1 and board_height > 1): raise ValueError("The board width and height must be bigger than 1!")
        # Set the size of the board
        self.BOARD_SIZE = (board_width, board_height)
        
        # Get a set of tuples with all coordinates of the game board. This is used by self._spawn_apple() to find coordinates on the board, that are not occupied by the snakes body.
        # Create an empty list.
        self.POSITIONS_ON_GAME_BOARD = list()
        # Loop over all x coordinates.
        for x in range(self.BOARD_SIZE[0]):
            # Loop over all y coordinates.
            for y in range(self.BOARD_SIZE[1]):
                # Add the current (x,y) coordinates to the list.
                self.POSITIONS_ON_GAME_BOARD.append((x,y))
        # Convert the list to an unmutable set, so self._spawn_apple() can subtract the set of all coordinates of the snake body from it. This way we get all unoccupied coordinates.
        self.POSITIONS_ON_GAME_BOARD = set(self.POSITIONS_ON_GAME_BOARD)
        
        #   INITIALISE SNAKE
        #
        # Set the initial size and position of the snake
        # The snake may not be shorter than 2. If it's to short, moving with relative directions doesn't work anymore.
        if not isinstance(initial_length, int) or not initial_length >= 2: raise ValueError("The snake must have a length of at least 1 (only integer values allowed).")
        # Initialise position and length of the snake
        # The snake head will be placed in the middle of the first row. The body will be placed of screen.
        # Position of the body of the snake. List of tupels. Every np.array ist one point on the board. The first element is the head. The last element is the tail.
        self.position_snake_body = [ np.array([self._get_max_x()//2, i]) for i in range(0, -initial_length, -1) ]
        # Save the initial length of the snake. Used when generating trainging data for neural networks.
        self.initial_length = initial_length
        
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
        
        # INITIALISE GAME STATE VARIABLES
        #
        # Variable to keep track of the status of the game. False means the snake lives and the game can go on. True means the snake is dead and the game is over.    
        self._snake_dead = False
        # Integer keeping track of the players points
        self.score = 0
        # Step counter. Integer keeping track of how many steps the player needed to get the apple. Used for score computation
        self.step_counter = 0
        # Step counter. How many moves did the game last?
        self.gameDuration_counter = 0
        
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
        # Get a set with all coordinates of the snakes body.
        # Turn the list of numpy arrays into a set of tuples.
        positionOfSnake = set([ tuple(bodyPiece) for bodyPiece in self.position_snake_body ])
        # Subtract the set of all coordinates blocked by the snake from the set of all coordinates on the game board. -> Set of all unoccupied coordinates.
        # Save the result as list, so random.choice can pick one of element of the list.
        availableApplePositions = list( self.POSITIONS_ON_GAME_BOARD - positionOfSnake )
        
        # Is the list of available coordinates empty? In other words does the snake occupy the whole game board?
        if len(availableApplePositions) != 0:
            # If there are still coordinates unoccupied choose one of the at random.
            # Overwrite the current position of the apple with the new position
            self.position_apple = np.array( random.choice(availableApplePositions) )
        else:
            # If there is no place left to put the apple, place it outside of the game board.
            self.position_apple = np.array( self.BOARD_SIZE )
            # Raise a stop iteration to signal, that the game is over. No more places to put the apple.
            raise StopIteration("Game Over: There are no more free coordinates to place the apple. The player must've won the game!")
    
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
        # Update score count (Use score multiplier to make it harder to get points in easy levels)
        self.score += points
        # Reset step counter
        self.step_counter = 0
    
    @property
    def nextAction(self):
        """
        Return the next move the snake should do. This property must be implemented by the subclass.

        Returns
        -------
        Valid Direction (int or numpy.array)
            gameEngine.NORTH, gameEngine.EAST, gameEngine.SOUTH, gameEngine.WEST, gameEngine.LEFT, gameEngine.FORWARD, or gameEngine.RIGHT.

        """     
        raise NotImplementedError("The property gameEngine.nextAction must be implemented by the subclass! See the docstring for details.")
    
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
        # Increase total step counter by one. Used to keep track on how long the game lasted.
        self.gameDuration_counter += 1
        
        # Compute the future position of the snakes head
        future_snake_head_position = self.position_snake_body[0] + direction
        # Add a new element at the beginning of the list for the new position of the snakes head
        self.position_snake_body.insert(0, future_snake_head_position)
        
        # Check if the snake has reached the apple
        collision_with_apple = (future_snake_head_position == self.position_apple).all()
        
        if collision_with_apple == True:
            # Spawn a new apple if the snake has reached the apple
            # Do not delete the tail of the snake. The snake will become longe because of that
            self._update_score()
            self._spawn_apple()
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
    
    def draw(self, SURFACE, origin:tuple=(0,0)):
        """
        Draw the current state of the game in a pygame window. SURFACE must be a pygame display.
        """
        
        # Clear the screen
        background = pygame.Rect( origin, tuple([length*self.BOX_SIZE for length in self.BOARD_SIZE])  )
        pygame.draw.rect(SURFACE, self.BACKGROUND_COLOR, background)
        
        # >>>> RENDER SNAKE AND APPLE
        #
        # Draw the apple
        position_apple = tuple(self.position_apple*self.BOX_SIZE+self.APPLE_MARGIN) + np.array(origin)
        apple = pygame.Rect(position_apple, (self.BOX_SIZE-2*self.APPLE_MARGIN, self.BOX_SIZE-2*self.APPLE_MARGIN))
        pygame.draw.rect(SURFACE, self.APPLE_COLOR, apple, border_radius=self.APPLE_BORDER_RADIUS)
        
        # Draw the snake
        for snake_element in self.position_snake_body:
            # Ignore all elements that are outside if the game board (the head is outside, when the snake's dead)
            if ( snake_element >= np.zeros(2) ).all() and ( snake_element < np.array(self.BOARD_SIZE) ).all():
                position_snake = tuple(snake_element*self.BOX_SIZE+self.SNAKE_MARGIN) + np.array(origin)
                snake = pygame.Rect(position_snake, (self.BOX_SIZE-2*self.SNAKE_MARGIN, self.BOX_SIZE-2*self.SNAKE_MARGIN))
                pygame.draw.rect(SURFACE, self.SNAKE_COLOR, snake, border_radius=self.SNAKE_BORDER_RADIUS)
        
        # So far the body of the snake is a bunch of unconnected boxes. This loop connects them together by drawing new boxes between the segments of the snake.
        for snake_current, snake_next in zip(self.position_snake_body[:-1], self.position_snake_body[1:]):
            # Ignore all elements that are outside if the game board (the head is outside, when the snake's dead)
            if ( snake_current >= np.zeros(2) ).all() and ( snake_current < np.array(self.BOARD_SIZE) ).all():
                direction_snake_tail = (snake_next-snake_current)
                snake_tail_connector = pygame.Rect((0,0), (self.BOX_SIZE-2*self.SNAKE_MARGIN, self.BOX_SIZE-2*self.SNAKE_MARGIN))
                snake_tail_connector.center = snake_current*self.BOX_SIZE + self.BOX_SIZE/2 + direction_snake_tail*self.BOX_SIZE/2 + np.array(origin)
                pygame.draw.rect(SURFACE, self.SNAKE_COLOR, snake_tail_connector)
        #
        # <<<< RENDER SNAKE AND APPLE
        
    def run(self, gui=True, fps:int=15):
        """
        Play a game of snake.

        Parameters
        ----------
        gui: bool, optional
            Should the game be displayed in a window?
        fps : int, optional
            Frames per Second. The default is 15.

        Returns
        -------
        None.

        """
        self.guiEnabled = gui
        # Initialise game engine 
        pygame.init()
        
        # Run the pygame code in a try-catch-block, so pygame can be quit savely if something goes wrong
        try:
            SCREEN_SIZE = tuple([i*self.BOX_SIZE for i in self.BOARD_SIZE])
            FPS = fps
            
            # >>>> SETUP GAME
            #
            if self.guiEnabled == True:
                # Setup the game clock
                frame_rate = pygame.time.Clock()
                
                # Setup display
                SCREEN = pygame.display.set_mode(SCREEN_SIZE)
                
                # Set the caption of the display window
                pygame.display.set_caption(f"Snake")
            #
            # <<<< SETUP GAME
            
            # >>>> START GAME LOOP
            self.running = True
            self.pause = False
            self.won = False
            while self.running:
                               
                self.gameLoop_preHook()
                
                #   MOVING 
                if self.won == self.pause == False:
                    # Move the snake by one step
                    try:
                        self.move(self.nextAction)
                    # Handle StopIteration. This is raised by self._spawn_apple() if there are no more free coordinates to spawn the apple. -> The Game was won.
                    except StopIteration as e:
                        # Remember that the player won the game. This is used to pause the game perminently. Can be used by child class to check if the game was won.
                        self.won = True
                    
                # UPDATE THE SCREEN
                if self.guiEnabled == True:
                    # Clear the screen
                    SCREEN.fill((0,0,0))
                    # Draw the snake game to the pygame display
                    self.draw(SCREEN)
                    # Update display
                    pygame.display.update()
                    # Tick the clock
                    frame_rate.tick(FPS)            
                
            #
            # <<<< END GAME LOOP
            
        # Exit pygame and reraise errors
        except Exception as e:
            # Catch any errors, close the game and reraise the exception
            print("The Game crashed!")
            self.exit_run()
            raise e        
        
        # Exit the game
        self.exit_run()
        
    def gameLoop_preHook(self):
        """
        This function will be called inside the run function at the start of every iteration of the game loop. Subclasses may override this function to customise the game behaviour. The function does nothing by default.

        Returns
        -------
        None.

        """
        pass
    
    def exit_run(self):
        """
        This routine is used to clean up after the game has ended. It's called at the end of the run method.
        """
        # END PYGAME
        pygame.quit()
            
    @property
    def highscoreList(self):
        """
        Get a dictionary with the ten highes scores. Keys are scores, values are player names.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        # Check if high score list was already read from file. Get it if it was not read already.
        if not hasattr(self, "_highscoreList"):
            # Read the highscore file and interpret the yaml file
            try:
                yamlData = self.HIGHSCORE_FILE.read_text()
                # Make the hsighscore list a HighscoreDict object, so the printouts are pretty.
                self._highscoreList = util.HighscoreDict( yaml.safe_load(yamlData) )
                # If the file does not exist, use an empty dictionary.
            except FileNotFoundError:
                # Make the hsighscore list a HighscoreDict object, so the printouts are pretty.
                self._highscoreList = util.HighscoreDict()

        return self._highscoreList
    
    @property
    def highscore(self):
        """
        Return the highest score reached in the game.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        if len(self.highscoreList) == 0: 
            return 0
        else:
            return max(self.highscoreList)
    
    @highscore.setter
    def highscore(self, score):
        """
        Add a new high score to the list of high scores.

        Parameters
        ----------
        score : TYPE, optional
            DESCRIPTION. The default is self.score.

        Returns
        -------
        None.

        """
        # Get currrent high score list
        highscoreList_tmp = self.highscoreList
        
        # Is the current score higher than all previous highscores?
        # Update high score list if so.
        if score > self.highscore:
            highscoreList_tmp.update({score: self.playerName})
        
            # Sort the list of highscores and slice it down to maximal 10 entries in the list.
            sortingKey = sorted(highscoreList_tmp, reverse=True)[:10]
            highscoreList_tmp = util.HighscoreDict({ score:highscoreList_tmp[score] for score in sortingKey })
        
            # Update class attribute and file
            self._highscoreList = highscoreList_tmp
            self.HIGHSCORE_FILE.write_text( yaml.dump(self._highscoreList) )
    
    @property
    def playerName(self):
        """
        Return the name of the player. This property must be implemented by the subclass.

        Returns
        -------
        String
            Player's name.

        """     
        raise NotImplementedError("The property gameEngine.playerName must be implemented by the subclass! See the docstring for details.")
        

#        
#
#   END OF CLASS GAMEENGINE
#
#   
    

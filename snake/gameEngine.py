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
    
    def __init__(self, board_width:int=32, board_height:int=18, box_size:int=BOX_SIZE, initial_length:int=3, max_score_per_apple:int=50, min_score_per_apple:int=10, max_step_to_apple:int=20):
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
        
        # Check the requested size of each drawn block (important for graphics)
        if not isinstance(box_size, int): raise ValueError("The box size must be an integer.")
        if not box_size > 0: raise ValueError("The box size muste be bigger than 0.")
        # The the size of each block the graphics will be build with
        self.BOX_SIZE=box_size
        
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
        
    def run(self, fps:int=15):
        """
        Play a game of snake.

        Parameters
        ----------
        fps : int, optional
            Frames per Second. The default is 15.

        Returns
        -------
        None.

        """
        # Initialise game engine
        pygame.init()
        
        # Run the pygame code in a try-catch-block, so pygame can be quit savely if something goes wrong
        try:
            SCREEN_SIZE = tuple([i*self.BOX_SIZE for i in self.BOARD_SIZE])
            FPS = fps
            
            # >>>> SETUP GAME
            #
            # Setup the game clock
            frame_rate = pygame.time.Clock()
            
            # Setup display
            SCREEN = pygame.display.set_mode(SCREEN_SIZE)
            #
            # <<<< SETUP GAME
            
            # >>>> START GAME LOOP
            # direction_stack is used to memorize which direction the player wants to go
            direction_stack = []
            running = True
            pause = False
            self.won = False
            while running:
                
                # Clear the screen
                SCREEN.fill((0,0,0))
                
                # >>>> HANDLE EVENTS AND KEY PRESSES
                #
                for event in pygame.event.get():
                    
                    # Quit if the user closes the gui.
                    if event.type == pygame.locals.QUIT:
                        running = False
                        break
                    
                    # Did the player press a key?
                    if event.type == pygame.KEYDOWN:
                        # Was the button p pressed? -> Pause the game.
                        if event.key == pygame.K_p: pause = not pause
                        
                        # Check all the arrow keys and save the direction the player wants to go.
                        # This allows the player to push multiple keys by turn and the game will execute each direction turn by turn
                        # Important: Add key presses only to the stack if the game is not paused.
                        if event.key == pygame.K_UP    and not pause: direction_stack.append(NORTH)
                        if event.key == pygame.K_RIGHT and not pause: direction_stack.append(EAST)
                        if event.key == pygame.K_LEFT  and not pause: direction_stack.append(WEST)
                        if event.key == pygame.K_DOWN  and not pause: direction_stack.append(SOUTH)
                
                if self.won:
                    # Do this part only if the player won the game. Skip the rest of the game loop.
                    # This makes sure that the player can look at the completed game until he closes the gui.
                    # Set the caption of the display window with the current game score
                   pygame.display.set_caption(f"Snake - Score: {self.score} - Game Over! You won!")
                   # Skip to the end of the loop and update the screen. Therefore not moving the snake.
                   
                elif pause:
                    # Do this part only if the game is paused. Skip the rest of the game loop.
                    # Set the caption of the display window with the current game score
                    pygame.display.set_caption(f"Snake (PAUSED) - Score: {self.score} - press p to unpause")
                    # Skip to the end of the loop and update the screen. Therefore not moving the snake.
                else:
                    # 
                    # MOVING >>>>>>>>>>>>>>>>>>>>>>>>>>
                    # Do this part only if the game is neither won nor paused. This code block moves the snake.
                    try:
                        # Get the direction the player wants to go in the next move
                        absolute_direction = direction_stack.pop(0)
                        
                        #   CONVERT ABSOLUTE DIRECTIONS TO RELATIVE DIRECTIONS
                        #   This is done, because the neural network should be trained with relative directions and I want to use games played by the user as training data.
                        #
                        # Get the current direction of the snake
                        current_direction = self.position_snake_body[0]-self.position_snake_body[1]
                        # Compute the relative direction with the inner product
                        # This relise on the definition of snake.LEFT, snake.FORWARD and snake.RIGHT to be integers -1, 0 and 1
                        direction = int(absolute_direction[1]*current_direction[0]-absolute_direction[0]*current_direction[1])
                        
                    except IndexError:
                        # If the player didn't push a key don't change the direction
                        direction = FORWARD
                    #
                    # <<<< HANDLE EVENTS AND KEY PRESSES
                    
                    # Move the snake by one step
                    try:
                        self.move(direction)
                    # Handle StopIteration. This is raised by self._spawn_apple() if there are no more free coordinates to spawn the apple. -> The Game was won.
                    except StopIteration as e:
                        print(f"Congratulations! You've won the game with {self.score} points!")
                        # Remember that the player won the game. This is used to pause the game perminently. Can be used by child class to check if the game was won.
                        self.won = True
                        
                    # Set the caption of the display window with the current game score
                    pygame.display.set_caption(f"Snake - Score: {self.score} - press p to pause")
                    
                    #
                    #   MOVING <<<<<<<<<<<<<<<<<<<
                    #
                    
                # UPDATE THE SCREEN
                    
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
    
    def exit_run(self):
        """
        This routine is used to clean up afte the game has ended.
        """
        # END PYGAME
        pygame.quit()
        
        # CHECK FOR NEW HIGHSCORE
        # Get the file with the highscores
        highscoreFile = Path(__file__).parent.parent / "data/highscores.yml"
        # Read the highscore file and interpret the yaml file
        try:
            yamlData = highscoreFile.read_text()
            highscores = yaml.safe_load(yamlData)
        # If the file does not exist, use an empty dictionary.
        except FileNotFoundError:
            highscores = {}
        # Is the current score higher than all previous highscores?
        newHighscore = self.score > max(highscores)
        # Ask the player for his name and put it into the list of highscores, if the player reached an new highscore
        if newHighscore == True:
            playerName = input("Congratulations! You reached a new highscore! Enter player name: ")
            highscores.update({self.score: playerName})
        
        # Sort the list of highscores and slice it down to maximal 10 entries in the list.
        sortingKey = sorted(highscores, reverse=True)[:10]
        highscores = { score:highscores[score] for score in sortingKey }
        highscoreFile.write_text( yaml.dump(highscores) )
        
        # Print highscores
        print(" <<< YOUR SCORE >>> ".center(20))
        print(f"{self.score}".center(20))
        print(" <<< HIGHSCORES >>> ".center(20))
        for score, player in highscores.items():
            print(f"{score: >8}: {player}")

#        
#
#   END OF CLASS SNAKE
#
#   
    
    
if __name__ == "__main__":
    
    # Play Snake
    snake = GameEngine()
    snake.play()
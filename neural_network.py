#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 18:02:18 2021

@author: jonas


This file implements a class that learns to play the game snake with a neural network. The class inherits from the Snake class (that's where the game logic is implemented).

"""

# Import the snake game logic
from snake import Snake, FORWARD, LEFT, RIGHT

# Import Pathlib for reading, writing files
from pathlib import Path
# Import random to do random walks
import random as r
# Store training data as json
import json
# Progress bar
from tqdm import tqdm

# Used for math and neural network
import numpy as np

# Use for neural network
import tflearn as tfl


class NeuralNetwork(Snake):
    """
    This class inherits the game logic from the Snake class and trys to learn ply the game snake with a neural network
    """
    
  
    def __init__(self, *args, **kwargs):
        """
        Initialise the class and call the initialisation of the snake game class.

        Parameters
        ----------
        *args : 
            Passed to Snake class.
        **kwargs :
            Passed to Snake class.

        Returns
        -------
        Instance of the NeuralNetwork class.

        """
        # Initialise parent
        super().__init__(*args, **kwargs)    
        
        # Initialise array. Will hold all game states of one game before they're written to file. Used for generating training data.
        self.game_state_history = []
        
        #
        # Create the layout of the neural network
        #
        # Create the input layer, with 6 input nodes and unknown number of input data points 
        neural_net = tfl.input_data(shape=[None, 6])
        # Create the first hidden layer with 32 nodes
        neural_net = tfl.fully_connected(neural_net, 32)
        # Create the second hidden layer with 32 nodes
        neural_net = tfl.fully_connected(neural_net, 32)
        # Create the output layer with 3 nodes (LEFT, RIGHT, FORWARD)
        neural_net = tfl.fully_connected(neural_net, 3, activation="softmax")
        # Add a regression model to the neural net. Not sure what this step is doing.
        neural_net = tfl.regression(neural_net)
        
        # TODO CREATE MODEL (see http://tflearn.org/tutorials/quickstart.html)
    
    #
    #   >>> PREPROCESS GAME STATES
    #
    def reduce_gameState_dimensions(self, gameState):
        """
        This method takes the state of a game as input and uses some math shit to create an array of numbers between 0 and 1. Each number describes one property of the game state (like how far the walls are away in every direction, ...)
        
        TODO: DOCSTRING

        Parameters
        ----------
        gameState : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        #
        #   TODO: 
        #       - The facial recognition stuff to determine where the body of the snake is placed (left or right?, forward or backward?, close or far away?)
        #       - repairing hamiltonean cycles
        #       - ...?
        #   DONE:
        #       - Relative distances (distance to walls, distance to body (can the body move out of the way in time?), distance to apple )
        
        
        #
        #   Get some important stats about the game state
        #
        # Get the position of the snakes head
        SNAKE_HEAD = np.array(gameState["snake_position"][0])
        # Get the size of the board
        BOARD_SIZE = np.array(gameState["BOARD_SIZE"])
        # Get the direction the snake is currently facing
        FORWARD_ABSOLUTE = SNAKE_HEAD - np.array(gameState["snake_position"][1])
        # Rotate the direction the snake is currently facing by 90° clockwise
        # This yields the vector facing to the right of the snake
        RIGHT_ABSOLUTE = FORWARD_ABSOLUTE @ np.array([ [0, 1], [-1, 0] ])
        # Get the transformation matrix to convert absolute normalised vectors into vectors relative to the snakes travelling direction
        # This is done by writing the basis vectors of the new basis columnwise in the matrix.
        ABSOLUTE_TO_RELATIVE_DIRECTION= np.array([ FORWARD_ABSOLUTE, RIGHT_ABSOLUTE ]).T
        
        # Get the normalised position of the snake's head
        # Normalise with the board size. This way the neural net knows where the walls are. If one component is either 0 or 1, it hot a wall.
        snakeHeadX, snakeHeadY = SNAKE_HEAD / BOARD_SIZE
        
        #
        # >>> DISTANCE TO WALL OR BODY
        #
        # Get the distance to the nearest part of the snake body
        # If the body is not in the way, use the distance to the wall
        
        # Get the relative and normalised position of the snakes body and view them relative to the direction of travel
        relativeSnakeBody = [ ( ( SNAKE_HEAD - np.array(body) ) / BOARD_SIZE ) @ ABSOLUTE_TO_RELATIVE_DIRECTION 
                              for body in gameState["snake_position"] ]
        # Make a list of the points on the wall the snake can run into, when walking along a straight line (relative positions).
        relativeWallPosition = [ np.array(0         , snakeHeadY),
                                 np.array(snakeHeadX, 0         ),
                                 np.array(1         , snakeHeadY),
                                 np.array(snakeHeadX, 1         ) ]
        # Make a list of all things that the snake might run into (relative positions of the snake body and the walls)
        relativeSnakeObstacles = relativeSnakeBody + relativeWallPosition
        
        # Get the distance to the nearest obstacle in the directions FORWARD, RIGHT and LEFT
        # Get all distances to the the obstacles in front of the snake
        relativeDistanceObstacleForward = [ # Get eucledean distance (Because of relative directions the second component is 0.)
                                            pos[0]
                                            # Loop over all obstacles
                                            for pos in relativeSnakeObstacles
                                            # Use only obstacles that are in the FORWARD direction ([1,0]).
                                            if ( np.linalg.norm(pos) == np.array([1,0]) ).all() ]
        # Get the smallest distance in front of the snake
        relativeDistanceObstacleForward = min(relativeDistanceObstacleForward)
        
        # Get all distances to the the obstacles to the right of the snake
        relativeDistanceObstacleRight = [ # Get eucledean distance (Because of relative directions the first component is 0.)
                                          pos[1]
                                          # Loop over all obstacles
                                          for pos in relativeSnakeObstacles
                                          # Use only obstacles that are in the RIGHT direction ([0,1]).
                                          if ( np.linalg.norm(pos) == np.array([0,1]) ).all() ]
        # Get the smallest distance to the right
        relativeDistanceObstacleRight = min(relativeDistanceObstacleRight)
        
        # Get all distances to the the obstacles to the right of the snake
        relativeDistanceObstacleLeft = [ # Get eucledean distance (Because of relative directions the first component is 0 and the second is always negative.)
                                          -pos[1]
                                          # Loop over all obstacles
                                          for pos in relativeSnakeObstacles
                                          # Use only obstacles that are in the LEFT direction ([0,-1]).
                                          if ( np.linalg.norm(pos) == np.array([0,-1]) ).all() ]
        # Get the smallest distance to the left
        relativeDistanceObstacleLeft = min(relativeDistanceObstacleLeft)
        #
        # <<< DISTANCE TO WALL OR BODY DONE
        #
        
        # Get the normalised difference vector from the snakes head to the apple. This way the snake knows where the apple is and how far away it is.
        absoluteDirectionApple = ( np.array(gameState["apple_position"]) - SNAKE_HEAD ) / BOARD_SIZE
        # Transform the absolute vector into a vector relative to the snakes travelling direction. 
        directionAppleX, directionAppleY = absoluteDirectionApple @ ABSOLUTE_TO_RELATIVE_DIRECTION
        # Get the normalised distance from the snake's head to the apple
        distanceApple = np.sqrt(directionAppleX**2 + directionAppleY**2)
        
        # Return 1D numpy array to describe the state of the game (with reduced dimensions)
        return np.array([ directionAppleX, directionAppleY, distanceApple, 
                          relativeDistanceObstacleForward, relativeDistanceObstacleRight, relativeDistanceObstacleLeft
                        ])
    
    def evaluate_action(self, gameState):
        """
        This function takes in the current gameState and the planned action (the action is part of the gameState dictionary) to create a score. This score determines how good the move was.
        
        TODO: DOCSTRING

        Parameters
        ----------
        gameState : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        
        # This variable contains the value of this move. The function will change the variable, depending on how good the move is and return the value.
        GAMESCORE = 0.1
        
        
        
        # TODO: Predict the next gameState by executing the action.
        
        
        
        # Introduce first metric of success. Just check if the snake is getting closer to the apple
        #
        # 1. Get currenct distance to apple
        #
        # Get the vector from the snakes head to the apple
        directionToApple = np.array(gameState["apple_position"]) - np.array(gameState["snake_position"][0])
        # Get the current distance between the snakes head and the apple
        currentDistanceToApple = np.sqrt(sum(directionToApple**2))
        #
        # 2. Get future distance to apple
        #    Predict the distance from the snakes head to the apple after the action
        #
        # Get the direction the snake is currently facing
        current_direction = np.array(gameState["snake_position"][0]) - np.array(gameState["snake_position"][1])
        # CONVERT RELATIVE ACTION (LEFT; RIGHT; FORWARD) TO ABSOLUTE DIRECTIONS (VECTOR)
        # Define a rotation angle based on the relative direction (LEFT=-90°, FORWARD=0°, RIGHT=+90°)
        rotation_angle = gameState["next_action"]*np.pi/2
        # Rotate the current absolute direction with a rotation matrix. Matrix will rotate the current_direction by rotation_angle radians.
        absoluteAction = current_direction @ np.array([ [  int(np.cos(rotation_angle)), int(np.sin(rotation_angle))], 
                                                        [ -int(np.sin(rotation_angle)), int(np.cos(rotation_angle))] ])
        # Get the new direction to the apple by adding the absolute action vector (is the snake walking NORTH, SOUTH, EAST or WEST) on to the direction to the apple vector
        newDirectionToApple = absoluteAction + directionToApple
        # Get the euclidean distance
        newDistanceToApple = np.sqrt(sum(newDirectionToApple**2))
        #
        # 3. Compare the old and new distance
        #
        # Give the snake 0.3 points, if it got closer to the apple
        if newDistanceToApple > currentDistanceToApple: GAMESCORE += 0.3
        

        # Check if the snake found the apple: Set the gamescore to 1, if the snake ate the apple
        if newDistanceToApple == 0: GAMESCORE = 1
        
        
        
        # Check if the move was deadly. Reset the snakes points to 0, if dead.
        if gameState["next_action_deadly"] == True: GAMESCORE = 0



        # Return single number between 0 and 1. Describes the value of the move. 0: bad, 1: good.
        return GAMESCORE
    
    def preprocess_gameStates(self, gameStates):
        """
        Convert a single game state into a numpy array that can be inputed into a neural network. This function expects the game state as a dictionary of a specific form. Therefore this method should not be called directly. There are other methods, that create the right formatted dictionary and call this method.
        So far these functions are:
            - preprocess_trainingDataFile
            
        The idea of the preprocessing is to reduce the dimensions of the game state.
        
        TODO: DOCSTRING

        Parameters
        ----------
        gameStates : TYPE
            DESCRIPTION.

        Returns
        -------
        3 numpy arrays with
        1. arrays describing the state of the game (reduced dimensions, see self.reduce_gameState_dimensions).
        2. arrays describing the move the snake will take in the next step ([1,0,0]=LEFT, [0,1,0]=FORWARD, [0,0,1]=RIGHT).
        3. a score describing how good the move was (see self.evaluate_gameStates).

        """
        
        # Create a numpy array describing the state of the game
        input_state = np.array([ self.reduce_gameState_dimensions(state) for state in gameStates ])
        
        # Create labels for the game state. The labels are the direction the snake moved to.
        # LEFT    = [ 1 0 0 ]
        # FORWARD = [ 0 1 0 ]
        # RIGHT   = [ 0 0 1 ]
        output_action = np.array([ [ 1 if state["next_action"] == LEFT    else 0, 
                                     1 if state["next_action"] == FORWARD else 0,
                                     1 if state["next_action"] == RIGHT   else 0  ]
                                   for state in gameStates ])
        
        # Create an array with scores for every move in output_action. The score determines how good this move is.
        action_value = np.array([ self.evaluate_action(state) for state in gameStates ])
        
        # Return the preprocessed information
        return input_state, output_action, action_value
    
    def preprocess_trainingDataFile(self, path_to_files):
        """
        Convert the game states generated by generate_human_training_data() and generate_random_training_data() into a numpy arrays that can be put into the neueral network.
        
        TODO: DOCSTRING

        Parameters
        ----------
        gameStates : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        
        # Get a list of genertors. For every element of path_to_files exists a generator with all json-files in that directory.
        files = [ Path(folder).glob("*.json") for folder in path_to_files ]
        # Flatten the list
        files = [ file for file_glob in files for file in file_glob ]

        # Read every file and convert the json format into a python object.
        gameStates = ( json.loads(file.read_text()) for file 
                       in tqdm(files, desc="Read training data", unit=" files") )
        # Flatten the list, because every file contains a list of game states.
        gameStates = [ state for game in gameStates for state in game ]

        # Input the list of game states into the preprocessing routine
        return self.preprocess_gameStates(gameStates)

    #
    #   <<< PREPROCESS GAME STATES
    #
        
    #
    #   >>> GENERATE TRAINING DATA
    #
    def generate_human_training_data(self, save_gamestate_to:Path, *args, **kwargs):
        """
        Wrapper for Snake.play() method. This is used to generate training data from the games played by a human.
        This wrapper saves the location of a file, where the gamestates will be saved after every move and then it calls it's play() method (inherited from Snake class).
        The NeuralNetwork method move() uses the file path to save the gamestate. 

        Parameters
        ----------
        save_gamestate_to : Path
            Directory where to save the gamestates?
        *args : TYPE
            Some shit passed to self.play().
        **kwargs : TYPE
            Some shit passed to self.play().

        Returns
        -------
        None.

        """
        # Create the empty file to store the game states in
        save_gamestate_to = Path(save_gamestate_to)
        
        # Wipe the variable storing a list of all previous game states
        # It will be refilled during the executiion of self.play()
        self.game_state_history = []
        
        # Play the game
        self.play(*args, **kwargs)
        
        # Write all previous states of the game to json-file
        save_gamestate_to.write_text(json.dumps(self.game_state_history)+"\n")
        
        
    def move(self, action, *args, **kwargs):
        """
        Wrapper around the parents move() method. It saves the game state to a file, when moving the snake

        Parameters
        ----------
        save_gamestate_to : Path
            DESCRIPTION.
        *args, **kwargs : TYPE
            Shit passed to Snake.move().

        Returns
        -------
        None.

        """
        # Check if the action the snake should perform is a relative direction
        if not isinstance(action, int) or not action in [LEFT, FORWARD, RIGHT]:
            # Check if the parameter direction is a valid relative direction. Valid relative directions are the ints LEFT, RIGHT and FORWARD (defined above the class snake.Snake.)
            raise ValueError("Wrong value passed for parameter 'action'. neural_network.NeuralNetwork.move() expects the directions Snake.LEFT, Snake.FORWARD and Snake.RIGHT.")
        
        # GET PREV. GAME STATE
        # Get the state of the game BEFORE moving the snake. Save also the intended walking direction
        # Convert numpy arrays of numpy ints to tuples for python ints so they can be saved as in json
        prev_game_state = {"snake_position": [ elem.tolist() for elem in self.position_snake_body ],
                           "apple_position": self.position_apple.tolist(),
                           "board_size": self.BOARD_SIZE,
                           "steps_walked_since_last_apple": self.step_counter,
                           "next_action": action}
        
        # Move the snake
        super().move(action, *args, **kwargs)
        
        # Was the move deadly? Append this information to the game_state
        prev_game_state["next_action_deadly"] = self._snake_dead
        
        # Save the game state
        self.game_state_history.append(prev_game_state)
            
        
    def generate_random_training_data(self, save_to:Path, training_games:int=1000, maximal_steps_per_game:int=500):
        """
        Generate training data by random walking a bunch of games. The data is not processed in anyway. It's just the raw game output

        Parameters
        ----------
        save_to : pathlib.Path
            Empty directory for saving the unpreprocessed training data. String will be converted to pathlib.Path object. Non existing directory will be created.
        training_games : int, optional
            How many games should the programm play? The default is 100.
        maximal_steps_per_game : int, optional
            After how many steps should the programm abort a training game? The default is 100.

        Returns
        -------
        Exit status (0=OK).

        """
        
        # Convert directory to Path object
        training_directory = Path(save_to)
        # Create the directory if it doesn't exist
        training_directory.mkdir(parents=True, exist_ok=True)
        
        # Create progress bar for a loop that plays snake games with random walks
        with tqdm(iterable=range(training_games),
                         unit=" games", desc="Playing Random",
                         position=1, leave=False) as outer_progressbar:
            # Start playing snake games with random walk
            for game_number in range(training_games):
                # Convert game number to easy readable string
                game_number_string = "0"*(len(str(training_games))-1-len(str(game_number))) + str(game_number)
                
                # Generate a file name. This random walk will be saved to that file
                game_file = training_directory/("randomGame_"+  game_number_string + ".json")
                
                # Update the outer progress bar (this progressbar keeps track of the whole process and not just one game)
                outer_progressbar.update()
                
                # Reset the memory holding the whole history of the game
                self.game_state_history = []
                
                # Play the game and add a progressbar with tqdm
                for _ in tqdm(iterable=range(maximal_steps_per_game),
                             desc=f"Game {game_number_string}", unit=" steps",
                             position=0):
                    # Generate a random walking direction
                    action = r.choice([LEFT, FORWARD, RIGHT])

                    # Move the snake
                    self.move(action)
                    
                    # End the game if the player died
                    if self._snake_dead == True:
                        break
                    
                    # Redraw outer progress bar (this progressbar keeps track of the whole process and not just one game)
                    outer_progressbar.refresh()
                
                # Write all previous states of the game to json-file
                game_file.write_text(json.dumps(self.game_state_history)+"\n")
                
            
                # Rerun the constructor of the Snake class. This resets the state of the game. 
                # Make sure to pass all arguments, if you're not using the default settings!
                super().__init__(board_width=self.BOARD_SIZE[0], board_height=self.BOARD_SIZE[1], box_size=self.BOX_SIZE, 
                                 initial_length=self.initial_length, max_score_per_apple=self.MAXIMAL_SCORE_PER_APPLE,
                                 min_score_per_apple=self.MINIMAL_SCORE_PER_APPLE, max_step_to_apple=self.MAXIMAL_STEP_COUNT)
        
        # Return exit status
        return 0
    
    #
    #   <<< GENERATE TRAINING DATA
    #
    
if __name__ == "__main__":
    
    import time
    
    # Play Snake
    snake = NeuralNetwork()
    
    # Start a game of snake
    save_games_to = Path(f"/home/jonas/code/python/snake/training_data/human_walk/humanGame_{int(time.time())}.json")
    snake.generate_human_training_data(save_gamestate_to=save_games_to)
    #snake.preprocess_trainingDataFile(["/home/jonas/code/python/snake/training_data/human_walk"])
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
        
        # Initialise array. Will hold all game states of one game before they're written to file.
        self.game_state_history = []
    
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
        #       - Relative distances (distance to walls, distance to body (can the body move out of the way in time?), distance to apple )
        #       - The facial recognition stuff to determine where the body of the snake is placed (left or right?, forward or backward?, close or far away?)
        #       - repairing hamiltonean cycles
        #       - ...?
        #
        
        # TODO: return 1D numpy array
        return [None]
    
    def evaluate_gameState(self, gameState_current, gameState_next):
        """
        This function takes in the current gameState and the following gameState to create a score. This score determines how good the move was.
        
        TODO: DOCSTRING

        Parameters
        ----------
        gameState : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        # TODO, return single number between 0 and 1
        return None
    
    def preprocess_gameStates(self, gameStates):
        """
        Convert a single game state into a numpy array that can be inputed into a neural network. This function expects the game state as a dictionary of a specific form. Therefore this method should not be called directly. There are other methods, that create the right formatted dictionary and call this method.
        So far these functions are:
            - preprocess_trainingDataFile
            
        The idea of the preprocessing is to reduce the dimensions of the game state.
        
        TODO: DOCSTRING

        Parameters
        ----------
        gameState : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

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
        # The first step is to extract for every game state the following state of the game.
        # If the snake dies with the next move, then there is no next game state. In this case put None in the generator.
        # At this point it's very important, that only complete games are used. If the snake didn't die, this generator comprehension can't determine where one game begins and ends in the flat list gameStates.
        scorable_gameStates = ( ( current_state,
                                  # Put here the next state of the game or None, if the game is over.
                                  None if current_state["next_action_deadly"] == True else next_state ) 
                                # Loop over all game states
                                for current_state, next_state in zip(gameStates, gameStates[1:]+[None]) )
        # Feed scorable_gameStates into a function that computes how good the game move was.
        action_value = np.array([ [self.evaluate_gameState(current_state, next_state)] 
                                  for current_state, next_state in scorable_gameStates ])
        
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
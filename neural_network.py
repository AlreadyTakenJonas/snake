#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 18:02:18 2021

@author: jonas


This file implements a class that learns to play the game snake with a neural network. The class inherits from the Snake class (that's where the game logic is implemented).

"""

# Import the snake game logic
from snake import Snake, NORTH, SOUTH, EAST, WEST, FORWARD, LEFT, RIGHT

# Import Pathlib for reading, writing files
from pathlib import Path
# Import random to do random walks
import random as r
# Store training data as json
import json
# Progress bar
from tqdm import tqdm
# Math and shit
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
        
        super().__init__(*args, **kwargs)    
            
    def move(self, save_gamestate_to:Path, *args, **kwargs):
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
        
        # Convert the prev_game_state into a json-foramt
        game_state_json = json.dumps(prev_game_state)
        # Write the state of the game to file
        with save_gamestate_to.open("a") as f:
            f.write(game_state_json+"\n")
            
        
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
                game_file = training_directory/("randomGame_"+  game_number_string + ".rsg")
                # Create an empty and overwrite any existing file
                game_file.write_text("")
                
                # Update the outer progress bar (this progressbar keeps track of the whole process and not just one game)
                outer_progressbar.update()
                
                # Play the game and add a progressbar with tqdm
                for _ in tqdm(iterable=range(maximal_steps_per_game),
                             desc=f"Game {game_number_string}", unit=" steps",
                             position=0):
                    # Generate a random walking direction
                    action = r.choice([LEFT, FORWARD, RIGHT])
                    # Get the state of the game BEFORE moving the snake. Save also the intended walking direction
                    # Convert numpy arrays of numpy ints to tuples for python ints so they can be saved as in json
                    #prev_game_state = {"snake_position": [ elem.tolist() for elem in self.position_snake_body ],
                    #                   "apple_position": self.position_apple.tolist(),
                    #                   "board_size": self.BOARD_SIZE,
                    #                   "steps_walked_since_last_apple": self.step_counter,
                   #                    "next_action": action}
                    # Move the snake
                    self.move(action)
                    # Was the move deadly? Append this information to the game_state
                    #prev_game_state["next_action_deadly"] = self._snake_dead
                    
                    # Convert the prev_game_state into a json-foramt
                    #game_state_json = json.dumps(prev_game_state)
                    # Write the state of the game to file
                    #with game_file.open("a") as f:
                    #    f.write(game_state_json+"\n")
                    
                    # End the game if the player died
                    if self._snake_dead == True:
                        break
                    
                    # Redraw outer progress bar (this progressbar keeps track of the whole process and not just one game)
                    outer_progressbar.refresh()
                
            
                # Rerun the constructor of the Snake class. This resets the state of the game. 
                # Make sure to pass all arguments, if you're not using the default settings!
                super().__init__(board_width=self.BOARD_SIZE[0], board_height=self.BOARD_SIZE[1], box_size=self.BOX_SIZE, 
                                 initial_length=self.initial_length, max_score_per_apple=self.MAXIMAL_SCORE_PER_APPLE,
                                 min_score_per_apple=self.MINIMAL_SCORE_PER_APPLE, max_step_to_apple=self.MAXIMAL_STEP_COUNT)
        
        # Return exit status
        return 0
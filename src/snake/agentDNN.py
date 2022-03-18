#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 17:50:36 2022

@author: jonas
"""

from snake.gameEngine import GameEngine, LEFT, FORWARD, RIGHT
import tensorflow as tf
import tflearn
import numpy as np
import pygame
from tqdm import tqdm

class AgentDNN(GameEngine):
    """
    This Agent decides its movements with a deep neural network. This class contains methods to manipulate and manage the corresponding deep neural net.
    """
    
    def __init__(self, dnnConstructor, preprocessor, *args, **kwargs):
        """
        Construct the neural network and call the constructor of the Game Engine.
        
        Notes on dnnConstructor and preprocessor: Each move preprocessor gets called with the instance of this class as argument. It must return a numpy array, that can be passed to the tflearn.DNN.predict function. The DNN must have three output neurons.

        Parameters
        ----------
        dnnConstructor : callable
            Callable returning an instance of tflearn.dnn class.
        preprocessor : callable
            Callable performing the preprocessing of the game state before feeding the game state into the DNN.
        *args : positional arguments
            Passed to game engine constructor.
        **kwargs : optional arguments
            Passed to game engine constructor.

        Returns
        -------
        None.

        """
        # Create the deep neural network by calling the dnnConstructor
        with self._brain.session:
            self._brain = dnnConstructor()
            # Did the callable return a deep neural network?
            assert isinstance(self._brain, tflearn.DNN), "dnnConstructor must return an instance of tflearn.DNN!"
        
        # Saving the prerpocessing routine as attribute
        self.PREPROCESS = preprocessor
        
        # Call constructor of game engine
        super().__init__(*args, **kwargs)
    
    def run(self, iterations=1, *args, **kwargs):
        # Create lists to keep track of stats for every game
        gameScores = list()
        gameWon = list()
        gameDuration = list()
        
        # Run as many games as iterations required
        for _ in tqdm(range(iterations)):
            # Run the game
            super().run(*args, **kwargs)
            
            # Remember stats of the game
            gameScores.append(self.score)
            gameWon.append(self.won)
            gameDuration.append(self.gameDuration_counter)
            
            # Reset the gameEngine to the state it had before running the game
            super().__init__(**self.initParameterList)
        
        # Average the game stats
        averageGameScore = np.mean(gameScores)
        averageGameWon = np.mean(gameWon)
        averageGameDuration = np.mean(gameDuration)
        
        # Return the game stats
        return averageGameScore, averageGameWon, averageGameDuration
    
    def gameLoop_preHook(self):
        """
        This function will be called before every iteration of the game loop. Handle key press events and customises caption of the game window.
        """
        # Are we running with gui activated? -> Give control to the player.
        if self.guiEnabled == True:    
            # >>>> HANDLE EVENTS AND KEY PRESSES
            #
            for event in pygame.event.get():
                # Quit if the user closes the gui.
                if event.type == pygame.locals.QUIT:
                    self.running = False
                    break
                # Did the player press a key?
                # Was the button p pressed? -> Pause the game.
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p: self.pause = not self.pause
                
                
            # Modify caption of the window
            if self.won:
                # Do this part only if the player won the game.
                # This makes sure that the player can look at the completed game until he closes the gui.
                # Set the caption of the display window with the current game score
                pygame.display.set_caption(f"Snake - Score: {self.score} - Game Over! You won!")
                   
            elif self.pause:
                # Do this part only if the game is paused.
                # Set the caption of the display window with the current game score
                pygame.display.set_caption(f"Snake (PAUSED) - Score: {self.score} - press p to unpause")
            
            else:
                # Do this part if the game is neither paused nor won.
                # Set the caption of the display window with the current game score
                pygame.display.set_caption(f"Snake - Score: {self.score} - press p to pause")
        
        # Is the game running without gui? -> End the game loop as soon as snake is dead.
        else:
            if self._snake_dead == True: self.running = False
        
    def loadBrainFromFile(self, path, *args, **kwargs):
        """
        Load weights of preexisting neural network from file.

        Parameters
        ----------
        path : string / Path object
            Path to saved DNN model.
        *args : positional arguments
            Passed on to tflearn.DNN.load.
        **kwargs : optional arguments
            Passed on to tflearn.DNN.load.

        Returns
        -------
        None.

        """
        # Load the weights of the DNN from file
        with self._brain.session:
            self._brain.load(str(path), *args, **kwargs)
            
    def saveBrainToFile(self, path, *args, **kwargs):
        """
        Save the weights of the DNN to file.

        Parameters
        ----------
        path : string / Path object
            Path to save DNN model to.
        *args : positional arguments
            Passed on to tflearn.DNN.load.
        **kwargs : optional arguments
            Passed on to tflearn.DNN.load.

        Returns
        -------
        None.

        """
        # Save the weights of the DNN to file
        with self._brain.session:
            self._brain.save(str(path), *args, **kwargs)
        
    def __getitem__(self, index):
        
        # Write docstring
        # Write __setitem__
        # Write cache that knows, if __setitem__ changed something in the DNN.
        
        if isinstance(index, int) == False: raise TypeError("Index must be integer!")
        with self._brain.session:
            # Loop over dictionary with all trainable tensorflow variables (tensors with weights and tensors with biases)
            # Keys are the length (number of elements) of the tensor (saved as value of key) plus the length of all previous tensors in the dictionary.
            # This loop finds the tensorflow variable ("var") containing the element the given index is associated with.
            # Which tensor contains the element the given index is referring to?
            for length, var in self.brainMap.items():
                # Is the smaller than the biggest index ("length") mapped to the tensorflow variable "tensor"?
                # Break the loop if it is.
                if index < length: break
                         
            # The loop ran over all key-value-pairs and didn't found a matching value.
            # The index must be out of range.
            # Raise an IndexError to make the object iterable
            else:
                raise IndexError("Index out of range.")
    
        # Get the tensor of the tensorflow variable
        tensor = tflearn.variables.get_value(var)
    
        # Subtract the number of elements of all tensors in the list before this one.
        # In other words. Take the index of an element of the DNN (given as parameter) and convert it to an index of the tensor found by the for loop.
        # Which element of the tensor is meant by the given index?
        # Length is the sum of the number of elements in all tensors that are listed in the dictionary before and including this one. Add the product of the dimensions to only subtract the previous tensor's length.
        index = index - length + np.prod(tensor.shape)
        
        # Is the tensor a vector with biases?
        if tensor.ndim is 1:
            # Select one element from the vector.
            item = tensor[index]
        # Is the tensor a matrix with weights?
        elif tensor.ndim is 2:
            # Get the row and column in the selected tensor corresponding to the given index.
            # i is the first index of the matrix element, j is the second index of the matrix element.
            j = index % tensor.shape[1]
            i = int( (index - j)/tensor.shape[1] )
            # Select the element from the matrix.
            item = tensor[i][j]
        # Something went wrong.
        else:
            raise NotImplementedError(f"Can't handle tensors with {tensor.ndim} dimensions. Only support for 1 or 2 dimensions.")
        
        # Return the selected element.
        return item
    
    def __setitem__(self, index, value):
        pass
    
    @property
    def brainMap(self):
        """
        Get a dictionary mapping an index to a tensorflow variable of the DNN.
        All indices smaller than the key of the dictionary should be mapped on to the tensorflow variable (a tensor) stored in the corresponding value.
        The current key is the sum of the previous key and the last index of the key's value.
        
        Parameters
        ----------
        None.

        Returns
        -------
        Dictionary mapping indices to tensorflow variables of the DNN.
        """
        with self._brain.session:
            # Create the brainMap if it does not exist yet.
            if not hasattr(self, "_brainMap"):
                brainMap = dict()
                maxIndexForVariable = 0
                # Loop over all trainable tensorflow variables (in the scope of the DNN of this instance).
                for var in tflearn.variables.get_all_trainable_variable():
                    # Get the tensor of the current tensorflow variable
                    tensor = tflearn.variables.get_value(var)
                    # Add the length of the current tensor to the running counter
                    maxIndexForVariable = maxIndexForVariable + np.prod(tensor.shape)
                    # Add key value pair to dictionary.
                    # The key is the running counter (sum of lengths of all tensors so far).
                    # The value is the tensorflow variable with the weights or biases of one DNN layer.
                    brain[maxIndexForVariable] = var                   
                # Make brainMap an attribute of the instance.
                self._brainMap = brainMap
            
            # Return the brainMap
            return self._brainMap
            
    @property
    def nextAction(self):
        """
        Use the neural network in _brain and the preprocessing routine PREPROCESS to predict the best possible move.

        Returns
        -------
        nextMove : int
            Move the snake will do: LEFT, FORWARD or RIGHT.

        """
        # Get a 1D-vector representation (np.array) of the game state
        gameState = self.PREPROCESS(self)
        # Input the game state into the neural net and let it compute how good the possible moves LEFT, FORWARD and RIGHT are
        nextMovePropabilities  = self._brain.predict(gameState)
        
        # Pick the move with the highest score / pick the best move according to the neural net.
        possibleMoves = [LEFT, FORWARD, RIGHT]
        nextMove = possibleMoves[ np.argmax(nextMovePropabilities) ]

        # Return the move
        return nextMove
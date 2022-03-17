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
        # Get a graph object to have a seperate namespace for the tf variables
        self.TENSORFLOW_NAMESPACE = tf.Graph()
        
        # Create the deep neural network by calling the dnnConstructor
        with self.TENSORFLOW_NAMESPACE.as_default():
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
        with self.TENSORFLOW_NAMESPACE.as_default():
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
        with self.TENSORFLOW_NAMESPACE.as_default():
            self._brain.save(str(path), *args, **kwargs)
        
    def __getitem__(self, index):
        if isinstance(index, int) == False: raise TypeError("Index must be integer!")
        with self.TENSORFLOW_NAMESPACE.as_default():
            # Get all trainable tensorflow variables
            # Return one weight or bias of one tensorflow variable depending on the given index
            # This function should map a unique index to every weight and bias of the neural network in self._brain
            # Implement raise StopIteration() to make the object iterable. 
            raise NotImplementedError()
    
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
            if not hasattr(self, "_brainMap"):
                brainMap = dict()
                maxIndexForVariable = 0
                for var in tflearn.variables.get_all_trainable_variable():
                    maxIndexForVariable = maxIndexForVariable + np.prod(var.shape)
                    brain[maxIndexForVariable] = var                   
                self._brainMap = brainMap
        
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
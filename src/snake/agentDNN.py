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
    def nextAction(self):
        """
        Use the neural network in _brain and the preprocessing routine PREPROCESS to predict the best possible move.

        Returns
        -------
        nextMove : int
            Move the snake will do: LEFT, FORWARD or RIGHT.

        """
        # Get a 1D-vector representation (np.array) of the game state
        gameState = self.PREPROCESS()
        # Input the game state into the neural net and let it compute how good the possible moves LEFT, FORWARD and RIGHT are
        nextMovePropabilities  = self._brain.predict(gameState)
        
        # Pick the move with the highest score / pick the best move according to the neural net.
        possibleMoves = [LEFT, FORWARD, RIGHT]
        nextMove = possibleMoves[ np.argmax(nextMovePropabilities) ]
        
        # Return the move
        return nextMove
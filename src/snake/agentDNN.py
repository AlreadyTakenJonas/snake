#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 17:50:36 2022

@author: jonas
"""

from snake.gameEngine import GameEngine
import tensorflow as tf
import tflearn

class AgentDNN(GameEngine):
    """
    This Agent decides its movements with a deep neural network. This class contains methods to manipulate and manage the corresponding deep neural net.
    """
    
    def __init__(self, dnnConstructor, preprocessor, *args, **kwargs):
        """
        Construct the neural network and call the constructor of the Game Engine.

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
        # Do a dimension reduction on the game state : REDUCEDGAMESTATE = self.PREPROCESS( GAMESTATE )
        # self._brain.predict( REDUCEDGAMESTATE ) -> which way to go -> Return this value.
        raise NotImplementedError()
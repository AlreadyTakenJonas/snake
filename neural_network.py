#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 18:02:18 2021

@author: jonas


This file implements a class that learns to play the game snake with a neural network. The class inherits from the Snake class (that's where the game logic is implemented).

"""

# Import the snake game logic
import snake

class NeuralNetwork(snake.Snake):
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
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  5 13:33:32 2022

This file implements some useful code snippets used by the other modules.

@author: jonas
"""

from yaml import YAMLObject

class HighscoreDict(dict, YAMLObject):
    """
    This class inherits from the built-in dictionary and changes the behaviour of the string __str__-method to get a nice print out of the high score list. It also implements the possibility to assign __str__ a new callable object. It also implements support for yaml.dump. The class will be dumped as a built-in dictionary. Recovering the HighscoreDict from a yaml file will generate a built-in dictionary.
    """
    def _toString(self):
        # Sort the list of highscores.
        sortingKey = sorted(self, reverse=True)[:10]
        highscoreList = { score:self[score] for score in sortingKey }
        # Convert the highscore list into a nice string.
        output  = " <<< HIGHSCORES >>> ".center(20) + "\n"
        output += "\n".join([ f"{score: >8}: {player}" for score, player in highscoreList.items() ])
        return output
    @property
    def __str__(self):
        return self._toString
    @__str__.setter
    def __str__(self, func):
        if callable(func):
            self._toString = func
        else:
            raise TypeError("Only callable objects can be assigned to HighscoreList.__str__!")
    
    # Make the class behave like a built-in dictionary, if it gets dumped by yaml.
    # Careful! Loading the dumped class will generate a dictionary, not a HighscoreDict!
    yaml_tag = ""
    @classmethod
    def to_yaml(cls, dumper, data): return dumper.represent_data( dict(data) )
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 17:47:43 2022

@author: jonas
"""


import snake.gameEngine as gameEngine
import pygame

class AgentHuman(gameEngine.GameEngine):
    
    # Use this list to remeber the keys the player pressed.
    direction_stack = []
    
    @property
    def nextAction(self):
        """
        Return the action the player will do next.
        """
        try:
            # Get the next action from the direction stack
            return self.direction_stack.pop(0)
        except IndexError:
            # If the player didn't push a key don't change the direction
            return gameEngine.FORWARD
    
    def gameLoop_preHook(self):
        """
        This function will be called before every iteration of the game loop. Handle key press events and customises caption of the game window.
        """
        # >>>> HANDLE EVENTS AND KEY PRESSES
        #
        for event in pygame.event.get():
            
            # Quit if the user closes the gui.
            if event.type == pygame.locals.QUIT:
                self.running = False
                break
            
            # Did the player press a key?
            if event.type == pygame.KEYDOWN:
                # Was the button p pressed? -> Pause the game.
                if event.key == pygame.K_p: self.pause = not self.pause
                
                # Check all the arrow keys and save the direction the player wants to go.
                # This allows the player to push multiple keys by turn and the game will execute each direction turn by turn
                # Important: Add key presses only to the stack if the game is not paused.
                if event.key == pygame.K_UP    and not self.pause: self.direction_stack.append(gameEngine.NORTH)
                if event.key == pygame.K_RIGHT and not self.pause: self.direction_stack.append(gameEngine.EAST)
                if event.key == pygame.K_LEFT  and not self.pause: self.direction_stack.append(gameEngine.WEST)
                if event.key == pygame.K_DOWN  and not self.pause: self.direction_stack.append(gameEngine.SOUTH)
        
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
    
    def exit_run(self):
        # Exit the game
        super().exit_run()
        
        # Did the player win the game?
        if self.won == True:
            print(f"Congratulations! You've won the game with {self.score} points!")
        
        # Update high score list, if player reached a new high score.
        if self.score > self.highscore:
            print("Congratulations! You reached a new highscore!")
            self.highscore = self.score
            
        # Print highscores
        print(" <<< YOUR SCORE >>> ".center(20))
        print(f"{self.score}".center(20))
        print(self.highscoreList)
            
    @property
    def playerName(self):
        """
        Define a property that returns the players name. Get it via command line input, if it wasn't set yet. Used by gameEngine to update high score list.
        """
        if not hasattr(self, "_playerName"):
            self._playerName = input("Enter player name: ")
        return self._playerName
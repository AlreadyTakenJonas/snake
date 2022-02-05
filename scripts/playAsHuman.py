#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  5 15:15:49 2022

This script creates a human controllable agent, that can run the snake game and starts the game.

Simply: This script starts the snake game for a human player.

@author: jonas
"""

from snake.agentHuman import AgentHuman

def main():
    # Play Snake
    game = AgentHuman()
    game.run()


if __name__ == "__main__":
    main()
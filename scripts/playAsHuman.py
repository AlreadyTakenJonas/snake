#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  5 15:15:49 2022

This script creates a human controllable agent, that can run the snake game and starts the game.

Simply: This script starts the snake game for a human player.

@author: jonas
"""

from snake.agentHuman import AgentHuman

import argparse

def main():
    
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-d', '--difficulty', choices = ["easy", "normal", "hard"], help = "Select game difficulty.", default="normal")
    args = parser.parse_args()
    
    if args.difficulty == "easy":
        fps = 10
    elif args.difficulty == "normal":
        fps = 15
    else:
        fps = 20
    
    # Play Snake
    game = AgentHuman()
    game.SCORE_MULTIPLIER = fps/15
    game.run(fps=fps)


if __name__ == "__main__":
    main()
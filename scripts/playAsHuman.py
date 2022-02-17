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
    parser.add_argument('-d', '--difficulty', choices = ["easy", "normal", "hard", "e", "n", "h", 0, 1, 2], help = "Select game difficulty. Available options: e(asy), n(ormal), h(ard).", default="normal", metavar = "level")
    args = parser.parse_args()
    
    if args.difficulty in ["easy", "e", 0]:
        fps = 10
        minScorePerApple = 5
        maxScorePerApple = 25
    elif args.difficulty in ["normal", "n", 1]:
        fps = 15
        minScorePerApple = 10
        maxScorePerApple = 50
    else:
        fps = 20
        minScorePerApple = 15
        maxScorePerApple = 75
    
    # Play Snake
    game = AgentHuman(max_score_per_apple=maxScorePerApple, min_score_per_apple=minScorePerApple)
    game.run(fps=fps)


if __name__ == "__main__":
    main()
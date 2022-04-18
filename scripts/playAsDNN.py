# -*- coding: utf-8 -*-
"""
Created on Sun Mar  6 15:03:48 2022

@author: jonas
"""


from snake.agentDNN import AgentDNN
import tflearn
from snake.brainDNN import BrainDNN
import numpy as np


def createDNN():
    net = tflearn.input_data(shape=[None, 3])
    net = tflearn.fully_connected(net, 32)
    net = tflearn.fully_connected(net, 3, activation='softmax')
    net = tflearn.regression(net)
    
    model = BrainDNN(net)
    return model

def preprocessGameState(gameEngine):
    snakeHead = gameEngine.position_snake_body[0]
    snakeDirection = snakeHead - gameEngine.position_snake_body[1]
    apple = gameEngine.position_apple
    boardSize = np.array([ gameEngine._get_max_x(), gameEngine._get_max_y() ])
    
    directionToApple = apple - snakeHead
    directionToApple = directionToApple / boardSize
    
    if snakeDirection[0] == -1:
        distanceToWall = snakeHead[0] / boardSize[0]
    elif snakeDirection[1] == -1:
        distanceToWall = snakeHead[1] / boardSize[1]
    elif snakeDirection[0] == 1:
        distanceToWall = (boardSize[0] - snakeHead[0]) / boardSize[0]
    elif snakeDirection[1] == 1:
        distanceToWall = (boardSize[1] - snakeHead[1]) / boardSize[1]
    else:
        raise NotImplementedError("Cannot compute the distance to the wall. The code is propably shit.")
        
    gameState = np.append(directionToApple, distanceToWall)
    
    gameState = gameState.reshape((1,3))
    
    #print(f"Input vector: {gameState}")
    
    return gameState
    
def main():
    
    brain = createDNN()
    
    stepsize = 0.1
    gameSettings = {"maxStepsPerApple": 25, "gui":False, "fps":10, "iterations":10}
    
    with brain.session:
    
        dim = len(brain)
        gradient = np.zeros(dim)
    
        print("Measure initial game performance ...")
        currentScore, currentWon, currentDuration = AgentDNN(brain, preprocessGameState).run(**gameSettings)
        
        for index, value in enumerate(brain):
        
            print(f"Dimension {index+1}/{dim}.")
            print("Measure game performance")
            
            brain[index] = value + stepsize
            
            nextScore, nextWon, nextDuration = AgentDNN(brain, preprocessGameState).run(**gameSettings)
            
            gradient[index] = (nextDuration - currentDuration)/stepsize + (nextScore - currentScore)/stepsize + (nextWon - currentWon)/stepsize
            
            print(f"Current gradient element: {gradient[index]}")
            
            brain[index] = value
            
    print("Gradient computation done.")
    print(gradient)
    
if __name__ == "__main__":
    main()
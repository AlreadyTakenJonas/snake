# -*- coding: utf-8 -*-
"""
Created on Sun Mar  6 15:03:48 2022

@author: jonas
"""


from snake.agentDNN import AgentDNN
import tflearn
from snake.brainDNN import BrainDNN
import numpy as np
from tqdm import tqdm

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
    

def getGradient(brain, gameSettings, stepsize = 0.1,
                gradientScoreBias = 1, gradientDurationBias = 1, gradientWinBias = 1):
    """
    Let the DNN play the game and nudge the weights a little bit. Compute the gradient of the game performance plotted against the weights of the network.
    """
    
    print("""
          **********************
           GRADIENT CALCULATION
          **********************
          
          """)
    
    totalBias = gradientScoreBias + gradientDurationBias + gradientWinBias
    scoreBias = gradientScoreBias / totalBias
    durationBias = gradientDurationBias / totalBias
    winBias = gradientWinBias / totalBias
    
    # Create empty gradient vector
    dim = len(brain)
    gradient = np.zeros(dim)
    
    # Get the current game performance
    currentScore, currentWon, currentDuration = AgentDNN(brain, preprocessGameState).run(**gameSettings, tqdmSettings={"desc": "Measure Current Performance"})
    
    # Loop over all weights and biases
    for index, value in tqdm(enumerate(brain), 
                             position=0, leave=False, desc="Compute Gradient Vector", total=dim):
        
        # Nudge the current weight
        brain[index] = value + stepsize
            
        # Get the new game performance
        nextScore, nextWon, nextDuration = AgentDNN(brain, preprocessGameState).run(**gameSettings, tqdmSettings={"desc": "Compute Gradient Element", "position":1, "leave":False})
            
        # Compute one element of the gradient
        # Use the biases to make the 3 different scores differently important (average duration of game, average score of the game, how often did the player win on average).
        gradient[index] = durationBias*(nextDuration - currentDuration)/stepsize + scoreBias*(nextScore - currentScore)/stepsize + winBias*(nextWon - currentWon)/stepsize
        
        # Reset the current weight to its original value            
        brain[index] = value
    
    # Normalise the gradient
    magnitude = np.linalg.norm(gradient)
    gradient = gradient / magnitude
    
    print("GRADIENT RESULT")
    print("gradient magnitude")
    print(magnitude)
    print("normalised gradient vector")
    print(gradient)
    print("\nGRADIENT COMPUTATION DONE\n")
    
    # Return the normalised gradient and its magnitude
    return gradient, magnitude


def main():
    
    brain = createDNN()
    gameSettings = {"maxStepsPerApple": 25, "gui":False, "fps":10, "iterations":10}
    
    with brain.session:
        gradient, magnitude = getGradient(brain, gameSettings)
        
        print("Add gradient to DNN weights ...")
        import time
        start = time.time()
        brain += gradient
        end = time.time()
        additionTime = end - start
        print(f"Adding took {additionTime} seconds.")
        
        gradient2, magnitude2 = getGradient(brain, gameSettings)
        
        print("DELTA MAGNITUDE")
        print(magnitude2-magnitude)
    
        print("DELTA VECTOR")
        print(gradient2-gradient)
        
        
if __name__ == "__main__":
    main()
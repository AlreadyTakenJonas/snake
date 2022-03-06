# -*- coding: utf-8 -*-
"""
Created on Sun Mar  6 15:03:48 2022

@author: jonas
"""


from snake.agentDNN import AgentDNN
import tflearn


def createDNN():
    net = tflearn.input_data(shape=[None, 2])
    net = tflearn.fully_connected(net, 32)
    net = tflearn.fully_connected(net, 3, activation='softmax')
    net = tflearn.regression(net)
    
    model = tflearn.DNN(net)
    return model

def preprocessGameState(gameEngine):
    snakeHead = gameEngine.position_snake_body[0]
    apple = gameEngine.position_apple
    direction = apple - snakeHead
    direction[0] = direction[0] / gameEngine._get_max_x()
    direction[1] = direction[1] / gameEngine._get_max_y()
    direction = direction.reshape((1,2))
    
    return direction
    
def main():
    
    game = AgentDNN(createDNN, preprocessGameState)
    averageScore, averageWon, averageDuration = game.run(fps=10, gui=True, iterations=10)
    print(f"Averages\nScore: {averageScore}\nWin: {averageWon}\nDuration: {averageDuration}")

if __name__ == "__main__":
    main()
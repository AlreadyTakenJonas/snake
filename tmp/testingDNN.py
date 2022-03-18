# -*- coding: utf-8 -*-
"""
Created on Sun Mar  6 14:48:24 2022

@author: jonas
"""


import tflearn
import tensorflow as tf
import numpy as np

graph = tf.Graph()

with graph.as_default():
    net = tflearn.input_data(shape=[None, 6])
    net = tflearn.fully_connected(net, 32)
    net = tflearn.fully_connected(net, 32)
    net = tflearn.fully_connected(net, 2, activation='softmax')
    net = tflearn.regression(net)
    model = tflearn.DNN(net)

with model.session as sess: 
    var = tflearn.variables.get_all_trainable_variable()
    print("TRAINABLE VARIABLES")
    for i in var:
        print(i)
    print("")   
    print( tflearn.variables.get_value(var[0]) )
    print( np.prod(var[0].shape) )
    
    # Map index to index in matrix
    
    vector = tflearn.variables.get_value(var[0])
    print(vector.ndim)
    for i in range(192):
        k = i % vector.shape[-1]
        j = int( (i - k)/vector.shape[-1])
        print(j, k)
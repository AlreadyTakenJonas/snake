# -*- coding: utf-8 -*-
"""
Created on Sun Mar  6 14:48:24 2022

@author: jonas
"""


import tflearn
import tensorflow as tf


graph = tf.Graph()

with graph.as_default():
    net = tflearn.input_data(shape=[None, 6])
    net = tflearn.fully_connected(net, 32)
    net = tflearn.fully_connected(net, 32)
    net = tflearn.fully_connected(net, 2, activation='softmax')
    net = tflearn.regression(net)
    model = tflearn.DNN(net)

    var = tflearn.variables.get_all_trainable_variable()
    print("TRAINABLE VARIABLES")
    for i in var:
        print(i)
    print("")

with tf.compat.v1.Session(graph = graph) as sess:
    print( tflearn.variables.get_value(var[0]) )
    
    
    
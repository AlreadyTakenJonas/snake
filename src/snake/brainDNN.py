#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  18 12:56:36 2022

@author: jonas
"""

import tflearn
import numpy as np

class BrainDNN(tflearn.DNN):
    """
    TODO
    """
    
    def __init__(self, *args, **kwargs):
        # Call constructor of tflearn.DNN
        super().__init__(*args, **kwargs)
        
    def __iadd__(self, other):
        assert np.iterable(a), "Can only add iterables!"
        assert len(other) == len(self), "Can't add vectors of different length!"
        
        for index, (s, o) in enumerate( zip(self, other) ):
            self[index] = s + o
        
        return self
    
    def __isub__(self, other):
        assert np.iterable(a), "Can only subtract iterables!"
        assert len(other) == len(self), "Can't subtract vectors of different length!"
        
        for index, (s, o) in enumerate( zip(self, other) ):
            self[index] = s - o
                    
        return self
    
    def _readBrainMap(self, index):
        
        # Write docstring
        # Write __setitem__
        # Write cache that knows, if __setitem__ changed something in the DNN.
        
        if isinstance(index, int) == False: raise TypeError("Index must be integer!")
        
        # Loop over dictionary with all trainable tensorflow variables (tensors with weights and tensors with biases)
        # Keys are the length (number of elements) of the tensor (saved as value of key) plus the length of all previous tensors in the dictionary.
        # This loop finds the tensorflow variable ("var") containing the element the given index is associated with.
        # Which tensor contains the element the given index is referring to?
        for length, var in self.brainMap.items():
            # Is the index smaller than the biggest index ("length") mapped to the tensorflow variable "tensor"?
            # Break the loop if it is.
            if index < length: break
                     
        # The loop ran over all key-value-pairs and didn't found a matching value.
        # The index must be out of range.
        # Raise an IndexError to make the object iterable
        else:
            raise IndexError("Index out of range.")
    
        # Get the tensor of the tensorflow variable
        tensor = tflearn.variables.get_value(var)
    
        # Subtract the number of elements of all tensors in the list before this one.
        # In other words. Take the index of an element of the DNN (given as parameter) and convert it to an index of the tensor found by the for loop.
        # Which element of the tensor is meant by the given index?
        # Length is the sum of the number of elements in all tensors that are listed in the dictionary before and including this one. Add the product of the dimensions to only subtract the previous tensors' length.
        index = index - length + np.prod(tensor.shape)
        
        # Is the tensor a vector with biases?
        if tensor.ndim is 1:
            # Select one element from the vector.
            pass# item = tensor[index]
        # Is the tensor a matrix with weights?
        elif tensor.ndim is 2:
            # Get the row and column in the selected tensor corresponding to the given index.
            # i is the first index of the matrix element, j is the second index of the matrix element.
            j = index % tensor.shape[1]
            i = int( (index - j)/tensor.shape[1] )
            # Select the element from the matrix.
            index = [i, j]#item = tensor[i][j]
        # Something went wrong.
        else:
            raise NotImplementedError(f"Can't handle tensors with {tensor.ndim} dimensions. Only support for 1 or 2 dimensions.")
        
        # Return the selected element.
        return var, tensor, index#return item
        
    def __getitem__(self, index):
        _, tensor, tensorIndex = self._readBrainMap(index)
        
        if tensor.ndim is 1:
            item = tensor[tensorIndex]
        else:
            item = tensor[tensorIndex[0], tensorIndex[1]]
            
        return item
    
    def __setitem__(self, index, value):
        #if not isinstance(value, float) and not isinstance(value, int):
        #    raise TypeError(f"Type of value must be int or float, not {type(value)}!")
    
        tfvar, tensor, tensorIndex = self._readBrainMap(index)
        
        if tensor.ndim is 1:
            tensor[tensorIndex] = value
        else:
            tensor[tensorIndex[0], tensorIndex[1]] = value
            
        tflearn.variables.set_value(tfvar, tensor)
    
    @property
    def brainMap(self):
        """
        Get a dictionary mapping an index to a tensorflow variable of the DNN.
        All indices smaller than the key of the dictionary should be mapped on to the tensorflow variable (a tensor) stored in the corresponding value.
        The current key is the sum of the previous key and the last index of the key's value.
        
        Parameters
        ----------
        None.

        Returns
        -------
        Dictionary mapping indices to tensorflow variables of the DNN.
        """
        # Create the brainMap if it does not exist yet.
        if not hasattr(self, "_brainMap"):
            brainMap = dict()
            maxIndexForVariable = 0
            # Loop over all trainable tensorflow variables (in the scope of the DNN of this instance).
            for var in tflearn.variables.get_all_trainable_variable():
                # Get the tensor of the current tensorflow variable
                tensor = tflearn.variables.get_value(var)
                # Add the length of the current tensor to the running counter
                maxIndexForVariable = maxIndexForVariable + np.prod(tensor.shape)
                # Add key value pair to dictionary.
                # The key is the running counter (sum of lengths of all tensors so far).
                # The value is the tensorflow variable with the weights or biases of one DNN layer.
                brainMap[maxIndexForVariable] = var                   
            # Make brainMap an attribute of the instance.
            self._brainMap = brainMap
        
        # Return the brainMap
        return self._brainMap
        
    def __len__(self):
        return max(self.brainMap)
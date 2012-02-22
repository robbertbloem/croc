from __future__ import print_function
from __future__ import division


import os
import time
import numpy
import itertools
import pylab 
import matplotlib 
import matplotlib.pyplot as plt

import croc
import croc.Debug

reload(croc.Debug)

if croc.Debug.reload_flag:
    reload(croc)






def correlation(array, maxtau = 200, step_type = "tau"):
    """
    Calculation of the correlation using the method Jan used.
    
    For every iteration, the copied array will be 'rolled' or 'rotated' left by 1 for maxtau times. The copied array will be multiplied with the original array, but only the elements with a certain step between them will be used. The larger the step size, the quicker the method but also the more noisy the result will become.
    
    INPUT:
    array (ndarray): 1-d array with the data
    maxtau (int): the maximum shift, also the maximum to where the correlation is calculated. This directly affects the speed of the calculation. (with N^2?)
    step_type ("1", "tau"): The step size. With "1" the step size is 1, this will result in a longer calculation but less noise. With "tau" the step size is the current "tau". The calculation will be faster but the result will be noisier.
    
    CHANGELOG:
    20120215: Introduced step_type
    """

    array = array - numpy.mean(array)
    
    array2 = numpy.copy(array)
    
    c = numpy.zeros(maxtau)

    for i in range(0, maxtau):
        
        array2 = numpy.roll(array2, -1)
        
        if step_type == "tau":
            step = i+1
        elif step_type == "1":
            step = 1
        else:   
            print("croc.Functions (correlation): step_type is not recognized, will use 'tau'")
            step = i+1

        a = list(itertools.islice(array * array2, None, len(array)-i-1, step))
        
        c[i] = numpy.sum(a) / len(a)
    
    return c/c[0]




def correlation_fft(array):

    # fix that is proposed for numpy, but not implemented yet
    a = (array - numpy.mean(array)) / (numpy.std(array) * len(array))
    v = (array - numpy.mean(array)) /  numpy.std(array)
    
    # calculate the autocorrelation
    r = numpy.correlate(a, v, mode="full")
    
    # select the part we want
    r = r[len(r)/2:]
    
    return numpy.real(r/r[0])





def derivative(array):
    """
    Very rudimentary way to calculate the derivative
    """
    
    n, dump = numpy.shape(array)
    
    der_array = numpy.zeros((n,2))
    
    for i in range(1, n-1):
        der_array[i,0] = array[i,0]
        der_array[i,1] = (array[i+1,1] - array[i-1,1]) / (array[i+1,0] - array[i-1,0])
    
    der_array[0,0] = array[0,0]
    der_array[0,1] = der_array[1,1]
    der_array[-1,0] = array[-1,0]
    der_array[-1,1] = der_array[-2,1]
    
    return der_array
    
    
    
    
    
    
    






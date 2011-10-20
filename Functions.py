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






def correlation(array, maxtau = 200):

    array = array - numpy.mean(array)
    
    array2 = numpy.copy(array)
    
    c = numpy.zeros(maxtau)

    for i in range(0, maxtau):
        
        array2 = numpy.roll(array2, -1)
        
        step = numpy.ceil((i+1)/4)

        a = list(itertools.islice(array * array2, None, len(array), step))
        
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
    
    
    
    
    
    
    






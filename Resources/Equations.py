from __future__ import print_function
from __future__ import division

import numpy
import matplotlib 
import matplotlib.pyplot as plt

### FUNCTIONS ###

def rb_cos(A, t):
    """
    4 parameters
    function: A[0] + A[1] * numpy.cos(2 * numpy.pi * A[2] * t + A[3])
    A[0]: offset
    A[1]: amplitude
    A[2]: frequency
    A[3]: phase
    """
    return A[0] + A[1] * numpy.cos(2 * numpy.pi * A[2] * t + numpy.pi*A[3])


def linear(A, t):
    return A[0] + A[1] * t    

def Sellmeier(A, t):
    """
    Calculates the index of refraction using the Sellmeier equation.
    
    CHANGELOG:
    20110909/RB: started
    
    INPUT:
    A (array): the Sellmeier Coefficients
    t (array): wavelengths to calculate the index of refraction.
    """
    
    return A[6] + (A[0] * t**2) / (t**2 - A[1]) + (A[2] * t**2) / (t**2 - A[3]) + (A[4] * t**2) / (t**2 - A[5]) 


def double_exp(A,t):
    return A[0]*numpy.exp(-t/A[1]) + A[2]*numpy.exp(-t/A[3])
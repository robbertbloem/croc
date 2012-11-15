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
    
def quadratic(A, t):
    return A[0] + A[1] * t + A[2] * t**2  

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
    
def rb_exp(A,t):
    return A[0]*numpy.exp(-t/A[1]) 

def single_exp_offset(A,t):
    return A[0]*numpy.exp(-t/A[1]) + A[2]

def rb_gaussian(A, t, ignore = -1):
    """
    A[0]: sigma (sigma^2 = variance)
    A[1]: mu (mean)
    A[2]: offset 
    A[3]: scale, before offset
    
    ignore: 
    == 2: ignore the offset
    == 3: ignore the scale
    == 23: ignore both the scale and offset
    """

    if ignore == 2:
        return (A[3]/(A[0]*numpy.sqrt(2*numpy.pi))) * numpy.exp(-(t-A[1])**2/(2*A[0]**2)) 
        
    elif ignore == 3:
        return (A[3]/(A[0]*numpy.sqrt(2*numpy.pi))) * numpy.exp(-(t-A[1])**2/(2*A[0]**2))         

    elif ignore == 23:
        return (1/(A[0]*numpy.sqrt(2*numpy.pi))) * numpy.exp(-(t-A[1])**2/(2*A[0]**2))   

    else:
        return (A[3]/(A[0]*numpy.sqrt(2*numpy.pi))) * numpy.exp(-(t-A[1])**2/(2*A[0]**2)) + A[2]



def rb_two_gaussians(A, t, ignore = -1):
    
    return rb_gaussian(A[:4], t, ignore = ignore) + rb_gaussian(A[4:], t, ignore = ignore)
      

def rb_lorentzian(A, t, ignore = -1):
    """
    A[0]: gamma
    A[1]: mean
    A[2]: offset
    A[3]: scale

    ignore: 
    == 2: ignore the offset
    == 3: ignore the scale
    == 23: ignore both the scale and offset
    """
    if ignore == 2:
        return A[3]/(numpy.pi * A[0] * (1 + ((t - A[1])/A[0])**2))
    
    elif ignore == 3:
        return 1/(numpy.pi * A[0] * (1 + ((t - A[1])/A[0])**2)) + A[2]
    
    elif ignore == 23:
        return 1/(numpy.pi * A[0] * (1 + ((t - A[1])/A[0])**2))
    
    else:
        return A[3]/(numpy.pi * A[0] * (1 + ((t - A[1])/A[0])**2)) + A[2]


def rb_two_lorentzians(A, t, ignore = -1):
    
    return rb_lorentzian(A[:4], t, ignore = ignore) + rb_lorentzian(A[4:], t, ignore = ignore)

    

# to calculate the non-rephasing and rephasing diagrams
def g(t, delta, t_corr):
    """
    20101209/RB: started/continued
    These are the g(t) functions used to make the non-rephasing and rephasing diagrams.

    INPUT:
    t: time array

    OUTPUT:
    An array with the results
    """
    # delta= 1/1000
    # t_corr = 1000
    return delta**2 * t_corr**2 * ( numpy.exp(-t/t_corr) + t/t_corr - 1)

# calculate the non-rephasing diagram
def non_rephasing(t1, t2, t3, w, anh, delta, t_corr):
    """
    20101209/RB: started/continued
    Calculates the non-rephasing diagram

    INPUT:
    t1, t3 (mesh): coherence times in fs
    t1_axis = numpy.arange(start, stop, step)
    t3_axis = numpy.arange(start, stop, step)
    t1, t3 = numpy.meshgrid(t1_axis, t3_axis)
    
    t2 (integer/float?): population time in fs
    w (integer): frequency (in cm-1)
    anh (integer): anharmonicity (in cm-1)
    delta (float): ?
    t_corr (float): correlation time

    OUTPUT:
    A 2D array of the response in for the coherence times
    """

    return (numpy.exp(-1j * (t3 + t1) * w) - numpy.exp(-1j * (t3 * (w - anh) + t1 * w))) * (numpy.exp(-g(t1, delta, t_corr) - g(t2, delta, t_corr) - g(t3, delta, t_corr) + g(t1+t2, delta, t_corr) + g(t2+t3, delta, t_corr) - g(t1+t2+t3, delta, t_corr)))

#calculate the rephasing diagram
def rephasing(t1, t2, t3, w, anh, delta, t_corr):
    """
    20101209/RB: started/continued
    Calculates the non-rephasing diagram

    see for details the non_rephasing function
    """
    return (numpy.exp(-1j * (t3 - t1) * w) - numpy.exp(-1j * (t3 * (w - anh) - t1 * w))) * (numpy.exp(-g(t1, delta, t_corr) + g(t2, delta, t_corr) - g(t3, delta, t_corr) - g(t1+t2, delta, t_corr) - g(t2+t3, delta, t_corr) + g(t1+t2+t3, delta, t_corr)))

    
    
    
    
    
    
    
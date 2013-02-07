"""
croc.Resources.Mathematics



"""

from __future__ import print_function
from __future__ import division

import numpy

import numpy
import matplotlib 
import matplotlib.pyplot as plt

from scipy.optimize.minpack import leastsq

import itertools



def square_formula(a, b, c):
    """
    Calculates 
    ax^2 + bx + c = 0
    
    """
    x0 = (-b + numpy.sqrt(b**2 - 4*a*c))/(2*a)
    x1 = (-b - numpy.sqrt(b**2 - 4*a*c))/(2*a)
    return x0, x1


### CODE FOR FITTING PROCEDURE ###

def minimize(A, t, y0, function):
    """
    does something, not sure what
    """
    return y0 - function(A, t)

def fit(x_array, y_array, function, A_start):
    """
    used to fit things
    20101209/RB: started
    
    INPUT:
    x_array: the array with time or something
    y-array: the array with the values that have to be fitted
    function: one of the functions, in the format as in the file "functions"
    A_start: a starting point for the fitting
    
    OUTPUT:
    A_final: the final parameters of the fitting
    
    WARNING:
    Always check the result, it might sometimes be sensitive to a good starting point.

    """
    param = (x_array, y_array, function)

    A_final, cov_x, infodict, mesg, ier = leastsq(minimize, A_start, args=param, full_output=True)#, warning=True)
    
    return A_final

### FOURIER TRANSFORM STUFF ###

# the general Fourier transform method
def fourier(array, zero_in_middle = False, first_correction = False, zeropad_to = None, window_function = "none", window_length = 0, flag_plot = False):
    """
    A Fourier transform for any dimension.
    
    INPUT:
    - array (x-dimensions ndarray): to be FFT'd
    - zero_in_middle (BOOL): for FFT the zero-time should be the first element of the array. If the zero is in the middle, it will be shifted first
    - first_correction (BOOL): if the first element of the array has to be halved, check this as True
    - zeropad_to (number): Length of the transformed axis of the output. If n is smaller than the length of the input, the input is cropped. If it is larger, the input is padded with zeros. If n is None, the length of the input (along the axis specified by axis) is used.
    
    OUTPUT:
    array (x-dimensions ndarray): Fourier transformed array
    
    CHANGELOG:
    20101204 RB: started
    20110909 RB: added zeropadding
    
    """
    # shift time = 0 to first element
    if zero_in_middle == True:
        array = numpy.fft.ifftshift(array)
    
    
    
    # half the first element
    if first_correction == True: 
        dim = len(numpy.shape(array))
        if dim == 1:
            array[0] /= 2
        elif dim == 2:
            array[0,:] /= 2
            array[:,0] /= 2
        elif dim > 2:
            print("WARNING (fourier.fourier.py): correction of the first element is not done!")
    
    
    # window function
    if window_function != "none": 
        array = window_functions(array, window_function, window_length, flag_plot = flag_plot)
    
    
    
    # the fft
    array = numpy.fft.fft(array, n = zeropad_to)
    
    # move the array back if it was shifted
    if zero_in_middle == True:
        array = numpy.fft.fftshift(array)
    
    return array 




def window_functions(array, window_function, window_length = 0, flag_plot = False):
    """
    croc.Absorptive.window_functions
    
    Different window functions.
    
    INPUT:
    - array (ndarray): the array where the window-functions will be applied to
    - window_length (int): the length of the window. If the length is 0 or equal or larger than the length of array, this will be set to the length of the array.
    - window_function: the function
        - none: will apply a rectangular window with 1's for all elements
        - ones: will make a rectangular window with a certain length and pads with zeros.
        - triangular: will make a triangular window with a certain length and pads with zeros
        - gaussian: will make a gaussian window for the full length of array, but will go to zero at around window_length.
    
    """

    dim = len(numpy.shape(array))
    
    # for single dimensions
    if dim == 1:
        # the window function should end up with the same length as the array
        array_length = numpy.shape(array)[0]
    
        # if it is smaller than the length, make it that length
        if window_length > 0 and window_length < array_length:
            n_max = window_length
            zeros = numpy.zeros(array_length - window_length) 
        else:
            n_max = array_length
            zeros = []
        
        # the windows
        if window_function == "none":
            window = numpy.ones(array_length)
        
        elif window_function == "ones":
            window = numpy.concatenate((numpy.ones(n_max).T, zeros)) 
        
        elif window_function == "triangle":
            window = numpy.concatenate((numpy.linspace(1, 0, n_max).T, zeros))   

        elif window_function == "gaussian":
            window = numpy.exp(-(2.2*numpy.arange(0, array_length)/(n_max))**2)
            #window = numpy.exp(-numpy.arange(0, array_length)**2 / (n_max**1.7)).T  
        
        elif window_function == "experimental": 
            window = numpy.exp(-(2.2*numpy.arange(0, array_length)/(n_max))**2)

        else:
            print("ERROR (croc.Absorptive.window_functions): Unknown window function.")
            window = numpy.ones(array_length)
    
        if flag_plot:
            m = numpy.max(array)
        
            plt.figure()
            plt.plot(array)
            plt.plot(window * m)
            plt.plot(array*window)
            plt.title("window function is scaled")
            plt.show()
    
        return array * window

    # for higher dimensions
    else:
        print("ERROR (croc.Absorptive.window_functions): Not implemented yet for multiple dimensions.")
        return 0        



# make FT axis
def make_ft_axis(length, dt, undersampling = 0, normalized_to_period = 0, zero_in_middle = False):
    """
    fourier transform the time axis
    20101204/RB: started
    
    INPUT:
    length: amount of samples
    dt: time between samples
    undersampling: 
    normalized_to_period: will normalize the spectrum to 1 for the specified period. If the number is 0, the spectrum will not be normalized.
    zero_in_middle: determines the frequency axes.
    
    OUTPUT:
    A frequency axis.     
    
    """

    if normalized_to_period == 0:   
        resolution = 1 / ( 3e-5 * length * dt)
    else:
        resolution = normalized_to_period / (length * dt)
        
    array = numpy.arange((undersampling)*length/2, (undersampling+1)*length/2)*resolution
    
    if zero_in_middle == False:
        return numpy.concatenate((array,-numpy.flipud(array)))
    else:
        return numpy.concatenate((-numpy.flipud(array), array))





### CORRELATION STUFF ###


def correlation(array, maxtau = 200, step_type = "tau", flag_normalize = True):
    """
    Calculation of the correlation using the method Jan used. Use correlation_fft instead.
    
    For every iteration, the copied array will be 'rolled' or 'rotated' left by 1 for maxtau times. The copied array will be multiplied with the original array, but only the elements with a certain step between them will be used. The larger the step size, the quicker the method but also the more noisy the result will become.
    
    INPUT:
    array (ndarray): 1-d array with the data
    maxtau (int): the maximum shift, also the maximum to where the correlation is calculated. This directly affects the speed of the calculation. (with N^2?)
    step_type ("1", "tau"): The step size. With "1" the step size is 1, this will result in a longer calculation but less noise. With "tau" the step size is the current "tau". The calculation will be faster but the result will be noisier.
    flag_normalize (BOOL, True): see note below.
    
    NOTE:
    This method is slow. 
    
    CHANGELOG:
    20120215/RB: Introduced step_type
    20130131/RB: introduced flag_normalize
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
    
    if flag_normalize:
        return c/c[0]
    else:
        return c



def correlation_fft(array, flag_normalize = True):
    """
    201202xx/RB: started function
    20130205/RB: the function now uses an actual Fourier transform
    20130207/RB: take the first part of the array, not the last part reversed. This was done to agree with Jan's correlation method, but now it seems that one is wrong.
    """

    array = array - numpy.mean(array)
    
    # zeropad to closest 2^n 
    l = 2 ** int(1+numpy.log2(len(array) * 2))
    
    s = numpy.fft.fft(array, n=l)
    r = numpy.fft.ifft(s * numpy.conjugate(s))
    
    r = r[:len(array)]
    
    if flag_normalize:
        return numpy.real(r/r[0])
    else:
        return numpy.real(r)
    




### DERIVATIVE ###


# def derivative(array):
#     """
#     Very rudimentary way to calculate the derivative
#     """
#     
#     n, dump = numpy.shape(array)
#     
#     der_array = numpy.zeros((n,2))
#     
#     for i in range(1, n-1):
#         der_array[i,0] = array[i,0]
#         der_array[i,1] = (array[i+1,1] - array[i-1,1]) / (array[i+1,0] - array[i-1,0])
#     
#     der_array[0,0] = array[0,0]
#     der_array[0,1] = der_array[1,1]
#     der_array[-1,0] = array[-1,0]
#     der_array[-1,1] = der_array[-2,1]
#     
#     return der_array

    
def derivative(x, y):
    """
    20110909/RB: rudimentary method to calculate the derivative
    """
    
    dx = x[1] - x[0]
    
    l = len(y)
    
    x_temp = numpy.zeros(l-2)
    y_temp = numpy.zeros(l-2)
    
    for i in range(1,l-1):
        x_temp[i-1] = x[i]
        
        dy = (y[i] - y[i-1] + y[i+1] - y[i]) / 2
        
        y_temp[i-1] = dy / dx
    
    return x_temp, y_temp    
    
    



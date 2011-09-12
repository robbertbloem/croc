"""
croc.Absorptive



"""

from __future__ import print_function
from __future__ import division

import numpy



# the general Fourier transform method
def fourier(array, zero_in_middle = False, first_correction = False, zeropad_to = None, window_function = "none", window_length = 0):
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
        array = window_functions(array, window_function, window_length)
    
    
    
    # the fft
    array = numpy.fft.fft(array, n = zeropad_to)
    
    # move the array back if it was shifted
    if zero_in_middle == True:
        array = numpy.fft.fftshift(array)
    
    return array 




def window_functions(array, window_function, window_length = 0):
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
            #print(window_function)
            #print(window)
        
        elif window_function == "ones":
            window = numpy.concatenate((numpy.ones(n_max).T, zeros)) 
            #print(window_function)
            #print(window)
        
        elif window_function == "triangle":
            window = numpy.concatenate((numpy.linspace(1, 0, n_max).T, zeros)) 
            #print(window_function)
            #print(window)   

        elif window_function == "gaussian":
            window = numpy.exp(-numpy.arange(0, array_length)**2 / (n_max**1.5)).T    
            #print(window_function)
            #print(window)

        else:
            print("ERROR (croc.Absorptive.window_functions): Unknown window function.")
            window = numpy.ones(array_length)
    
        return array * window

    # for higher dimensions
    else:
        print("ERROR (croc.Absorptive.triangle_window): Not implemented yet for multiple dimensions.")
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









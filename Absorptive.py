"""
croc.Absorptive



"""

from __future__ import print_function
from __future__ import division

import numpy
#import types

# the general Fourier transform method
def fourier(array, zero_in_middle = False, first_correction = False, zeropad_to = None):
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
    
    # the fft
    array = numpy.fft.fft(array, n = zeropad_to)
    
    # move the array back if it was shifted
    if zero_in_middle == True:
        array = numpy.fft.fftshift(array)
    
    return array 



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









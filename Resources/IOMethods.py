"""
IOMethods is for importing/exporting of data outside the DataClass structure.
"""

from __future__ import print_function
from __future__ import division

import numpy
import matplotlib 
import matplotlib.pyplot as plt


def import_data_FS(path_and_filename, n_shots = 30000, n_channels = 37, return_fringes = False):
    """
    This method is a derivative of croc.Pe.PeFS.import_raw_data, but without the reliance on the class structure.
    
    """
    
    data = numpy.fromfile(path_and_filename)
    
    # remove the two fringes at the end
    fringes = [data[-2], data[-1]]
    data = data[:-2]
    
    # construct m
    m = numpy.zeros((n_channels, n_shots), dtype = "cfloat")
    
    # order the data in a 2d array
    for i in range(n_shots):
        for j in range(n_channels):
            m[j, i] = data[j + i * n_channels] 
    
    return m, fringes



def import_data_correlation(path, mess_array, mess_i, scan_array, scan_j, mess_date, sort = "fft"):
    
    path_and_filename = path + mess_array[mess_i] + scan_array[scan_j] + "_corr_" + sort + ".bin"
    
    data = numpy.fromfile(path_and_filename)
    
    return data

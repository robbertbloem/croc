"""
IOMethods is for importing/exporting of data outside the DataClass structure.
"""

from __future__ import print_function
from __future__ import division

import os

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import croc
#import croc.Pe
from croc.Resources.DataClasses import mess_data

def import_data_FS(path_and_filename, n_shots = 30000, n_channels = 37, flag_counter = False):
    """
    This method is a derivative of croc.Pe.PeFS.import_raw_data, but without the reliance on the class structure.
    
    INPUT:
    - path_and_filename (string): where the file can be found
    - n_shots (int): number of shots
    - n_channels (int): number of channels
    
    OUTPUT:
    - m (2d ndarray): array with (channels x shots)
    - fringes (array with two elements): the begin and end fringe, as appended to the data.
    
    CHANGELOG:
    - 201110xx RB: wrote function
    - 201202xx RB: rewrote the function for wider purpose, moved it to IOMethods
    
    """    
    try:
        data = numpy.fromfile(path_and_filename)
        
        # remove the two fringes at the end
        fringes = [data[-2], data[-1]]
        data = data[:-2]
        
        # construct m
        m = numpy.zeros((n_channels, n_shots), dtype = "cfloat")
        
        if flag_counter:
            c = data[-n_shots:]
            data = data[:-n_shots]
        
        # order the data in a 2d array
        for i in range(n_shots):
            for j in range(n_channels):
                m[j, i] = data[j + i * n_channels] 
                
        if flag_counter:
            return m, c, fringes
        else:
            return m, fringes
    except IOError:
        print("ERROR (croc.Resources.IOMethods.import_data_FS): Unable to import data from file " + path_and_filename)
        raise
        return 0, 0


def import_data_correlation(path, mess_array, mess_i, scan_array, scan_j, mess_date, sort = "fft"):
    
    path_and_filename = path + mess_array[mess_i] + scan_array[scan_j] + "_corr_" + sort + ".bin"
    
    data = numpy.fromfile(path_and_filename)
    
    return data

















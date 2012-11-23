"""
IOMethods is for importing/exporting of data outside the DataClass structure.
"""

from __future__ import print_function
from __future__ import division

import os
import inspect

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import croc
#import croc.Pe
from croc.Resources.DataClasses import mess_data
import croc.Resources.Constants as C
import croc.Debug as D

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
            if c[-1] == 0:
                # this is to repair a (now fixed) bug from VB6. 
                c = data[-n_shots-1:-1]
            
            data = data[:-n_shots]
        
        # order the data in a 2d array
        i_range = range(n_shots)
        j_range = range(n_channels)
        for i in i_range:
            for j in j_range:
                m[j, i] = data[j + i * n_channels] 
                
        if flag_counter:
            return m, c, fringes
        else:
            return m, fringes
    except IOError:
#        print("ERROR (croc.Resources.IOMethods.import_data_FS): Unable to import data from file " + path_and_filename)
        D.printError("Unable to import raw data from file " + path_and_filename, inspect.stack())
        
        raise
        return 0, 0

def import_labview_data(path, base_filename):
    
    try:
        # data
        path_and_filename = path + base_filename + ".csv"
        data = numpy.loadtxt(path_and_filename, dtype = "float", delimiter = ",")
        data = data.T
        
        # time axis in fringes
        path_and_filename = path + base_filename + "_t1.csv"
        t1_axis = numpy.loadtxt(path_and_filename, dtype = "float", delimiter = ",") 
        
        # frequency axis
        path_and_filename = path + base_filename + "_w3.csv"
        w3_axis = numpy.loadtxt(path_and_filename, dtype = "float", delimiter = ",") 
        
        # phase
        path_and_filename = path + base_filename + "_phase.txt"
        phase = numpy.loadtxt(path_and_filename, dtype = "float")
        
        # last pump
        path_and_filename = path + base_filename + "_lastpump.txt"
        lastpump = numpy.loadtxt(path_and_filename, dtype = "str")
        
        # determine number of fringes
        n_fringes = int((len(t1_axis)-1)/2)
        n_pixels = len(w3_axis)
        
        # convert NaN to zeros
        data = numpy.nan_to_num(data)
        
        # labview measures 4000-N to 4000+N, we want the data split into 4000-N to 4000 (non-rephasing) and 4000 to 4000+N (rephasing)
        R = data[n_fringes:, :]
        NR = numpy.flipud(data[:n_fringes+1, :])
        
        # fringe 4000 is included twice. 
        
        # for the FFT, we don't want 4000 to be zero. The axes run from 0 to N
        # also: calculate the axis in fs        
        t1fr_axis = numpy.arange(n_fringes+1)
        t1fs_axis = numpy.arange(n_fringes+1) * C.hene_fringe_fs
        
        # return everything
        return R, NR, t1fs_axis, t1fr_axis, w3_axis, phase, lastpump, n_fringes, n_pixels
    
    except IOError:
        D.printError("Unable to LabView data from file " + path + "/" + base_filename, inspect.stack())
        raise
        return 0, 0, 0    





def import_binned_data(path_and_filename, n_pixels, diagram):

    try:
        data = numpy.fromfile(path_and_filename)

        fringes = [data[-2], data[-1]]
        b_axis = numpy.arange(fringes[0], fringes[1] + 1)
        n_fringes = len(b_axis)
        
        # without the two fringes at the end, the number of elements should be equal to (2*n_pixels + 1), for each chopper state the pixels and the count
        
        if ((len(data)-2)/n_fringes) == (2 * n_pixels + 2):
            
            b_count = [0]*2
            b_count[0] = data[-2 - 2*n_fringes:-2 - n_fringes]
            b_count[1] = data[-2 - n_fringes:-2]
            
            data = data[:2*n_pixels*n_fringes]         
    
            # rearrange the data
            b = numpy.zeros((4, n_fringes, n_pixels), dtype = "cfloat")
            
            for i in range(2): # the two chopper states
                for j in range(n_fringes):
                    for p in range(n_pixels):
                        b[i+diagram*2,j,p] = data[i * n_fringes * n_pixels + j * n_pixels + p]
    
            return b, b_count, b_axis
        
        else:
            D.printWarning("The file does not contain binned data: " + path_and_filename, inspect.stack())
            return 1, 1, 1
        
    except IOError:
        D.printError("Unable to import binned data from file " + path_and_filename, inspect.stack())
        raise
        return 0, 0, 0    










def import_data_correlation(path, mess_array, mess_i, scan_array, scan_j, mess_date, sort = "fft"):
    
    path_and_filename = path + mess_array[mess_i] + scan_array[scan_j] + "_corr_" + sort + ".bin"
    
    data = numpy.fromfile(path_and_filename)
    
    return data

















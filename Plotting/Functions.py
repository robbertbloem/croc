from __future__ import print_function
from __future__ import division

import numpy
import matplotlib 
import matplotlib.pyplot as plt


def rwb_map():
    cdict = {'red':   [(0.0,  0.0, 0.0),(0.475,  1.0, 1.0),(0.525,  1.0, 1.0),
                (1.0,  1.0, 1.0)],
             'green': [(0.0,  0.0, 0.0),(0.475,  1.0, 1.0),(0.525,  1.0, 1.0),
                (1.0,  0.0, 0.0)],
             'blue':  [(0.0,  1.0, 1.0),(0.475,  1.0, 1.0),(0.525,  1.0, 1.0),
                (1.0,  0.0, 0.0)]
            }
    return matplotlib.colors.LinearSegmentedColormap('rwb_colormap', cdict, 256)
    

        
def find_subplot_size(n_plots, prefer_columns = True):
    
    s = numpy.sqrt(n_plots)
    C = numpy.ceil(s)
    F = numpy.floor(s)
        
    if C * F < n_plots:
        C = C + 1

    if prefer_columns:
        return F, C
    else:
        return C, F


def make_contours_2d(data, zlimit = 0, contours = 21, verbose = False):
    """
    zlimit = 0, show all, not don't care about centering around zero
    zlimit = -1, show all, centered around zero
    zlimit = all else, use that, centered around zero
    zlimit = [a,b], plot from a to b
    """
    if zlimit == 0:
        ma = numpy.amax(data)
        mi = numpy.amin(data)
        if verbose:
            print("make_contours_2d, minimum, maximum")
            print(mi, ma)
        return numpy.linspace(mi, ma, num=contours)
        
    elif zlimit == -1:
        ma = numpy.amax(data)
        mi = numpy.amin(data)
        if verbose:
            print("make_contours_2d, minimum, maximum")
            print(mi, ma)
        if abs(mi) > abs(ma):
            ma = abs(mi)
        else:
            ma = abs(ma)
        return numpy.linspace(-ma, ma, num=contours) 
        
    elif type(zlimit) == list:
        return numpy.linspace(zlimit[0], zlimit[1], num=contours)   
    
    else:
        return numpy.linspace(-abs(zlimit), abs(zlimit), num=contours) 

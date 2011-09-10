from __future__ import print_function
from __future__ import division

import numpy
import pylab 
import matplotlib 
import matplotlib.pyplot as plt

cdict = {'red':   [(0.0,  0.0, 0.0),(0.475,  1.0, 1.0),(0.525,  1.0, 1.0),
            (1.0,  1.0, 1.0)],
         'green': [(0.0,  0.0, 0.0),(0.475,  1.0, 1.0),(0.525,  1.0, 1.0),
            (1.0,  0.0, 0.0)],
         'blue':  [(0.0,  1.0, 1.0),(0.475,  1.0, 1.0),(0.525,  1.0, 1.0),
            (1.0,  0.0, 0.0)]
        }
my_cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap',cdict, 256)





def linear(data, axis, x_range = [0, 0], y_range = [0, 0], x_label = "", y_label = "", title = "", new_figure = True):

    # make the x-axis
    if x_range == [0, 0]:
        x_min = axis[0]
        x_max = axis[-1]
    else:
        x_min = x_range[0]
        x_max = x_range[1]

    # make the y_axis
    if y_range == [0, 0]:
        # find the minimum and maximum for the plotted range
        y_min = numpy.nanmin(data[numpy.where(axis < x_max)[0][0]:numpy.where(axis > x_min)[0][-1]])        
        y_max = numpy.nanmax(data[numpy.where(axis < x_max)[0][0]:numpy.where(axis > x_min)[0][-1]])
        
        # give the plot some air
        y_min -= (y_max - y_min)/10
        y_max += (y_max - y_min)/10
        
    else:
        y_min = y_range[0]
        y_max = y_range[1]

    if new_figure:  
        plt.figure()

    # the actual plot
    plt.plot(axis, data)
    
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    
    plt.title(title)
    
    plt.show()










def find_axes(x_axis, y_axis, x_range, y_range):
    """
    croc.Plotting.find_axis
    
    INPUT:
    - x_axis, y_axis (ndarray): the axes
    - x_range, y_range (array): the ranges to be plotted
        Possible cases:
        - [min, max]: plot range min to max
        - [0, 0]: plot the whole range
        - [0, -1]: use the range from the other axis. If both have this, it will plot both axes complete. (ie. it is identical to both having [0,0])
    
    OUTPUT:
    - xmin, xmax, ymin, ymax: a value
    
    CHANGELOG
    - 20110910 RB: init
    
    """

    # x_min and x_max are determined by y
    if x_range[0] == 0 and x_range[1] == -1:

        # they are both dependent on each other, plot everything
        if y_range[0] == 0 and y_range[1] == -1:
            x_min = x_axis[0]
            x_max = x_axis[-1]
            y_min = y_axis[0]
            y_max = y_axis[-1]     

        # take the whole y-axis, the same for the x-axis
        # it may extend beyond the range of the data 
        elif y_range[0] == 0 and y_range[1] == 0:
            x_min = y_axis[0]
            x_max = y_axis[-1]
            y_min = y_axis[0]
            y_max = y_axis[-1]         
        
        # take part of the y-axis, the same for the x-axis
        # it may extend beyond the range of the data
        else:
            x_min = y_range[0]
            x_max = y_range[1]
            y_min = y_range[0]
            y_max = y_range[1]  
    
    else:
        # plot the whole x-axis
        if x_range[0] == 0 and x_range[1] == 0:
            x_min = x_axis[0]
            x_max = x_axis[-1]
        # plot only part of the x-axis
        else:
            x_min = x_range[0]
            x_max = x_range[1]
        
        # plot the whole y-axis
        if y_range[0] == 0 and y_range[1] == 0:
            y_min = y_axis[0]
            y_max = y_axis[-1]
        # use the range of the x-axis
        elif y_range[0] == 0 and y_range[1] == -1:
            y_min = x_min
            y_max = x_max
        # use the specified range
        else:
            y_min = y_range[0]
            y_max = y_range[1]        
                 
    return x_min, x_max, y_min, y_max    
 

def make_contours_2d(data, zlimit = 0, contours = 21):
    """
    zlimit = 0, show all, not don't care about centering around zero
    zlimit = -1, show all, centered around zero
    zlimit = all else, use that, centered around zero
    zlimit = [a,b], plot from a to b
    """
    if zlimit == 0:
        ma = numpy.amax(data)
        mi = numpy.amin(data)
        #print(mi, ma)
        return numpy.linspace(mi, ma, num=contours)
    if zlimit == -1:
        ma = numpy.amax(data)
        mi = numpy.amin(data)
        #print(mi, ma)
        if abs(mi) > abs(ma):
            ma = abs(mi)
        else:
            ma = abs(ma)
        return numpy.linspace(-ma, ma, num=contours) 
    if type(zlimit) == int:
        return numpy.linspace(-abs(zlimit), abs(zlimit), num=contours) 
    if type(zlimit) == list:
        return numpy.linspace(zlimit[0], zlimit[1], num=contours)   





def contourplot(data, x_axis, y_axis, x_range = [0, 0], y_range = [0, -1], zlimit = 0, contours = 12, filled = True, black_contour = True, x_label = "", y_label = "", title = "", diagonal_line = True, new_figure = True):

    """
    croc.Plotting.contourplot
    
    INPUT:
    - data (2d ndarray): the data, in the form of (y, x)
    - x_axis, y_axis (ndarray): the axes. Should have the same length as the corresponding axes in data
    - x_range, y_range (array with 2 elements): the range to be plotted. 
        Possible cases:
        - [min, max]: plot range min to max
        - [0, 0]: plot the whole range
        - [0, -1]: use the range from the other axis. If both have this, it will plot both axes complete. (ie. it is identical to both having [0,0])
    - zlimit (number): the z-range that will be used
        Possible cases:
        zlimit = 0, show all, not don't care about centering around zero
        zlimit = -1, show all, centered around zero
        zlimit = all else, use that, centered around zero
        zlimit = [a,b], plot from a to b
    - contours (number): number of contours to be used
    - filled (BOOL): use colors
    - black_contour (BOOL): use the black contour lines
    - x_label, y_label (string): the labels for the x and y axes
    - title (string): the title of the plot
    - diagonal_line (BOOL): plot a diagonal line
    - new_figure (BOOL): will make a new figure. To make subplots etc, set it to False
    
    """
    
    # CHECKS
    y, x = numpy.shape(data)
    if len(x_axis) != x or len(y_axis) != y:
        # oops, the shape of the data does not correspond with the axes.
        
        # see if they are switched
        if len(x_axis) == y and len(y_axis) == x:
            print("WARNING (croc.Plotting.contourplot): the shape of the data seems to be flipped. The data will be transposed.\n")
            data = data.T
        else:
            print("ERROR (croc.Plotting.contourplot): the shape of the data does not correspond with the axes. ")
            return 0

    # determine the range to be plotted
    x_min, x_max, y_min, y_max = find_axes(x_axis, y_axis, x_range, y_range)
    
    # make the contours
    # first find the area to be plotted
    # not the most elegant way I guess
    try:
        y_min_i = numpy.where(y_axis < y_min)[0][-1]
    except: 
        y_min_i = 0
    
    try:
        y_max_i = numpy.where(y_axis > y_max)[0][0]
    except: 
        y_max_i = -1

    try:
        x_min_i = numpy.where(x_axis < x_min)[0][-1]
    except: 
        x_min_i = 0
    
    try:
        x_max_i = numpy.where(x_axis > x_max)[0][0]
    except: 
        x_max_i = -1
        
    V = make_contours_2d(data[y_min_i:y_max_i, x_min_i:x_max_i], zlimit, contours)
    

    # make the actual figure
    if new_figure:
        plt.figure()
    if filled:
        plt.contourf(x_axis, y_axis, data, V, cmap = my_cmap)
    if black_contour:
        plt.contour(x_axis, y_axis, data, V, linewidths=1, linestyles="solid", colors="k")    

    
    # we only want to see a certain part of the spectrum   
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    
    if diagonal_line:
        plt.plot([0, 10000], [0, 10000], "k")
    
    # add some text
    if x_label != "":
        plt.xlabel(x_label)

    if y_label != "":
        plt.ylabel(y_label)
    
    if title != "":
        plt.title(title)    
    
    # show it!
    plt.show()     
    
    
 
    
    

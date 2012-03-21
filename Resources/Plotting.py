from __future__ import print_function
from __future__ import division

import numpy
import pylab 
import matplotlib 
import matplotlib.pyplot as plt

import croc.Debug

reload(croc.Debug)

debug_flag = croc.Debug.debug_flag


# make the colormap
cdict = {'red':   [(0.0,  0.0, 0.0),(0.475,  1.0, 1.0),(0.525,  1.0, 1.0),
            (1.0,  1.0, 1.0)],
         'green': [(0.0,  0.0, 0.0),(0.475,  1.0, 1.0),(0.525,  1.0, 1.0),
            (1.0,  0.0, 0.0)],
         'blue':  [(0.0,  1.0, 1.0),(0.475,  1.0, 1.0),(0.525,  1.0, 1.0),
            (1.0,  0.0, 0.0)]
        }
my_cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap', cdict, 256)







def linear(data, axis, x_range = [0, 0], y_range = [0, 0], x_label = "", y_label = "", title = "", new_figure = True, plot_real = True):
    
    if plot_real:
        data = numpy.real(data)
    
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

    try:
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

    except:
        if croc.Debug.FlagRunningOn == "server":
            print("ERROR (croc.Resources.Plotting.linear): no plotting available on the server!")
        else:
            raise









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
        if debug_flag:
            print("make_contours_2d, minimum, maximum")
            print(mi, ma)
        return numpy.linspace(mi, ma, num=contours)
        
    elif zlimit == -1:
        ma = numpy.amax(data)
        mi = numpy.amin(data)
        if debug_flag:
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





def contourplot(data, x_axis, y_axis, x_range = [0, 0], y_range = [0, -1], zlimit = -1, contours = 12, filled = True, black_contour = True, x_label = "", y_label = "", title = "", diagonal_line = True, new_figure = True, invert_colors = False, flag_aspect_ratio = True):

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
    - invert_colors (BOOL, False): will make the red blue and the other way around
    - flag_aspect_ratio (BOOL, True): the aspect ratio will be corresponding to the range plotted
    
    """
            
    # CHECKS
    if invert_colors:
        data = -data

    # check if the lengths of the axes correspond to the shape of the data
    y, x = numpy.shape(data)
    try:
        if len(x_axis) != x or len(y_axis) != y:
            # oops, the shape of the data does not correspond with the axes.
            
            # see if they are switched
            if len(x_axis) == y and len(y_axis) == x:
                print("\nWARNING (croc.Plotting.contourplot): the shape of the data seems to be flipped. The data will be transposed.\n")
                data = data.T
            else:
                print("\nERROR (croc.Plotting.contourplot): the shape of the data does not correspond with the axes. ")
                return 0
    except TypeError:
        print("\nERROR (croc.Plotting.contourplot): The x or y axis seems to have no length. It should be an array, not an integer.")
        print("x-axis:", x_axis)
        print("y-axis:", y_axis)
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
        y_max_i = len(y_axis)

    try:
        x_min_i = numpy.where(x_axis < x_min)[0][-1]
    except: 
        x_min_i = 0
    
    try:
        x_max_i = numpy.where(x_axis > x_max)[0][0]
    except: 
        x_max_i = len(x_axis)
    
    
    
    # now make the actual contours   
    V = make_contours_2d(data[y_min_i:y_max_i, x_min_i:x_max_i], zlimit, contours)
    
    # print some extra stuff if the debug flag is set
    if debug_flag:
        print("Range to be plotted (x_min, x_max, y_min, y_max):")
        print(x_min, x_max, y_min, y_max)
    
        print("Indices of plotted range (x_min_i, x_max_i, y_min_i, y_max_i):")
        print(x_min_i, x_max_i, y_min_i, y_max_i)
        
    if zlimit == -1:
        print("zlimit: " + str(V[-1]))
    
    try:
        # make the actual figure
        if new_figure:
            plt.figure()
    
        if filled:
                    
            plt.contourf(x_axis, y_axis, data, V, cmap = my_cmap)
            if debug_flag:
                plt.colorbar()
        if black_contour:
            if filled:
                plt.contour(x_axis, y_axis, data, V, linewidths = 1, linestyles = "solid", colors = "k")
            else:
                # this will make dashed lines for negative values
                plt.contour(x_axis, y_axis, data, V, colors = "k")            
    
        if flag_aspect_ratio and new_figure:
            # setting the aspect ration will break the subplots
            plt.axes().set_aspect("equal")

        # the diagonal line
        if diagonal_line:
            plt.plot([0, 10000], [0, 10000], "k")
    
        # we only want to see a certain part of the spectrum   
        plt.xlim(x_min, x_max)
        plt.ylim(y_min, y_max)
        
        # add some text
        if x_label != "" and x_label != "no_label":
            plt.xlabel(x_label)
    
        if y_label != "" and y_label != "no_label":
            plt.ylabel(y_label)
        
        if title != "":
            plt.title(title)    
        
        # show it!
        if new_figure:
            plt.show()     
    except:
        if croc.Debug.FlagRunningOn == "server":
            print("ERROR (croc.Resources.Plotting.contourplot): no plotting available on the server!")
        else:
            raise
    
 
    
    

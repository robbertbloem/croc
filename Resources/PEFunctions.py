"""
croc.Resources.PEFunctions

A set of functions that are needed for croc.Pe. The functions were moved here to clean up Pe.py and were selected on how easy it was to move them out, ie. they are probably not very dependent on the class-structure.


"""

from __future__ import print_function
from __future__ import division

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import croc.Resources.Plotting as P

reload(P)


def find_z(s, s_axis, x_range = [0,0], y_range = [0, -1]):
    
    # determine the range to be plotted
    x_min, x_max, y_min, y_max = P.find_axes(s_axis[2], s_axis[0], x_range, y_range)
    
    # make the contours
    # first find the area to be plotted
    # not the most elegant way I guess
    try:
        y_min_i = numpy.where(s_axis[0] < y_min)[0][-1]
    except: 
        y_min_i = 0
    
    try:
        y_max_i = numpy.where(s_axis[0] > y_max)[0][0]
    except: 
        y_max_i = len(s_axis[0])

    try:
        x_min_i = numpy.where(s_axis[2] < x_min)[0][-1]
    except: 
        x_min_i = 0
    
    try:
        x_max_i = numpy.where(s_axis[2] > x_max)[0][0]
    except: 
        x_max_i = len(s_axis[2])
        
    ma = numpy.amax(s[y_min_i:y_max_i, x_min_i:x_max_i])
    mi = numpy.amin(s[y_min_i:y_max_i, x_min_i:x_max_i])
    
    return ma, mi








def bin_info(b_axis, b_count):
    """
    croc.Pe.pefs.bin_info()
    
    Will plot some stuff related to the binning. 
    The first plot shows the amount of samples for every fringe.
    The second plot shows a histogram of the samples per bin.
    
    """

    plt.figure()
    plt.plot(b_axis[0], b_count[0], ".-")
    plt.plot(b_axis[0], b_count[1], ".-") 
    plt.plot(b_axis[0], b_count[2], ".-")
    plt.plot(b_axis[0], b_count[3], ".-")   
    plt.title("Shots per fringe (4000 = 0)")
    plt.xlabel("Fringe")
    plt.ylabel("Shots per fringe")

    plt.figure()
    plt.plot(numpy.bincount(numpy.array(b_count[0], dtype=numpy.int)))
    plt.plot(numpy.bincount(numpy.array(b_count[1], dtype=numpy.int)))
    plt.plot(numpy.bincount(numpy.array(b_count[2], dtype=numpy.int)))
    plt.plot(numpy.bincount(numpy.array(b_count[3], dtype=numpy.int)))
    plt.title("Bins with certain number of shots")
    plt.xlabel("Number of shots")
    plt.ylabel("Number of bins")
    
    plt.show()    
    



def reconstruct_counter(data, x_channel, y_channel, start_counter = 0, end_counter = 0, flag_plot = False):
    """
    croc.Resources.PEFunctions.reconstruct_counter()
    
    This function will use the feedback from the HeNe's and reconstruct the fringes. It will check whether y > 0 and whether x changes from x[i-1] < 0 to x[i+1] > 0 and whether x[i-1] < x[i] < x[i+1] (or the other way around for a count back). 
    After a count in a clockwise direction, it can only count again in the clockwise direction after y < 0. 
    
    INPUT:
    - data (2darray, channels x samples): data. 
    - start_counter (int, 0): where the count starts. 
    - flag_plot (BOOL, False): plot the x and y axis and the counts. Should be used for debugging purposes.
    - x_channel, y_channel (int): the channel with the x and y data
    
    OUTPUT:
    - m_axis (1d-ndarray, length of samples): the exact fringe for that sample
    - counter (int): the last value of the fringes. It is the same as m_axis[-1]. For legacy's sake.
    
    
    CHANGELOG:
    20110920 RB: started the function
    20111003 RB: change the way it counts. It will now not only check if the x goes through zero, it will also make sure that the point in between is actually in between. This reduced the miscounts from 80/400 t0 30/400.
    20120227 RB: moved the function to croc.Resources.PEFunctions
    
    
    """
    
    
    # put the required data in some better readable arrays
    x = data[x_channel,:]
    y = data[y_channel,:]
    
    # determine the median values
    med_x = numpy.min(x) + (numpy.max(x) - numpy.min(x))/2
    med_y = numpy.min(y) + (numpy.max(y) - numpy.min(y))/2
    
    # some stuff
    length = len(x)
    counter = start_counter
    
    # the fringe count will be written in this array
    m_axis = numpy.zeros(length)
    
    # this is the (counter-) clockwise lock
    c_lock = False
    cc_lock = False
    
    count_c = 0
    count_cc = 0
    
    count_limit = 20
    length_limit = 1500
    
    # where did the counter start
    m_axis[0] = counter
    
    if flag_plot:
        change_array = numpy.zeros(length)
    
    # do the loop
    for i in range(1, length - 1):
        # count can only change when y > 0
        if y[i] > med_y:
            if c_lock == False:
                if x[i-1] < med_x and x[i] > med_x: 
                    # add 1 to the counter
                    counter += 1        
                    
                    # lock clockwise count       
                    c_lock = True
                    
                    count_c += 1
                    
                    # if we are the beginning or end, unlock  counterclockwise 
                    if count_c < count_limit or i > length - length_limit:
                        cc_lock = False
                    else:
                        cc_lock = True
                    
                    if flag_plot:
                        change_array[i] = 0.05

            if cc_lock == False:
                if x[i-1] > med_x and x[i] < med_x:
                    counter -= 1
                    
                    cc_lock = True  
                    
                    count_cc += 1
                    
                    if count_cc < count_limit or i > length - length_limit:
                        c_lock = False
                    else:
                        c_lock = True
                    
                    if flag_plot:
                        change_array[i] = -0.05

        else:
            # we are at y<0
            # only unlock clockwise if we have more than 100 counts up
            if count_c > count_limit:              
                c_lock = False
            if count_cc > count_limit:
                cc_lock = False
            # or if we are the beginning or end
            if i < length_limit or i > length - length_limit:
                c_lock = False
                cc_lock = False
            
        m_axis[i] = counter
    
    m_axis[-1] = counter
    
    if counter == end_counter:
        correct_count = True
    else:
        correct_count = False
        #print(counter, end_counter)

    if flag_plot:        
        plt.figure()
        plt.plot(x-0.1, ".-")
        plt.plot(y+0.1, ".-")
        plt.axhline(med_y+0.1, color = "k")
        plt.axhline(med_x - 0.1, color = "k")
        plt.plot(change_array, ".")
        plt.xlabel("Shots")
        plt.ylabel("Volts")
        plt.title("x (blue), y (green) and counts up or down (red)")
        plt.show()

    return m_axis, counter, correct_count   









def angle_distribution(m, x_channel, y_channel, m_axis, k = 0, skip_first = 0, skip_last = 0, flag_normalize_circle = True, flag_scatter_plot = True, new_figure = True):   
    """
    croc.Resources.PEFunction.angle_distribution()
    
    Checks the distribution of the samples within the fringes, ie. it checks whether there is a bias-angle.
    
    CHANGELOG:
    201110xx/RB: started function
    20120227/RB: moved function outside of Pe.py
    
    INPUT:
    - m (2d-array (channels*samples)): data, with an x and y channel defined in the data structure
    - x_channel, y_channel (int): the channel where the x and y data is stored
    - m_axis (1d-array (length of samples)): the fringes corresponding to the data in m
    - k (int, 0): makes a difference between different files. 
    - skip_first (int, 0): option to skip the first n samples. The first few and last fringes the motors are stationary, which should result in the feedback not changing. This would appear as to bias the measurement.
    - skip_last (int, 0): option to skip the last n samples
    - flag_normalize_circle (BOOL, True): The circle can be a bit ellipsoid, which would bias the results. This will make the ellipsoid into a circle and prevents the bias.
    - flag_scatter_plot (BOOL, True): will make a scatter plot (fringes by angle). If false, it will make a histogram. Note that the histogram will have different colors and orientation depending on 'k'. This is to compare the different runs (2 motors, moving forward and backward).
    
    OUTPUT:
    - a graph with the distribution of points over the circle
    
    
    
    """ 
    
    l = len(m_axis)

    # select the desired part of the data
    m = m[:,skip_first:(l-skip_last)]
    m_axis = m_axis[skip_first:(l-skip_last)]
    l = len(m_axis)
    
    # determine the average of the data, select the data and subtract the average
    x_max = numpy.nanmax(m[x_channel,:])
    x_min = numpy.nanmin(m[x_channel,:]) 
    x_ave = x_min + (x_max - x_min)/2
    m_x = m[x_channel,:] - x_ave

    # determine the average etc. and normalize it so that it is a true circle        
    y_max = numpy.nanmax(m[y_channel,:])
    y_min = numpy.nanmin(m[y_channel,:]) 
    y_ave = y_min + (y_max - y_min)/2
    if flag_normalize_circle:
        m_y = (m[y_channel,:] - y_ave) * (x_max - x_min)/(y_max - y_min)
    else:
        m_y = (m[y_channel,:] - y_ave)
    
    # make the array where the angles will be written to
    m_angle = numpy.zeros(numpy.shape(m_axis))
    
    # calculate the angle
    for i in range(l):
        if m_y[i] > 0:
            m_angle[i] = numpy.arctan(m_x[i] / m_y[i]) * 180 /numpy.pi
        elif m_y[i] < 0:
            m_angle[i] = numpy.arctan(m_x[i] / m_y[i]) * 180 /numpy.pi + 180
        else:
            m_angle[i] = 0
            print("Divide by zero")
    
    if flag_scatter_plot:
    
        if new_figure:
            plt.figure()
        
        # make an - in effect - scatter plot
        plt.plot(m_axis, m_angle, "b.")
        plt.xlabel("Fringes")
        plt.ylabel("Angle (deg)")
        plt.title("Distribution of samples over the fringes (0 = top)")
         
    else:
        
        # decide on the bin size
        if l <= 1000:
            bin_size = 15 # in degrees
            n_bins = 360 / bin_size  
        elif l <= 1800:                        
            bin_size = 10 # in degrees
            n_bins = 360 / bin_size              
        elif l <= 3600:                        
            bin_size = 5 # in degrees
            n_bins = 360 / bin_size
        else:                
            bin_size = 5 # in degrees
            n_bins = 360 / bin_size
        
        # make the histogram       
        h, b_e = numpy.histogram(m_angle, bins = n_bins)
        
        # make the axis
        axis = b_e[:-1]
        
        if new_figure:
            plt.figure()
        
        # plot it
        if k == 0:
            plt.plot(axis, h, "b")
        elif k == 1:
            plt.plot(axis, h, "g")
        elif k == 2:
            plt.plot(axis, -h, "b")
        elif k == 3:
            plt.plot(axis, -h, "g")    
        
        plt.xlabel("Angle")
        plt.ylabel("Occurances")
        plt.title("Histogram of angles (negative for non-rephasing)")
        
    plt.show()
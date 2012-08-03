from __future__ import print_function
from __future__ import division

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import croc
import croc.Resources.DataClasses as DC
import croc.Resources.Plotting as PL
import croc.Resources.Mathematics as MATH
import croc.Resources.Equations as EQ
import croc.Resources.Functions as FU


    
    
def plot_lineshape_overlap(c_array, ax, index = 1, flag_CLS = False, flag_median = False):
    """
    Specialized method to plot the results from the calculation of the tilt.
    
    c_array has two Lineshape objects.
    
    """
    
    
    ax.plot([1500, 2500], [1500, 2500], c = "k")
    
    for i in range(2):
        data = c_array[i].mess.s[c_array[i].plot_y_i[0]:c_array[i].plot_y_i[1], c_array[i].plot_x_i[0]:c_array[i].plot_x_i[1]]
        x_axis = c_array[i].mess.s_axis[2][c_array[i].plot_x_i[0]:c_array[i].plot_x_i[1]]
        y_axis = c_array[i].mess.s_axis[0][c_array[i].plot_y_i[0]:c_array[i].plot_y_i[1]]
        
        V = PL.make_contours_2d(data, zlimit = -1, contours = 14)
        
        ax.contour(x_axis, y_axis, data, V, colors = c_array[i].color_overlap_array[i])
        
    markersize = 8
    linewidth = 3
    
    if flag_CLS:
        
        # plot the minima and maxima of the double lorentzian fits
#        for i in range(2):
#            
           # y = c_array[i].mess.s_axis[0][c_array[i].dl_y_i[0]:c_array[i].dl_y_i[1]]
#            
#            x = c_array[i].dl_ble
#            ax.plot(x, y, ".", c = c_array[i].color_overlap_array[i], markersize = markersize)

#            x = c_array[i].dl_esa
#            ax.plot(x, y, ".", c = c_array[i].color_overlap_array[i], markersize = markersize)
            

        # plot the linear fits of the minima and maxima
        for i in range(2):

            y = [c_array[i].mess.s_axis[0][c_array[i].dl_y_i[0] + c_array[i].l_i[0]], c_array[i].mess.s_axis[0][c_array[i].dl_y_i[0] + c_array[i].l_i[1]]] 

            x = [(y[0] - c_array[i].l_A_ble[0])/c_array[i].l_A_ble[1], (y[1] - c_array[i].l_A_ble[0])/c_array[i].l_A_ble[1]]
            ax.plot(x, y, "-", c = c_array[i].color_overlap_array[i], linewidth = linewidth)
            
#            x = [(y[0] - c_array[i].l_A_esa[0])/c_array[i].l_A_esa[1], (y[1] - c_array[i].l_A_esa[0])/c_array[i].l_A_esa[1]]
#            ax.plot(x, y, "-", c = c_array[i].color_overlap_array[i], linewidth = linewidth)

         
#    if flag_median:
#        
#        for i in range(2): 
#        
#            x_min_i, x_max_i, y_min_i, y_max_i = find_indices(c_array[i].mess.s_axis[2], c_array[i].mess.s_axis[0], c_array[i].sl_x, c_array[i].sl_y)
#            
#            x = c_array[i].mess.s_axis[2][x_min_i:x_max_i]                       
#            y = c_array[i].sl_A[:,1]
#            ax1.plot(x, y, ":", c = c_array[i].color_overlap_array[i])
#

    # plot properties
    ax.set_title("blue:" + c_array[0].objectname + "\nred: " + c_array[1].objectname)
     
#    ax.set_xlim(c_array[i].mess.s_axis[2][c_array[i].plot_x_i[0]], c_array[i].mess.s_axis[2][c_array[i].plot_x_i[1]-1])
#    ax.set_ylim(c_array[i].mess.s_axis[0][c_array[i].plot_y_i[0]], c_array[i].mess.s_axis[0][c_array[i].plot_y_i[1]-1])

#    ax.set_xlim(2090,2140)
#    ax.set_ylim(2085,2135)



    





class Lineshape(DC.ClassTools):
    """
    Some tools to calculate the line shape of spectra. The methods work for the spectra we are looking at right now, but I'm not sure how it will work out in the future. 
    
    CHANGELOG:
    20120622/RB: started the method, based on functions that were in an earlier separate script.
    
    USAGE:
    When you initialize the class, you should give it a 'mess': a spectrum. This is a leftover from when it was an independent script. Then you should set some variables. The ones with an 'i' at the end indicate a minimum and maximum index. These can be found using 'croc.Resources.Function.find_indices(axis, range). You should also set fitting parameters. 
    
    
    """
    

    def __init__(self, mess):
        """
        
        """
    
    
        self.mess = mess
        self.objectname = self.mess.objectname
        
        # double Lorentzian fit
        self.dl_x_i = [0,0]   # indices
        self.dl_y_i = [0,0]
        
        self.dl_A_in = [0,0,0, 0,0,0] # input fitting parameters
        self.dl_A = []      # fitting parameters
        self.dl_ble = []    # freq of minima 
        self.dl_esa = []    # freq of maxima

        # linear fit on min/max lorentzian fit
        self.l_i = [4, 8]       # linear fit, range, in indices OF THE INDICES OF THE DOUBLE LORENTZIAN

        self.l_A_in = [0, 1]    # fitting parameter
        self.l_A_ble = []
        self.l_A_esa = []
        
        self.l_angle_ble = 0
        self.l_angle_esa = 0
        
        self.l_slope_ble = 0
        self.l_slope_esa = 0

        ### stuff for ellipse ###
        self.e_x = [2040, 2150]
        self.e_y = [2050, 2160]
        
        self.e_dia_ble = 0
        self.e_adia_ble = 0
        self.e_ellipticity_ble = 0

        self.e_dia_esa = 0
        self.e_adia_esa = 0
        self.e_ellipticity_esa = 0

        ### center frequency using contour method ###
        # requires ellipse to run
        self.cf_ble = [0,0]
        self.cf_esa = [0,0]
        
        
        ### find peak heights ###
        self.ph_ble_x_i = [0,0]
        self.ph_ble_y_i = [0,0]
        
        self.ph_ble_max = 0
        self.ph_ble_min = 0

        self.ph_esa_x_i = [0,0]
        self.ph_esa_y_i = [0,0]
        
        self.ph_esa_max = 0
        self.ph_esa_min = 0
        
        ### find peak along w1 ###
        self.w1_peaks_x_i = [0,0]
        self.w1_peaks_y_i = [0,0]       
        
        self.w1_peaks_A_in = [0,0,0,0]
        
        self.w1_peaks = [0]
        
        ### plot related stuff ###
        self.color_array = ["b", "g", "r", "c", "m", "y", "k"]
        self.color_overlap_array = ["b", "r"]
        
        self.plot_x_i = [0,0]
        self.plot_y_i = [0,0]

  
    def fit_double_lorentzian(self, flag_plot = False, verbose = False):
        """
        For a selection of points on the w1-axis, take a cut (giving w3 vs z (intensity) plot) and fit it with a double Lorentzian. 
        """
        
        if verbose:
            print("Fit double Lorentzian for " + self.objectname)
            print("  x_min", self.dl_x_i[0], self.mess.s_axis[2][self.dl_x_i[0]])
            print("  x_max", self.dl_x_i[1], self.mess.s_axis[2][self.dl_x_i[1]])
            print("  y_min", self.dl_y_i[0], self.mess.s_axis[0][self.dl_y_i[0]])
            print("  y_max", self.dl_y_i[1], self.mess.s_axis[0][self.dl_y_i[1]])
        
        data = self.mess.s[self.dl_y_i[0]:self.dl_y_i[1], self.dl_x_i[0]:self.dl_x_i[1]]
        x_axis = self.mess.s_axis[2][self.dl_x_i[0]:self.dl_x_i[1]]
        y_axis = self.mess.s_axis[0][self.dl_y_i[0]:self.dl_y_i[1]]
    
        n_y, n_x = numpy.shape(data)
        
        y_max = numpy.zeros(n_y)
        y_min = numpy.zeros(n_y)
        
        y_out_array = numpy.zeros((n_y, 8))

        if flag_plot:
            plt.figure()
            color_array = ["b", "g", "r", "c", "m", "y", "k"]

        for i in range(n_y):
        
            y = data[i,:]

            A_out = MATH.fit(x_axis, y, EQ.rb_two_lorentzians, self.dl_A_in)        
                
            y_out_array[i,:] = A_out
    
            x_fit = numpy.arange(x_axis[0], x_axis[-1], 0.1)
            y_fit = EQ.rb_two_lorentzians(A_out, x_fit)
            
            if flag_plot:  
                plt.plot(x_fit, y_fit, c = color_array[i%len(color_array)])
                plt.plot(x_axis, y, ":", c = color_array[i%len(color_array)])
                
                        
            y_max[i] = x_fit[numpy.argmax(y_fit)]
            y_min[i] = x_fit[numpy.argmin(y_fit)]

        self.dl_ble = y_min
        self.dl_esa = y_max
        self.dl_A = y_out_array
        
        if flag_plot:
            plt.show()

    def fit_tilt(self, verbose = False):
        
        if verbose:
            print("Fit tilt for " + self.objectname)
            print("  x_min", self.dl_x_i[0], self.mess.s_axis[2][self.dl_x_i[0]])
            print("  x_max", self.dl_x_i[1], self.mess.s_axis[2][self.dl_x_i[1]])
            print("  y_min", self.dl_y_i[0] + self.l_i[0], self.mess.s_axis[0][self.dl_y_i[0] + self.l_i[0]])
            print("  y_max", self.dl_y_i[0] + self.l_i[1], self.mess.s_axis[0][self.dl_y_i[0] + self.l_i[1]])

        y = self.mess.s_axis[0][self.dl_y_i[0] + self.l_i[0]:self.dl_y_i[0] + self.l_i[1]]     

        x = self.dl_ble[self.l_i[0]:self.l_i[1]]
        self.l_A_ble = MATH.fit(x, y, EQ.linear, self.l_A_in)
        
        x = self.dl_esa[self.l_i[0]:self.l_i[1]]
        self.l_A_esa = MATH.fit(x, y, EQ.linear, self.l_A_in)
        
        self.l_angle_ble = 90 - numpy.arctan(self.l_A_ble[1]) * 180 / numpy.pi
        self.l_angle_esa = 90 - numpy.arctan(self.l_A_esa[1]) * 180 / numpy.pi
        
        self.l_slope_ble = 1 / self.l_A_ble[1]
        self.l_slope_esa = 1 / self.l_A_esa[1]
    
    def find_ellipticity_helper(self, cntr, level, axes):
    
        nlist = cntr.Cntr.trace(level/2, level, nchunk = cntr.nchunk)

        nlist = numpy.array(nlist[0])

        axes.plot(nlist[:,0], nlist[:,1], c = "k")

        x_mean = numpy.abs(numpy.max(nlist[:,0]) + numpy.min(nlist[:,0]))/2
        y_mean = numpy.abs(numpy.max(nlist[:,1]) + numpy.min(nlist[:,1]))/2

        axes.plot(x_mean, y_mean, ".")
        
        x = nlist[:,0] - x_mean
        y = nlist[:,1] - y_mean

        X, Y = FU.rb_rotate(x, y, 45 * numpy.pi/180)

        X = X + x_mean
        Y = Y + y_mean
        axes.plot(X, Y, c = "r")
        
        return X, Y

    def find_peak_center_helper(self, cntr, level, axes):

        nlist = cntr.Cntr.trace(0.9 * level, level, nchunk = cntr.nchunk)

        nlist = numpy.array(nlist[0])
        
        X = nlist[:,0]
        Y = nlist[:,1]

        X = numpy.min(X) + (numpy.max(X) - numpy.min(X))/2
        Y = numpy.min(Y) + (numpy.max(Y) - numpy.min(Y))/2
        
        axes.scatter(X, Y, c = "r", marker = "x")
        
        return X, Y

    def find_ellipticity(self, color_index = 0, new_figure = False, verbose = False):

        if verbose:
            print("Find ellipticity")
            print("  x_min", self.e_x_i[0], self.mess.s_axis[2][self.e_x_i[0]])
            print("  x_max", self.e_x_i[1], self.mess.s_axis[2][self.e_x_i[1]])
            print("  y_min", self.e_y_i[0], self.mess.s_axis[0][self.e_y_i[0]])
            print("  y_max", self.e_y_i[1], self.mess.s_axis[0][self.e_y_i[1]])

        data = self.mess.s[self.dl_y_i[0]:self.dl_y_i[1], self.dl_x_i[0]:self.dl_x_i[1]]
        x_axis = self.mess.s_axis[2][self.dl_x_i[0]:self.dl_x_i[1]]
        y_axis = self.mess.s_axis[0][self.dl_y_i[0]:self.dl_y_i[1]]

        ma, mi = self.mess.find_z(x_range = [x_axis[0], x_axis[-1]], y_range = [y_axis[0], y_axis[-1]])
        
        V = PL.make_contours_2d(data, zlimit = -1, contours = 14)
        
        if new_figure:
            fig = plt.figure()
            ax1 = fig.add_subplot(111, aspect = "equal")
            cntr = ax1.contour(x_axis, y_axis, data, V, colors = "b")  
            ax1.set_title(self.objectname)
        else:
            fig = plt.figure(1000)
            ax1 = fig.add_subplot(111, aspect = "equal")
            cntr = ax1.contour(x_axis, y_axis, data, V, colors = self.color_array[color_index % len(self.color_array)])  

        self.cf_ble = self.find_peak_center_helper(cntr, mi, ax1)
        X, Y = self.find_ellipticity_helper(cntr, mi, ax1)
        self.e_dia_ble = numpy.max(X) - numpy.min(X)
        self.e_adia_ble = numpy.max(Y) - numpy.min(Y)
        self.e_ellipticity_ble = (self.e_dia_ble**2 - self.e_adia_ble**2) / (self.e_dia_ble**2 + self.e_adia_ble**2) 

        self.cf_esa = self.find_peak_center_helper(cntr, ma, ax1)
        X, Y = self.find_ellipticity_helper(cntr, ma, ax1)
        self.e_dia_esa = numpy.max(X) - numpy.min(X)
        self.e_adia_esa = numpy.max(Y) - numpy.min(Y)
        self.e_ellipticity_esa = (self.e_dia_esa**2 - self.e_adia_esa**2) / (self.e_dia_esa**2 + self.e_adia_esa**2) 
        
        plt.show()

    def find_peak_heights(self, verbose = False):
        
        if verbose:
            print("Find peak heights for bleach of " + self.objectname)
            print("  x_min", self.ph_ble_x_i[0], self.mess.s_axis[2][self.ph_ble_x_i[0]])
            print("  x_max", self.ph_ble_x_i[1], self.mess.s_axis[2][self.ph_ble_x_i[1]])
            print("  y_min", self.ph_ble_y_i[0], self.mess.s_axis[0][self.ph_ble_y_i[0]])
            print("  y_max", self.ph_ble_y_i[1], self.mess.s_axis[0][self.ph_ble_y_i[1]])
        
        data = self.mess.s[self.ph_ble_y_i[0]:self.ph_ble_y_i[1], self.ph_ble_x_i[0]:self.ph_ble_x_i[1]]

        self.ph_ble_min = numpy.min(data)
        self.ph_ble_max = numpy.max(data)


        if verbose:
            print("Find peak heights for ESA of " + self.objectname)
            print("  x_min", self.ph_esa_x_i[0], self.mess.s_axis[2][self.ph_esa_x_i[0]])
            print("  x_max", self.ph_esa_x_i[1], self.mess.s_axis[2][self.ph_esa_x_i[1]])
            print("  y_min", self.ph_esa_y_i[0], self.mess.s_axis[0][self.ph_esa_y_i[0]])
            print("  y_max", self.ph_esa_y_i[1], self.mess.s_axis[0][self.ph_esa_y_i[1]])
        
        data = self.mess.s[self.ph_esa_y_i[0]:self.ph_esa_y_i[1], self.ph_esa_x_i[0]:self.ph_esa_x_i[1]]

        self.ph_esa_min = numpy.min(data)
        self.ph_esa_max = numpy.max(data)
        
    def find_w1_peaks(self, verbose = False):
        
        data = self.mess.s[self.w1_peaks_y_i[0]:self.w1_peaks_y_i[1], self.w1_peaks_x_i[0]:self.w1_peaks_x_i[1]]
        # x_axis = self.mess.s_axis[2][self.w1_peaks_x_i[0]:self.w1_peaks_x_i[1]]
        y_axis = self.mess.s_axis[0][self.w1_peaks_y_i[0]:self.w1_peaks_y_i[1]]        

        y = numpy.sum(data,1)
   
        A_out = MATH.fit(y_axis, y, EQ.rb_lorentzian, self.w1_peaks_A_in)
           
        self.w1_peaks[0] = A_out[1]
        
        # plt.figure()
        # plt.plot(y_axis, y)
        # t = numpy.linspace(y_axis[0], y_axis[-1], 100)
        # y_fit = EQ.rb_lorentzian(A_out, t)
        # plt.plot(t, y_fit)
        # plt.title(self.objectname)
        # plt.show()
        
        


            
            
        















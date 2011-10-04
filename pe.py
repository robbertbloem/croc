"""
pe.py

DESCRIPTION
    This file contains the data analysis details for the 2DIR setup.


CHANGELOG
    RB 20091214 - first draft.
    RB 20110908 - combined some stuff together

REMARKS
- T3 is not imported. I didn't think about it too much, but I think that would need an extra dimension or so.


"""

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import fileinput
import re

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import scipy

import croc
# to prevent a conflict with other classes (like ftir)
from croc.DataClasses import mess_data
import croc.Absorptive
import croc.Plotting
import croc.Constants
import croc.Debug

reload(croc.Debug)

if croc.Debug.reload_flag:
    reload(croc)
    reload(croc.Absorptive)
    reload(croc.Plotting)
    reload(croc.Constants)


debug_flag = croc.Debug.debug_flag

class pe(croc.DataClasses.mess_data):
    """
    croc.pe.pe
    
    This class contains all the functions to import, calculate and plot a photon-echo 2DIR spectrum.
    
    CHANGELOG
    20110910 RB: started the class, using stuff from earlier work
    20110912 RB: wrote subclasses for specific cases 
    
    
    """
    
    
    
    def __init__(self, object_name):
        """
        20101209 RB: continued
        20110910 RB: implemented the new file formats
        
        initialize the mess_data class
        
        INPUT:
        object_name (string): a name
        population_time (number): the population time in fs
        time_stamp (number): as hhmm, use 0000 for old-style
        """
        
        print("=== CROCODILE PHOTON ECHO ===")
        
        if debug_flag:
            print(">>> DEBUG MODE <<<")
        
        # photon echo has 3 dimensions: t1/w1, t2, w3
        croc.DataClasses.mess_data.__init__(self, object_name, measurements = 2, dimensions = 3)



    # plot the spectrum
    def plot(self, plot_type = "S", x_range = [0, 0], y_range = [0, -1], zlimit = -1, contours = 12, filled = True, black_contour = True, title = "", x_label = "", y_label = "", diagonal_line = True, new_figure = True):
        """
        croc.pe.plot
        
        INPUT:
        - plot_type: 'S' plots the purely absorptive spectrum (default), 'R' plots the rephasing part, 'NR' the non-rephasing part.
        
        This function will plot the purely absorptive spectrum. It is a wrapper function for croc.Plotting.contourplot. It will put the data in the right format, adds some labels etc. This should do for 99% of the cases. 
        For details about the options, see croc.Plotting.contourplot.    
        """
        
        if plot_type == "spectrum" or plot_type == "S":
            data = self.s
        elif plot_type == "rephasing" or plot_type == "R":
            data = numpy.real(numpy.exp(-1j * self.phase_rad) * self.f[0])
        elif plot_type == "non-rephasing" or plot_type == "NR":
            data = numpy.real(numpy.exp(1j * self.phase_rad) * self.f[1])  
        else:
            print("ERROR (croc.pe.plot): invalid plot type. ")
            return 0
        
        x_axis = self.s_axis[2]
        y_axis = self.s_axis[0]
        
        if x_label == "":
            x_label = "w3 (" + str(self.s_units[2]) + ")"
        if y_label == "":
            y_label = "w1 (" +  str(self.s_units[0]) + ")"
        
        if title == "":
            title = self.objectname + ", t2: " + str(self.r_axis[1]) + "\n scans x shots: " + str(self.n_scans) + "x" + str(self.n_shots)
        
               
        croc.Plotting.contourplot(data, x_axis, y_axis, x_range = x_range, y_range = y_range, zlimit = zlimit, contours = contours, filled = filled, black_contour = black_contour, title = title, x_label = x_label, y_label = y_label, diagonal_line = diagonal_line, new_figure = new_figure)  




    # plot the rephasing part of the spectrum
    def plot_R(self, x_range = [0, 0], y_range = [0, -1], zlimit = -1, contours = 12, filled = True, black_contour = True, title = "", x_label = "", y_label = "", new_figure = True): 
    
        print("ADVISE (croc.pe.plot_R): The function only calls croc.pe.plot(plot_type='R'), but may not be completely up-to-date.\n")                      
        self.plot(plot_type = "R", x_range = x_range, y_range = y_range, zlimit = zlimit, contours = contours, filled = filled, black_contour = black_contour, title = title, x_label = x_label, y_label = y_label, new_figure = new_figure)  

  
    # plot the non-rephasing part of the spectrum
    def plot_NR(self, x_range = [0, 0], y_range = [0, -1], zlimit = -1, contours = 12, filled = True, black_contour = True, title = "", x_label = "", y_label = "", new_figure = True):          
    
        print("ADVISE (croc.pe.plot_NR): The function only calls croc.pe.plot(plot_type='NR'), but may not be completely up-to-date.\n")          
        self.plot(plot_type = "NR", x_range = x_range, y_range = y_range, zlimit = zlimit, contours = contours, filled = filled, black_contour = black_contour, title = title, x_label = x_label, y_label = y_label, new_figure = new_figure)


    # plot the time domain
    def plot_T(self, pixel = 0, x_range = [0, 0], y_range = [0, 0], zlimit = -1, contours = 12, filled = True, black_contour = True, title = "", x_label = "", y_label = "", new_figure = True, flag_no_units = False):
        """
        croc.pe.plot_T
        
        This function will plot the measured data, still in the time domain. It is a wrapper function for croc.Plotting.contourplot. It will put the data in the right format, adds some labels etc. This should do for 99% of the cases. 
        For details about the options, see croc.Plotting.contourplot.    
        """
        
        # concatenate the two diagrams
        data = numpy.concatenate((numpy.flipud(self.r[1]), self.r[0])).T
        
        x_axis = numpy.concatenate((-numpy.flipud(self.r_axis[0]), self.r_axis[0]))
         
        if flag_no_units == False:
            y_axis = self.r_axis[2]
            
            if x_label == "":
                x_label = "Time (" + str(self.r_units[0]) + ")"
            if y_label == "":
                y_label = "Frequency (" + str(self.r_units[2]) + ")"
                
                  
        else:
            x_axis = 4000 + x_axis / 2.11
            y_axis = numpy.arange(len(self.r_axis[2]))
            if x_label == "":
                x_label = "Fringes"
            if y_label == "":
                y_label = "Pixels"

        
        if pixel == 0:
            croc.Plotting.contourplot(data, x_axis, y_axis, x_range = x_range, y_range = y_range, zlimit = zlimit, contours = contours, filled = filled, black_contour = black_contour, title = title, x_label = x_label, y_label = y_label, new_figure = new_figure,  diagonal_line = False)  
        
        else:
            croc.Plotting.linear(data[pixel,:], x_axis, x_range = [0, 0], y_range = [0, 0], x_label = "Time (fs)", y_label = "Absorbance", title = "Time", new_figure = True)







class pe_sub(pe):

    """
    croc.pe.pe_sub
    
    This subclass of croc.pe.pe contains the specifics for when two measurements are subtracted from each other. 
    
    INPUT:
    - objectname: a name
    - class_plus: a class
    - class_min: the class that will be subtracted
    
    CHANGELOG:
    20110912 RB: split this of croc.pe.pe
    
    """

    def __init__(self, objectname, class_plus, class_min):
        
        croc.Pe.pe.__init__(self, objectname)

        self.s = class_plus.s - class_min.s
        self.s_axis[0] = class_plus.s_axis[0]
        self.s_axis[1] = class_plus.s_axis[1]
        self.s_axis[2] = class_plus.s_axis[2]
        self.comment = ("Subtraction of " + class_plus.objectname + " with " + class_min.objectname)

    
    

    


class pe_exp(pe):
    """
    croc.pe.pe_exp
    
    This subclass of croc.pe.pe contains the specifics for experimentally measured 2DIR measurements. 
    
    
    """


    def __init__(self, objectname, base_filename, population_time, undersampling, time_stamp = 0000):
    
        croc.Pe.pe.__init__(self, objectname)
        
        self.base_filename = base_filename
        self.r_axis[1] = population_time
        self.undersampling = undersampling
        self.time_stamp = time_stamp   
        self.path = self.base_filename + "_" + str(self.time_stamp) + "_T" + str(self.r_axis[1]) + "/"     
        

         
        
    def import_data(self, scans = [0], noise = True, meta = True):
        """
        croc.pe.import_data
        
        Imports data from experimentally measured spectra.
        
        INPUT
        - scans: 
            - [0]: import file where everything is already averaged
            - [n]: import scan n
            - [a, b, c]: import scans a, b, c and average them
        - noise: will also load the noise files (only for new-style)
        - meta: will also load the meta-file (only for new-style)
        
        CHANGELOG:
        20110910 RB: started
        
        """
        
        # this method will always import experimental data
        self.mess_type = "exp"
        
        # determine old-style or new-style
        if self.time_stamp == 0000:
            print("not implemented yet")
        
        # new-style
        else:  
            # construct the file name  
            filebase = self.path + self.base_filename + "_" + str(self.time_stamp) + "_T" + str(self.r_axis[1])
            
             # import a single scan
            if len(scans) == 1:
                
                # import the averaged data
                if scans[0] == 0:
                    file_R = filebase + ".dat"
                    file_NR = filebase + "_NR.dat"
                    
                    if noise:
                        file_R_noise = filebase + "_R_noise.dat"
                        file_NR_noise = filebase + "_NR_noise.dat"                    
                
                # import a single scan
                else:
                    file_R = filebase + "_R_" + str(scans[0]) + ".dat"
                    file_NR = filebase + "_NR_" + str(scans[0]) + ".dat"
                    
                    if noise:
                        file_R_noise = filebase + "_R_" + str(scans[0]) + "_noise.dat"
                        file_NR_noise = filebase + "_NR_" + str(scans[0]) + "noise_.dat"                     
                
                # load the actual data
                try:
                    temp = numpy.loadtxt(file_R)
                except IOError:
                    print("ERROR (croc.pe.import_data): unable to load file:", file_R)
                    raise
                    return 0   
                self.r_axis[0] = temp[1:,0]
                self.r_axis[2] = temp[0,1:]
                self.r[0] = temp[1:,1:]
                
                try:
                    temp = numpy.loadtxt(file_NR)
                except IOError:
                    print("ERROR (croc.pe.import_data): unable to load file:", file_NR)
                    raise
                    return 0
                self.r[1] = temp[1:,1:]               
                
                if noise:
                    try:
                        temp = numpy.loadtxt(file_R_noise)
                    except IOError:
                        print("ERROR (croc.pe.import_data): unable to load file:", file_R_noise)
                        raise
                        return 0
                    self.r_noise[0] = temp[1:,1:]                   
                        
                    try:
                        temp = numpy.loadtxt(file_NR_noise)
                    except IOError:
                        print("ERROR (croc.pe.import_data): unable to load file:", file_NR_noise)
                        raise
                        return 0
                    self.r_noise[1] = temp[1:,1:]     
            
                # fill in some details 
                self.r_units = ["fs", "fs", "cm-1"]
                self.r_resolution = [(self.r_axis[0][1] - self.r_axis[0][0]), 0, (self.r_axis[2][1] - self.r_axis[2][0])]   
                self.n_steps = len(self.r_axis[0])         
            
            
            # import multiple scans and average them
            else:
                print("ERROR (croc.pe.import_data): The ability to import specific scans is not yet implemented.")
                return 0
            
            # import the meta data
            if meta: 
                self.import_meta()  
            
                     
                
                
    def import_meta(self):
        """
        croc.pe.import_meta
        
        Import data from the meta-data files.

        INPUT: 
        - a class
        
        COMMENTS
        - it will scan the meta-file for n_scans, n_shots, phase and comments
        
        CHANGELOG
        RB 20110909: started function        
        
        
        """
        
        temp_scans = 0
        
        # construct file name
        filebase = self.path + self.base_filename + "_" + str(self.time_stamp) + "_T" + str(self.r_axis[1]) + "_meta.txt"
        
        # close older files
        fileinput.close()
        
        # found at: http://docs.python.org/library/re.html#matching-vs-searching , is equivalent to scanf(..%f..)
        regex = re.compile("[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?")
        
        # scan the file
        try:
            for line in fileinput.input(filebase):
            
                if re.match("Shots", line): 
                    self.n_shots = int((re.search(regex, line)).group())
            
                #if re.match("Phase", line):
                #    self.phase_degrees = float((re.search(regex, line)).group()) + 180.0
                
                if re.match("Comments", line):
                    self.comment = line[9:]
                    
                if re.match("Scan", line):
                    temp_scans = int((re.search(regex, line[4:7])).group())
        except IOError:
            print("ERROR (croc.pe.import_meta): unable to load file:", filebase)
            raise
            return 0            
  
        # close the file     
        fileinput.close()
        
        # number of scans is (number of scans started) - 1, because the last one wasn't finished
        if temp_scans:
            self.n_scans = temp_scans - 1
        else:
            self.n_scans = 1









    def fourier_helper(self, array, window_function = "none", window_length = 0, flag_plot = False):
        """
        fourier_helper
        
        20101204/RB: started
        20110909 RB: continued
        
        This is a function to Fourier Transform experimental 2DIR spectra, ie, spectra with a time and frequency axis. It basically repeats the Fourier function for all pixels.
        
        INPUT:
        - array (numpy.ndarray): a 2d array of time * pixels
        - window_function (name, "none"): "none", "guassian" etc
        - window_length (int, 0): length of the window. 0 means the whole range
        - flag_plot (BOOL, False): will plot the windowed time domain
         
        """
    
        # you need a new array that also has complex numbers  
        # the length depends on zeropadding      
        [x, y] = numpy.shape(array)
        if self.zeropad_to != None:
            x = self.zeropad_to
        ft_array = numpy.reshape( numpy.zeros(x*y, dtype=numpy.cfloat), (x, y))

        # iterate over all the pixels
        
        for i in range(y):
            ft_array[:,i] = croc.Absorptive.fourier(array[:,i], zero_in_middle = False, first_correction = True, zeropad_to = self.zeropad_to, window_function = window_function, window_length = window_length, flag_plot = flag_plot)  
            flag_plot = False
        return ft_array  
        
      
        
          


  
                
    def absorptive(self, window_function = "none", window_length = 0, flag_plot = False):
        """
        croc.pe.fourier
        
        This function does the Fourier transform.
        It checks the undersampling.
        It phases the spectrum.
        It makes the axes.
        
        INPUT:
        - window_function (name, "none"): "none", "guassian" etc
        - window_length (int, 0): length of the window. 0 means the whole range
        - flag_plot (BOOL, False): will plot the windowed time domain
        
        """
        
        # CHECKS
        # checks the undersampling. It can be 0, but that is hardly used
#         if self.undersampling == 0:
#             print("\nWARNING (croc.pe.pe_exp.absorptive): undersampling is 0!\n")
        
        # do the fft
        # copy the arrays to prevent changing the originals
        try:
            self.f[0] = self.fourier_helper(numpy.copy(self.r[0]), window_function = window_function, window_length = window_length, flag_plot = flag_plot)
            self.f[1] = self.fourier_helper(numpy.copy(self.r[1]), window_function = window_function, window_length = window_length, flag_plot = flag_plot)
        except ValueError:
            print("\nERROR (croc.pe.pe_exp.absorptive): Problem with the Fourier Transforms. Are r[0] and r[1] assigned?")
            return 0
        
        # phase the spectrum
        self.s = numpy.real(numpy.exp(-1j * self.phase_rad) * self.f[0] + numpy.exp(1j * self.phase_rad) * self.f[1])
        
        # select part of the data
        if self.undersampling % 2 == 0:
            self.f[0] = self.f[0][:(len(self.f[0])/2)][:]
            self.f[1] = self.f[1][:(len(self.f[1])/2)][:]
            self.s = self.s[:(len(self.s)/2)][:]
        else:
            self.f[0] = self.f[0][(len(self.f[0])/2):][:]
            self.f[1] = self.f[1][(len(self.f[1])/2):][:]
            self.s = self.s[(len(self.s)/2):][:]        
        
        # fix the axes
        try:
            self.s_axis[0] = croc.Absorptive.make_ft_axis(length = 2*numpy.shape(self.s)[0], dt = self.r_axis[0][1]-self.r_axis[0][0], undersampling = self.undersampling)
        except TypeError:
            print("\nERROR (croc.pe.pe_exp.absorptive): Problem with making the Fourier Transformed axis. Is r_axis[0] assigned?")
            return 0
            
        self.s_axis[0] = self.s_axis[0][0:len(self.s_axis[0])/2]
        self.s_axis[2] = self.r_axis[2] + self.r_correction[2]  
        
        # add some stuff to self
        self.s_units = ["cm-1", "fs", "cm-1"]
        try:
            self.s_resolution = [(self.s_axis[0][1] - self.s_axis[0][0]), 0, (self.s_axis[2][1] - self.s_axis[2][0])]
        except TypeError:
            print("\nERROR (croc.pe.pe_exp.absorptive): The resolution of the spectrum can not be determined. This can mean that the original axes (r_axis) or the spectral axes (s_axis) contains an error.")
            print("r_axis[0]:", self.r_axis[0])
            print("r_axis[2]:", self.r_axis[2])
            print("s_axis[0]:", self.s_axis[0])
            print("s_axis[2]:", self.s_axis[2])
            return 0                
            
            



class pefs(pe_exp):

    """
    croc.Pe.pefs
    
    Data processing for fast scanning.

    
    
    """

    def __init__(self, objectname, base_filename, population_time, time_stamp):
    
        """
        croc.Pe.pefs.__init__
        
        This will init the pefs-class. 
        
        INPUT:
        - objectname (string): a name
        - base_filename (string): the base name of the file ("azide") or so
        - population_time (integer): the population time in fs
        - time_stamp (integer): when the measurement started.
        
        SPECIAL STUFF:
        Fast scanning will result in more data. This is why the data should not be imported, but should be added. The addition of data is done in add_data. Each shot will be assigned a fringe. Then the data is binned per fringe. This is saved in self.b, the particular fringes in self.b_axis and the count of how much data there is in each bin is saved in self.b_count. 
        Each measurement can be added to these bins. Then the rephasing and non-rephasing diagram can be constructed. 
        
        
        
        """
        
        croc.Pe.pe.__init__(self, objectname)
        
        self.base_filename = base_filename
        self.r_axis[1] = population_time   
        self.time_stamp = time_stamp   
        #self.path = self.base_filename + "_" + str(self.time_stamp) + "_T" + str(self.r_axis[1]) + "/"  
        
        self.mess_type = "FastScan"
        
        # self.b* will contain the data, binned, but not yet averaged. This allows for easy adding of data.
        self.b = [0] * 2  
        self.b_axis = [0] * 2
        self.b_count = [0] * 2
        
        self.n = [[],[]]
#        self.n0 = numpy.ndarray([0])
#        self.n1 = numpy.ndarray([0])
        
        # some channels have a special meaning
        self.n_channels = 37
        self.x_channel = 32
        self.y_channel = 33
        self.chopper_channel = 36
        
        self.n_pixels = 32
        
        # the number of fringes should be nearly the same, but this will 
        self.extra_fringes = 20
        
        self.imported_scans = []

        self.reference = []
        
        self.incorrect_count = [0,0,0,0]





    def import_reference(self):

        filename = self.path + self.base_filename + "_" + str(self.time_stamp) + "_T" + str(self.r_axis[1]) + "_ref.dat"
                
        data = numpy.loadtxt(filename)
        
        self.r_axis[2] = data[0,1:(self.n_pixels+1)]
        
        self.reference = data[1,1:]
        
        
        
        
                

    
    def add_data(self, 
        scan, 
        flag_import_override = False, 
        flag_construct_r = True, 
        flag_calculate_noise = False, 
        flag_find_correlation = False, 
        flag_find_angle = False):
        """
        Adds data for a single scan.
        The data is imported as data.
        Then it is written to m as channel * shot. m_axis contains the fringe for that shot.
        Then it is binned to self.b. In self.b_axis the corresponding fringes are written. In self.b_count contains how many data points are in that bin.
        All three self.b* are a bit longer than the amount of shots, to make up for variations between measurements.
        
        INPUT:
        - scan (integer): the number of the scan to be imported
        - flag_import_override (BOOL, False): If set to False, it will prevent a scan from being re-imported. If set to True, it will give a warning, but will continue anyway.
        - flag_construct_r (BOOL, True): will construct self.r at the end.  
        - flag_calculate_noise (BOOL, False): (experimental) will calculate the noise
        - flag_find_correlation (BOOL, False): (experimental) will calculate the correlation function
        - flag_find_angle (BOOL, False): (experimental) will show the distribution of the measured points
        
        """
        
        if len(self.imported_scans) == 0:
            self.import_reference()
            self.import_meta()
    
        # see if we already imported this file
        if self.imported_scans.count(scan) != 0:
            if flag_import_override == False: 
                print("ERROR (croc.Pe.pefs.add_data): Scan is already imported.")  
                return 0
            else:
                print("WARNING (croc.Pe.pefs.add_data): Scan is already imported, but will be imported anyway because flag_import_override is set to True.")
            
        # construct filenames
        filename = [0] * 4  # the filenames

        filename[0] = self.path + self.base_filename + "_" + str(self.time_stamp) + "_T" + str(self.r_axis[1]) + "_R1" + "_" + str(scan) + ".bin"
        filename[1] = self.path + self.base_filename + "_" + str(self.time_stamp) + "_T" + str(self.r_axis[1]) + "_R2" + "_" + str(scan) + ".bin"
        filename[2] = self.path + self.base_filename + "_" + str(self.time_stamp) + "_T" + str(self.r_axis[1]) + "_NR1" + "_" + str(scan) + ".bin"
        filename[3] = self.path + self.base_filename + "_" + str(self.time_stamp) + "_T" + str(self.r_axis[1]) + "_NR2" + "_" + str(scan) + ".bin"

        # for the 4 files
        for k in range(4):
        
            # to distuinguish between the two diagrams
            if k < 2:
                diagram = 0
            else:
                diagram = 1
            
            # import the data
            [m, fringes] = self.import_raw_data(filename[k])
            
            # reconstruct the counter
            m_axis, counter = self.reconstruct_counter(m, fringes[0])
            
            if k == 0:
                n_fringes = counter - 4000
            
            # check for consistency
            if counter != fringes[1]:
                print("\nWARNING (croc.Pe.pefs.add_data): There is a miscount with the fringes!")
                print("Scan: ", scan, ", File:", k, "\n")
                self.incorrect_count[k] += 1

            # if it is consistent, continue
            else:
                print("Scan: ", scan, ", File:", k, "Count is correct!")
            
                # make b the correct size, if it isn't already
                if numpy.shape(self.b_axis)[-1] == 2:
                    self.b = [numpy.zeros((n_fringes + 2 * self.extra_fringes, self.n_channels))] * 4
                    self.b_axis[0] = numpy.arange(- self.extra_fringes, n_fringes + self.extra_fringes)
                    self.b_axis[1] = numpy.arange(- self.extra_fringes, n_fringes + self.extra_fringes)
                    self.b_count = numpy.zeros((4, n_fringes + 2 * self.extra_fringes))
                    self.r = [numpy.zeros((n_fringes + self.extra_fringes, 32))] * 2
            
                # bin the data
                self.bin_data(m, m_axis, diagram, flag_calculate_noise = flag_calculate_noise)
                
                # calculate the noise
                if flag_calculate_noise:
                    self.bin_for_noise(m, m_axis, diagram)
                    
                if flag_find_correlation:
                    self.find_correlation(m)
                    
                if flag_find_angle:
                    self.find_angle(m, m_axis, k)

                # all the data is now written into self.b* 

        # construct the actual measurement
        if flag_construct_r:
            self.construct_r(flag_calculate_noise = flag_calculate_noise)

        # now append that we imported this scan
        self.imported_scans.append(scan)
        
        self.n_scans = len(self.imported_scans)



    def import_raw_data(self, path_and_filename):
        
        # import the data
        data = numpy.fromfile(path_and_filename) 
       
        # read the fringes and remove them from the measurement data
        fringes = [data[-2], data[-1]]
        data = data[:-2]
        
        # determine the length
        if self.n_shots == 0:
            self.n_shots = int(numpy.shape(data)[0] / self.n_channels)            
        
        # construct m
        m = numpy.zeros((self.n_channels, self.n_shots))
        
        # order the data in a 2d array
        for i in range(self.n_shots):
            for j in range(self.n_channels):
                m[j, i] = data[j + i * self.n_channels] 
        
        return m, fringes



    def find_correlation(self, m):
        
        n_channels, n_shots = numpy.shape(m)
        
        # select the channel we want to use
        channel = 16
        
        # select the data we want to use
        m_x = m[channel,:] 
        
        # fix that is proposed for numpy, but not implemented yet
        a = (m_x - numpy.mean(m_x)) / (numpy.std(m_x) * len(m_x))
        v = (m_x - numpy.mean(m_x)) /  numpy.std(m_x)
        
        # calculate the autocorrelation
        r = numpy.correlate(a,v, mode="full")
        
        # select the part we want
        r = r[len(r)/2:]

        # plot it
        plt.plot(r)




    def find_angle(self, m, m_axis, k = 0, skip_first = 0, skip_last = 0, flag_normalize_circle = True, flag_scatter_plot = True):   
        """
        croc.pe.pefs.find_angle()
        
        Checks the distribution of the samples within the fringes, ie. it checks whether there is a bias-angle.
        
        INPUT:
        - m (2d-array (channels*samples)): data, with an x and y channel defined in the data structure
        - m_axis (1d-array (length of samples)): the fringes corresponding to the data in m
        - k (int, 0): makes a difference between different files. 
        - skip_first (int, 0): option to skip the first n samples. The first few and last fringes the motors are stationary, which should result in the feedback not changing. This would appear as to bias the measurement.
        - skip_last (int, 0): option to skip the last n samples
        - flag_normalize_circle (BOOL, True): The circle can be a bit ellipsoid, which would bias the results. This will make the ellipsoid into a circle and prevents the bias.
        - flag_scatter_plot (BOOL, True): will make a scatter plot (fringes by angle). If false, it will make a histogram. Note that the histogram will have different colors and orientation depending on 'k'. This is to compare the different runs (2 motors, moving forward and backward).
        
        
        
        """ 
        
        l = len(m_axis)

        # select the desired part of the data
        m = m[:,skip_first:(l-skip_last)]
        m_axis = m_axis[skip_first:(l-skip_last)]
        l = len(m_axis)
        
        # determine the average of the data, select the data and subtract the average
        x_max = numpy.nanmax(m[self.x_channel,:])
        x_min = numpy.nanmin(m[self.x_channel,:]) 
        x_ave = x_min + (x_max - x_min)/2
        m_x = m[self.x_channel,:] - x_ave

        # determine the average etc. ALSO: normalize it so that it is a true circle        
        y_max = numpy.nanmax(m[self.y_channel,:])
        y_min = numpy.nanmin(m[self.y_channel,:]) 
        y_ave = y_min + (y_max - y_min)/2
        if flag_normalize_circle:
            m_y = (m[self.y_channel,:] - y_ave) * (x_max - x_min)/(y_max - y_min)
        else:
            m_y = (m[self.y_channel,:] - y_ave)
        
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

            # plot it
            if k == 0:
                plt.plot(axis, h, "b")
            elif k == 1:
                plt.plot(axis, h, "g")
            elif k == 2:
                plt.plot(axis, -h, "b")
            elif k == 3:
                plt.plot(axis, -h, "g")    


    def bin_for_noise(self, m, m_axis, diagram):
        
        b_fringes = len(self.b_axis[0]) 
        
        n_shots = len(m_axis)
        
        b = numpy.zeros((2, b_fringes, self.n_channels))
        b_count = numpy.zeros((2, b_fringes))
        
        r = numpy.zeros((b_fringes - self.extra_fringes, 32)) 
        
        
        for i in range(n_shots):            
            # find the fringe
            j = (-1)**diagram * int(m_axis[i]) + self.extra_fringes - (-1)**diagram * 4000

            # add it to the bin, depending on pem-state and diagram
            # and add 1 to counter 
            if m[self.chopper_channel, i] < 2.5:         
                b[0, j, :] += m[:,i] 
                b_count[0, j] += 1
            else:
                b[1, j, :] += m[:,i] 
                b_count[1, j] += 1        
        
        temp = numpy.zeros((2, b_fringes, self.n_channels))
        
        # average the data for the two diagrams
        for j in range(2):
            for i in range(b_fringes):
                if b_count[j][i] != 0:
                    temp[j,i,:] = b[j,i,:] / b_count[j][i]    
                else:    
                    temp[j,i,:] = 0                
        
        # now only select the part where fringes are not negative
        temp = temp[:,self.extra_fringes:,:self.n_pixels]
        
        # now convert it to mOD
        r[:,:self.n_pixels] = -numpy.log10(1+ 2*(temp[0,:,:self.n_pixels] - temp[1,:,:self.n_pixels])/self.reference[:self.n_pixels])
        
        r = numpy.nan_to_num(r)
        
        f = self.fourier_helper(numpy.copy(r))
        
        f = f[:len(f)/2]
        
        self.n[diagram].append(f)  
        
        if diagram == 1:
            plt.plot(numpy.abs(r[:,14]))
    
        


    def calculate_noise(self, pixel = 12):
        
        if numpy.shape(self.n)[1] != 0:
        
            shape0 = numpy.shape(self.n[0])
            shape1 = numpy.shape(self.n[1])
            #print(shape)
            
            std0 = numpy.zeros((shape0[1]))
            std1 = numpy.zeros((shape1[1]))
            
            #f0 = numpy.zeros((shape0[1]))
            #f1 = numpy.zeros((shape1[1]))        
            
            a0 = numpy.zeros(shape0[1])
            a1 = numpy.zeros(shape1[1])
    
            for i in range(shape0[1]): # frequency
                for j in range(shape0[0]): # scans
                    a0[j] = self.n[0][j][i][pixel]
                
                std0[i] = numpy.std(a0)
                #f0[i] = numpy.mean(a0)
    
            for i in range(shape1[1]): # frequency
                for j in range(shape1[0]): # scans
                    a1[j] = self.n[1][j][i][pixel]
                
                std1[i] = numpy.std(a1)
                #f1[i] = numpy.mean(a1)
    
            plt.figure()
            plt.plot(self.s_axis[0], std0[:])
            plt.plot(self.s_axis[0], std1[:])
            
            plt.show()
        
        else:
            print("ERROR (croc.pe.pefs.calculate_noise): There is no data to work with. Make sure that during the import you select 'flag_calculate_noise'. ")
        
        
        
        
        
        

        
        
        
        
        
        
        


    def bin_data(self, m, m_axis, diagram, flag_calculate_noise = False):
    
        n_shots = len(m_axis)
        
        for i in range(n_shots):            
            # find the fringe
            j = (-1)**diagram * int(m_axis[i]) + self.extra_fringes - (-1)**diagram * 4000

            # add it to the bin, depending on pem-state and diagram
            # and add 1 to counter 
            if m[self.chopper_channel, i] < 2.5:         
                self.b[2 * diagram][j, :] += m[:,i] 
                self.b_count[2 * diagram, j] += 1
            else:
                self.b[2 * diagram + 1][j, :] += m[:,i] 
                self.b_count[2 * diagram + 1, j] += 1



    def bin_info(self):
        plt.figure()
        plt.plot(self.b_axis[0], self.b_count[0], ".-")
        plt.plot(self.b_axis[0], self.b_count[1], ".-") 
        plt.plot(self.b_axis[0], self.b_count[2], ".-")
        plt.plot(self.b_axis[0], self.b_count[3], ".-")   
        plt.title("Shots per fringe (4000 = 0)")
        plt.xlabel("Fringe")
        plt.ylabel("Shots per fringe")

        plt.figure()
        plt.plot(numpy.bincount(numpy.array(self.b_count[0], dtype=numpy.int)))
        plt.plot(numpy.bincount(numpy.array(self.b_count[1], dtype=numpy.int)))
        plt.title("Bins with certain number of shots")
        plt.xlabel("Number of shots")
        plt.ylabel("Number of bins")
        
        plt.show()           
        




    def construct_r(self, flag_calculate_noise = False):
    
        n_fringes = len(self.b_axis[0])
        
        temp = numpy.zeros((4, n_fringes, self.n_channels))
        
        # average the data for the two diagrams
        for j in range(4):
            for i in range(n_fringes):
                if self.b_count[j][i] != 0:
                    temp[j,i,:] = self.b[j][i,:] / self.b_count[j][i]    
                else:    
                    temp[j,i,:] = 0                
        
        # now only select the part where fringes are not negative
        temp = temp[:,self.extra_fringes:,:self.n_pixels]
              
        # make the r_axis
        self.r_axis[0] = self.b_axis[0][self.extra_fringes:] * croc.Constants.hene_fringe_fs

        # now convert it to mOD
        for j in range(2):
            self.r[j][:,:self.n_pixels] = -numpy.log10(1+ 2*(temp[2*j,:,:self.n_pixels] - temp[2*j+1,:,:self.n_pixels])/self.reference[:self.n_pixels])
        
        self.r = numpy.nan_to_num(self.r)
        
        self.r_units = ["fs", "fs", "cm-1"]



       

                
    
    
    
    
    
    def reconstruct_counter(self, data, start_counter):
        
        # put the required data in some better readable arrays
        x = data[self.x_channel,:]
        y = data[self.y_channel,:]
        
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
        
        # where did the counter start
        m_axis[0] = counter
        
        #change_array = numpy.zeros(length)
        
        # do the loop
        for i in range(1, length - 1):
            # count can only change when y > 0
            if y[i] > med_y:
                if c_lock == False:
                    if x[i-1] < med_x and x[i+1] > med_x and x[i-1] < x[i] and x[i+1] > x[i]: 
                        counter += 1               
                        c_lock = True
                        cc_lock = False
                        
                        #change_array[i] = 0.05

                if cc_lock == False:
                    if x[i-1] > med_x and x[i+1] < med_x and x[i-1] > x[i] and x[i+1] < x[i]:
                        counter -= 1
                        c_lock = False
                        cc_lock = True  
                        
                        #change_array[i] = -0.05

            else:
                c_lock = False
                cc_lock = False
            
            m_axis[i] = counter
        
        m_axis[-1] = counter
        
#         plt.figure()
#         plt.plot(x, ".-")
#         plt.plot(y, ".-")
#         plt.plot(change_array, ".")
#         plt.show()

        return m_axis, counter     
























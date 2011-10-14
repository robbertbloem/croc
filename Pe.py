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
import os.path

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


def make_pickle_name(base_filename, pop_time, time_stamp, path = ""):
    return path + base_filename + "_" + str(time_stamp) + "_T" + str(pop_time) + ".pickle"

def make_path(base_filename, pop_time, time_stamp, path = ""):
    return path + base_filename + "_" + str(time_stamp) + "_T" + str(pop_time) + "/"

def check_pickle_exists(path_and_filename):
    return os.path.exists(path_and_filename)






def import_data(mess_date, import_mess, import_from, import_to, mess_array,
        flag_calculate_noise = False,
        flag_no_pickle = False
    ):
    """
    croc.Croc.import_data()
    
    Imports data and saves it into a pickle.
    
    
    
    """
    if import_from == 0 or import_to == 0:
        return 0
    else:
    
        # first check if mess_i actually exists
        try:
            mess_array[import_mess]
            
            # default name of the pickle
            # use the _fs postfix to differentiate it from other pickles
            pickle_name = str(mess_date) + "_fs.pickle"
            
            # first, check if there is a pickle
            if croc.Pe.check_pickle_exists(pickle_name):
                # found a pickle, now import it
                print("Found pickle")
                mess = croc.DataClasses.import_db(pickle_name)
            else:
                # there is no pickle, so make a new a new data structure
                print("No pickle found")
                mess = [0]
                mess[0] = croc.Pe.pefs(mess_array[0][0], mess_array[0][1], mess_array[0][2], mess_array[0][3])
            
            # see if we have to extend mess to fit with mess_array
            if len(mess) < len(mess_array):
                for i in range(len(mess_array)):
                    try:
                        # this works if mess[i] exists
                        mess[i].objectname
                    except IndexError:
                        # it does not work if it does not exists
                        mess.append(croc.Pe.pefs(mess_array[i][0], mess_array[i][1], mess_array[i][2], mess_array[i][3]))
                        
            # pickle can confuse the order of measurements
            # use the unique object names to find the correct one
            for i in range(len(mess)):
                if mess[i].objectname == mess_array[import_mess][0]:
                    mess_i = i
                
            # construct the import range
            import_range = range(import_from, import_to + 1)
            
            flag_change = False
            
            # import the data
            for i in import_range:
                print("Importing object: " + mess[mess_i].objectname + ", scan:", str(i))
                result = mess[mess_i].add_data(scan = i, flag_construct_r = False, flag_calculate_noise = flag_calculate_noise)
                
                if result == True:  
                    flag_change = True
            
            if flag_no_pickle == False:
                if flag_change:
                    print("Updating pickle...")
                    croc.DataClasses.make_db(mess, pickle_name)
                else:
                    print("No need to update pickle...")
            else:
                print("flag_no_pickle == True")
        
        except IndexError:
            # mess_i does not exist
            print("ERROR (script_import.py): mess_i is outside of the range of mess_array")
            
          
      
      
      
      
      
        
def print_summary(object_array):
    print("")
    
    for i in range(len(object_array)):
        print("OBJECT: " + object_array[i].objectname + ", t2: " + str(object_array[i].r_axis[1]) + ", time stamp: " + str(object_array[i].time_stamp)) 
        print("Imported scans: " + str(object_array[i].imported_scans))
        
        if numpy.all(object_array[i].r):
            print("r constructed")
        else:
            print("r not constructed")

        if numpy.all(object_array[i].s):
            print("s calculated")
        else:
            print("s not calculated")   
            
             
        
        print("")
        









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
    def plot(self, plot_type = "S", x_range = [0, 0], y_range = [0, -1], zlimit = -1, contours = 12, filled = True, black_contour = True, title = "", x_label = "", y_label = "", diagonal_line = True, new_figure = True, flag_no_units = False, pixel = -1):
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
        
        if pixel < 0:
        
            if flag_no_units:
                x_axis = numpy.arange(len(self.s_axis[2]))
                y_axis = numpy.arange(len(self.s_axis[0]))
                y_range = [0,0]
                if x_label == "":
                    x_label = "FT (steps)"
                if y_label == "":
                    y_label = "spectrometer (pixels)"
                diagonal_line = False

            else:
                x_axis = self.s_axis[2]
                y_axis = self.s_axis[0]    
                if x_label == "":
                    x_label = "w3 (" + str(self.s_units[2]) + ")"
                if y_label == "":
                    y_label = "w1 (" +  str(self.s_units[0]) + ")"
            
            if title == "":
                title = self.objectname + ", t2: " + str(self.r_axis[1]) + "\n scans x shots: " + str(self.n_scans) + "x" + str(self.n_shots)
            
                   
            croc.Plotting.contourplot(data, x_axis, y_axis, x_range = x_range, y_range = y_range, zlimit = zlimit, contours = contours, filled = filled, black_contour = black_contour, title = title, x_label = x_label, y_label = y_label, diagonal_line = diagonal_line, new_figure = new_figure) 
        
        else:
            data = data.T
            
            if flag_no_units:
                x_axis = numpy.arange(len(self.s_axis[0]))
                y_range = [0,0]
                if x_label == "":
                    x_label = "FT (steps"
                if y_label == "":
                    y_label = "Intensity"

            else:
                x_axis = self.s_axis[0]  
                if x_label == "":
                    x_label = "w1 (" + str(self.s_units[0]) + ")"
                if y_label == "":
                    y_label = "Intensity"
            
            if title == "":
                title = "Spectrum for pixel " + str(pixel) + " - " + self.objectname + ", t2: " + str(self.r_axis[1]) + "\n scans x shots: " + str(self.n_scans) + "x" + str(self.n_shots)            
        
            croc.Plotting.linear(data[pixel,:], x_axis, x_range = [0, 0], y_range = [0, 0], x_label = x_label, y_label = y_label, title = title, new_figure = new_figure)
            




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
                
                if re.match("Fringes", line): 
                    self.n_fringes = int((re.search(regex, line)).group())            
                
                if re.match("Phase", line):
                    self.phase_degrees = float((re.search(regex, line)).group()) + 180.0
                
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
        if self.mess_type != "FastScan":
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
        Fast scanning will result in more data. This is why the data should not be imported, but should be added. The addition of data is done in add_data. Each shot will be assigned a fringe. Then the data is binned per fringe and per PEM-state. This is saved in self.b, the particular fringes in self.b_axis and the count of how much data there is in each bin is saved in self.b_count. 
        Each measurement can be added to these bins. Then the rephasing and non-rephasing diagram can be constructed. 
        
        
        """
        
        croc.Pe.pe.__init__(self, objectname)
        
        self.base_filename = base_filename
        self.r_axis[1] = population_time   
        self.time_stamp = time_stamp   
        self.path = self.base_filename + "_" + str(self.time_stamp) + "_T" + str(self.r_axis[1]) + "/"  
        
        self.mess_type = "FastScan"
        
        # self.b* will contain the data, binned, but not yet averaged. This allows for easy adding of data.
        self.b = [0] * 2  
        self.b_axis = [0] * 2
        self.b_count = [0] * 2
        
        # for the noise
        self.n = [[],[]]
        
        # some channels have a special meaning
        self.x_channel = 32
        self.y_channel = 33
        self.chopper_channel = 36
        
        
        
        # the following parameters are to shape the arrays.
        self.n_channels = 37    # all channels
        self.n_pixels = 32      # the number of channels for pixels
        self.n_fringes = 0      # the set number of fringes
        self.extra_fringes = 20 # some extra fringes for if the motor overshoots
        
        
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
        flag_noise_time_domain = False):
        """
        Adds data for a single scan.
        The data is imported as data.
        Then it is written to m as channel * shot. m_axis contains the fringe for that shot.
        Then it is binned to self.b. In self.b_axis the corresponding fringes are written. In self.b_count contains how many data points are in that bin.
        All three self.b* are a bit longer than the amount of shots, to make up for variations between measurements.
        
        INPUT:
        - scan (integer): the number of the scan to be imported
        - flag_import_override (BOOL, False): If set to False, it will prevent a scan from being re-imported. If set to True, it will give a warning, but will continue anyway.
        - flag_construct_r (BOOL, True): will construct self.r. Set to False and do it separately if you import a lot of files.  
        - flag_calculate_noise (BOOL, False): (experimental) will calculate the noise
        
        """
        
        if len(self.imported_scans) == 0:
            # set self.reference
            self.import_reference()
            # set phase, shots, 
            self.import_meta()
    
        # see if we already imported this file
        if self.imported_scans.count(scan) != 0:
            if flag_import_override == False: 
                print("ERROR (croc.Pe.pefs.add_data): Scan is already imported.")  
                return 0
            else:
                print("WARNING (croc.Pe.pefs.add_data): Scan is already imported, but will be imported anyway because flag_import_override is set to True.")
            
        filename = self.make_filenames(scan)

        # for the 4 files
        for k in range(4):
        
            # to distuinguish between the two diagrams
            if k < 2:
                diagram = 0
            else:
                diagram = 1
            
            # import the data
            try:
                [m, fringes] = self.import_raw_data(filename[k])
            except IOError:
                return False
            
            # if the number of fringes can not be set using the meta file, find it here 
            if self.n_fringes == 0:
                self.n_fringes = int(numpy.abs(fringes[1] - fringes[0]))
            
            # reconstruct the counter
            m_axis, counter, correct_count = self.reconstruct_counter(m, fringes[0], fringes[1], flag_plot = False)
            
            # check for consistency
            if correct_count == False:
                print("Scan: " + str(scan) + ", File: " + str(k) + ": Miscount!")
                self.incorrect_count[k] += 1

            # if it is consistent, continue
            else:
                print("Scan: " + str(scan) + ", File: " + str(k) + ": Count is correct!")
            
                # make b the correct size, if it isn't already
                if numpy.shape(self.b_axis)[-1] == 2:
                    self.make_arrays()
        
                # bin the data
                self.bin_data(m, m_axis, diagram)
                
                # calculate the noise
                if flag_calculate_noise:
                    self.bin_for_noise(m, m_axis, diagram, flag_noise_time_domain)

                # all the data is now written into self.b* 

        # construct the actual measurement
        if flag_construct_r:
            self.construct_r()

        # now append that we imported this scan
        self.imported_scans.append(scan)
        
        self.n_scans = len(self.imported_scans)
        
        return True





    def make_filenames(self, scan):
        """
        croc.Pe.pefs.make_filenames()
        
        Makes the filenames. Apart from the path, all the variables should have been entered in the init. 
        
        INPUT:
        - scan (int): the number of the scan
        
        IMPLICIT REQUIREMENTS:
        In the data structure, the following variables should be set:
        - self.path
        - self.base_filename
        - self.time_stamp
        - self.r_axis[1]: (population time)

        
        
        """
        
    
        # construct filenames
        filename = [0] * 4  # the filenames

        filename[0] = self.path + self.base_filename + "_" + str(self.time_stamp) + "_T" + str(self.r_axis[1]) + "_R1" + "_" + str(scan) + ".bin"
        filename[1] = self.path + self.base_filename + "_" + str(self.time_stamp) + "_T" + str(self.r_axis[1]) + "_R2" + "_" + str(scan) + ".bin"
        filename[2] = self.path + self.base_filename + "_" + str(self.time_stamp) + "_T" + str(self.r_axis[1]) + "_NR1" + "_" + str(scan) + ".bin"
        filename[3] = self.path + self.base_filename + "_" + str(self.time_stamp) + "_T" + str(self.r_axis[1]) + "_NR2" + "_" + str(scan) + ".bin"
        return filename






    def make_arrays(self):
        """
        croc.Pe.pefs.make_arrays()
        
        Creates correctly sized arrays for self.b, self.b_count, self.b_axis and self.r.
        
        INPUT:
        - none
        
        IMPLICIT REQUIREMENTS:
        In the data structure, the following variables should be set:
        - self.n_fringes
        - self.extra_fringes
        - self.n_channels
        
        """
    
        self.b = [numpy.zeros((self.n_fringes + 2 * self.extra_fringes, self.n_channels)),numpy.zeros((self.n_fringes + 2 * self.extra_fringes, self.n_channels)),numpy.zeros((self.n_fringes + 2 * self.extra_fringes, self.n_channels)),numpy.zeros((self.n_fringes + 2 * self.extra_fringes, self.n_channels))] 
        self.b_axis[0] = numpy.arange(- self.extra_fringes, self.n_fringes + self.extra_fringes)
        self.b_axis[1] = numpy.arange(- self.extra_fringes, self.n_fringes + self.extra_fringes)
        self.b_count = numpy.zeros((4, self.n_fringes + 2 * self.extra_fringes))
        self.r = [numpy.zeros((self.n_fringes, 32)),numpy.zeros((self.n_fringes, 32))] 








    def import_raw_data(self, path_and_filename):
        """
        croc.Pe.pefs.import_raw_data()
        
        Imports the actual data and parses it.
        
        The data comes in binary form as an array. Also, the start and stop fringe are added to the end. 
        
        INPUT:
        - path_and_filename (string): where the file can be found


        IMPLICIT REQUIREMENTS:
        In the data structure, the following variables should be set:
        - self.n_shots (optional)
        - self.n_channels
        
        OUTPUT:
        - m (2d array): the data in channels x samples format
        - fringes (array): an array with the fringe at the beginning ([0]) and the end ([1])
        - self.n_shots: number of shots, if not determined earlier
        
        
        """
        
        # import the data
        try:
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
        except IOError:
            print("ERROR (croc.Pe.pefs.add_data): Unable to import data from file " + path_and_filename)
            raise
            return 0, 0


   
        
        


    def bin_data(self, m, m_axis, diagram):
        """
        croc.Pe.pefs.bin_data()
        
        After determining the fringe for all shots, this will bin the data in the correct bin. There are 4 bins: 2 (for rephasinga and non-rephasing) x 2 (for the two PEM-states). 
        The PEM trigger should vary between ~0V and ~5V. It will check if the state of the PEM is higher or lower than 2.5V. 

        
        INPUT:
        - m (2d-ndarray, channels x samples): the data
        - m_axis (1d-ndarray, length of samples): the fringe for each sample
        - diagram (number): rephasing (0) or non-rephasing (1)

        
        IMPLICIT REQUIREMENTS:
        In the data structure, the following variables should be set:
        - self.n_shots
        - self.chopper_channel
        - self.b
        - self.b_count        
        
        """
        self.bin_data_helper(m, m_axis, diagram, b = self.b, b_count = self.b_count)
        



    def bin_data_helper(self, m, m_axis, diagram, b, b_count):

        for i in range(self.n_shots):            
            # find the fringe
            j = (-1)**diagram * int(m_axis[i]) + self.extra_fringes - (-1)**diagram * 4000

            # add it to the bin, depending on pem-state and diagram
            # and add 1 to counter 
            if m[self.chopper_channel, i] < 2.5:         
                b[2 * diagram][j, :] += m[:,i] 
                b_count[2 * diagram, j] += 1
            else:
                b[2 * diagram + 1][j, :] += m[:,i] 
                b_count[2 * diagram + 1, j] += 1
        
        return b, b_count


    def bin_info(self):
        """
        croc.Pe.pefs.bin_info()
        
        Will plot some stuff related to the binning. 
        The first plot shows the amount of samples for every fringe.
        The second plot shows a histogram of the samples per bin.
        
        """
    
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
        plt.plot(numpy.bincount(numpy.array(self.b_count[2], dtype=numpy.int)))
        plt.plot(numpy.bincount(numpy.array(self.b_count[3], dtype=numpy.int)))
        plt.title("Bins with certain number of shots")
        plt.xlabel("Number of shots")
        plt.ylabel("Number of bins")
        
        plt.show()           
        




    def construct_r(self, flag_no_logarithm = False):
        """
        croc.Pe.pefs.construct_r()
        
        This function will construct the rephasing and non-rephasing diagrams. 
        
        It will first average the data. Then it will select the part where the fringes are not negative. Then it will take the difference between the two PEM-states and calculate the optical density. Data points that are not-a-number will be converted to zero.
        
        
        IMPLICIT REQUIREMENTS:
        In the data structure, the following variables should be set:
        - self.n_fringes
        - self.extra_fringes
        - self.b
        - self.b_count
        - self.b_axis
        - self.n_pixels
        - self.r: this will be overwritten
        
        
        OUTPUT:
        - self.r_axis[0]: the times
        - self.r
        - self.r_units
        
        """
        b_fringes = self.n_fringes + 2 * self.extra_fringes
        
        temp = numpy.zeros((4, b_fringes, self.n_channels))
        
        # average the data for the two diagrams
        for j in range(4):
            for i in range(b_fringes):
                if self.b_count[j][i] != 0:
                    temp[j,i,:] = self.b[j][i,:] / self.b_count[j,i]    
                else:    
                    temp[j,i,:] = numpy.zeros(self.n_channels)                
        
        # select n_fringes, ie. discard the extra fringes
        temp = temp[:,self.extra_fringes:(self.n_fringes+self.extra_fringes),:self.n_pixels]
              
        # make the r_axis
        self.r_axis[0] = self.b_axis[0][self.extra_fringes:(self.n_fringes+self.extra_fringes)] * croc.Constants.hene_fringe_fs

        if flag_no_logarithm:
            # for testing purposes
            for j in range(2):
                self.r[j][:,:self.n_pixels] = temp[2*j,:,:self.n_pixels] - temp[2*j+1,:,:self.n_pixels]
        
        else:
            # convert it to mOD
            for j in range(2):
                self.r[j][:,:self.n_pixels] = -numpy.log10(1+ 2*(temp[2*j,:,:self.n_pixels] - temp[2*j+1,:,:self.n_pixels])/self.reference[:self.n_pixels])                
        
        self.r = numpy.nan_to_num(self.r)
        
        self.r_units = ["fs", "fs", "cm-1"]



       

                
    
    
    
    
    
    def reconstruct_counter(self, data, start_counter = 0, end_counter = 0, flag_plot = False):
        """
        croc.Pe.pefs.reconstruct_counter()
        
        
        
        This function will use the feedback from the HeNe's and reconstruct the fringes. It will check whether y > 0 and whether x changes from x[i-1] < 0 to x[i+1] > 0 and whether x[i-1] < x[i] < x[i+1] (or the other way around for a count back). 
        After a count in a clockwise direction, it can only count again in the clockwise direction after y < 0. 
        
        INPUT:
        - data (2darray, channels x samples): data. It will use self.x_channel and self.y_channel to find the data.
        - start_counter (int, 0): where the count starts. 
        - flag_plot (BOOL, False): plot the x and y axis and the counts. Should be used for debugging purposes.


        IMPLICIT REQUIREMENTS:
        In the data structure, the following variables should be set:
        - self.x_channel, self.y_channel
        
        
        
        
        OUTPUT:
        - m_axis (1d-ndarray, length of samples): the exact fringe for that sample
        - counter (int): the last value of the fringes. It is the same as m_axis[-1]. For legacy's sake.
        
        
        CHANGELOG:
        20110920 RB: started the function
        20111003 RB: change the way it counts. It will now not only check if the x goes through zero, it will also make sure that the point in between is actually in between. This reduced the miscounts from 80/400 t0 30/400.
        
        
        """
        
        
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
        
        if flag_plot:
            change_array = numpy.zeros(length)
        
        # do the loop
        for i in range(1, length - 1):
            # count can only change when y > 0
            if y[i] > med_y:
                if c_lock == False:
                    if x[i-1] < med_x and x[i+1] > med_x and x[i-1] < x[i] and x[i+1] > x[i]: 
                        counter += 1               
                        c_lock = True
                        cc_lock = False
                        if flag_plot:
                            change_array[i] = 0.05

                if cc_lock == False:
                    if x[i-1] > med_x and x[i+1] < med_x and x[i-1] > x[i] and x[i+1] < x[i]:
                        counter -= 1
                        c_lock = False
                        cc_lock = True  
                        if flag_plot:
                            change_array[i] = -0.05

            else:
                c_lock = False
                cc_lock = False
            
            m_axis[i] = counter
        
        m_axis[-1] = counter
        
        if counter == end_counter:
            correct_count = True
        else:
            correct_count = False

        if flag_plot:        
            plt.figure()
            plt.plot(x, ".-")
            plt.plot(y, ".-")
            plt.plot(change_array, ".")
            plt.xlabel("Shots")
            plt.ylabel("Volts")
            plt.title("x (blue), y (green) and counts up or down (red)")
            plt.show()

        return m_axis, counter, correct_count   













    def find_correlation(self, m, channel = 16, new_figure = False):
        """
        croc.Pe.pefs.find_correlation
        
        Check the correlation of the laser. 
    
        INSTRUCTIONS FOR THE MEASUREMENT:
        - get the OPA to work 
        - align the experiment
        - balance the incoupling as if it were a serious measurment
        - block the other beams (to prevent scattering etc)
        - measure the fast scanning for as long as possible, without moving the motors
        
        INPUT:
        - m (2d-array, channels x samples): the data
        - channel (int, 16): the channel you want to look at  
        
        IMPLICIT REQUIREMENTS:
        In the data structure, the following variables should be set:   
        - none    
        """
        
        n_channels, n_shots = numpy.shape(m)
        
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
        if new_figure:
            plt.figure()
        
        plt.plot(m_x)
        
        if new_figure:
            plt.show()




    def find_angle(self, m, m_axis, k = 0, skip_first = 0, skip_last = 0, flag_normalize_circle = True, flag_scatter_plot = True, new_figure = True):   
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
        
        
        
        IMPLICIT REQUIREMENTS:
        In the data structure, the following variables should be set:
        - self.x_channel, self.y_channel
        
        
        
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

        # determine the average etc. and normalize it so that it is a true circle        
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



    def bin_for_noise(self, m, m_axis, diagram, flag_noise_time_domain = False):
        """
        croc.Pe.pefs.bin_for_noise()
        
        Allows the calculation of the noise. It will bin the data and fourier transform it per run. Using croc.Pe.pefs.calculate_noise() the mean square noise is calculated.
        Note: this will use a large amount of memory and slows the data importing down quite a bit.

        IMPLICIT REQUIREMENTS:
        In the data structure, the following variables should be set:
        - self.n_fringes
        - self.extra_fringes
        - self.n_channels
        - self.n_pixels
        - self.reference

        OUTPUT:
        - self.n: it will write FT's to self.n
        
        """
        
        b_fringes = self.n_fringes + 2 * self.extra_fringes
        
        n_shots = len(m_axis)


        b = [numpy.zeros((self.n_fringes + 2 * self.extra_fringes, self.n_channels)),numpy.zeros((self.n_fringes + 2 * self.extra_fringes, self.n_channels)),numpy.zeros((self.n_fringes + 2 * self.extra_fringes, self.n_channels)),numpy.zeros((self.n_fringes + 2 * self.extra_fringes, self.n_channels))] 
        b_count = numpy.zeros((4, self.n_fringes + 2 * self.extra_fringes))

        
#         b = numpy.zeros((4, b_fringes, self.n_channels))
#         b_count = numpy.zeros((4, b_fringes))
        
        r = numpy.zeros((self.n_fringes, 32)) 
        
        diagramx = 0
        
        b, b_count = self.bin_data_helper(m, m_axis, diagramx, b, b_count)
        
        
#         for i in range(n_shots):            
#             # find the fringe
#             j = (-1)**diagram * int(m_axis[i]) + self.extra_fringes - (-1)**diagram * 4000
# 
#             # add it to the bin, depending on pem-state and diagram
#             # and add 1 to counter 
#             if m[self.chopper_channel, i] < 2.5:         
#                 b[0, j, :] += m[:,i] 
#                 b_count[0, j] += 1
#             else:
#                 b[1, j, :] += m[:,i] 
#                 b_count[1, j] += 1     
        
        #print(numpy.shape(b_count))
        b = [b[0], b[1]]
        b_count = [b_count[0], b_count[1]]
        
        #print(numpy.shape(b_count))
        
        temp = numpy.zeros((2, b_fringes, self.n_channels))
        
        # average the data for the two diagrams
        for j in range(2):
            for i in range(b_fringes):
                if b_count[j][i] != 0:
                    temp[j,i,:] = b[j][i,:] / b_count[j][i]    
                else:    
                    temp[j,i,:] = numpy.zeros(self.n_channels)               
        
        # now only select the part where fringes are not negative
        temp = temp[:,self.extra_fringes:(self.n_fringes+self.extra_fringes),:self.n_pixels]
        
        # now convert it to mOD
        r[:,:self.n_pixels] = -numpy.log10(1 + 2 * (temp[0,:,:self.n_pixels] - temp[1,:,:self.n_pixels]) / self.reference[:self.n_pixels])
        
        r = numpy.nan_to_num(r)
        
        if flag_noise_time_domain:
            self.n[diagram].append(r)
        else:        
            f = self.fourier_helper(numpy.copy(r))
            
            f = f[:len(f)/2]
            
            self.n[diagram].append(f)  




    def bin_for_noise_time(self, m, m_axis, diagram):

        self.n_fringes = 1200
    
        try:
            self.q
        except:
            self.q = [numpy.zeros((self.n_fringes + 2 * self.extra_fringes, self.n_channels)),numpy.zeros((self.n_fringes + 2 * self.extra_fringes, self.n_channels))]
            self.t = [numpy.zeros((self.n_fringes + 2 * self.extra_fringes, self.n_channels)),numpy.zeros((self.n_fringes + 2 * self.extra_fringes, self.n_channels))]
            self.t_count = [numpy.zeros(self.n_fringes + 2 * self.extra_fringes), numpy.zeros(self.n_fringes + 2 * self.extra_fringes)]
        
        axis = range(self.n_fringes + 2 * self.extra_fringes)
        
#         if diagram == 0 or diagram == 1:
#             d_axis = numpy.arange(4000 - self.extra_fringes, 4000 + self.n_fringes + self.extra_fringes)
#         else:
#             d_axis = numpy.arange(4000 - self.n_fringes - self.extra_fringes, 4000 + self.extra_fringes)

        r = numpy.zeros(self.n_channels)

        for i in axis:
            #print(self.b_axis[diagram][i])
            # find the indices where the fringe has a certain value
            w = numpy.where(m_axis == self.b_axis[diagram][i]+4000)
            
            print(w)
            
            # select the stuf in m where the fringes have that value
            n = m[:,w[0]]

            # from this selection, find the state of the chopper
            a = numpy.where(n[self.chopper_channel] < 2.5)
            b = numpy.where(n[self.chopper_channel] > 2.5)
            
            # now take the mean of one state of the chopper and subtract the mean of the other state of the chopper
            r = numpy.mean(m[:,((w[0])[a[0]])], axis = 1) - numpy.mean(m[:,((w[0])[b[0]])], axis = 1)
            
            # transform NaN to zeros            
            r = numpy.nan_to_num(r)
            
            # add it to the arrays
            self.t[diagram][i,:] = r
            self.q[diagram][i,:] = r**2
            self.t_count[diagram][i] += 1





            
    def calculate_noise_time(self, pixel = 16, max_scans = 0):
         
        b_fringes = self.n_fringes + 2 * self.extra_fringes
        
        # rephasing, non-rephasing
        temp = numpy.zeros((2, b_fringes, self.n_channels))     
        
        for i in range(2):
            for j in range(b_fringes):
                temp[i,j,:] = numpy.sqrt((numpy.mean(self.q[i][j,:]) - (self.t[i][j,:])**2 / self.t_count[i][j]) / (self.t_count[i][j]-1))
        
        temp = temp[:,self.extra_fringes:(self.n_fringes+self.extra_fringes),:self.n_pixels]
        
        plt.figure()
        plt.plot(temp[0, 1:-1, pixel])
        plt.plot(temp[1, 1:-1, pixel])
        plt.show()
        
        
        
             
 





    def calculate_noise_time_old(self, pixel = 16, max_scans = 0):
                
        b_fringes = self.n_fringes + 2 * self.extra_fringes
        
        temp = numpy.zeros((4, b_fringes, self.n_channels))
        tempq = numpy.zeros((4, b_fringes, self.n_channels))
        
        noise = numpy.zeros((4, b_fringes, self.n_channels))
        
        # average the data for the two diagrams
        for j in range(4):
            for i in range(b_fringes):
                if self.b_count[j][i] != 0:
                    temp[j,i,:] = self.b[j][i,:] / self.b_count[j,i] 
                    tempq[j,i,:] = self.q[j][i,:] 
                    noise[j,i,:] = numpy.sqrt((tempq[j,i,:] - temp[j,i,:]**2) / (self.b_count[j,i] - 1))
                else:    
                    temp[j,i,:] = 0  
                    tempq[j,i,:] = 0
                    noise[j,i,:] = 0
        
        # select n_fringes, ie. discard the extra fringes
        noise = noise[:,self.extra_fringes:(self.n_fringes+self.extra_fringes),:self.n_pixels]

        
        print(numpy.shape(noise))
        
        plt.figure()
        plt.plot(noise[0][:, pixel])
        plt.plot(noise[1][:, pixel])
        plt.plot(noise[2][:, pixel])
        plt.plot(noise[3][:, pixel])
        plt.show()
   
    
    
    
        


    def calculate_noise(self, pixel = 16, max_scans = 0, flag_noise_time_domain = False):
        """
        croc.Pe.pefs.calculate_noise()
        
        This function calculates the noise between the FT of different measurements. 
        The data is stored in self.n. The data has first to be unpacked. Then it will take the standard deviation of the different FT's. 
        
        """
        
        shape0 = numpy.shape(self.n[0])
        shape1 = numpy.shape(self.n[1])
        
        if max_scans == 0 or max_scans > shape0[0]:
            max_scans0 = shape0[0]
        else:
            max_scans0 = max_scans

        if max_scans == 0 or max_scans > shape1[0]:
            max_scans1 = shape1[0]
        else:
            max_scans1 = max_scans
        
        std0 = numpy.zeros((shape0[1], shape0[2]))
        std1 = numpy.zeros((shape1[1], shape1[2]))     

        f0 = numpy.zeros((shape0[1], shape0[2]), dtype = "cfloat")
        f1 = numpy.zeros((shape1[1], shape1[2]), dtype = "cfloat")
        
        a0 = numpy.zeros((max_scans0, shape0[2]), dtype = "cfloat")
        a1 = numpy.zeros((max_scans1, shape1[2]), dtype = "cfloat")
        
        for i in range(shape0[1]): # frequency
            for j in range(max_scans0): # scans
                a0[j] = self.n[0][j][i][:]
            std0[i] = numpy.std(a0, axis = 0) 
            f0[i] = numpy.mean(a0, axis = 0)

        for i in range(shape1[1]): # frequency
            for j in range(max_scans1): # scans
                a1[j] = self.n[1][j][i][:]                
            std1[i] = numpy.std(a1, axis = 0) 
            f1[i] = numpy.mean(a1, axis = 0)     

        s_axis = numpy.arange(shape0[1]) * croc.Constants.hene_fringe_fs


        if flag_noise_time_domain:

    
            plt.figure()
            
            plt.subplot(211)
            for j in range(max_scans0):
                plt.plot(self.r_axis[0][:], self.n[0][j][:,pixel])
            plt.title("Rephasing, individual time domain, " + str(max_scans0) + "x")
            
            plt.subplot(212)
            
            ratio = numpy.nanmax(f0[:, pixel]/std0[:, pixel]) / numpy.nanmax(f0[:, pixel])
            
            
            plt.plot(self.r_axis[0][:], ratio * std0[:, pixel], "b")
            plt.plot(self.r_axis[0][:], ratio *f0[:, pixel], "g")
            plt.plot(self.r_axis[0][:], numpy.abs(f0[:, pixel])/std0[:, pixel], "r")
            plt.plot
            plt.title("STD (blue), <time> (green) (both normalized) and SNR (abs(time)/STD) (red)")
            plt.xlabel("fs")
            plt.ylabel("Ratio")
            plt.show()
                
            plt.figure()
            plt.subplot(211)
            for j in range(max_scans1):
                plt.plot(self.r_axis[0][:], self.n[1][j][:,pixel])
            plt.title("Non-rephasing, individual time domain, " + str(max_scans1) + "x")
            
            plt.subplot(212)   
            ratio = numpy.nanmax(f1[:, pixel]/std1[:, pixel]) / numpy.nanmax(f1[1:, pixel])
            plt.plot(self.r_axis[0][:], ratio * std1[:, pixel],"b")
            plt.plot(self.r_axis[0][:], ratio * f1[:, pixel], "g")
            plt.plot(self.r_axis[0][:], numpy.abs(f1[:, pixel])/std1[:, pixel], "r")
            plt.title("STD (blue), <time> (green) (both normalized) and SNR (abs(time)/STD)(red)")
            plt.xlabel("fs")
            plt.ylabel("Ratio")
            plt.show()
        
        else:
    
            plt.figure()
            
            plt.subplot(211)
            for j in range(max_scans0):
                plt.plot(self.s_axis[0][1:], numpy.abs(self.n[0][j][1:,pixel]))
            plt.title("Rephasing, individual abs(FT), " + str(max_scans0) + "x")
            
            plt.subplot(212)
            
            ratio = numpy.nanmax(numpy.abs(f0[1:, pixel])/std0[1:, pixel]) / numpy.nanmax(numpy.abs(f0[1:, pixel]))
            
            
            plt.plot(self.s_axis[0][1:], ratio * std0[1:, pixel], "b")
            plt.plot(self.s_axis[0][1:], ratio * numpy.abs(f0[1:, pixel]), "g")
            plt.plot(self.s_axis[0][1:], numpy.abs(f0[1:, pixel])/std0[1:, pixel], "r")
            plt.plot
            plt.title("STD (blue), abs(<FT>) (green) (both normalized) and SNR (red)")
            plt.xlabel("cm-1")
            plt.ylabel("Ratio")
            plt.show()
                
            plt.figure()
            plt.subplot(211)
            for j in range(max_scans1):
                plt.plot(self.s_axis[0][1:], numpy.abs(self.n[1][j][1:,pixel]))
            plt.title("Non-rephasing, individual abs(FT), " + str(max_scans1) + "x")
            
            plt.subplot(212)   
            ratio = numpy.nanmax(numpy.abs(f1[1:, pixel])/std1[1:, pixel]) / numpy.nanmax(numpy.abs(f1[1:, pixel]))
            plt.plot(self.s_axis[0][1:], ratio * std1[1:, pixel],"b")
            plt.plot(self.s_axis[0][1:], ratio * numpy.abs(f1[1:, pixel]), "g")
            plt.plot(self.s_axis[0][1:], numpy.abs(f1[1:, pixel])/std1[1:, pixel], "r")
            plt.title("STD (blue), abs(<FT>) (green) (both normalized) and SNR (red)")
            plt.xlabel("cm-1")
            plt.ylabel("Ratio")
            plt.show()
        
 
        
       
        

        
        
        
        
     











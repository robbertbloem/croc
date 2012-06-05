"""
pe.py

DESCRIPTION
    This file contains the data analysis details for the 2DIR setup.


CHANGELOG
    RB 20091214 - first draft.
    RB 20110908 - combined some stuff together
    RB 20120227 - moved some functions to croc.Resources.PEFunctions
    RB 20120302 - wrote new import method

REMARKS
- T3 is not imported. I didn't think about it too much, but I think that would need an extra dimension or so.


"""

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import fileinput
import re
import os.path
import time
import inspect

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import scipy

import croc
# to prevent a conflict with other classes (like ftir)
from croc.Resources.DataClasses import mess_data
import croc.Resources.Mathematics as M
import croc.Resources.Plotting as P
import croc.Resources.Constants as C
import croc.Resources.PEFunctions as PEF
import croc.Resources.IOMethods as IOM
import croc.Debug as D

reload(D)

if D.reload_flag:
    reload(croc)
    reload(croc.Resources.DataClasses)
    reload(M)
    reload(P)
    reload(C)
    reload(PEF)
    reload(IOM)
    


debug_flag = croc.Debug.debug_flag

### METHODS TO WORK WITH PICKLES ###
def test():
    D.printError("test", inspect.stack())
    D.printWarning("test")
    print(inspect.stack()[0][3])

def make_pickle_name(base_filename, pop_time, time_stamp, path = ""):
    return path + base_filename + "_" + str(time_stamp) + "_T" + str(pop_time) + ".pickle"

def make_path(base_filename, pop_time, time_stamp, path = ""):
    return path + base_filename + "_" + str(time_stamp) + "_T" + str(pop_time) + "/"

def check_pickle_exists(path_and_filename):
    return os.path.exists(path_and_filename)

def import_pickle(mess_date, mess_array = [], pickle_name = "", flag_remove_objects = False):
    """
    This functions checks if a pickle file exists, it opens it and puts the objects in the pickle in the order of mess_array
    """
    if pickle_name == "":
        pickle_name = str(mess_date) + "_fs.pickle"
    
    if check_pickle_exists(pickle_name) == False:  
        D.printError("the pickle does not exist!", inspect.stack())
        return False
        
    obj = croc.Resources.DataClasses.import_db(pickle_name)

    new_obj = [0] * len(mess_array)

    if len(mess_array) == 0:
        new_obj = obj   
    else:
        # this will take the objects and orders them according to mess_array. If an objects is missing in mess_array, it will be discarded. If mess_array has more objects than the pickle, it will create a new one.
        success_mess = [0]*len(mess_array)
        success_obj = [0]*len(obj)
        for i in range(len(mess_array)):
            for j in range(len(obj)):
                if mess_array[i][0] == obj[j].objectname:
                    new_obj[i] = obj[j]
                    success_mess[i] = 1
                    success_obj[j] = 1
            if success_mess[i] == 0:
                new_obj[i] = croc.Pe.pefs(mess_array[i][0], mess_array[i][1], mess_array[i][2], mess_array[i][3])
        
        # gives a warning when mess_array is shorter
        if numpy.sum(success_obj) < len(obj): 
            D.printWarning("Object is missing in mess_array. It is not deleted from the HD.", inspect.stack())
        
    return new_obj



def save_pickle(obj, pickle_name, flag_overwrite = False):
    croc.Resources.DataClasses.make_db(obj, pickle_name, flag_overwrite = flag_overwrite)




# IMPORT METHODS

def test_unique_object_id(mess_array, object_id = 0):
    """
    croc.Pe.test_unique_object_id
    
    Tests if the identifiers in mess_array are unique. If they are not unique it becomes a mess.
    
    CHANGELOG:
    20120302 RB: started
    
    INPUT:
    - mess_array (array): an array with measurements
    - object_id (int): the place in the array where the object_id can be found.
    
    """
    
    for i in range(len(mess_array)):
        for j in range(i+1, len(mess_array)):
            if mess_array[i][object_id] == mess_array[j][object_id]:
                D.printError("The objectnames have to be unique! This is not the case. Aborting.", inspect.stack())
                return False 
    return True 




def import_FS(mess_date, mess_array, scan_array, pickle_name = "", data_dir = "", anal_dir = "", flag_ignore_pickle = False, flag_intermediate_saving = 50):
    
    """
    croc.Pe.import_FS
    
    Method to import scans.
    
    CHANGELOG:
    20120302 RB: started, replacing import_mess_array and import_data
    
    INPUT:
    - mess_date (int): the date of the measurement as yyyymmdd
    - mess_array (array): array with measurements. The following elements should be present, in this order: object_id as string, base_filename as string, population time as int, timestamp (hhmm) as int. Optional is n_scans, see scan_array input.
    - scan_array (integer or array): scan_array determines which measurements will be imported. 
        - integer: the number points to the column in mess_array where the number of measurements are indicated. It will import all measurements.
        - an array with, for every object in mess_array, an:
            - integer: same as above, will import all measurements
            - sub-array: will import the specific measurements
        + examples:
            mess_array = [
                ['obj1', 'molecule', 300, 1000, 2],
                ['obj2', 'molecule', 300, 1100, 3],
            ]
            scan_array = 4: will look at 5th column and import scans 1 and 2 for obj1 and scans 1, 2, 3 for obj2.
            scan_array = [2, [2,4]]: will import scans 1 and 2 for obj1 and 2 and 4 for obj2.
    
    - pickle_name (string, ""): If given, it will use this name for the pickle. If not given (default), it will use a default name: "yyyymmdd_fs.pickle"
    - data_dir (string, ""): If given it will use this for the path to the data. If not given, it will assume you are currently in /analysis/yyyymmdd/ and will look for the data in /data/yyyymmdd/.
    - anal_dir (string, ""): It will read/write the pickle here. If not given, it will read/write in the current directory.
    - flag_ignore_pickle (BOOL, False): Will not try to import the data. When the pickle is saved it will add new objects to the current pickle, and overwrite objects that are already present. WARNING: this is a good way to ruin your data.
    - flag_intermediate_saving (int, 50): the interval of successful imports with which the pickle is saved during the importing. 
    
    """

    flag_change = False
    
    if test_unique_object_id(mess_array) == False:
        return False
    
    if type(scan_array) == int:
        scan_int = scan_array
        scan_array = [0]*len(mess_array)
        if scan_array == 0:
            print("croc.Pe.import_FS: Nothing to import.")
            return True
        else:
            for i in range(len(mess_array)):
                scan_array[i] = numpy.arange(1,mess_array[i][scan_int]+1) 
    else:
        if len(scan_array) != len(mess_array):
            D.printError("The length of the mess_array and scan_array should be the same.", inspect.stack())
            return False  
        else:
            for i in range(len(scan_array)):
                if type(scan_array[i]) == int:
                    if scan_array[i] == 0:
                        scan_array[i] = [0]
                    else:
                        temp = scan_array[i]    
                        scan_array[i] = numpy.arange(1,temp+1) 
    
    if anal_dir == "":
        anal_dir = os.getcwd() + "/"
    if anal_dir[-1] != "/":
        anal_dir += "/"
    
    if data_dir == "":
        # removes the '/analysis/20121212/'
        data_dir = os.getcwd()[:-17] + "data/" + str(mess_date) + "/"
    if data_dir[-1] != "/":
        data_dir += "/"
    
    if pickle_name == "":
        pickle_name = str(mess_date) + "_fs.pickle"
    if pickle_name[-7:] != ".pickle":
        pickle_name = pickle_name + ".pickle"
        
    if flag_ignore_pickle == False and check_pickle_exists(pickle_name) == True:
        print("Importing objects from pickle")
        obj = import_pickle(mess_date, mess_array = mess_array, pickle_name = anal_dir + pickle_name)
        if obj == False:
            return False
    else:
        if flag_ignore_pickle == True:
            print("Creating new objects - ignoring possible old pickle")
        if check_pickle_exists(pickle_name) == False:
            print("Creating new objects - no older pickle found")
        obj = [0] * len(mess_array)
        for i in range(len(mess_array)):
            obj[i] = croc.Pe.pefs(mess_array[i][0], mess_array[i][1], mess_array[i][2], mess_array[i][3])
        flag_change = True
        
    # we now have the array with objects, either new or imported
    # let's add some data
    
    for i in range(len(obj)):
        obj[i].path = data_dir + obj[i].base_filename + "_" + str(obj[i].time_stamp) + "_T" + str(obj[i].r_axis[1]) + "/"
    
    counter = 0
    for i in range(len(mess_array)):
        for j in range(len(scan_array[i])):
            
            if scan_array[i][j] == 0:
                print("Nothing to import for " + obj[i].objectname)
            else:
        
                result = obj[i].add_data(scan = scan_array[i][j], flag_construct_r = False)
            
                if result == True:  
                    flag_change = True
                    counter += 1
                
                if counter > flag_intermediate_saving and flag_change == True:
                    print("Intermediate saving of pickle!")
                    print(obj[i].base_filename, "scan:", scan_array[i][j])
                    croc.Resources.DataClasses.make_db(obj, pickle_name)
                    counter = 0
                    flag_change = False
                    
        if type(obj[i].b_count[0]) != int:
            obj[i].construct_r()

    # now save it 
    if flag_change == True:
        croc.Resources.DataClasses.make_db(obj, pickle_name)
    else: 
        print("No changes to be pickled.")
            

def rearrange_measurements(obj, mess_array, index):
    """
    Use the numbers in column mess_array[index] to add or subtract measurements.
    
    INPUT:
    - obj (DataClasses.Pe object): the object with all the measurments
    - mess_array (array): the array with all the measurements
    - index (integer): the column where it is defined what should be done with the measurements.  

    USAGE:
    In the column mess_array[index] there is a number (integer). If it is positive, it will be added, if negative, it will be subtracted, if it is zero, it will be ignored.
    The integers also group the measurements. The measurement at -2 will be subtracted from +2. 
    You can use arbitrary numbers. They don't have to be consecutive.


    """

    if len(mess_array) != len(obj):
        D.printError("Number of objects does not correspond to mess_array.", inspect.stack())
        return False, False, False    

    max_val = 0
    if type(index) == int:
        for i in range(len(mess_array)):
            if abs(mess_array[i][index]) > max_val:
                max_val = abs(mess_array[i][index])
    elif type(index) == list:
        for i in range(len(index)):
            if abs(index[i]) > max_val:
                max_val = abs(index[i])
    
    array = range(1,max_val+1)
    new_array = []
    for i in range(len(array)):
        flag_exists = False
        for j in range(len(mess_array)):
            if type(index) == int:
                if mess_array[j][index] == array[i] or mess_array[j][index] == -array[i]:
                    flag_exists = True
            elif type(index) == list:
                if index[j] == array[i] or index[j] == -array[i]:
                    flag_exists = True
        if flag_exists:
            new_array.append(i+1)
            
    plus_array = [0] * len(new_array)
    min_array = [0] * len(new_array)
    names = [""] * len(new_array)

    for i in range(len(new_array)):
        plus_array[i] = []
        min_array[i] = []
    
    for i in range(len(obj)):
        if type(index) == int:
            for j in range(len(new_array)):
                j_val = new_array[j]
                if mess_array[i][4] == -j_val:
                    min_array[j].append(obj[i])
                elif mess_array[i][4] == j_val:  
                    plus_array[j].append(obj[i])
                else:
                    pass 
        elif type(index) == list:  
            for j in range(len(new_array)):
                j_val = new_array[j]
                if index[i] == -j_val:
                    min_array[j].append(obj[i])
                elif index[i] == j_val:  
                    plus_array[j].append(obj[i])
                else:
                    pass                 
    
    for i in range(len(new_array)):
        if plus_array[i] != [] and min_array[i] != []:
            names[i] = plus_array[i][0].objectname + " - " + min_array[i][0].objectname
        elif plus_array[i] != [] and min_array[i] == []:
            names[i] = plus_array[i][0].objectname
        elif plus_array[i] == [] and min_array[i] != []:
            names[i] = "-(" +  min_array[i][0].objectname + ")"
    
    return plus_array, min_array, names
    
    

     





       
    
    
def import_mess_array(mess_date, mess_array, n_scans, pickle_name, data_dir = "", anal_dir = ""):
    """
    croc.Pe.import_mess_array
    Depreciated.
    Imports a whole mess_array in one go.
    
    """

    if type(n_scans) == int:
        n_scans = [n_scans] * len(mess_array)   
    
    scan_array = [0]*len(n_scans)
    for i in range(len(scan_array)):
        scan_array[i] = numpy.arange(1,n_scans[i]+1)
    
    import_FS(mess_date, mess_array, scan_array, pickle_name = pickle_name, data_dir = data_dir, anal_dir = anal_dir, flag_ignore_pickle = False, flag_intermediate_saving = 50)
        

def import_data(mess_date, import_mess, import_from, import_to, mess_array, data_dir = "", anal_dir = "", pickle_name = "", flag_calculate_noise = False, flag_no_pickle = False, flag_overwrite_pickle = False):
    """
    croc.Pe.import_data
    Depreciated.
    Imports a range of measurements of a single measurement in a mess_array.   
    
    """

    
    if import_from == 0 or import_to == 0:
        print("No need to import!")
    else:
        scan_array = [0]*len(mess_array)
        scan_array[import_mess] = numpy.arange(import_from, import_to+1)
        
        import_FS(mess_date, mess_array, scan_array, pickle_name = pickle_name, data_dir = data_dir, anal_dir = anal_dir, flag_ignore_pickle = flag_overwrite_pickle, flag_intermediate_saving = 50)
    
   

           
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
        






class pe(croc.Resources.DataClasses.mess_data):
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
        
        D.printBlue("=== CROCODILE PHOTON ECHO ===")
        
        if debug_flag:
            print(">>> DEBUG MODE <<<")
        
        # photon echo has 3 dimensions: t1/w1, t2, w3
        croc.Resources.DataClasses.mess_data.__init__(self, object_name, measurements = 2, dimensions = 3)




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
            ft_array[:,i] = M.fourier(array[:,i], zero_in_middle = False, first_correction = True, zeropad_to = self.zeropad_to, window_function = window_function, window_length = window_length, flag_plot = flag_plot)  
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
            D.printError("Problem with the Fourier Transforms. Are r[0] and r[1] assigned?", inspect.stack())
            return 0
        
        # phase the spectrum
        self.s = numpy.real(numpy.exp(1j * self.phase_rad) * self.f[0] + numpy.exp(-1j * self.phase_rad) * self.f[1])
        
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
            self.s_axis[0] = M.make_ft_axis(length = 2*numpy.shape(self.s)[0], dt = self.r_axis[0][1]-self.r_axis[0][0], undersampling = self.undersampling)
        except TypeError:
            D.printError("Problem with making the Fourier Transformed axis. Is r_axis[0] assigned?", inspect.stack())
            return 0
            
        self.s_axis[0] = self.s_axis[0][0:len(self.s_axis[0])/2]
        self.s_axis[2] = self.r_axis[2] + self.r_correction[2]  
        
        # add some stuff to self
        self.s_units = ["cm-1", "fs", "cm-1"]
        try:
            self.s_resolution = [(self.s_axis[0][1] - self.s_axis[0][0]), 0, (self.s_axis[2][1] - self.s_axis[2][0])]
        except TypeError:
            D.printError("The resolution of the spectrum can not be determined. This can mean that the original axes (r_axis) or the spectral axes (s_axis) contains an error.", inspect.stack())
            print("r_axis[0]:", self.r_axis[0])
            print("r_axis[2]:", self.r_axis[2])
            print("s_axis[0]:", self.s_axis[0])
            print("s_axis[2]:", self.s_axis[2])
            return 0                
            
            

    def find_z(self, x_range = [0,0], y_range = [0, -1]):
        """
        Finds the z for a certain area of the spectrum. 
        """
        return PEF.find_z(self.s, self.s_axis, x_range = x_range, y_range = y_range)





    # plot the spectrum
    def plot(self, plot_type = "S", x_range = [0, 0], y_range = [0, -1], zlimit = -1, contours = 12, filled = True, black_contour = True, title = "", x_label = "", y_label = "", diagonal_line = True, new_figure = True, flag_no_units = False, pixel = -1, invert_colors = False, flag_aspect_ratio = True, linewidth = -1):
        """
        croc.pe.plot
        
        INPUT:
        - plot_type: 'S' plots the purely absorptive spectrum (default), 'R' plots the rephasing part, 'NR' the non-rephasing part.
        
        This function will plot the purely absorptive spectrum. It is a wrapper function for P.contourplot. It will put the data in the right format, adds some labels etc. This should do for 99% of the cases. 
        For details about the options, see P.contourplot.    
        """

        if plot_type == "spectrum" or plot_type == "S":
            data = self.s
        elif plot_type == "rephasing" or plot_type == "R":
            data = numpy.real(numpy.exp(-1j * self.phase_rad) * self.f[0])
        elif plot_type == "non-rephasing" or plot_type == "NR":
            data = numpy.real(numpy.exp(1j * self.phase_rad) * self.f[1])  
        else:
            D.printError("Invalid plot type.", inspect.stack())
            return 0
        
        if pixel < 0:
            
            if flag_no_units:
                x_axis = numpy.arange(len(self.s_axis[2]))
                y_axis = numpy.arange(len(self.s_axis[0]))
                x_range = [0,0]
                y_range = [0,0]
                if x_label == "":
                    x_label = "spectrometer (pixels)"
                if y_label == "":
                    y_label = "FT (steps)"
                diagonal_line = False
                flag_aspect_ratio = False

            else:
                x_axis = self.s_axis[2]
                y_axis = self.s_axis[0]    
                if x_label == "":
                    x_label = "w3 (" + str(self.s_units[2]) + ")"
                if y_label == "":
                    y_label = "w1 (" +  str(self.s_units[0]) + ")"
            
            if title == "":
                title = self.objectname + ", t2: " + str(self.r_axis[1]) + "\n scans x shots: " + str(self.n_scans) + "x" + str(self.n_shots)
            
            P.contourplot(data, x_axis, y_axis, x_range = x_range, y_range = y_range, zlimit = zlimit, contours = contours, filled = filled, black_contour = black_contour, title = title, x_label = x_label, y_label = y_label, diagonal_line = diagonal_line, new_figure = new_figure, invert_colors = invert_colors, flag_aspect_ratio = flag_aspect_ratio, linewidth = linewidth) 
        
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
        
            P.linear(data[pixel,:], x_axis, x_range = x_range, y_range = y_range, x_label = x_label, y_label = y_label, title = title, new_figure = new_figure)
            




    # plot the rephasing part of the spectrum
    def plot_R(self, x_range = [0, 0], y_range = [0, -1], zlimit = -1, contours = 12, filled = True, black_contour = True, title = "", x_label = "", y_label = "", new_figure = True): 
    
        print("ADVISE (croc.pe.plot_R): The function only calls croc.pe.plot(plot_type='R'), but may not be completely up-to-date.\n")                      
        self.plot(plot_type = "R", x_range = x_range, y_range = y_range, zlimit = zlimit, contours = contours, filled = filled, black_contour = black_contour, title = title, x_label = x_label, y_label = y_label, new_figure = new_figure)  

  
    # plot the non-rephasing part of the spectrum
    def plot_NR(self, x_range = [0, 0], y_range = [0, -1], zlimit = -1, contours = 12, filled = True, black_contour = True, title = "", x_label = "", y_label = "", new_figure = True):          
    
        print("ADVISE (croc.pe.plot_NR): The function only calls croc.pe.plot(plot_type='NR'), but may not be completely up-to-date.\n")          
        self.plot(plot_type = "NR", x_range = x_range, y_range = y_range, zlimit = zlimit, contours = contours, filled = filled, black_contour = black_contour, title = title, x_label = x_label, y_label = y_label, new_figure = new_figure)


    # plot the time domain
    def plot_T(self, pixel = -1, x_range = [0, 0], y_range = [0, 0], zlimit = -1, contours = 12, filled = True, black_contour = True, title = "", x_label = "", y_label = "", new_figure = True, flag_no_units = False):
        """
        croc.pe.plot_T
        
        This function will plot the measured data, still in the time domain. It is a wrapper function for P.contourplot. It will put the data in the right format, adds some labels etc. This should do for 99% of the cases. 
        For details about the options, see P.contourplot.    
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

        
        if pixel == -1:
            P.contourplot(data, x_axis, y_axis, x_range = x_range, y_range = y_range, zlimit = zlimit, contours = contours, filled = filled, black_contour = black_contour, title = title, x_label = x_label, y_label = y_label, new_figure = new_figure, diagonal_line = False, flag_aspect_ratio = False)  
        
        else:
            P.linear(data[pixel,:], x_axis, x_range = x_range, y_range = y_range, x_label = "Time (fs)", y_label = "Absorbance", title = title, new_figure = new_figure)




class pe_combine(pe):
    """
    croc.Pe.pe_combine(pe)
    
    Combines two classes, either adding or subtracting.
    
    CHANGELOG:
    20120228 RB: made this function, replacing pe_sub and pe_add
    
  
    
    
    
    """

    def __init__(self, objectname, class_plus = [], class_min = []):
        """
        INPUT:
        - objectname (string): unique name
        - class_plus (array with class objects): these objects will be added together
        - class_min (array with class objects): these objects will be subtracted
        
        
        NOTES:
        Each measurement is normalized. For stepped scan, it is done in the computer, for fast scan we do bins/bin_count. If we have more scans, the bins are 'fuller' but the bin_count is correspondingly higher.
        
        When we add measurements
        
        4 measurements m[0] to m[3] have n[0] to n[3] n_scans. We add the first two and subtract the other two as follows:
        {m[0]*n[0]/(n[0]+n[1]) + m[1]*n[1]/(n[0]+n[1])} - {m[2]*n[2]/(n[2]+n[3]) + m[3]*n[3]/(n[2]+n[3])}
        
        
        USAGE:
        - Add two objects: mess1+mess2
        Use: Use: croc.Pe.pe_combine("object", class_plus = [mess1, mess2])
        If mess1 has 10 scans and mess2 has 100 scans, the time and frequency domain spectrum will be added by weight: (10*mess1.spectrum + 100*mess2.spectrum)/(10+100). The same is for two spectra that are both subtracted.
        
        - Subtract one object from the other: mess1 - mess2
        Use: croc.Pe.pe_combine("object", class_plus = [mess1], class_min = [mess2])
        If mess1 has 10 scans and mess2 100 scans, the subtraction will not be weighed.
        
        - Add and subtract multiple objects: (mess1+mess2)-(mess3-mess4)
        Use: croc.Pe.pe_combine("object", class_plus = [mess1, mess2], class_min = [mess3, mess4])    

        
        """
        
        croc.Pe.pe.__init__(self, objectname)
        
        flag_variables_set = False
    
        n_scans = 0
        flag_s = 0.0
        flag_r = 0.0
        flag_b = 0.0
        
        for i in range(len(class_plus)):
            n_scans += class_plus[i].n_scans
            
            self.mess_type = class_plus[i].mess_type
            
            if self.mess_type == "FastScan":            
                self.b = [0] * 4  
                self.b_axis = [0] * 4
                self.b_count = [0] * 4
                self.incorrect_count = [0] * 4
            
            try:
                if numpy.shape(class_plus[i].s)[0] > 1:
                    flag_s += 1
                else:
                    slag_s = -1
            except AttributeError:
                flag_s = -1

            try:
                if numpy.shape(class_plus[i].r[0])[0] > 1:
                    flag_r += 1
                else:
                    slag_r = -1
            except AttributeError:
                flag_r = -1

            try:
                if numpy.shape(class_plus[i].b[0])[0] > 1:
                    flag_b += 1
                else:
                    slag_b = -1
            except AttributeError:
                flag_b = -1
            except IndexError:
                flag_b = -1

        for i in range(len(class_plus)):
            if flag_s / len(class_plus) == 1:
                self.s += class_plus[i].s * class_plus[i].n_scans / n_scans
        
            if flag_r / len(class_plus) == 1:
                for j in range(len(class_plus[i].r)):
                    self.r[j] += class_plus[i].r[j] * class_plus[i].n_scans / n_scans

            if flag_b / len(class_plus) == 1:
                for j in range(len(class_plus[i].b)):
                    self.b[j] += class_plus[i].b[j]
                    self.b_count[j] += class_plus[i].b_count[j]

            if flag_variables_set == False:
                self.set_variables(class_plus[i])
                flag_variables_set = True

        self.n_scans = n_scans
  
    
        ### subtraction ###
        n_scans = 0
        flag_s = 0.0
        flag_r = 0.0
        flag_b = 0.0
                
        for i in range(len(class_min)):
            n_scans += class_min[i].n_scans

            self.mess_type = class_min[i].mess_type
            
            if self.mess_type == "FastScan":            
                self.b = [0] * 4  
                self.b_axis = [0] * 4
                self.b_count = [0] * 4
                self.incorrect_count = [0] * 4
            
            try:
                if numpy.shape(class_min[i].s)[0] > 1:
                    flag_s += 1
                else:
                    slag_s = -1
            except AttributeError:
                flag_s = -1

            try:
                if numpy.shape(class_min[i].r[0])[0] > 1:
                    flag_r += 1
                else:
                    slag_r = -1
            except AttributeError:
                flag_r = -1

            try:
                if numpy.shape(class_min[i].b[0])[0] > 1:
                    flag_b += 1
                else:
                    slag_b = -1
            except AttributeError:
                flag_b = -1
            except IndexError:
                flag_b = -1
        
        for i in range(len(class_min)):
            
            if flag_s / len(class_min) == 1:
                self.s -= class_min[i].s * class_min[i].n_scans / n_scans
        
            if flag_r / len(class_min) == 1:
                for j in range(len(class_min[i].r)):
                    self.r[j] -= class_min[i].r[j] * class_min[i].n_scans / n_scans

            if flag_b / len(class_min) == 1:
                for j in range(len(class_min[i].b)):
                    self.b[j] -= class_min[i].b[j]
                    self.b_count[j] -= class_min[i].b_count[j]

            if flag_variables_set == False:
                self.set_variables(class_min[i])
                flag_variables_set = True



    def set_variables(self, obj):   
    
        self.phase_degrees = obj.phase_degrees
        
        self.n_shots = obj.n_shots
        self.n_steps = obj.n_steps
        
        self.r_axis = obj.r_axis
        self.r_domain = obj.r_domain
        self.r_resolution = obj.r_resolution
        self.r_units = obj.r_units
        self.r_correction = obj.r_correction
        self.r_correction_applied = obj.r_correction_applied
        
        self.s_axis = obj.s_axis
        self.s_domain = obj.s_domain
        self.s_resolution = obj.s_resolution
        self.s_units = obj.s_units

        
        if self.mess_type == "FastScan":
            try:
                self.chopper_channel = obj.chopper_channel
                self.n_channels = obj.n_channels
                self.n_fringes = obj.n_fringes
                self.extra_fringes = obj.extra_fringes
            except AttributeError:  
                pass            
            
        











class pe_sub(pe):

    """
    croc.pe.pe_sub
    
    Subtracts one class from the other. Use pe_combine instead. This class is only for legacy purposes.
    
    """

    def __init__(self, objectname, class_plus, class_min):
        
        croc.Pe.pe_combine(objectname, class_plus = [class_plus], class_min = [class_min])

    
    
class pe_add(pe):
    """
    croc.pe.pe_sub
    
    Adds two classes. Use pe_combine instead. This class is only for legacy purposes.
    
    """    
    def __init__(self, objectname, class1, class2):
        
        croc.Pe.pe_combine(objectname, class_plus = [class1, class2])

        
        
        
        
        
    


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
        self.n_pixels = 32  
    
    
        
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
            D.printError("Old style not implemented yet", inspect.stack())
        
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
                    D.printError(("Unable to load file: " + file_R), inspect.stack())
                    raise
                    return 0   
                self.r_axis[0] = temp[1:,0]
                self.r_axis[2] = temp[0,1:self.n_pixels+1]
                self.r[0] = temp[1:,1:self.n_pixels+1]
                
                try:
                    temp = numpy.loadtxt(file_NR)
                except IOError:
                    D.printError(("Unable to load file: " + file_NR), inspect.stack())
                    raise
                    return 0
                self.r[1] = temp[1:,1:self.n_pixels+1]               
                
                if noise:
                    try:
                        temp = numpy.loadtxt(file_R_noise)
                    except IOError:
                        D.printError(("Unable to load file: " + file_R_noise), inspect.stack())
                        raise
                        return 0
                    self.r_noise[0] = temp[1:,1:self.n_pixels+1]                   
                        
                    try:
                        temp = numpy.loadtxt(file_NR_noise)
                    except IOError:
                        D.printError(("Unable to load file: " + file_NR_noise), inspect.stack())
                        raise
                        return 0
                    self.r_noise[1] = temp[1:,1:self.n_pixels+1]     
            
                # fill in some details 
                self.r_units = ["fs", "fs", "cm-1"]
                self.r_resolution = [(self.r_axis[0][1] - self.r_axis[0][0]), 0, (self.r_axis[2][1] - self.r_axis[2][0])]   
                self.n_steps = len(self.r_axis[0])         
            
            
            # import multiple scans and average them
            else:
                D.printError("The ability to import specific scans is not yet implemented.", inspect.stack())
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
            
                if re.match("Start_time", line):
                
                    self.date = int(str(line[11:15]) + str(line[16:18]) + str(line[19:21]))
                
                if re.match("mess2Dheterodyne_meta_format", line): 
                    self.data_type_version = str(line[-5:-2])               
            
                if re.match("Shots", line): 
                    self.n_shots = int((re.search(regex, line)).group())
                
                if re.match("Fringes", line): 
                    self.n_fringes = int((re.search(regex, line)).group())            
                
                try:
                    if re.match("Phase", line):
                        self.phase_degrees = float((re.search(regex, line)).group())
                except AttributeError:
                    D.printWarning("no or invalid phase", inspect.stack())
                
                if re.match("Comments", line):
                    self.comment = line[9:]
                    
                if re.match("Scan", line):
                    temp_scans = int((re.search(regex, line[4:7])).group())
        except IOError:
            D.printError(("Unable to load file: " + filebase), inspect.stack())
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
        if self.path == "":
            self.path = self.base_filename + "_" + str(self.time_stamp) + "_T" + str(self.r_axis[1]) + "/"  
        else:
            self.path = self.path + "/" + self.base_filename + "_" + str(self.time_stamp) + "_T" + str(self.r_axis[1]) + "/"
        
        
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
        
        print(self.path)
                
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
        
        error_flag = False
        
        if len(self.imported_scans) == 0:
            # set self.reference
            self.import_reference()
            # set phase, shots, 
            self.import_meta()

        # see if we already imported this file
        if self.imported_scans.count(scan) != 0:
            if flag_import_override == False: 
                D.printError("Scan is already imported.")  
                return 0
            else:
                D.printWarning("Scan is already imported, but will be imported anyway because flag_import_override is set to True.", inspect.stack())
            
        filename = self.make_filenames(scan)

        # for the 4 files
        for k in range(4):
        
            flag_skip_binning = False
        
            # to distuinguish between the two diagrams
            if k < 2:
                diagram = 0
            else:
                diagram = 1
            
            # import the data
            try:
                if self.data_type_version == "1.2":
                    [m, fringes] = self.import_raw_data(filename[k])
                elif self.data_type_version == "1.3":
                    [m, c, fringes] = self.import_raw_data(filename[k], flag_counter = True)
                elif self.data_type_version == "1.4":

                    result = self.import_binned_data(filename[k], diagram)
                    flag_skip_binning = True

                    if result == False:
                        try:
                            [m, c, fringes] = self.import_raw_data(filename[k], flag_counter = True)
                            flag_skip_binning = False
                        except IOError:
                            return False
                            
            except IOError:
                return False
                                    
            # if the number of fringes can not be set using the meta file, find it here 
            if self.n_fringes == 0:
                self.n_fringes = int(numpy.abs(fringes[1] - fringes[0]))
            
            # reconstruct the counter
            if self.data_type_version == "1.2":
                m_axis, counter, correct_count = self.reconstruct_counter(m, fringes[0], fringes[1], flag_plot = False)
                
            elif self.data_type_version == "1.3":   

                m_axis = c + fringes[0]

                if m_axis[-1] == fringes[1]:
                    correct_count = True
                else:
                    correct_count = False
            
            elif self.data_type_version == "1.4": 
                # the case where the binning failed and VB6 reverts to data version 1.3
                if flag_skip_binning == False:
                    m_axis = c + fringes[0]
    
                    if m_axis[-1] == fringes[1]:
                        correct_count = True
                    else:
                        correct_count = False   
                else:
                    correct_count = True
                
            else:
                D.printError("Unknown data type", inspect.stack())
                correct_count = False
            
            # check for consistency
            if correct_count == False:
                print("Scan: " + str(scan) + ", File: " + str(k) + ": Miscount!")
                
                self.incorrect_count[k] += 1

            # if it is consistent, continue to bin the data
            elif flag_skip_binning == False:
                print("Scan: " + str(scan) + ", File: " + str(k) + ": Count is correct!")
                          
                # make b the correct size, if it isn't already
                if numpy.shape(self.b_axis)[-1] == 2:
                    self.make_arrays()
        
                # bin the data
                self.bin_data(m, m_axis, diagram)
                
                # calculate the noise
                if flag_calculate_noise:
#                    print("This function does not exist anymore.")
                    self.bin_for_noise(m, m_axis, diagram, flag_noise_time_domain)
            
            else:
                print("Scan: " + str(scan) + ", File: " + str(k) + ": Scan imported")
                

                # all the data is now written into self.b* 

        # construct the actual measurement
        # this should catch the situation that there are 4 miscounts in the first scan
        if type(self.b_count) == numpy.ndarray:
            if flag_construct_r:
                self.construct_r()
        else:
            error_flag = True

        # now append that we imported this scan
        self.imported_scans.append(scan)
        
        self.n_scans = len(self.imported_scans)
        
        if error_flag:
            return False
        else:
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
    
        self.b = [numpy.zeros((self.n_fringes + 2 * self.extra_fringes, self.n_channels), dtype = "cfloat"),numpy.zeros((self.n_fringes + 2 * self.extra_fringes, self.n_channels), dtype = "cfloat"),numpy.zeros((self.n_fringes + 2 * self.extra_fringes, self.n_channels), dtype = "cfloat"),numpy.zeros((self.n_fringes + 2 * self.extra_fringes, self.n_channels), dtype = "cfloat")] 
        # from -20 to 920
        self.b_axis[0] = numpy.arange(- self.extra_fringes, self.n_fringes + self.extra_fringes)
        # from -20 to 920
        self.b_axis[1] = numpy.arange(- self.extra_fringes, self.n_fringes + self.extra_fringes)
        self.b_count = numpy.zeros((4, self.n_fringes + 2 * self.extra_fringes))
        self.r = [numpy.zeros((self.n_fringes, 32), dtype = "cfloat"),numpy.zeros((self.n_fringes, 32), dtype = "cfloat")] 



    def import_binned_data(self, path_and_filename, diagram):
    
        b, b_count, b_axis = IOM.import_binned_data(path_and_filename, self.n_pixels, diagram)
        
        # if b etc are integers, the importing went wrong
        if type(b) == int:
            return False
        
        if numpy.shape(self.b_axis)[-1] == 2:
            self.make_arrays()        

        # to get rid of the bins outside of the range
        if diagram == 0:
            short = -int(self.b_axis[0][0] - b_axis[0] + 4000)
            long = -int(self.b_axis[0][-1] - b_axis[-1] + 4000)
        else:
            short = int(self.b_axis[1][-1] + b_axis[0] - 4000)
            long = int(self.b_axis[1][0] - b_axis[-1] + 4000)

        # work around since self.b[list][2D-numpy.array]
        self.b[diagram*2][short:long, :self.n_pixels] += b[diagram*2,:,:]
        self.b[diagram*2+1][short:long, :self.n_pixels] += b[diagram*2+1,:,:]
        
        self.b_count[diagram*2:diagram*2+2, short:long] += b_count[:][:]

        return True



    def bin_data(self, m, m_axis, diagram):
        """
        See croc.Resources.PEFunctions.bin_data() for instructions. This function is for legacy purposes.
        
        """
        self.bin_data_helper(m, m_axis, diagram, b = self.b, b_count = self.b_count)


        



    def bin_data_helper(self, m, m_axis, diagram, b, b_count):
        i_range = range(self.n_shots)
        for i in i_range:            
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
        
        temp = numpy.zeros((4, b_fringes, self.n_channels), dtype = "cfloat")
        
        # average the data for the two diagrams
        i_range = range(b_fringes)
        for j in range(4):
            for i in i_range:
                if self.b_count[j][i] != 0:
                    temp[j,i,:] = self.b[j][i,:] / self.b_count[j,i]    
                else:    
                    temp[j,i,:] = numpy.zeros(self.n_channels)                
        
        # select n_fringes, ie. discard the extra fringes
        temp = temp[:,self.extra_fringes:(self.n_fringes+self.extra_fringes),:self.n_pixels]
              
        # make the r_axis
        self.r_axis[0] = self.b_axis[0][self.extra_fringes:(self.n_fringes+self.extra_fringes)] * C.hene_fringe_fs

        if flag_no_logarithm:
            # for testing purposes
            for j in range(2):
                self.r[j][:,:self.n_pixels] = temp[2*j,:,:self.n_pixels] - temp[2*j+1,:,:self.n_pixels]
        
        else:
            # convert it to mOD
            for j in range(2):
                self.r[j][:,:self.n_pixels] = -numpy.log10(1+ 2*(temp[2*j,:,:self.n_pixels] - temp[2*j+1,:,:self.n_pixels])/self.reference[:self.n_pixels]) 
                
                # the time order for the NR data binned in VB6 is reverse
                if self.data_type_version == "1.4" and j == 1:
                    self.r[j][:,:] = self.r[j][::-1,:]
        
        #self.r = numpy.nan_to_num(self.r)
        
        self.r_units = ["fs", "fs", "cm-1"]



       

                
  
    def reconstruct_counter(self, data, start_counter = 0, end_counter = 0, flag_plot = False):
        """
        See croc.Resources.PEFunctions.reconstruct_counter for instructions. This function is for legacy purposes.   
        """
        return PEF.reconstruct_counter(data, self.x_channel, self.y_channel, start_counter = start_counter, end_counter = end_counter, flag_plot = flag_plot)

    def find_angle(self, m, m_axis, k = 0, skip_first = 0, skip_last = 0, flag_normalize_circle = True, flag_scatter_plot = True, new_figure = True):   
        """
         See croc.Resources.PEFunctions.angle_distribution for instructions. This function is for legacy purposes. 
        """ 
        PEF.angle_distribution(m = m, x_channel = self.x_channel, y_channel = y_channel, m_axis = m_axis, k = k, skip_first = skip_first, skip_last = skip_last, flag_normalize_circle = flag_normalize_circle, flag_scatter_plot = flag_scatter_plot, new_figure = new_figure)

    def import_raw_data(self, path_and_filename, flag_counter = False):
        """
        See croc.Resources.IOMethods.import_data_FS for instructions. This function is for legacy purposes.
        """        
        return IOM.import_data_FS(path_and_filename, n_shots = self.n_shots, n_channels = self.n_channels, flag_counter = flag_counter)

    def bin_info(self):   
        """
        See croc.Resources.bin_info for instructions. Gives some statistics about the binning.
        """ 
        PEF.bin_info(self.b_axis, self.b_count)   
        







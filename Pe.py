"""
pe.py

DESCRIPTION
    This file contains the data analysis details for the 2DIR setup.


CHANGELOG
    RB 20091214 - first draft.
    RB 20110908 - combined some stuff together
    RB 20120227 - moved some functions to croc.Resources.PEFunctions

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
from croc.Resources.DataClasses import mess_data
import croc.Resources.Mathematics as M
import croc.Resources.Plotting as P
import croc.Resources.Constants as C
import croc.Resources.PEFunctions as PEF
import croc.Resources.IOMethods as IOM
import croc.Debug

reload(croc.Debug)

if croc.Debug.reload_flag:
    reload(croc)
    reload(croc.Resources.DataClasses)
    reload(M)
    reload(P)
    reload(C)
    reload(PEF)
    reload(IOM)
    


debug_flag = croc.Debug.debug_flag

### METHODS TO WORK WITH PICKLES ###

def make_pickle_name(base_filename, pop_time, time_stamp, path = ""):
    return path + base_filename + "_" + str(time_stamp) + "_T" + str(pop_time) + ".pickle"

def make_path(base_filename, pop_time, time_stamp, path = ""):
    return path + base_filename + "_" + str(time_stamp) + "_T" + str(pop_time) + "/"

def check_pickle_exists(path_and_filename):
    return os.path.exists(path_and_filename)

def import_pickle(mess_date, mess_array = [], pickle_name = ""):

    if pickle_name == "":
        pickle_name = str(mess_date) + "_fs.pickle"
    
    obj = croc.Resources.DataClasses.import_db(pickle_name)

    new_obj = [0] * len(obj)

    if len(mess_array) == 0:
        new_obj = obj
    else:
        for i in range(len(mess_array)):
            for j in range(len(obj)):
                if mess_array[i][0] == obj[j].objectname:
                    new_obj[i] = obj[j]
    
    return new_obj



def save_pickle(obj, pickle_name):
    croc.Resources.DataClasses.make_db(obj, pickle_name)




def import_mess_array(mess_date, mess_array, n_scans, pickle_name, data_dir = "", anal_dir = ""):
    """
    croc.Pe.import_mess_array
    
    Imports a whole array with measurements without saving, closing and re-opening the pickle all the time. This significantly reduces time for long series of measurements. 
    """
    
    for i in range(len(mess_array)):
        for j in range(i+1, len(mess_array)):
            if mess_array[i][0] == mess_array[j][0]:
                print("ERROR (croc.Pe.import_mess_array): The objectnames have to be unique! This is not the case. Aborting.")
                return False
                
    if type(n_scans) == int:
        n_scans = [n_scans] * len(mess_array)
    
    if data_dir == "":
        data_dir = os.getcwd()[:-17] + "data/" + str(mess_date) + "/"   
    
    imp = [0] * len(mess_array)

    for i in range(len(mess_array)):
        imp[i] = croc.Pe.pefs(mess_array[i][0], mess_array[i][1], mess_array[i][2], mess_array[i][3])
        imp[i].path = data_dir + imp[i].path
        
        for j in range(n_scans[i]):
            imp[i].add_data(scan = j + 1, flag_construct_r = False)
        
        imp[i].construct_r()
    
    croc.Resources.DataClasses.make_db(imp, pickle_name)

def import_data(mess_date, import_mess, import_from, import_to, mess_array, 
        data_dir = "", 
        anal_dir = "",
        pickle_name = "",
        flag_calculate_noise = False,
        flag_no_pickle = False,
        flag_overwrite_pickle = False
    ):
    """
    croc.Resources.IOMethods.import_data
    
    Imports data and saves it into a pickle. The method will import several scans from a measurement. This works best when you have fewer measurements with more scans. 
    """
    if import_from == 0 or import_to == 0:
        print("No import required...")
        return 0
    else:
    
        # first check if mess_i actually exists
        try:
            mess_array[import_mess]
            
            if anal_dir == "":
                anal_dir = os.getcwd() + "/"
            
            if data_dir == "":
                # the 'root' is removes the '/analysis/20111111/'
                data_dir = os.getcwd()[:-17] + "data/" + str(mess_date) + "/"
                
            # default name of the pickle
            # use the _fs postfix to differentiate it from other pickles
            if pickle_name == "":
                pickle_name = str(mess_date) + "_fs.pickle"

            # first, check if there is a pickle
            if flag_overwrite_pickle == False and croc.Pe.check_pickle_exists(pickle_name): 
                # found a pickle, now import it
                print("Found pickle")
                mess = croc.Resources.DataClasses.import_db(pickle_name)
            else:
                # there is no pickle, so make a new a new data structure
                print("No pickle found")
                mess = [0]
                mess[0] = croc.Pe.pefs(mess_array[0][0], mess_array[0][1], mess_array[0][2], mess_array[0][3])
                mess[0].path = data_dir + mess[0].path
            
            # see if we have to extend mess to fit with mess_array
            if len(mess) < len(mess_array):
                for i in range(len(mess_array)):
                    try:
                        # this works if mess[i] exists
                        mess[i].objectname
                    except IndexError:
                        # it fails if it does not exists, so make a new one
                        mess.append(croc.Pe.pefs(mess_array[i][0], mess_array[i][1], mess_array[i][2], mess_array[i][3]))    
                        mess[-1].path = data_dir + mess[-1].path
            
                        
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
                    croc.Resources.DataClasses.make_db(mess, pickle_name)
                else:
                    print("No need to update pickle...")
            else:
                print("flag_no_pickle == True")
        
        except IndexError:
            # mess_i does not exist
            print("ERROR (script_import.py): mess_i is outside of the range of mess_array")






# def import_data(mess_date, import_mess, import_from, import_to, mess_array, data_dir = "", anal_dir = "", pickle_name = "", flag_calculate_noise = False, flag_no_pickle = False, flag_overwrite_pickle = False):
#     IOM.import_data(mess_date, import_mess, import_from, import_to, mess_array, data_dir = data_dir, anal_dir = anal_dir, pickle_name = pickle_name, flag_calculate_noise = flag_calculate_noise, flag_no_pickle = flag_no_pickle, flag_overwrite_pickle = flag_overwrite_pickle)       

           
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
        
        print("=== CROCODILE PHOTON ECHO ===")
        
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
            print("\nERROR (croc.pe.pe_exp.absorptive): Problem with the Fourier Transforms. Are r[0] and r[1] assigned?")
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
            
            

    def find_z(self, x_range = [0,0], y_range = [0, -1]):
        """
        Finds the z for a certain area of the spectrum. 
        """
        return PEF.find_z(self.s, self.s_axis, x_range = x_range, y_range = y_range)





    # plot the spectrum
    def plot(self, plot_type = "S", x_range = [0, 0], y_range = [0, -1], zlimit = -1, contours = 12, filled = True, black_contour = True, title = "", x_label = "", y_label = "", diagonal_line = True, new_figure = True, flag_no_units = False, pixel = -1, invert_colors = True):
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
            print("ERROR (croc.pe.plot): invalid plot type. ")
            return 0
        
        if pixel < 0:
        
            if flag_no_units:
                x_axis = numpy.arange(len(self.s_axis[2]))
                y_axis = numpy.arange(len(self.s_axis[0]))
                y_range = [0,0]
                if x_label == "":
                    x_label = "spectrometer (pixels)"
                if y_label == "":
                    y_label = "FT (steps)"
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
            
                   
            P.contourplot(data, x_axis, y_axis, x_range = x_range, y_range = y_range, zlimit = zlimit, contours = contours, filled = filled, black_contour = black_contour, title = title, x_label = x_label, y_label = y_label, diagonal_line = diagonal_line, new_figure = new_figure, invert_colors = invert_colors) 
        
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
        
            P.linear(data[pixel,:], x_axis, x_range = [0, 0], y_range = [0, 0], x_label = x_label, y_label = y_label, title = title, new_figure = new_figure)
            




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
            P.contourplot(data, x_axis, y_axis, x_range = x_range, y_range = y_range, zlimit = zlimit, contours = contours, filled = filled, black_contour = black_contour, title = title, x_label = x_label, y_label = y_label, new_figure = new_figure, diagonal_line = False)  
        
        else:
            P.linear(data[pixel,:], x_axis, x_range = [0, 0], y_range = [0, 0], x_label = "Time (fs)", y_label = "Absorbance", title = "Time", new_figure = new_figure)




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
        
        print(flag_s, flag_r, flag_b)

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
        
        print(flag_s, flag_r, flag_b)
        
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
                self.r_axis[2] = temp[0,1:self.n_pixels+1]
                self.r[0] = temp[1:,1:self.n_pixels+1]
                
                try:
                    temp = numpy.loadtxt(file_NR)
                except IOError:
                    print("ERROR (croc.pe.import_data): unable to load file:", file_NR)
                    raise
                    return 0
                self.r[1] = temp[1:,1:self.n_pixels+1]               
                
                if noise:
                    try:
                        temp = numpy.loadtxt(file_R_noise)
                    except IOError:
                        print("ERROR (croc.pe.import_data): unable to load file:", file_R_noise)
                        raise
                        return 0
                    self.r_noise[0] = temp[1:,1:self.n_pixels+1]                   
                        
                    try:
                        temp = numpy.loadtxt(file_NR_noise)
                    except IOError:
                        print("ERROR (croc.pe.import_data): unable to load file:", file_NR_noise)
                        raise
                        return 0
                    self.r_noise[1] = temp[1:,1:self.n_pixels+1]     
            
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
                    self.phase_degrees = float((re.search(regex, line)).group())
                
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
#                    print("This function does not exist anymore.")
                    self.bin_for_noise(m, m_axis, diagram, flag_noise_time_domain)

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
        self.b_axis[0] = numpy.arange(- self.extra_fringes, self.n_fringes + self.extra_fringes)
        self.b_axis[1] = numpy.arange(- self.extra_fringes, self.n_fringes + self.extra_fringes)
        self.b_count = numpy.zeros((4, self.n_fringes + 2 * self.extra_fringes))
        self.r = [numpy.zeros((self.n_fringes, 32), dtype = "cfloat"),numpy.zeros((self.n_fringes, 32), dtype = "cfloat")] 







    def bin_data(self, m, m_axis, diagram):
        """
        See croc.Resources.PEFunctions.bin_data() for instructions. This function is for legacy purposes.
        
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
        for j in range(4):
            for i in range(b_fringes):
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

    def import_raw_data(self, path_and_filename):
        """
        See croc.Resources.IOMethods.import_data_FS for instructions. This function is for legacy purposes.
        """
        return IOM.import_data_FS(path_and_filename, n_shots = self.n_shots, n_channels = self.n_channels)

    def bin_info(self):   
        """
        See croc.Resources.bin_info for instructions. Gives some statistics about the binning.
        """ 
        PEF.bin_info(self.b_axis, self.b_count)   
        







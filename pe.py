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

import croc
# to prevent a conflict with other classes (like ftir)
from croc.DataClasses import mess_data
import croc.Absorptive
import croc.Plotting

reload(croc)
reload(croc.Absorptive)
reload(croc.Plotting)

class pe(croc.DataClasses.mess_data):
    """
    croc.pe.pe
    
    This class contains all the functions to import, calculate and plot a photon-echo 2DIR spectrum.
    
    CHANGELOG
    20110910 RB: started the class, using stuff from earlier work
    
    
    """
    
    
    
    def __init__(self, object_name, base_filename, population_time, undersampling, time_stamp = 0000):
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
        
        # photon echo has 3 dimensions: t1/w1, t2, w3
        croc.DataClasses.mess_data.__init__(self, object_name, diagrams = 2, dimensions = 3)
        self.base_filename = base_filename
        self.r_axis[1] = population_time
        self.undersampling = undersampling
        self.time_stamp = time_stamp





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
            
                if re.match("Phase", line):
                    self.phase_degrees = float((re.search(regex, line)).group())
                
                if re.match("Comments", line):
                    self.comment = line[9:]
                    
                if re.match("Scan", line):
                    temp_scans = int((re.search(regex, line[4:6])).group())
        except IOError:
            print("ERROR (croc.pe.import_meta): unable to load file:", filebase)
            raise
            return 0            
  
        # close the file     
        fileinput.close()
        
        # number of scans is (number of scans started) - 1, because the last one wasn't finished
        self.n_scans = temp_scans - 1



    def fourier_helper(self, array):
        """
        fourier_helper
        
        20101204/RB: started
        20110909 RB: continued
        
        This is a function to Fourier Transform experimental 2DIR spectra, ie, spectra with a time and frequency axis. It basically repeats the Fourier function for all pixels.
         
        """
    
        # you need a new array that also has complex numbers  
        # the length depends on zeropadding      
        [x, y] = numpy.shape(array)
        if self.zeropad_to != None:
            x = self.zeropad_to
        ft_array = numpy.reshape( numpy.zeros(x*y, dtype=numpy.cfloat), (x, y))

        # iterate over all the pixels
        for i in range(len(self.r_axis[2])):
            ft_array[:,i] = croc.Absorptive.fourier(array[:,i], zero_in_middle = False, first_correction = True, zeropad_to = self.zeropad_to)   
        
        return ft_array   


  
                
    def absorptive(self):
        """
        croc.pe.fourier
        
        This function does the Fourier transform.
        It checks the undersampling.
        It phases the spectrum.
        It makes the axes.
        """
        
        # CHECKS
        # checks the undersampling. It can be 0, but that is hardly used
        if self.undersampling == 0:
            print("WARNING (croc.pe.fourier): undersampling is 0!\n")
        
        # do the fft
        self.f[0] = self.fourier_helper(self.r[0])
        self.f[1] = self.fourier_helper(self.r[1])
        
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
        self.s_axis[0] = croc.Absorptive.make_ft_axis(length = 2*numpy.shape(self.s)[0], dt = self.r_axis[0][1]-self.r_axis[0][0], undersampling = self.undersampling)
        self.s_axis[0] = self.s_axis[0][0:len(self.s_axis[0])/2]
        self.s_axis[2] = self.r_axis[2]    
        
        # add some stuff to self
        self.s_units = ["cm-1", "fs", "cm-1"]
        self.s_resolution = [(self.s_axis[0][1] - self.s_axis[0][0]), 0, (self.s_axis[2][1] - self.s_axis[2][0])]
    





    # plot the spectrum
    def plot(self, plot_type = "S", x_range = [0, 0], y_range = [0, -1], zlimit = 0, contours = 12, filled = True, black_contour = True, title = "", x_label = "", y_label = "", diagonal_line = True, new_figure = True):
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
            x_label = self.s_units[2]
        if y_label == "":
            y_label = self.s_units[0] 
        if title == "":
            title = self.objectname + ", t2: " + str(self.r_axis[1]) + "\n scans x shots: " + str(self.n_scans) + "x" + str(self.n_shots)
        
               
        croc.Plotting.contourplot(data, x_axis, y_axis, x_range = x_range, y_range = y_range, zlimit = zlimit, contours = contours, filled = filled, black_contour = filled, title = title, x_label = x_label, y_label = y_label, diagonal_line = diagonal_line, new_figure = new_figure)  


    # plot the rephasing part of the spectrum
    def plot_R(self, x_range = [0, 0], y_range = [0, -1], zlimit = 0, contours = 12, filled = True, black_contour = True, title = "", x_label = "", y_label = "", new_figure = True): 
    
        print("ADVISE (croc.pe.plot_R): The function only calls croc.pe.plot(plot_type='R'), but may not be completely up-to-date.\n")                      
        self.plot(plot_type = "R", x_range = x_range, y_range = y_range, zlimit = zlimit, contours = contours, filled = filled, black_contour = filled, title = title, x_label = x_label, y_label = y_label, new_figure = new_figure)  

  
    # plot the non-rephasing part of the spectrum
    def plot_R(self, x_range = [0, 0], y_range = [0, -1], zlimit = 0, contours = 12, filled = True, black_contour = True, title = "", x_label = "", y_label = "", new_figure = True):          
    
        print("ADVISE (croc.pe.plot_NR): The function only calls croc.pe.plot(plot_type='NR'), but may not be completely up-to-date.\n")          
        self.plot(plot_type = "NR", x_range = x_range, y_range = y_range, zlimit = zlimit, contours = contours, filled = filled, black_contour = filled, title = title, x_label = x_label, y_label = y_label, new_figure = new_figure)





    # plot the time domain
    def plot_T(self, x_range = [0, 0], y_range = [0, 0], zlimit = 0, contours = 12, filled = True, black_contour = True, title = "", x_label = "", y_label = "", new_figure = True):
        """
        croc.pe.plot_T
        
        This function will plot the measured data, still in the time domain. It is a wrapper function for croc.Plotting.contourplot. It will put the data in the right format, adds some labels etc. This should do for 99% of the cases. 
        For details about the options, see croc.Plotting.contourplot.    
        """
        # concatenate the two diagrams
        data = numpy.concatenate((numpy.flipud(self.r[1]), self.r[0])).T
        x_axis = numpy.concatenate((-numpy.flipud(self.r_axis[0]), self.r_axis[0])) 
        y_axis = self.r_axis[2]
        if x_label == "":
            x_label = self.r_units[0]
        if y_label == "":
            y_label = self.r_units[2]
        
        croc.Plotting.contourplot(data, x_axis, y_axis, x_range = x_range, y_range = y_range, zlimit = zlimit, contours = contours, filled = filled, black_contour = filled, title = title, x_label = x_label, y_label = y_label, new_figure = new_figure,  diagonal_line = False)  

    
    

        
        
                
            
            
    
  
    
    
    













"""
ftir.py

DESCRIPTION
    Tools to plot FTIR spectra

"""

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import


import numpy
import matplotlib 
import matplotlib.pyplot as plt

import croc
from croc.DataClasses import mess_data
import croc.Plotting

reload(croc)
reload(croc.Plotting)



class ftir(croc.DataClasses.mess_data):
    
    
    def __init__(self, object_name, abs_diff = False):
        """
        croc.ftir.__init__
        
        Init the FTIR class.
        
        INPUT:
        - abs_diff: if False, it will show an absorption spectrum. If True, it will make a difference absorption spectrum. In order to do this, a second file has to be loaded. 
        
        """

        print("=== CROCODILE FTIR ===")
        if abs_diff:
            croc.DataClasses.mess_data.__init__(self, object_name, diagrams = 2, dimensions = 1)
            self.mess_type = "AbsDiff"
        else:
            croc.DataClasses.mess_data.__init__(self, object_name, diagrams = 1, dimensions = 1)
            self.mess_type = "Abs"





    def import_data(self):
    
        # for both
        if self.base_filename[-4:] != ".txt":
            self.base_filename = self.base_filename + ".txt"
            
        filename = self.path + self.base_filename    
        try:
            self.r_axis[0], self.r[0] = numpy.loadtxt(filename, delimiter = ",", unpack = True)
        except IOError:
            print("ERROR (croc.ftir.import_data): unable to load file:", filename)
            return 0  
        
        # only for difference absorption
        if self.mess_type == "AbsDiff":
            if self.sec_filename[-4:] != ".txt":
                self.sec_filename = self.sec_filename + ".txt"         
                
            filename = self.path + self.sec_filename
            try:
                self.r_axis[0], self.r[1] = numpy.loadtxt(filename, delimiter = ",", unpack = True)
            except IOError:
                print("ERROR (croc.ftir.import_data): unable to load file:", filename)
                return 0             
        
        # 
        if self.mess_type == "AbsDiff":
            self.s_axis[0] = self.r_axis[0]
            self.s[0] = -numpy.log10(self.r[0] / self.r[1])
        else:
            self.s_axis[0] = self.r_axis[0]
            self.s[0] = self.r[0]
        
        

            
    
    def plot(self, x_range = [0, 0], y_range = [0, 0], x_label = "", y_label = "", title = "", new_figure = True):
    
        data = self.s[0]
        axis = self.s_axis[0]
        
        if title == "": 
            title = self.objectname
            if self.mess_type == "AbsDiff":
                title += " Difference Absorption Spectrum"
            else:
                title += " Absorption Spectrum"
                    
        if x_label == "":
            x_label = self.s_units[0]
        if y_label == "":
            if self.mess_type == "AbsDiff":
                y_label = "Different Absorption (OD)"    
            else:
                y_label = "Absorption (OD)"
                
        
        croc.Plotting.linear(data, axis, x_range = x_range, y_range = y_range, x_label = x_label, y_label = y_label, title = title, new_figure = new_figure)
        
        


































        
        

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
from croc.Resources.DataClasses import mess_data
import croc.Resources.Plotting as P
import croc.Debug

reload(croc.Debug)

if croc.Debug.reload_flag:
    reload(croc)
    reload(P)



class ftir(croc.Resources.DataClasses.mess_data):
    
    
    def __init__(self, object_name):
        """
        croc.ftir.__init__
        
        Init the FTIR class.
        
        INPUT:

        
        """

        print("=== CROCODILE FTIR ===")

        croc.Resources.DataClasses.mess_data.__init__(self, object_name, measurements = 1, dimensions = 1)
        self.mess_type = "FTIR"





    def import_data(self):

        filename = self.path + self.base_filename

        try:
            self.s_axis[0], self.s[0] = numpy.loadtxt(filename, delimiter = ",", unpack = True)
            self.s_domain[0] = "cm-1"
        except IOError:
            print("ERROR (croc.ftir.import_data): unable to load file:", filename)
            return 0  
            

        

            
    
    def plot(self, x_range = [0, 0], y_range = [0, 0], x_label = "", y_label = "", title = "", scale = 1.0, new_figure = True):
    
        data = (self.s[0])[::-1] * scale
        axis = (self.s_axis[0])[::-1]

        if title == "": 
            title = self.objectname
                    
        if x_label == "":
            x_label = self.s_units[0]
        if y_label == "":
            y_label = "Absorption (OD)"
                
        
        P.linear(data, axis, x_range = x_range, y_range = y_range, x_label = x_label, y_label = y_label, title = title, new_figure = new_figure)
        
        


class ftir_combine(ftir):
    
    def __init__(self, objectname, class_plus = [], class_min = []):
        
        croc.Ftir.ftir.__init__(self, objectname)
        

        
        for i in range(len(class_plus)):
            
            self.s[0] += class_plus[i].s[0] / len(class_plus)
            self.s_axis = class_plus[i].s_axis

            
        for i in range(len(class_min)):
            self.s[0] -= class_min[i].s[0] / len(class_min)



















        
        

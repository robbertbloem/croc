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
        
        CHANGELOG:
        2011/xx/xx/RB: started
        2012/08/03/RB: removed difference between spectra and difference spectra and instead introduced class ftir_combine.
        
        INPUT:
        - objectname: a name

        
        """

        print("=== CROCODILE FTIR ===")

        croc.Resources.DataClasses.mess_data.__init__(self, object_name, measurements = 1, dimensions = 1)
        self.mess_type = "FTIR"
        
        self.concentration = 0
        self.pathlength = 0





    def import_data(self):
        """
        Before calling this function, set self.path and self.filename
        The function does not check the extension (.txt, .dpt)
        
        CHANGELOG:
        2011/xx/xx/RB: started
        2012/08/03/RB: removed checking for file extension
        
        """

        filename = self.path + self.base_filename

        try:
            self.s_axis[0], self.s[0] = numpy.loadtxt(filename, delimiter = ",", unpack = True)
            self.s_domain[0] = "cm-1"
            self.s_axis[0] = (self.s_axis[0])[::-1]
            self.s[0] = (self.s[0])[::-1]
        except IOError:
            print("ERROR (croc.ftir.import_data): unable to load file:", filename)
            return 0  
            

        

            
    
    def plot(self, x_range = [0, 0], y_range = [0, 0], x_label = "", y_label = "", title = "", scale = "OD", legend = "", new_figure = True):
        
        """
        Plot the linear spectrum.
        
        CHANGELOG:
        2011/xx/xx/RB: started
        2012/08/03/RB: changes
        
        INPUT:
        - x_range (list with 2 elements): range for the frequency axis. Set to [0,0] for the full range
        - y_range  (list with 2 elements): range for the optical density. Set to [0,0] for the full range
        - x_label (string): set the x_label. 
        - y_label (string): set the label for the y-axis. Default is OD.
        - title (string): set the title
        - scale (string): default is 'OD', alternatively: 'EC' for extinction coefficient. You should have set self.concentration and self.pathlength.
        - new_figure (BOOL): If set to True, it will call plt.figure(), plt.plot() and plt.show(). If set to False, it will only call plt.plot() and you need to call plt.figure() and plt.show() yourself. Usefull if you want to have sub-plots
        """
        # data = (self.s[0])[::-1]
        # y_label = "Absorption (OD)"
        
        print("plot...")
        
        if type(scale) == float:
            print("float")
            data = self.s[0] * scale
            if y_label == "":
                y_label = "Absorption (AU)"
            
        elif scale == "OD":
            data = self.s[0]
            if y_label == "":
                y_label = "Absorption (OD)"
            print("OD")
        elif scale == "EC":
            data = self.s[0] / (100 * self.concentration * self.pathlength)
            if y_label == "":
                y_label = "Extinction Coefficient (M-1cm-1)"
            print("EC")
        
        axis = self.s_axis[0]

        if title == "": 
            title = self.objectname
                    
        if x_label == "":
            x_label = self.s_units[0]

                
        
        P.linear(data, axis, x_range = x_range, y_range = y_range, x_label = x_label, y_label = y_label, title = title, legend = legend, new_figure = new_figure)
        
        


class ftir_combine(ftir):
    """
    
    Class to add or subtract FTIR spectra. It is based on croc.Pe.pe_combine()

    
    CHANGELOG:
    2012/08/03/RB: started. 
    """    
    
    def __init__(self, objectname, class_plus = [], class_min = []):
        """
        Subtract FTIR spectra.

        INPUT:
        - objectname (string): name
        - class_plus (list with ftir objects): these spectra will be added
        - class_min (list with ftir objects): these spectra will be added

        """

        croc.Ftir.ftir.__init__(self, objectname)
        

        
        # for i in range(len(class_plus)):
        #     
        #     self.s[0] += class_plus[i].s[0] / len(class_plus)
        #     self.s_axis = class_plus[i].s_axis
        # 
        #     
        # for i in range(len(class_min)):
        #     self.s[0] -= class_min[i].s[0] / len(class_min)

        self.s_axis = class_plus[0].s_axis

        plus = [0] * len(self.s_axis)
        subt = [0] * len(self.s_axis)

        for i in range(len(class_plus)):
            
            plus += class_plus[i].s[0] / len(class_plus)
            
        for i in range(len(class_min)):
            subt += class_min[i].s[0] / len(class_min)     
            
        self.s[0] = - numpy.log10(plus/subt)   
















        
        

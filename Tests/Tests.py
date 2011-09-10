from __future__ import print_function
from __future__ import division


import os
import numpy
import pylab 
import matplotlib 
import matplotlib.pyplot as plt

import croc
import croc.ftir
import croc.pe

reload(croc)
reload(croc.ftir)
reload(croc.pe)





def PE1():
    """
    croc.Tests.tests.singlePE
    
    Simplest test of the photon echo routines.
    
    CHANGELOG:
    - 20110910 RB: init
    
    """
    
    print("=== TEST ===\nSimple test of PE routines\n")
    
    mess = [0]
    mess[0] = croc.pe.pe("PE1", "AHA", 300, undersampling = 3, time_stamp = 1337)
    mess[0].path = os.path.join(os.path.dirname(__file__), "TestData/AHA_1337_T300/")
    mess[0].import_data()
    mess[0].absorptive()
    mess[0].plot()
    print(mess[0])





def PE2():
    """
    croc.Tests.tests.doublePE
    
    Test of the plotting routines of the PE.
    
    CHANGELOG:
    - 20110910 RB: init
    
    """
    
    print("=== TEST ===\nPlot test")
    
    print("Points of attention for plot 1\n" + 
        "1. Normal plot\n" +
        "2. Rephasing plot\n" +
        "3. Non-rephasing plot\n" +
        "4. The range is changed. The diagonal line should have moved.\n" +
        "5. The labels are changed. The diagonal line is removed. The zlimit is small, so most of the plot is white.\n" +
        "6. Zlimit is larger than the range. There should be loads of contour lines." +
        "Points of attention for the second plot\n" +
        "7. It should show up.\n")
    
    
    mess = [0]
    mess[0] = croc.pe.pe("PE2", "AHA", 300, undersampling = 3, time_stamp = 1337)
    mess[0].path = os.path.join(os.path.dirname(__file__), "TestData/AHA_1337_T300/")
    mess[0].import_data()
    mess[0].absorptive()
        
    plt.figure()       
    
    plt.subplot(2, 3, 1)
    mess[0].plot(new_figure = False)  
    
    plt.subplot(2, 3, 2)
    mess[0].plot(plot_type = "R", new_figure = False, title = "Rephasing") 
    
    plt.subplot(2, 3, 3)
    mess[0].plot(plot_type = "NR", new_figure = False, title = "Non-rephasing")       
    
    # different plot range
    plt.subplot(2, 3, 4)
    mess[0].plot(x_range = [2050, 2150], y_range = [2000, 2100], title = "Different range", new_figure = False)
    
    # different labels, no diagonal, zlimit smaller than range
    plt.subplot(2, 3, 5)
    mess[0].plot(title = "Labels, diagonal, zlimit", zlimit = 1, x_label = "Wavenumbers", y_label = "Wavenumbers", diagonal_line = False, new_figure = False)
    
    # zlimit larger than range, more contours
    plt.subplot(2, 3, 6)
    mess[0].plot(zlimit = 5, contours = 20, title = "zlimit, contours", new_figure = False)
    
    # and in a second plot, the time domain
    mess[0].plot_T()

    print(mess[0])




def FTIR1():
    """
    croc.Tests.Tests.FTIR1
    
    Simple test routine to see if FTIR works.
    
    CHANGELOG:
    - 20110910 RB: init
    
    """
    
    print("=== TEST ===\nSimple test of FTIR routines\n")

    mess = [0]  
    mess[0] = croc.ftir.ftir("FTIR1") 
    mess[0].path = os.path.join(os.path.dirname(__file__), "TestData/")
    mess[0].base_filename = "sample" # left the .txt out on purpose
    mess[0].import_data()
    mess[0].plot(x_range = [1000, 3000])
    print(mess[0])

def FTIR2():
    """
    croc.Tests.Tests.FTIR2
    
    Simple test routine to see if FTIR difference absorption works.
    
    CHANGELOG:
    - 20110910 RB: init
    
    """
    
    print("=== TEST ===\nSimple test of FTIR routines for difference absorption\n")    
    mess = [0]  
    mess[0] = croc.ftir.ftir("FTIR2", abs_diff = True)
    mess[0].path = os.path.join(os.path.dirname(__file__), "TestData/")
    mess[0].base_filename = "sample"
    mess[0].sec_filename = "buffer.txt"
    mess[0].import_data()
    mess[0].plot(x_range = [2000, 2200])
    print(mess[0])
    







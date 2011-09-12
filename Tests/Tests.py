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
import croc.Absorptive

reload(croc)
reload(croc.ftir)
reload(croc.pe)
reload(croc.Absorptive)





def PE1():
    """
    croc.Tests.tests.singlePE
    
    Simplest test of the photon echo routines.
    
    CHANGELOG:
    - 20110910 RB: init
    
    """
    
    print("=== TEST ===\nSimple test of PE routines\n")
    
    mess = [0]
    mess[0] = croc.pe.pe("PE1")
    mess[0].setup("AHA", 300, undersampling = 3, time_stamp = 1337)
    mess[0].path = os.path.join(os.path.dirname(__file__), "TestData/AHA_1337_T300/")
    mess[0].import_data()
    mess[0].absorptive()
    mess[0].plot()
    print(mess[0])





def PE2():
    """
    croc.Tests.tests.PE2
    
    Test of the plotting routines and their options of the PE.
    
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
    mess[0] = croc.pe.pe("PE2")
    mess[0].setup("AHA", 300, undersampling = 3, time_stamp = 1337)
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


def PE3():
    """
    croc.Tests.tests.PE3
    
    Test of window functions.
    
    CHANGELOG:
    - 20110910 RB: init
    
    """
    
    print("=== TEST ===\nTest of window functions\n")
    
    n = 100

    window_fxn = [
        ["none", n], 
        ["ones", n], 
        ["triangle", n], 
        ["gaussian", n], 
        ["none", n/2], 
        ["ones", n/2], 
        ["triangle", n/2], 
        ["gaussian", n/2]
    ]
    
    mess = [0]

    mess[0] = croc.pe.pe("PE1")
    mess[0].setup("AHA", 300, undersampling = 3, time_stamp = 1337)
    mess[0].path = os.path.join(os.path.dirname(__file__), "TestData/AHA_1337_T300/")
    mess[0].import_data()    
 
    
    plt.figure()
    
    for i in range(len(window_fxn)):
        mess[0].absorptive(window_function = window_fxn[i][0], window_length = window_fxn[i][1]) 
    
        plt.subplot(2, 4, i+1)
        title = window_fxn[i][0] + ", n=" + str(window_fxn[i][1])
        mess[0].plot(new_figure = False, title = title, zlimit = 0)




   
    
def PE4():
    """
    croc.Tests.Tests.PE4
    
    Test if the original data is unchanged during succesive operations. (Background: incorrect copying operations may make a new pointer to the same data, instead of making a new pointer to a copy of the data. This can lead to data corruption.
    
    """

    print("=== TEST ===\nTest of data integrity\n")

    mess = [0, 0]
    
    mess[0] = croc.pe.pe("PE3_1")
    mess[0].setup("AHA", 300, undersampling = 3, time_stamp = 1337)
    mess[0].path = os.path.join(os.path.dirname(__file__), "TestData/AHA_1337_T300/")
    mess[0].import_data()

    mess[1] = croc.pe.pe("PE3_2")
    mess[1].setup("AHA", 300, undersampling = 3, time_stamp = 1337)
    mess[1].path = os.path.join(os.path.dirname(__file__), "TestData/AHA_1337_T300/")
    mess[1].import_data()
    mess[1].absorptive()
    
    plt.figure()
    
    for i in range(2):
        mess[0].absorptive()
        
        if numpy.any((mess[0].r[0] - mess[1].r[0]) != 0) == False:
            print("Correct")
        else:
            print("WARNING: data is not the same")
        
        plt.subplot(1, 2, i+1)
        mess[0].plot(new_figure = False)
        
 
def PE5():
    mess = [0, 0]
    
    mess[0] = croc.pe.pe("PE5_AHA")
    mess[0].setup("AHA", 300, undersampling = 3, time_stamp = 1337)
    mess[0].path = os.path.join(os.path.dirname(__file__), "TestData/AHA_1337_T300/")
    mess[0].import_data()
    mess[0].absorptive()

    mess[1] = croc.pe.pe("PE5_D2O")
    mess[1].setup("d2o", 300, undersampling = 3, time_stamp = 1348)
    mess[1].path = os.path.join(os.path.dirname(__file__), "TestData/d2o_1348_T300/")
    mess[1].import_data()
    mess[1].absorptive()
    
    sub = [0]
    sub[0] = croc.pe.pe("PE_SUB")
    sub[0].r[0] = mess[0].s
    sub[0].r[1] = mess[1].s
    
    sub[0].s = mess[0].s - mess[1].s
    
    sub[0].s_axis[0] = mess[0].s_axis[0]
    sub[0].s_axis[1] = mess[0].s_axis[1]
    sub[0].s_axis[2] = mess[0].s_axis[2]
    
    sub[0].plot()
    
    

def PLOTTING1():
    pass 
    #array = numpy.reshape(numpy.arange



def ABSORPTIVE1():

    n = 100

    window_fxn = [
        ["none", n], 
        ["ones", n], 
        ["triangle", n], 
        ["gaussian", n], 
        ["none", n/2], 
        ["ones", n/2], 
        ["triangle", n/2], 
        ["gaussian", n/2]
    ]

    array = numpy.ones(n)
    
    plt.figure()
    
    for i in range(len(window_fxn)):    
    
        w_array = croc.Absorptive.window_functions(array, window_fxn[i][0], window_fxn[i][1])
        
        plt.subplot(2, 4, i+1)
        
        plt.plot(w_array)
        plt.title(window_fxn[i][0] + " " + str(window_fxn[i][1]))
        plt.ylim(0,1.1)
    plt.show()
    



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
    







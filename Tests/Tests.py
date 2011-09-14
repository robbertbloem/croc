from __future__ import print_function
from __future__ import division


import os
import numpy
import pylab 
import matplotlib 
import matplotlib.pyplot as plt

import croc
import croc.Ftir
import croc.Pe
import croc.Absorptive
import croc.Plotting
import croc.Debug

reload(croc.Debug)

if croc.Debug.reload_flag:
    reload(croc)
    reload(croc.Ftir)
    reload(croc.Pe)
    reload(croc.Absorptive)
    reload(croc.Plotting)




def PE1():
    """
    croc.Tests.tests.singlePE
    
    Simplest test of the photon echo routines.
    
    CHANGELOG:
    - 20110910 RB: init
    
    """
    
    print("=== TEST ===\nSimple test of PE routines\n")
    
    mess = [0]
    mess[0] = croc.Pe.pe_exp("PE1", "AHA", 300, undersampling = 3, time_stamp = 1337)
    
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
    mess[0] = croc.Pe.pe_exp("PE1", "AHA", 300, undersampling = 3, time_stamp = 1337)
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

    mess[0] = croc.Pe.pe_exp("PE1", "AHA", 300, undersampling = 3, time_stamp = 1337)
    mess[0].path = os.path.join(os.path.dirname(__file__), "TestData/AHA_1337_T300/")
    mess[0].import_data()    
 
    
    plt.figure()
    
    for i in range(len(window_fxn)):
        mess[0].absorptive(window_function = window_fxn[i][0], window_length = window_fxn[i][1]) 
    
        plt.subplot(2, 4, i+1)
        title = window_fxn[i][0] + ", n=" + str(window_fxn[i][1])
        mess[0].plot(new_figure = False, title = title, zlimit = -1)




   
    
def PE4():
    """
    croc.Tests.Tests.PE4
    
    Test if the original data is unchanged during succesive operations. (Background: incorrect copying operations may make a new pointer to the same data, instead of making a new pointer to a copy of the data. This can lead to data corruption.

    CHANGELOG:
    - 20110912 RB: init
    
    """

    print("=== TEST ===\nTest of data integrity\n")

    mess = [0, 0]
    
    mess[0] = croc.Pe.pe_exp("PE1", "AHA", 300, undersampling = 3, time_stamp = 1337)
    mess[0].path = os.path.join(os.path.dirname(__file__), "TestData/AHA_1337_T300/")
    mess[0].import_data()

    mess[1] = croc.Pe.pe_exp("PE1", "AHA", 300, undersampling = 3, time_stamp = 1337)
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
    """
    croc.Tests.Tests.PE5
    
    Test the subtraction of two plots    

    CHANGELOG:
    - 20110912 RB: init
    
    """
    mess = [0, 0]
    
    mess[0] = croc.Pe.pe_exp("PE5_AHA", "AHA", 300, undersampling = 3, time_stamp = 1337)
    mess[0].path = os.path.join(os.path.dirname(__file__), "TestData/AHA_1337_T300/")
    mess[0].import_data()
    mess[0].absorptive()

    mess[1] = croc.Pe.pe_exp("PE5_D2O", "d2o", 300, undersampling = 3, time_stamp = 1348)
    mess[1].path = os.path.join(os.path.dirname(__file__), "TestData/d2o_1348_T300/")
    mess[1].import_data()
    mess[1].absorptive()
    
    sub = [0]
    sub[0] = croc.Pe.pe_sub("PE_SUB", mess[0], mess[1])
    sub[0].plot()
    print(sub[0])
    
    

def PLOTTING1():
    """
    croc.Tests.Tests.PLOTTING1
    
    Tests if the contour lines are correctly placed.

    CHANGELOG:
    - 20110912 RB: init
    
    """
    
    print("=== TEST ===\nTest of plotting\n")
    
    print("PLOT 1:\n" + 
        "Ranges from -1 to 1. The white band should be in the middle.\n"+
        "PLOT 2:\n" + 
        "Ranges from -1 to 0.9. The white band should be rotated a bit clockwise."
    )
    
    # plot 1
    X, Y = numpy.meshgrid(numpy.linspace(-1, 0, num=11), numpy.linspace(0, 1, num=11))  
    x_axis = numpy.linspace(0, 1, num=11)
    y_axis = numpy.linspace(0, 1, num=11)
    S = X + Y
    title = "range:-1, 1, zlimit:-1"
    croc.Plotting.contourplot(S, x_axis, y_axis, zlimit = -1, title = title)

    # plot 2
    X, Y = numpy.meshgrid(numpy.linspace(-1, 0, num=11), numpy.linspace(0, 0.9, num=11))
    x_axis = numpy.linspace(0, 1, num=11)
    y_axis = numpy.linspace(0, 1, num=11)
    S = X + Y
    title = "range:-1, 0.9, zlimit:-1"
    croc.Plotting.contourplot(S, x_axis, y_axis, zlimit = -1)



def ABSORPTIVE1():
    """
    
    CHANGELOG:
    - 20110912 RB: init
    """
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
    mess[0] = croc.Ftir.ftir_abs("FTIR1", "sample") 
    mess[0].path = os.path.join(os.path.dirname(__file__), "TestData/")
#    mess[0].base_filename = "sample" # left the .txt out on purpose
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
    mess[0] = croc.Ftir.ftir_diffabs("FTIR2", "sample", "buffer.txt")
    mess[0].path = os.path.join(os.path.dirname(__file__), "TestData/")
#    mess[0].base_filename = ["sample", "buffer.txt"]
#    mess[0].sec_filename = "buffer.txt"
    mess[0].import_data()
    mess[0].plot(x_range = [2000, 2200])
    print(mess[0])
    







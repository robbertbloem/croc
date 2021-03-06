from __future__ import print_function
from __future__ import division


import os
import time
import numpy
import pylab 
import matplotlib 
import matplotlib.pyplot as plt

import croc
#import croc.Resources.DataClasses
import croc.Ftir
import croc.Pe
import croc.Resources.Mathematics as M
import croc.Resources.Functions as F
import croc.GroupVelocityDispersion
import croc.LaserCorrelation
import croc.Resources.Plotting as P
import croc.Debug

reload(croc.Debug)

if croc.Debug.reload_flag:
    print("reloading")
    reload(croc)
    reload(P)
    reload(croc.Ftir)
    reload(croc.Pe)
    reload(M)
    reload(F)
    reload(croc.GroupVelocityDispersion)
    reload(croc.LaserCorrelation)
#    reload(croc.Plotting)


def SubPlotTest():
    
    print("=== TEST ===\nTest of subplots\n")
    
    mess = [0]
    mess[0] = croc.Pe.pe_exp("PE1", "AHA", 300, undersampling = 3, time_stamp = 1337)
    
    mess[0].path = os.path.join(os.path.dirname(__file__), "TestData/AHA_1337_T300/")
    mess[0].import_data()  
    mess[0].absorptive()
    plt.figure()
    for i in range(3):
        plt.subplot(1,3,i+1)
        mess[0].plot(pixel = -1, new_figure = False)
    plt.show()
    print(mess[0])




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
    P.contourplot(S, x_axis, y_axis, zlimit = -1, title = title)

    # plot 2
    X, Y = numpy.meshgrid(numpy.linspace(-1, 0, num=11), numpy.linspace(0, 0.9, num=11))
    x_axis = numpy.linspace(0, 1, num=11)
    y_axis = numpy.linspace(0, 1, num=11)
    S = X + Y
    title = "range:-1, 0.9, zlimit:-1"
    P.contourplot(S, x_axis, y_axis, zlimit = -1)


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
    
        w_array = M.window_functions(array, window_fxn[i][0], window_fxn[i][1])
        
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
    mess[0] = croc.Ftir.ftir_abs("FTIR1", "sample") # left the .txt out on purpose
    mess[0].path = os.path.join(os.path.dirname(__file__), "TestData/")
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
    mess[0].import_data()
    mess[0].plot(x_range = [2000, 2200])
    print(mess[0])
    




def FS1a(flag_import_noise = False):
    """
    croc.Tests.Tests.FS1a
    
    Test to import data. It will save the data as a pickle (python data structure), which will be read in and processed in part B. This prevents you from reimporting data all the time.
    
    This test will only work if the data is present, which needs a separate download.
    
    """

    mess = [0]
    mess[0] = croc.Pe.pefs("FS3", "azide", 300, 1343)
    mess[0].path = os.path.join(os.path.dirname(__file__), "TestData/azide_1343_T300/")

    # import all data
    if flag_import_noise:
        end = 11
    else:
        end = 21

    for i in range(1, end):
        mess[0].add_data(scan = i, flag_construct_r = False, flag_calculate_noise = flag_import_noise)

    # there was an issue with the measure phase for this measurement
    mess[0].phase_degrees = -132 + 180 - 90
    
    # make the pickle
    if flag_import_noise:
        path_and_filename = os.path.join(os.path.dirname(__file__), "TestData/azide_1343_T300_pickle/azide_1343_T300_noise")
    else:
        path_and_filename = os.path.join(os.path.dirname(__file__), "TestData/azide_1343_T300_pickle/azide_1343_T300")
    
    croc.DataClasses.make_db(mess, path_and_filename)




def FS1b():
    """
    croc.Tests.Tests.FS1b
    
    This will import the pickle and do things with the data. This is the most straightforward way to test the Fast Scanning routine.
    
    """
    # import the pickle
    path_and_filename = os.path.join(os.path.dirname(__file__), "TestData/azide_1343_T300_pickle/azide_1343_T300")
    pick = croc.DataClasses.import_db(path_and_filename)
    
    # construct r 
    pick[0].construct_r()
    
    # calculate the spectrum
    pick[0].absorptive()
    
    # plot the spectrum
    pick[0].plot(plot_type = "S")#, x_range = [1930, 2150])

    # print the data structure
    print(pick[0])    



def FS1c():
    """
    croc.Tests.Tests.FS1c
    
    This will import the pickle and do things with the data. This is the most straightforward way to test the Fast Scanning routine.
    
    """
    # import the pickle
    path_and_filename = os.path.join(os.path.dirname(__file__), "TestData/azide_1343_T300_pickle/azide_1343_T300")
    pick = croc.DataClasses.import_db(path_and_filename)
    
    # you can also use pick[0].zeropad_to
    pick[0].zeropad_by = 2
    
    # construct r 
    pick[0].construct_r()
    
    # calculate the spectrum
    pick[0].absorptive(window_function = "none", window_length = 0)
    
    zlimit = numpy.nanmax(numpy.abs(pick[0].s))
    
    print(type(zlimit))
    
    # plot the spectrum
    pick[0].plot(plot_type = "S", zlimit = zlimit/10)#, x_range = [1930, 2150])

    # print the data structure
    print(pick[0])   


def FS1d():
    """
    croc.Tests.Tests.FS1d
    
    This will import the pickle and calculate the noise.
    
    """
    
    # import the pickle
    path_and_filename = os.path.join(os.path.dirname(__file__), "TestData/azide_1343_T300_pickle/azide_1343_T300_noise")
    pick = croc.DataClasses.import_db(path_and_filename)
    
    # construct r 
    pick[0].construct_r()
    
    # calculate the spectrum
    pick[0].absorptive()
    
    # calculate noise
    pick[0].calculate_noise(pixel = 16)
    
    # plot the spectrum
    pick[0].plot(plot_type = "S")#, x_range = [1930, 2150])

    # print the data structure
    print(pick[0])     







def FS2a():
    """
    croc.Tests.Tests.FS2a
    
    Test to import data. It will save the data as a pickle (python data structure), which will be read in and processed in part B.
    
    This test will only work if the data is present, which needs a separate download.
    
    """

    mess = [0, 0]
    mess[0] = croc.Pe.pefs("FS2_freq", "azide", 300, 1522)
    mess[0].path = ("/Volumes/public_hamm/PML3/data/20110928/azide_1522_T300/")

    mess[1] = croc.Pe.pefs("FS2_time", "azide", 300, 1522)
    mess[1].path = ("/Volumes/public_hamm/PML3/data/20110928/azide_1522_T300/")

    # import all data
    # it ranges from 1 to last_scan + 1
    # mess[0].r will not be constructed after every import
    begin = 1
    end = 3
    for i in range(1, 21):
        mess[0].add_data(scan = i, flag_construct_r = False, flag_calculate_noise = True, flag_noise_time_domain = False)
    
    print(mess[0].incorrect_count)
    
    for i in range(1, 21):
        mess[1].add_data(scan = i, flag_construct_r = False, flag_calculate_noise = True, flag_noise_time_domain = True)
        
    

    # there was an issue with the measure phase for this measurement
    mess[0].phase_degrees = mess[0].phase_degrees + 120
    
    # make the pickle
    path_and_filename = "azide_1522_T300"
    croc.DataClasses.make_db(mess, path_and_filename)


def FS2b():
    """
    croc.Tests.Tests.FS2b
    
    This will import the pickle and do things with the data. This prevents you from having to reimport all the data all the time. 
    

    """

    # import the pickle
    path_and_filename = "azide_1522_T300"    
    pick = croc.DataClasses.import_db(path_and_filename)
    
    i = [0,0]
    if pick[0].objectname == "FS2_freq":
        i[0] = 0
        i[1] = 1
    else:
        i[0] = 1
        i[1] = 0
    
    #pick[0].zeropad_by = 2
    # construct r 
    pick[i[0]].construct_r()
    pick[i[1]].construct_r()
    
    # calculate the spectrum
    pick[i[0]].absorptive()
    pick[i[1]].absorptive()
    
    # calculate the noise
    pick[i[0]].calculate_noise(pixel = 14, flag_noise_time_domain = False)
    pick[i[1]].calculate_noise(pixel = 14, flag_noise_time_domain = True)

    
    pick[i[0]].plot(pixel = 14, flag_no_units = False)
    pick[i[1]].plot_T(pixel = 14, flag_no_units = False)


    
    #pick[0].bin_info()

    #print(pick[0])    




def FS3():
    """
    croc.Tests.Tests.FS3
    
    Calculates spectrum without saving it as a pickle.
    
    """

    mess = [0]
    mess[0] = croc.Pe.pefs("FS2", "azide", 300, 1522)
    mess[0].path = ("/Volumes/public_hamm/PML3/data/20110928/azide_1522_T300/")


    # import all data
    # it ranges from 1 to last_scan + 1
    # mess[0].r will not be constructed after every import
    plt.figure()
    for i in range(2, 3):
        mess[0].add_data(scan = i, flag_construct_r = False, flag_calculate_noise = False)
    plt.show()
    
    
    print(mess[0].incorrect_count)

#     plt.figure()
#     plt.plot(mess[0].b[0][:,12], ".-")
#     plt.plot(mess[0].b[2][:,12], ".-")
#     plt.show()
    
#     mess[0].construct_r()
#     
#     plt.figure()
#     plt.plot(mess[0].r[0][:,12], ".-")
#     plt.plot(mess[0].r[1][:,12], ".-")
#     plt.show()    
#     
#     mess[0].absorptive()
#     
#     mess[0].plot(plot_type = "S")#, x_range = [1930, 2150])



def FS4(scans = 1, data_large = False):
    """
    croc.Tests.Tests.FS4
    
    Check the correlation of the laser. 
    
    INSTRUCTIONS FOR THE MEASUREMENT:
    - get the OPA to work 
    - align the experiment
    - balance the incoupling as if it were a serious measurment
    - block the other beams (to prevent scattering etc)
    - measure the fast scanning for as long as possible, without moving the motors
    
    INPUT:
    - scans (int, 1): the number of runs plotted.
    - data_large (BOOL, False): when False, a measurement with 1000 shots is used, when True, it will use a measurement with 20000 shots.
    
    """

    mess = [0]  
    if data_large:
        mess[0] = croc.Pe.pefs("corr", "corT2", 0, 1422)
        mess[0].path = ("/Volumes/public_hamm/PML3/data/20110930/corT2_1422_T0/")
    else:
        mess[0] = croc.Pe.pefs("corr", "corT1", 0, 1419)
        mess[0].path = ("/Volumes/public_hamm/PML3/data/20110930/corT1_1419_T0/")

    scan = 1
      
    filename = mess[0].make_filenames(scan)

    plt.figure()
    for i in range(scans):
        # import the raw data
        [m, fringes] = mess[0].import_raw_data(filename[i])
    
        # plot the correlation
        mess[0].find_correlation(m, maxtau = 5000, flag_fft_method = True)
    
    plt.show()




    
def FS5(flag_test = False):
    """
    croc.Tests.Tests.FS4
    
    Check if the samples are equally spaced within the fringes.
    
    The test routine is to verify the routine.
    
    
    """
    
    if flag_test:
        # number of samples
        n_samples = 10000
        
        k = [0]
        
        mess = [0]
        mess[0] = croc.Pe.pefs("FS5", "test", 0, 0)
        
        # make the array
        m = numpy.zeros((37, n_samples))
        
        # for a little bit of randomness        
        rnd = (numpy.random.randn(n_samples) - 0.5)/4

        # make the x and y wave
        m[mess[0].x_channel,:] = -numpy.sin(numpy.arange(n_samples) + rnd)
        m[mess[0].y_channel,:] = -2*numpy.cos(numpy.arange(n_samples) + rnd)
        
        start_counter = 4000
        
        [m_axis, counter, correct_count] = mess[0].reconstruct_counter(data = m, start_counter = 0, flag_plot = False)    
        # plot the circle
        plt.figure()
        plt.plot(m[mess[0].x_channel,:],m[mess[0].y_channel,:])
        plt.show()
        
        # plot the angle
        plt.figure()
        mess[0].find_angle(m, m_axis, k = 0, skip_first = 1000, skip_last = 1000, flag_normalize_circle = True, flag_scatter_plot = False)
        plt.show()
        
    else:
    
        mess = [0]
        mess[0] = croc.Pe.pefs("FS3", "azide", 300, 1343)
        mess[0].path = os.path.join(os.path.dirname(__file__), "TestData/azide_1343_T300/") 

        k = [0, 1, 2, 3]

        # construct the path and filename        
        path_and_filename = mess[0].make_filenames(scan = 2)

        # plot the angle as a histogram
        plt.figure()
        
        for i in range(len(k)):
        
            # import the raw data
            [m, fringes] = mess[0].import_raw_data(path_and_filename[k[i]])
            
            # reconstruct the counter
            [m_axis, counter, correct_count] = mess[0].reconstruct_counter(data = m, start_counter = 0, flag_plot = False)
            
            if correct_count:
                mess[0].find_angle(m, m_axis, k = i, skip_first = 1000, skip_last = 1000, flag_normalize_circle = True, flag_scatter_plot = False, new_figure = False)
       
        plt.show()
    
    
        # plot the angle
        plt.figure()
        
        for i in range(len(k)):
        
            # import the raw data
            [m, fringes] = mess[0].import_raw_data(path_and_filename[k[i]])
            
            # reconstruct the counter
            [m_axis, counter, correct_count] = mess[0].reconstruct_counter(data = m, start_counter = 0, flag_plot = False)
            
            if correct_count:
                mess[0].find_angle(m, m_axis, k = i, skip_first = 0, skip_last = 0, flag_normalize_circle = True, flag_scatter_plot = True, new_figure = False)
       
        plt.show()    
    
    
    
    


def PE6():
    """
    croc.Tests.tests.singlePE
    
    Simplest test of the photon echo routines.
    
    CHANGELOG:
    - 20110910 RB: init
    
    """
    
    print("=== TEST ===\nSimple test of PE routines\n")
    
    mess = [0]
    mess[0] = croc.Pe.pe_exp("PE6", "azide", 300, undersampling = 5, time_stamp = 1251)
    mess[0].path = ("/Volumes/public_hamm/PML3/data/20110921/azide_1251_T300/")
#    mess[0].path = os.path.join(os.path.dirname(__file__), "TestData/azide_1251_T300/")
    mess[0].import_data()
    mess[0].zeropad_by = 2
    mess[0].phase_degrees = -132 + 180 - 90
    #mess[0].phase_degrees + 120
      
    mess[0].absorptive()
    #window_function = "gaussian", window_length = 40, flag_plot = True)
    
    zlimit = numpy.nanmax(numpy.abs(pick[0].s))
    
    plt.figure()
    plt.plot(mess[0].s[:,14], zlimit = zlimit/10)
    plt.show()
    
    mess[0].plot_T(pixel=14)
    
    mess[0].plot(x_range = [1930, 2150])
    print(mess[0])





    
def F1():
    length = 50
    
    wa = croc.Resources.Mathematics.window_functions(numpy.ones(length), window_function = "gaussian", window_length = 25, flag_plot = False)  
    
    print(wa[-1])
    
    plt.figure()
    plt.plot(wa)
    plt.show() 


def GVD1():
    ### PARAMETERS ###
    material = "caf2"
    range_um = [1.0, 7.0] # [minimum, maximum]
    n_steps = 100 # more steps give a higher resolution
    material_path_mm = 3 # path through material 
    pulse_length_fs = 100 # pulse length
    
    flag_plot_n = False
    flag_plot_gvd = True
    y_range_gvd = [0,0]
    print_for_um = [1.3, 1.9, 4.9] # array, in micron
    
    n, gvd_x, gvd_y = croc.GroupVelocityDispersion.GVD(material = material, print_for_um = print_for_um, range_um = range_um, material_path_mm = material_path_mm, pulse_length_fs = pulse_length_fs, n_steps = n_steps, flag_plot_n = flag_plot_n, flag_plot_gvd = flag_plot_gvd, y_range_gvd = y_range_gvd)



def LASERCORRELATION1a():
    
    mess_array = ["correlation_30k_1845_T300"]
    scan_array = ["_NR1_1", "_NR2_1", "_R1_1", "_R2_1"]
    mess_date = 20111025
    
    pixel = 16
    
    maxtau = 1000
    
    path_input = "/Volumes/public_hamm/PML3/data/" + str(mess_date) + "/"
    path_output = "/Volumes/public_hamm/PML3/analysis/" + str(mess_date) + "/"
    
    croc.LaserCorrelation.import_and_process(path_input, path_output, mess_array, scan_array, mess_date, pixel = 16, maxtau = 2000, debug = False)

def LASERCORRELATION1b():
    
    mess_array = ["correlation_30k_1845_T300"]
    scan_array = ["_NR1_1", "_NR2_1", "_R1_1", "_R2_1"]
    mess_date = 20111025
    
    maxtau = 1000
    
    path_input = "/Volumes/public_hamm/PML3/data/" + str(mess_date) + "/"
    path_output = "/Volumes/public_hamm/PML3/analysis/" + str(mess_date) + "/"
    
    croc.LaserCorrelation.fit_correlation(path_output, mess_array, scan_array, mess_date, maxtau)



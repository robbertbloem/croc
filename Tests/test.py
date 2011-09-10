from __future__ import print_function
from __future__ import division

import numpy


import croc
import croc.ftir
import croc.pe

#import 
#import croc.DataClasses
import os

import pylab 
import matplotlib 
import matplotlib.pyplot as plt


reload(croc)
reload(croc.ftir)
reload(croc.pe)


#reload(croc.DataClasses)

def function_one(a):

    mess = [0]

    mess[0] = croc.pe.pe("AHA300", "AHA", 300, undersampling = 3, time_stamp = 1337)
    mess[0].path = "/Users/robbert/Desktop/20110805/AHA_1337_T300/"
    
    #plt.figure()
    
    for i in range(len(mess)):
    
        #mess[i].base_filename = "AHA"
        mess[i].import_data()
        #mess[i].undersampling = 3
        #mess[i].zeropad_by = 1.32      
        mess[i].absorptive()
        
        #plt.subplot(1,2,i)
        mess[i].plot(plot_type = "S", new_figure = True, contours = 20)
    
def function_two(a):

    mess = [0,0]

    mess[0] = croc.pe.pe("AHA300", "AHA", 300, undersampling = 3, time_stamp = 1337)
    mess[0].path = "/Users/robbert/Desktop/20110805/AHA_1337_T300/"

    mess[1] = croc.pe.pe("AHA300", "AHA", 500, undersampling = 3, time_stamp = 1412)
    #mess[1] = croc.pe.pe("AHA500", 500, 1412)
    mess[1].path = "/Users/robbert/Desktop/20110805/AHA_1412_T500/"
    
    #plt.figure()
    
    for i in range(len(mess)):
    
        #mess[i].base_filename = "AHA"
        mess[i].import_data()
        print(mess[i])
        #mess[i].undersampling = 3
        mess[i].zeropad_to = 88 
        mess[i].absorptive()
        
        #plt.subplot(1,2,i)
        mess[i].plot(plot_type = "S", new_figure = True)
        
        
def function_ftir(a):
    
    mess = [0]
    
    mess[0] = croc.ftir.ftir("fiets")
    mess[0].path = "/Users/robbert/Desktop/ASCII/"
    mess[0].base_filename = "pep0_3_5"
    mess[0].import_data()
    mess[0].plot(x_range = [1000, 3000])
    
#    print(mess[0])

def function_ftir_diff(a):
    
    mess = [0]
    
    mess[0] = croc.ftir.ftir("fiets", abs_diff = True)
    mess[0].path = "/Users/robbert/Desktop/ASCII/"
    mess[0].base_filename = "pep0_3_5"
    mess[0].sec_filename = "buffer.txt"
    mess[0].import_data()
    #plt.figure()
    mess[0].plot(x_range = [2050, 2150])
    
    #print(mess[0])    
    
def function_ftir_subplot(a):
    
    mess = [0, 0]
    
    mess[0] = croc.ftir.ftir("fiets", abs_diff = False)
    mess[0].path = "/Users/robbert/Desktop/ASCII/"
    mess[0].base_filename = "pep0_3_5"
    mess[0].import_data()
    
    mess[1] = croc.ftir.ftir("boot", abs_diff = False)
    mess[1].path = "/Users/robbert/Desktop/ASCII/"
    mess[1].base_filename = "buffer.txt"    
    mess[1].import_data()

    plt.figure()
    #plt.subplot(121)
    mess[0].plot(x_range = [2050, 2150], new_figure = False)  
    #plt.subplot(122)
    mess[1].plot(x_range = [2050, 2150], new_figure = False)  
    
    
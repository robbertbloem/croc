from __future__ import print_function
from __future__ import division


import os
import time
import numpy
import pylab 
import matplotlib 
import matplotlib.pyplot as plt

import croc
import croc.DataClasses
import croc.Ftir
import croc.Pe
import croc.Absorptive
import croc.Plotting
import croc.Debug

reload(croc.Debug)

if croc.Debug.reload_flag:
    reload(croc)
    reload(croc.DataClasses)
    reload(croc.Ftir)
    reload(croc.Pe)
    reload(croc.Absorptive)
    reload(croc.Plotting)




def make_gauss_cos(n_fringes, flag_add_noise = False):

    t_array =  numpy.arange(0, n_fringes)
    
    array = numpy.cos(4 * t_array + numpy.random.randn(n_fringes) * 0.05) * numpy.exp(-(2.2*t_array/(n_fringes))**2) + numpy.random.randn(n_fringes) * 0.1
    
    
    
    array_count = numpy.random.randint(2, high = 100, size = n_fringes)
    
    array *= array_count 
    
    return array, array_count




def make_zeros(n_fringes, noise_factor = 0.5, count_dev = 100):
    
    array = numpy.zeros(n_fringes, dtype = "float64") + numpy.random.randn(n_fringes) * noise_factor - noise_factor/2
    
    array_count = numpy.random.randint(2, high = count_dev, size = n_fringes)
    
    array *= array_count
    
    return array, array_count






def make_ones(n_fringes, noise_factor = 0.5, count_dev = 100):
    array = numpy.ones(n_fringes, dtype = "float64") + numpy.random.randn(n_fringes) * noise_factor - noise_factor/2
    
    array_count = numpy.random.randint(2, high = count_dev, size = n_fringes)
    
    array *= array_count
    
    return array, array_count
        
    
    

def SIM1():

    n_iter = 10
    noise_factor = 0.5
    count_dev = 100
    n_fringes = 1000
    
    sim = [0]
    sim[0] = croc.Pe.pefs("SIM1", "sim", 0, 0)
    
    sim[0].n_fringes = n_fringes
   
    sim[0].extra_fringes = 20
    sim[0].n_channels = 4
    
    sim[0].x_channel = 1
    sim[0].y_channel = 2
    sim[0].chopper_channel = 3
    sim[0].n_pixels = 1
    
    t = [0] * n_iter
    t_count = [0] * n_iter
    
    for i in range(n_iter):
        t[i], t_count[i] = make_zeros(sim[0].n_fringes, noise_factor, count_dev)
        
        
    # situation A: add all, then divide by all counts
    A = numpy.sum(t, axis = 0, dtype = "float64")
    A_count = numpy.sum(t_count, axis = 0)
    
    # situation B: first take average, then add different.
    B = [0] * n_iter
    for i in range(n_iter):
        B[i] = t[i][:]/t_count[i]
    
    B = numpy.mean(B, axis = 0, dtype = "float64")
    
    
    print(numpy.mean(A/A_count-B))#, numpy.mean(B))
    
    
    plt.figure()
    plt.plot(A/A_count - B)
    #plt.plot(B)
    plt.plot(A_count/(n_iter*count_dev/2) - 1)
    
    plt.title("Difference two methods (blue) and deviation in nr. shots (green) with 0 = no deviation, 1 = 100% ")
    plt.show()
    
    
    
    
    

def SIM2():

    x = [
        [1, 5, 3, 6, 2, 5],
        [6, 2, 6, 7, 0, 0],
        [6, 2, 6, 0, 0, 0]
    ]

    n = [6, 4, 3]
    
    A = numpy.sum(x) / numpy.sum(n)
    
    
    s = [0] * 3
    for i in range(3):
        s[i] = sum(x[i])/n[i]
    
    B = numpy.mean(s)
    
    print(A,B)
 
 
   
def correlation(array):


    l = len(array)
    
    print(l)
    
    c_array = numpy.zeros(l/4)
    
    a = array
    
    for k in range(1,int(l/4)): # step size
        
        if k == 0:
            n_steps = 1000
        else:
            n_steps = l // k
        
        s = 0
        
        for i in range(0, n_steps-1):
            #print(i*k, i*k+k)
            s += a[i*k] * a[i*k + k]
        
        c_array[k] = s / (4*n_steps)
    
    
    
    return c_array #/ c_array[0]
            
        
#(m_x - numpy.mean(m_x)) / (numpy.std(m_x) * len(m_x))        
    
    
def SIM3():
    
    n_samples = 1000
    
    I = numpy.zeros(n_samples)
    k = 1/50
    
    I[0] = 0
    
    sigma = 2 / numpy.sqrt(2 * k)
    
    for i in range(1, n_samples):
        first = I[i-1] * (1-k)
        second = sigma**2 * numpy.random.randn(1) * k
        
        #print(first, second)
        
        I[i] = first + second[0]
    
    
    c = correlation(I)
    
    
    #print(I)
    
    plt.figure()
    plt.plot(I)
    plt.show()
    
    plt.figure()
    plt.plot(c)
    #plt.ylim(-1.1, 1.1)
    plt.axhline(0)
    plt.axvline(k)
    plt.show()
    
    
    #sigma * np.random.randn(...) + mu

    
    
    
    












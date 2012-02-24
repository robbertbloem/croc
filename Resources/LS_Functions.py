from __future__ import print_function
from __future__ import division

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import Mathematics as M
import Equations as E

reload(M)
reload(E)


def position(shots, speed_profile = "uniform", variables = [2, 0.05]):
    
    """
    calculates the time and the bin
    
    speed_profile options and variables:
    - uniform: speed, variation
    - mostly uniform: speed, variation, speed increase, speed decrease (increase in fs/shot per shot)
    - sinsquare: max speed, variation
    - stepped: n_steps, stepsize (in bins), shots (per bin)
    speed is in fs/shot
    
    """
    

    
    if speed_profile == "sinsquare":
        length = len(shots)
        speed_max = variables[0] * (1-variables[1]*numpy.random.rand(1)) 
        speed = speed_max * numpy.sin(numpy.pi*numpy.arange(length)/length)**2
        shots[0][1] = 0
        for i in range(length-1):
            shots[i+1][0] = shots[i][0] + speed[i] 
            shots[i+1][1] = numpy.floor((shots[i+1][0]+1.055)/hene_fringe)   

    
    elif speed_profile == "stepped":
        
        n_steps = variables[0]
        stepsize = variables[1]
        n_shots = variables[2]
        
        if len(shots) != n_steps * n_shots:
            print("ERROR: position (speed_profile): array does not have the correct size")
            return 0
        
        bin = 0
        for i in range(n_steps):
            for j in range(n_shots):
                shots[i*n_shots+j, 1] = bin
                shots[i*n_shots+j, 0] = bin * hene_fringe
            bin = bin + variables[1]   
    
    elif speed_profile == "mostly_uniform":
    
        length = len(shots)
        speed_max = variables[0] * (1-variables[1]*numpy.random.rand(1))
        acc = variables[2] * (1-variables[1]*numpy.random.rand(1))
        dec = variables[2] * (1-variables[1]*numpy.random.rand(1))
        speed = numpy.ones(length) * speed_max
        
        for i in range(speed_max//acc+1):
            speed[i] = 0 + acc*i
        
        for i in range(speed_max//dec+1):
            speed[-1-i] = 0 + dec*i
        
        for i in range(length-1):
            shots[i+1][0] = shots[i][0] + speed[i] 
            shots[i+1][1] = numpy.floor((shots[i+1][0]+1.055)/hene_fringe)         
           
    elif speed_profile == "uniform":   
        
        speed = variables[0] * (1-variables[1]*numpy.random.rand(1))
        for i in range(len(shots)):
            shots[i][0] = i * speed
            shots[i][1] = numpy.floor((shots[i][0]+1.055)/hene_fringe)    
    
    else:
        print("Speed profile not recognized, using uniform")
        speed = variables[0] * (1-variables[1]*numpy.random.rand(1))
        for i in range(len(shots)):
            shots[i][0] = i * speed
            shots[i][1] = numpy.floor((shots[i][0]+hene_fringe/2)/hene_fringe) 
        
    return shots


def laser_intensity(n_shots, k, I0 = 0):
    """
    Calculates the noise per shot
    
    CHANGELOG:
    201201xx/RB: started function as separate script
    20120224/RB: integrated it into croc
    
    INPUT:
    - k: 1/correlation time, in shots
    - I0: start intensity (a bit of randomness is added)
    
    """
    
    I = numpy.zeros(n_shots)
    
    sigma = 2/numpy.sqrt(2*k)
    I[0] = I0 + 10 * numpy.random.randn(1) * sigma * k
    for i in range(n_shots-1):
        I[i+1] = I[i] * (1-k) + numpy.random.randn(1) * sigma * k
    
    return I

def laser_intensity_2(n_shots, a, t1, b, t2, I0 = 0):
    """
    Calculates the noise per shot
    
    CHANGELOG:
    201201xx/RB: started function as separate script
    20120224/RB: integrated it into croc
    
    INPUT:
    - k: 1/correlation time, in shots
    - I0: start intensity (a bit of randomness is added)
    
    """
    
    I = numpy.zeros(n_shots)
    
    k1 = 1/t1
    k2 = 1/t2
    
    sig1 = 2/numpy.sqrt(2*k1)
    sig2 = 2/numpy.sqrt(2*k2)
    I[0] = I0 + 10 * a * numpy.random.randn(1) * sig1 * k1 + 10 * b * numpy.random.randn(1) * sig2 * k2 
    for i in range(n_shots-1):
        I[i+1] = I[i] * (1 - a*k1 - b*k2) + numpy.random.randn(1) * sig1 * k1 + numpy.random.randn(1) * sig2 * k2 
    
    return I


if __name__ == "__main__": 
    
    n_shots = 5000
    k = 1/500
    I0 = 1
    
    a = 0.98
    t1 = 1000
    b = 0.02
    t2 = 5
    
    i = laser_intensity_2(n_shots, a, t1, b, t2, I0)
    
    c = M.correlation_fft(i)
    
    n_cut = 500
    c = c[:n_cut]
    
    x = numpy.arange(n_cut)
    A = [1, 1000, 0.1, 5]
    A_final = M.fit(x, c, E.double_exp, A)
    
    print(A_final)

    plt.figure()
    plt.plot(i)
    plt.show()
    
    plt.figure()
    plt.plot(c)
    plt.plot(E.double_exp(A_final, x))
    plt.show()

























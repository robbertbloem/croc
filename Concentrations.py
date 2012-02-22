from __future__ import print_function
from __future__ import division

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import Resources.Mathematics as M


def concentration_vs_percentage_bound(kd, concentration_ratio = [0,5], n_steps = 100, flag_new_plot = True):
    """
    Calculates the percentage bound as a function of concentration (ratio) for a given Kd. 
    
    """

    x0 = 1
    y0 = numpy.arange(1, n_steps + 1) * (concentration_ratio[1] - concentration_ratio[0])/n_steps
    
    xy = [0,0]
    x = [0,0]
    y = [0,0]
    
    r = numpy.zeros(n_steps)
    
    for i in range(n_steps):
        a = 1
        b = -(x0 + y0[i] + kd)
        c = x0 * y0[i]
        
        xy[0], xy[1] = M.square_formula(a, b, c)
        
        for j in range(2):
            x[j] = x0 - xy[j]
            y[j] = y0[i] - xy[j]
            
            if x[j] < 0 or y[j] < 0:
                pass
            else:
                r[i] = 100 - 100*y[j]/y0[i]
    
    if flag_new_plot:       
        plt.figure()
    plt.plot(y0/x0, r)
    plt.show()
    



if __name__ == "__main__": 
    plt.figure()
    concentration_vs_percentage_bound(0.01, flag_new_plot = False)
    concentration_vs_percentage_bound(0.03, flag_new_plot = False)
    

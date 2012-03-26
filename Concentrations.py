"""
A series of methods to calculate concentrations.

"""


from __future__ import print_function
from __future__ import division

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import Resources.Mathematics as M


def concentration_vs_percentage_bound(kd, concentration_ratio = [0,5], print_for = [], n_steps = 100):
    """
    Calculates the percentage bound as a function of concentration (ratio) for a given Kd for: A+B <=> AB.
    The concentration of A is fixed to 1, the 'concentration_ratio' gives the range of concentrations of B.
    
    CHANGELOG:
    201111??/RB: Wrote original function. 
    20120222/RB: Integrated it into croc.
    
    INPUT:
    - kd (int or array): the dissociation constant. Kd = 1/Ka
    - concentration_ratio (array with two elements): the minimum and maximum of the range over which it should be calculated
    - print_for (array or int): print the values for these concentrations.
    - n_steps (int): number of steps for the calculation
    
    OUTPUT:
    - a graph.
    - if print_for is given, a list with percentage bound for different concentrations for B for different values of Kd.
    
    
    """
    
    if type(kd) == float or type(kd) == int:
        kd = [kd]
    
    if type(print_for) == float or type(print_for) == int:
        print_for = [print_for]

    x0 = 1
    y0 = numpy.arange(1, n_steps + 1) * (concentration_ratio[1] - concentration_ratio[0])/n_steps
    
    xy = [0,0]
    x = [0,0]
    y = [0,0]
    
    r = numpy.zeros(n_steps)
    
    plt.figure()
    
    for k in range(len(kd)):
    
        for i in range(n_steps):
            a = 1
            b = -(x0 + y0[i] + kd[k])
            c = x0 * y0[i]
            
            xy[0], xy[1] = M.square_formula(a, b, c)
            
            for j in range(2):
                x[j] = x0 - xy[j]
                y[j] = y0[i] - xy[j]
                
                if x[j] < 0 or y[j] < 0:
                    pass
                else:
                    r[i] = 100 - 100*y[j]/y0[i]

        plt.plot(y0/x0, r, label = str(kd[k]))

        if len(print_for) != 0:
            print("For Kd: " + str(kd[k]))
            for i in range(len(print_for)):
                index = numpy.where(y0/x0 >= print_for[i])
                print(str((y0/x0)[index[0][0]]) + ": " + str(numpy.round(r[index[0][0]],1)) + "%")

        
    plt.title("Percentage bound as a function of concentration and Kd\nA+B <=> AB")
    plt.ylim(0,100)
    plt.xlabel("Concentration B/A")
    plt.ylabel("Percentage bound (%)")
    plt.legend()
    plt.show()
    

    



if __name__ == "__main__": 
    kd = 15.0e-6
    concentration_vs_percentage_bound(kd)#, [0.02,0.01], print_for = 1)

    

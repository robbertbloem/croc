"""
A series of methods to calculate concentrations.

"""


from __future__ import print_function
from __future__ import division

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import Resources.Mathematics as M

def concentration_vs_percentage_bound(kd, concentration_P = [1], concentration_L_limits = [0,5], n_steps = 100, print_for = []):

    if type(kd) == float or type(kd) == int:
        kd = [kd]   
    kd_range = range(len(kd))

    if type(concentration_P) == float or type(concentration_P) == int:
        concentration_P = [concentration_P] 
    concentration_P_range = range(len(concentration_P))
    
    step = (concentration_L_limits[1] - concentration_L_limits[0])/(n_steps-1)
    if concentration_L_limits[0] == 0:
        start = step
    else:
        start = concentration_L_limits[0]
    stop = concentration_L[1] + step/2
    concentration_L_range = numpy.arange(start, stop, step)
    
    xy = [0,0]
    
    plt.figure()
    
    for i in kd_range:
        for j in concentration_P_range:
            r = numpy.zeros(len(concentration_L))
            for k in concentration_L_range:
                a = 1
                b = -(concentration_P[j] + concentration_L[k] + kd[i])
                c = concentration_P[j] * concentration_L[k]
                
                xy[0], xy[1] = M.square_formula(a, b, c)
                
                for m in range(2):
                    if xy[m] > concentration_P[j] or xy[m] > concentration_L[k]:
                        pass
                    else:
                        r[k] = 100*xy[m]/concentration_L[k]

            if len(print_for) != 0:
                print("Kd: " + str(kd[i]) + " M, [P]: " + str(1000*concentration_A[j]) + " mM") 
                for k in range(len(print_for)):
                    index = numpy.where(concentration_B >= print_for[k])
                    print("    [L]: " + str(numpy.round(1000*concentration_B[index[0][0]],1)) + " mM: " + str(numpy.round(r[index[0][0]],1)) + "%")
            
            c = ["b", "g", "r"]
            
            plt.plot(1000*concentration_B, r, label = "kd: " + str(1000*kd[i]) + " mM, [P]: " + str(1000*concentration_A[j]) + " mM")#, color = c[j])
    plt.title("Percentage bound as a function of concentration and Kd\nP(rotein) + L(igand) <=> PL")
    plt.ylim(0,110)
    plt.xlim(1000*start, 1000*stop)
    plt.xlabel("[L] (mM)")
    plt.ylabel("Percentage bound (%)")
    plt.legend(loc="center right")  
#    plt.legend(loc="lower left")  
    plt.grid(b=True, which="both")  
    plt.show()  
    
    




    



if __name__ == "__main__": 
    kd = [58.0e-6] # 10.0e-6, 20.0e-6, , 30.0e-6
    a0 = [1.7e-3]
    b0_min = 0.5e-6
    b0_max = 5.0e-3
    concentration_vs_percentage_bound(kd, a0, [b0_min, b0_max], print_for = [1.5e-3, 2e-3])
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    

    

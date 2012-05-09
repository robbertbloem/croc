"""
A series of methods to calculate concentrations.

"""


from __future__ import print_function
from __future__ import division

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import Resources.Mathematics as M

def concentration_vs_percentage_bound(kd, concentration_A, concentration_B_range, n_steps = 100, print_for = []):

    if type(kd) == float or type(kd) == int:
        kd = [kd]   

    if type(concentration_A) == float or type(concentration_A) == int:
        concentration_A = [concentration_A] 
    
    step = (concentration_B_range[1] - concentration_B_range[0])/(n_steps-1)
    
    if concentration_B_range[0] == 0:
        start = step
    else:
        start = concentration_B_range[0]
    
    stop = concentration_B_range[1] + step/2

    concentration_B = numpy.arange(start, stop, step)
    
    print(len(concentration_B))
    #(1, n_steps + 1) * (concentration_B_range[1] - concentration_B_range[0])/n_steps
    
    xy = [0,0]
    
    plt.figure()
    
    for i in range(len(kd)):
        for j in range(len(concentration_A)):
            r = numpy.zeros(len(concentration_B))
            for k in range(len(concentration_B)):
                a = 1
                b = -(concentration_A[j] + concentration_B[k] + kd[i])
                c = concentration_A[j] * concentration_B[k]
                
                xy[0], xy[1] = M.square_formula(a, b, c)
                
                for m in range(2):
                    if xy[m] > concentration_A[j] or xy[m] > concentration_B[k]:
                        pass
                    else:
                        r[k] = 100*xy[m]/concentration_B[k]

            if len(print_for) != 0:
                print("Kd: " + str(kd[i]) + " M, [A]: " + str(1000*concentration_A[j]) + " mM") 
                for k in range(len(print_for)):
                    index = numpy.where(concentration_B >= print_for[k])
                    print("    [B]: " + str(numpy.round(1000*concentration_B[index[0][0]],1)) + " mM: " + str(numpy.round(r[index[0][0]],1)) + "%")
            
            c = ["b", "g", "r"]
            
            plt.plot(1000*concentration_B, r, label = "kd: " + str(1000*kd[i]) + " mM, [A]: " + str(1000*concentration_A[j]) + " mM")#, color = c[j])
    plt.title("Percentage bound as a function of concentration and Kd\nA+B <=> AB")
    plt.ylim(80,100)
    plt.xlim(1000*start, 1000*stop)
    plt.xlabel("[B] (mM)")
    plt.ylabel("Percentage bound (%)")
    plt.legend(loc="lower left")  
    plt.grid(b=True, which="both")  
    plt.show()  
    
    




    



if __name__ == "__main__": 
    kd = [5e-6, 15.0e-6, 25.0e-6] # 10.0e-6, 20.0e-6, , 30.0e-6
    a0 = [1.9e-3]
    b0_min = 0.5e-3
    b0_max = 2.5e-3
    concentration_vs_percentage_bound(kd, a0, [b0_min, b0_max], print_for = [1e-3, 2e-3])
    
    
    #kd, concentration_ratio = [0,2], n_steps = 4, print_for = [0.5,1,2])
    
#    A0 = 1e-3
#    B0 = 1e-3
#    kd = 15.0e-6
#    
#    a = 1.0
#    b = -(A0+B0+kd)
#    c = A0*B0
#    
#    print((-b - numpy.sqrt(b**2 - 4*a*c))/(2*a))
    
#    print(M.square_formula(a, b, c))

    
    
    
    
    
    
    
    
    
    
    
    
    

    

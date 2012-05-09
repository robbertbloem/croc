"""
A series of methods to calculate concentrations.

"""


from __future__ import print_function
from __future__ import division

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import Resources.Mathematics as M



def protein_ligand_kinetics(kd, cA, cX, X_steps = 100, print_for_X = [], A_name = "A", X_name = "X", flag_plot = True, y_range = [0,0]):
    """
    For the equilibrium A + X <-> AX, with dissociation constant kd and with concentrations for A and X, calculate the percentage of how much of X is bound to A. 
    In general, A is the protein at a known concentration and X is a range of ligand concentrations. The plot can be used to find the best concentration of the ligand for a given protein concentration.
    Once the ligand is added in a known concentration, the option print_for_X can be used to give the precise percentage bound. 
    
    All values are in M (molar). The values are printed and plotted in micro molar.
    
    Inputs:
    - kd (int or list): dissociation constant
    - cA (int or list): concentration of A
    - cX (int or list): concentration of variable on X-axis
    - X_steps: number of steps of ligand
        - cX = int or float: only this concentration will be used. X_steps will be ignored
        - cX = [a, b, c] and X_steps =< 1: only the concentrations a, b and c will be used
        - cX = [a, b, c] and X_steps > 1: the concentration of X will be between cX[0] and cX[-1] in X_steps. 
    - print_for_X: print for these concentrations of X
    - A_name, X_name: give the names, they will be used on the plot. This minimizes confusion.
    - flag_plot: If True, it will make a plot. If cX is an integer, it will not make a plot.
    - y_range: the plot will show the percentages in this range. Set to [0,0] to use the automatic range.
    
    
    
    """
    
    print("This routine calculates the percentage of " + X_name + " that is bound to " + A_name + ".")
    
    X_letter = X_name[0]
    A_letter = A_name[0]

    if type(kd) == float or type(kd) == int:
        kd = [kd]   
    
    if type(cA) == float or type(cA) == int:
        cA = [cA]
    
    if type(cX) == float or type(cX) == int:
        cX = [cX]
        flag_plot = False
    elif type(cX) == list and X_steps <= 1:
        pass
    elif type(cX) == list and X_steps > 1:
        step = (cX[-1] - cX[0])/(X_steps-1)
        if cX[0] == 0:
            start = step
        else:
            start = cX[0]
        stop = cX[-1] + step/2
        cX = numpy.arange(start, stop, step)
    
    xy = [0,0]
    
    if flag_plot:
        plt.figure()
        x_plot_prop = value_to_string(cX[-1], "M")
    
    for i in range(len(kd)):
        for j in range(len(cA)):
            r = numpy.zeros(len(cX))
            for k in range(len(cX)):
                a = 1
                b = -(cA[j] + cX[k] + kd[i])
                c = cA[j] * cX[k]
    
                xy[0], xy[1] = M.square_formula(a, b, c)
                
                for m in range(2):
                    if xy[m] > cA[j] or xy[m] > cX[k]:
                        pass
                    else:
                        r[k] = 100*xy[m]/cX[k]  
                        
            temp = value_to_string(kd[i], "M")
            kd_str = str(temp[0]) + " " + temp[1]
    
            temp = value_to_string(cA[j], "M")
            cA_str = str(temp[0]) + " " + temp[1]

            if len(print_for_X) != 0:
                print("Kd: " + kd_str + ", [" + A_letter + "]: " + cA_str) 
                for k in range(len(print_for_X)):
                    index = numpy.where(cX >= print_for_X[k])
                    temp = value_to_string(cX[index[0][0]], "M", flag_round = True)
                    cX_str = str(temp[0]) + " " + temp[1]
                    print("    [" + X_letter + "]: " + cX_str + ": " + str(numpy.round(r[index[0][0]],1)) + "%")

            if flag_plot:
                plt.plot(x_plot_prop[2]*cX, r, label = "kd: " + kd_str + ", [" + A_letter + "]: " + cA_str)
    
    if flag_plot:
    
        plt.title("Percentage " + X_letter + " bound to " + A_letter + " a function of concentration and Kd\n" + A_letter + "+" + X_letter + " <=> " + A_letter + X_letter)
        
        plt.ylabel("Percentage bound (%)")
        if y_range != [0,0]:
            plt.ylim(y_range[0], y_range[1])
        
        plt.xlim(x_plot_prop[2]*cX[0], x_plot_prop[2]*cX[-1])
        plt.xlabel("[" + X_letter + "] (" + x_plot_prop[1] + ")")
        
        plt.legend(loc=0)
        
        plt.grid(b=True, which="both")  
            
        plt.show()


def value_to_string(val, unit, flag_round = False, flag_debug = False):
    
    mp = 1

    if flag_debug == False:
        if 1e3 <= val < 1e6:
            mp = 1e-3
            val = val / mp
            unit = "k" + unit
        elif 1e-3 <= val < 1:
            mp = 1e3
            val = val * mp
            unit = "m" + unit
        elif 1e-6 <= val < 1e-3:
            mp = 1e6
            val = val * mp
            unit = "u" + unit
        elif 1e-9 <= val < 1e-6:
            mp = 1e9
            val = val * mp
            unit = "n" + unit
    
        if flag_round:
            val = numpy.round(val,1)

    return val, unit, mp



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
    
    kd = [48.5e-6, 58.5e-6, 68.5e-6]
    cA = [1.7e-3]
    cX = [0, 3e-3]
    print_for_X = [1.3e-3]
    
    protein_ligand_kinetics(kd, cA, cX, X_steps = 100, print_for_X = print_for_X, flag_plot = True, A_name = "Protein", X_name = "Ligand", y_range = [80,100])  
    

    
    
    
    
    
    
    
    
    
    
    
    
    

    

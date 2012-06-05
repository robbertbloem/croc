"""
A series of methods to calculate concentrations.

"""


from __future__ import print_function
from __future__ import division

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import Resources.Mathematics as M


def protein_ligand_kinetics(kd, cA, cX, X_steps = 100, print_for_X = [], A_name = "A", X_name = "X", flag_plot = True, y_range = [0,0], verbose = True):
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
    
    if verbose:
        print("This routine calculates the percentage of " + X_name + " that is bound to " + A_name + ".")
    
    X_letter = X_name[0]
    A_letter = A_name[0]

    if type(kd) == float or type(kd) == int or type(kd) == numpy.float64:
        kd = [kd]   
    
    if type(cA) == float or type(cA) == int or type(cA) == numpy.float64:
        cA = [cA]
    
    if type(cX) == float or type(cX) == int or type(cX) == numpy.float64:
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

    r = numpy.zeros( (len(kd),len(cA),len(cX)) )
    
    for i in range(len(kd)):
        for j in range(len(cA)):
            for k in range(len(cX)):
                a = 1
                b = -(cA[j] + cX[k] + kd[i])
                c = cA[j] * cX[k]
    
                xy[0], xy[1] = M.square_formula(a, b, c)
                
                for m in range(2):
                    if xy[m] > cA[j] or xy[m] > cX[k]:
                        pass
                    else:   
                        # percentage!
                        r[i, j, k] = 100*xy[m]/cX[k]  

    if len(print_for_X) != 0:

        for i in range(len(kd)):
            for j in range(len(cA)):
    
                temp = value_to_string(kd[i], "M")
                kd_str = str(temp[0]) + " " + temp[1]
        
                temp = value_to_string(cA[j], "M")
                cA_str = str(temp[0]) + " " + temp[1]
            
                print("Kd: " + kd_str + ", [" + A_letter + "]: " + cA_str) 
                for k in range(len(print_for_X)):
                    index = numpy.where(cX >= print_for_X[k])
                    temp = value_to_string(cX[index[0][0]], "M", flag_round = True)
                    cX_str = str(temp[0]) + " " + temp[1]
                    print("    [" + X_letter + "]: " + cX_str + ": " + str(numpy.round(r[i, j, index[0][0]],1)) + "%")

    if flag_plot:

        plt.figure()
        x_plot_prop = value_to_string(cX[-1], "M")

        for i in range(len(kd)):
            for j in range(len(cA)):
    
                temp = value_to_string(kd[i], "M")
                kd_str = str(temp[0]) + " " + temp[1]
        
                temp = value_to_string(cA[j], "M")
                cA_str = str(temp[0]) + " " + temp[1]

                plt.plot(x_plot_prop[2]*cX, r[i,j,:], label = "kd: " + kd_str + ", [" + A_letter + "]: " + cA_str)
    
        plt.title("Percentage " + X_letter + " bound to " + A_letter + " a function of concentration and Kd\n" + A_letter + "+" + X_letter + " <=> " + A_letter + X_letter)
        
        plt.ylabel("Percentage bound (%)")
        if y_range != [0,0]:
            plt.ylim(y_range[0], y_range[1])
        
        plt.xlim(x_plot_prop[2]*cX[0], x_plot_prop[2]*cX[-1])
        plt.xlabel("[" + X_letter + "] (" + x_plot_prop[1] + ")")
        
        plt.legend(loc=0)#"lower right")
        
        plt.grid(b=True, which="both")  
            
        plt.show()

    return r, kd, cA, cX


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
    
    
def ITC_sim():
    
    # in Steves plot, it takes 10 injections of ligand to reach molar ratio 1
    # the concentration of ligand is ~10x higher than of protein
    # this means that the volume ligand added is ~100x smaller volume of protein 
    
    kd = 50e-7
    
    volume_cell = 1e-3
    volume_added = 0.5e-5
    
    mol_A = 0.5e-3 * volume_cell
    mol_X_add = 5e-3 * volume_added
    
    n_steps = 40
    
    # kcal per mol injectant or whatever
    binding_energy = -1e8

    perc_X_bound = numpy.zeros(n_steps)
    mol_X_bound = numpy.zeros(n_steps)
    mol_X = numpy.zeros(n_steps)
    volume_AX = numpy.zeros(n_steps)
    cA = numpy.zeros(n_steps)
    cX = numpy.zeros(n_steps)
    
    binding_events = numpy.zeros(n_steps)
    
    for i in range(0, n_steps):
        
        mol_X[i] = (i+1) * mol_X_add
        volume_AX[i] = volume_cell + (i+1) * volume_added
        
        cA[i] = mol_A / volume_AX[i]
        cX[i] = mol_X[i] / volume_AX[i]
        
        temp = protein_ligand_kinetics(kd, cA[i], cX[i], verbose = False)
        
        perc_X_bound[i] = temp[0]
        mol_X_bound[i] = mol_X[i] * perc_X_bound[i] / 100
    
    for i in range(n_steps):
        
        if i == 0:
            binding_events[i] = mol_X_bound[i]
        else:
            binding_events[i] = mol_X_bound[i] - mol_X_bound[i-1]
            




        

    plt.figure()
#    plt.plot(mol_X/mol_A, mol_X_bound)
    plt.plot(mol_X/mol_A, binding_events * binding_energy)
    plt.grid(b=True, which="both")  
    plt.xlabel("Molar ratio X/A")
    plt.ylabel("Energy (au)")
    plt.show()
    
    

    


    



if __name__ == "__main__": 
    
    kd = [58.5e-6]
    cA = [1e-3, 2e-3, 3e-3, 5e-3, 7.5e-3, 10e-3]
    cX = [0, 10e-3]
    print_for_X = []
    
    protein_ligand_kinetics(kd, cA, cX, X_steps = 100, print_for_X = print_for_X, flag_plot = True, A_name = "Protein", X_name = "Ligand", y_range = [80,100])  
    
    #ITC_sim()

#    l = numpy.arange(0,10,0.1)
#    k = 1
#    q = (k*l)/(1+k*l)
#
#    d = numpy.zeros(len(q)-1)
#    for i in range(len(q)-1):
#        d[i] = (q[i+1]-q[i])
#    
#    plt.figure()
#    plt.plot(d)
#    plt.show()
    
    
    
    
    
    
    
    
    
    
    

    

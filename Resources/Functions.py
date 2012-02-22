from __future__ import print_function
from __future__ import division

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import Constants as C
import Mathematics as M
import Equations as E
import GVD_Materials

reload(C)
reload(M)
reload(E)
reload(GVD_Materials)














    
### GROUP VELOCITY DISPERSION ###    


def calculate_gvd(range_L, n_steps, SC):
    """
    Function to calculate the Group Velocity Dispersion using the Sellmeier Equation.
    
    CHANGELOG:
    20110909/RB: started
    
    INPUT:
    range_L (array, 2 elements): minimum and maximum
    n_steps (int): number of steps for the calculation.
    SC (array): Sellmeier Coefficients
    
    """

    # speed of light
    cms =  2.99792458e8
    
    # calculate the index of refraction over the defined range
    sm_L = numpy.linspace(range_L[0], range_L[1], num = n_steps)
    sm_n = numpy.sqrt(E.Sellmeier(SC, sm_L))
    
    # calculate the derivatives
    [d1x, d1y] = numpy.array(M.derivative(sm_L, sm_n))
    [d2x, d2y] = numpy.array(M.derivative(d1x, d1y))
    
    # define the x axes
    vg_x = d1x
    gvd_x = d2x
    
    vg_y = (cms / (vg_x)) / (1 - (vg_x / sm_n[1:-1]) * d1y)
    gvd_y = (gvd_x**3/(2*numpy.pi*cms*cms)) * d2y
    
    gvd_y *= 1e21
    
    return sm_L, sm_n, vg_x, vg_y, gvd_x, gvd_y





def calculate_effect_GVD(t0, gvd):
    """
    Calculates the effect the group velocity dispersion has on a pulse.
    
    CHANGELOG:
    20120221/RB: started the function
    
    INPUT:
    t0 (array or int): the pulse length(s) of the pulse before the gvd
    gvd (numpy.float or ndarray): the GVD in fs^2
    
    OUTPUT:
    t1 (ndarray): the new pulse length as a function of GVD.
    
    """
    
    if type(t0) == int:
        t0 = [t0]
    
    for i in range(len(t0)):
        t1 = t0[i] * numpy.sqrt(1 + (4 * numpy.log(2) * gvd / t0[i]**2)**2 )
    
    return t1


def GroupVelocityDispersion(material, print_for_um = [4], range_um = [1,10], material_path_mm = 0, pulse_length_fs = 0, n_steps = 100, flag_plot_n = True, flag_plot_gvd = True, y_range_gvd = [0,0]):
    
    # import properties
    [n, SC] = GVD_Materials.MaterialProperties(material)
    
    # calculate the index of refraction using the sellmeier equations
    if SC != []:
        [sm_L, sm_n, vg_x, vg_y, gvd_x, gvd_y] = calculate_gvd(range_um, n_steps, SC)
    
        # print stuff
        if print_for_um != []:
            print(material)
            
            if material_path_mm > 0:
                print(str(material_path_mm) + " mm path")
                print("um \tGVD (fs^2/mm)\t" + str(pulse_length_fs) + " fs")
                for i in range(len(print_for_um)):
                    index = numpy.where(gvd_x >= print_for_um[i])
                    new_pulse_length_fs = calculate_effect_GVD(pulse_length_fs, gvd_y[index[0][0]]*material_path_mm)
                    print(str(numpy.round(gvd_x[index[0][0]], 2)) + "\t" + str(numpy.round(gvd_y[index[0][0]], 3)) + "   \t" + str(numpy.round(new_pulse_length_fs, 1)))
                    
            else:
                print("um \tGVD (fs^2/mm)")
                for i in range(len(print_for_um)):
                    index = numpy.where(gvd_x >= print_for_um[i])
                    print(str(numpy.round(gvd_x[index[0][0]], 2)) + " \t" + str(numpy.round(gvd_y[index[0][0]], 3)))

            
    # plot index of refraction
    if flag_plot_n:
        plt.figure(0)
        if n != []:
            plt.plot(n[:,0], n[:,1])
        if SC != []:
            plt.plot(sm_L, sm_n, label = material)
        plt.legend()
        plt.xlabel('Wavelength (micron)')
        plt.ylabel('Index of refraction')
        plt.title('Index of Refraction: Experiment vs Sellmeier Equation')
        plt.xlim(range_um[0], range_um[1])
    
    # plot GVD   
    if SC != [] and flag_plot_gvd:
        plt.figure(1)
        plt.plot(gvd_x, gvd_y, label = material)
        plt.legend()
        plt.xlabel('Wavelength (micron)')
        plt.ylabel('GVD (fs^2/mm)')
        plt.title('Group Velocity Dispersion')
        plt.xlim(range_um[0], range_um[1])
        if y_range_gvd != [0, 0]:
            plt.ylim(y_range_gvd[0], y_range_gvd[1])       
    
    plt.show()
    
    return n, gvd_x, gvd_y





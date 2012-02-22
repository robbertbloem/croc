from __future__ import print_function
from __future__ import division

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import Resources.Constants as C
import Resources.Functions as F
import Resources.GVD_Materials

reload(C)
reload(F)
reload(Resources.GVD_Materials)

def GVD(material, print_for_um = [4], range_um = [1,10], material_path_mm = 0, pulse_length_fs = 0, n_steps = 100, flag_plot_n = True, flag_plot_gvd = True, y_range_gvd = [0,0]):
    
    # import properties
    [n, SC] = Resources.GVD_Materials.MaterialProperties(material)
    
    # calculate the index of refraction using the sellmeier equations
    if SC != []:
        [sm_L, sm_n, vg_x, vg_y, gvd_x, gvd_y] = F.calculate_gvd(range_um, n_steps, SC)
    
        # print stuff
        if print_for_um != []:
            print(material)
            
            if material_path_mm > 0:
                print(str(material_path_mm) + " mm path")
                print("um \tGVD (fs^2/mm)\t" + str(pulse_length_fs) + " fs")
                for i in range(len(print_for_um)):
                    index = numpy.where(gvd_x >= print_for_um[i])
                    new_pulse_length_fs = F.calculate_effect_GVD(pulse_length_fs, gvd_y[index[0][0]]*material_path_mm)
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












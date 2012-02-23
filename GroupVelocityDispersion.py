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



def GVD(material, print_for_um = [], range_um = [1,10], material_path_mm = 0, pulse_length_fs = 0, n_steps = 100, flag_plot_n = True, flag_plot_gvd = True, y_range_gvd = [0,0]):
    """
    croc.GroupVelocityDispersion.GVD calculates the GVD for a certain material in a certain wavelength range using the Sellmeier equation.
    
    CHANGELOG:
    201109??/RB: started the method.
    20120222/RB: integrated it into croc.
    
    INPUT:
    - material (string): the name of the material. The full list of names can be found in croc.Resources.GVD_Materials
    - print_for_um (int or array): print the GVD for these wavelengths, in micron
    - range_um (array, 2 elements): minimum and maximum of the calculation in micron. It should be between ~1 and ~10.
    - material_path_mm (int, default = 0): Path through material in mm. If >0 and pulse_lenth_fs > 0, it calculates the effect on the pulse length for the values in print_for_um
    - pulse_length_fs (int, default = 0): Pulse length in fs. If >0 and material_path_mm > 0, it calculates the effect on the pulse length for the values in print_for_um
    - flag_plot_n (BOOL, True): plot the index of refraction for range_um
    - flag_plot_gvd (BOOL, True): plot the gvd for range_um
    - y_range_gvd (array, 2 elements): Give the range of GVD that is plotted. Default is [0,0], which will give the full range.
    
    OUTPUT:
    - a graph of the GVD if flag_plot_gvd == True
    - a graph of the index of refraction if flag_plot_n == True
    - values of GVD for the wavelength given in print_for_um
    - if pulse_length_fs and material_path_mm are >0, it will also give the effect on the pulse length
    
    """
    
    if type(print_for_um) == float or type(print_for_um) == int:
        print_for_um = [print_for_um]
    
    # import properties
    [n, SC] = Resources.GVD_Materials.MaterialProperties(material)
    
    # calculate the index of refraction using the sellmeier equations
    if SC != []:
        [sm_L, sm_n, vg_x, vg_y, gvd_x, gvd_y] = F.calculate_gvd(range_um, n_steps, SC)
    
        # print stuff
        if print_for_um != []:
            print(material)
            
            if material_path_mm > 0 and pulse_length_fs > 0:
                print(str(material_path_mm) + " mm path")
                print("{0:4} {1:14} {2:5}".format("um", "GVD (fs^2/mm)", str(pulse_length_fs) + " fs"))
                for i in range(len(print_for_um)):
                    if print_for_um[i] > range_um[0] and print_for_um[i] < range_um[1]:
                        index = numpy.where(gvd_x >= print_for_um[i])
                        new_pulse_length_fs = F.calculate_effect_GVD(pulse_length_fs, gvd_y[index[0][0]]*material_path_mm)
                        s_a = str(numpy.round(gvd_x[index[0][0]], 2))
                        s_b = str(numpy.round(gvd_y[index[0][0]], 3))
                        s_c = str(numpy.round(new_pulse_length_fs, 1))
                        print("{0:4} {1:14} {2:5}".format(s_a.rjust(4), s_b.rjust(13), s_c.rjust(5)))
                    else:
                        print("ERROR (croc.GroupVelocityDispersion.GroupVelocityDispersion): Can not print value for wavelength that is out of range of the calculation.")
                    
            else:
                print("{0:4} {1:14}".format("um", "GVD (fs^2/mm)"))
                for i in range(len(print_for_um)):
                    if print_for_um[i] > range_um[0] and print_for_um[i] < range_um[1]:
                        index = numpy.where(gvd_x >= print_for_um[i])
                        s_a = str(numpy.round(gvd_x[index[0][0]], 2))
                        s_b = str(numpy.round(gvd_y[index[0][0]], 3))
                        print("{0:4} {1:14}".format(s_a.rjust(4), s_b.rjust(13)))
                    else:
                        print("ERROR (croc.GroupVelocityDispersion.GroupVelocityDispersion): Can not print value for wavelength that is out of range of the calculation.")
            
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



if __name__ == "__main__": 
    GVD("caf2", range_um = [1,11], print_for_um = [2,5,8, 10.5, 12], pulse_length_fs = 0, material_path_mm = 2, flag_plot_n = False, flag_plot_gvd = False)








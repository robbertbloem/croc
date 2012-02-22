from __future__ import print_function
from __future__ import division

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import Resources.Constants as C
import Resources.Functions as F

reload(C)
reload(F)

def GroupVelocityDispersion(material, print_for_um = [4], range_um = [1,10], material_path_mm = 0, pulse_length_fs = 0, n_steps = 100, flag_plot_n = True, flag_plot_gvd = True, y_range_gvd = [0,0]):
    
    n, gvd_x, gvd_y = F.GroupVelocityDispersion(material = material, print_for_um = print_for_um, range_um = range_um, material_path_mm = material_path_mm, pulse_length_fs = pulse_length_fs, n_steps = n_steps, flag_plot_n = flag_plot_n, flag_plot_gvd = flag_plot_gvd, y_range_gvd = y_range_gvd)
    
    return n, gvd_x, gvd_y







from __future__ import print_function
from __future__ import division

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import Resources.LS_Functions as L



def calculate_time_array(n_shots, speed_profile = "uniform", speed_variables = [2, 0.05], phase_mod_profile = "none"):

    """
    Makes a 2d-array
    0: time (t1)
    1: bin (depends on t1)
    2: noise
    3: signal (depends on t1)
    4: phase modulation state
    5: total signal
    """

    vib1 = [1600, 900, 1]
    vib2 = [1700, 1000, 0.3]
    vib3 = [1650, 10000, 1] # acts as scattering
    
    width = 6
    shots = numpy.reshape(numpy.zeros(n_shots*width), (n_shots,width))
    
    # make the time array and the bins
    shots = position(shots, speed_profile = speed_profile, variables = speed_variables)
    # make the instensity fluctuations
#     if speed_profile == "stepped":
#         shots = noise_stepped(shots, k_laser, speed_variables)
#     else:
    shots = laser_intensity(shots, k_laser)
    
    if flag_plot_noise:
        plt.figure()
        plt.plot(shots[:,2])
        plt.show()





if __name__ == "__main__": 

    pass
    
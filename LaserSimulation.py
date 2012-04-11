from __future__ import print_function
from __future__ import division

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import croc.Resources.LS_Functions as LS
import croc.Resources.IOMethods as IOM

reload(LS)



#def calculate_time_array(n_shots, speed_profile = "uniform", speed_variables = [2, 0.05], phase_mod_profile = "none"):
#
#	 """
#	 Makes a 2d-array
#	 0: time (t1)
#	 1: bin (depends on t1)
#	 2: noise
#	 3: signal (depends on t1)
#	 4: phase modulation state
#	 5: total signal
#	 """
#
#	 vib1 = [1600, 900, 1]
#	 vib2 = [1700, 1000, 0.3]
#	 vib3 = [1650, 10000, 1] # acts as scattering
#	 
#	 width = 6
#	 shots = numpy.reshape(numpy.zeros(n_shots*width), (n_shots,width))
#	 
#	 # make the time array and the bins
#	 shots = position(shots, speed_profile = speed_profile, variables = speed_variables)
#	 # make the instensity fluctuations
##	   if speed_profile == "stepped":
##		   shots = noise_stepped(shots, k_laser, speed_variables)
##	   else:
#	 shots = laser_intensity(shots, k_laser)
#	 
#	 if flag_plot_noise:
#		 plt.figure()
#		 plt.plot(shots[:,2])
#		 plt.show()





if __name__ == "__main__": 
	# T: time
	# I: laser intensity
	# S (S_1, S_2): signal 
	# S_M: signal with modulation
	# M: modulation
	
	n_shots = 8000

	speed_profile = "sinsquare"
	speed_variables = [2,0.05]
	
	T_fs, T_bin = LS.position(n_shots, speed_profile = speed_profile, variables = speed_variables)
	
	I = numpy.fromfile("/Users/robbert/Developer/laser_intensity/laser_0.bin")
	I = I[numpy.where(I)]
	I = I[:n_shots]

	w_cm = 1600
	tau_fs = 1000
	amplitude = 1
	
	S_1 = LS.signal(T_fs, w_cm, tau_fs, amplitude)
	
	w_cm = 1700
	tau_fs = 500
	amplitude = 0.5
	
	S_2 = LS.signal(T_fs, w_cm, tau_fs, amplitude)
	
	S = S_1 + S_2
	
	S = LS.add_noise_to_signal(S, I)

	S_M, M = LS.add_phase_modulation(S, phase_mod_profile = "pem")

	B, B_count, B_axis = LS.binning(S_M, T_bin, M, speed_profile = speed_profile, speed_variables = speed_variables)






	
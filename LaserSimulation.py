from __future__ import print_function
from __future__ import division

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import croc.Resources.LS_Functions as LS
import croc.Resources.IOMethods as IOM
import croc.Resources.Mathematics 
import croc.Debug 

reload(LS)

def import_laser(n):
	
	max_n = 12
	n = n % max_n
	
	path_and_filename = "/Users/robbert/Developer/laser_intensity/laser_" + str(n) + ".bin"
	laser = numpy.fromfile(path_and_filename)
	
	# they somehow got saved with some extra zeros. remove them here
	laser = laser[numpy.where(laser)]
	
	return laser

# T: time
# I: laser intensity
# S (S_1, S_2): signal 
# S_M: signal with modulation
# M: modulation

def medium_PEM(laser_file_n, vibrations, n_runs, plot_all = False):
	
	n_shots = 6000
	last_bin = 4000
	
	B_exists = False
	
	if plot_all:
		plt.figure()
	
	for i in range(n_runs):
		
		speed_profile = "sinsquare"
		speed_variables = [3,0.05]
		
		# determine the position
		T_fs, T_bin = LS.position(n_shots, speed_profile = speed_profile, variables = speed_variables)	
		
		print("last bin:", T_bin[-1])
	
		# import the laser
		I = import_laser(n = laser_file_n + i)
		I = -I[:n_shots]
		
		S = numpy.zeros(n_shots)
		for j in range(len(vibrations)):
			S += LS.signal(T_fs, vibrations[j][0], vibrations[j][1], vibrations[j][2])
			
		S = LS.signal_and_laser(S, I)
		
		S, M = LS.add_phase_modulation(S, phase_mod_profile = "pem")
		
		temp_b, temp_b_count, temp_b_axis = LS.binning(S, T_bin, M, last_bin)
				
		if B_exists:
			B += temp_b
			B_count += temp_b_count
			B_axis = temp_b_axis
		else:
			B = temp_b
			B_count = temp_b_count
			B_axis = temp_b_axis	
			B_exists = True
		
		if plot_all:
			R, R_axis = LS.construct_r(B, B_count, B_axis, M) 
			
			F = numpy.fft.fft(R)
			
			dt = (R_axis[1] - R_axis[0]) * 632/299.792458
			
			F_axis = croc.Resources.Mathematics.make_ft_axis(len(R_axis), dt, undersampling = 0, normalized_to_period = 0, zero_in_middle = False)
			
			F = F[:len(F)/2]
			F_axis = F_axis[:len(F)]
		
			plt.plot(F_axis, F)

		
	if plot_all == False:
		R, R_axis = LS.construct_r(B, B_count, B_axis, M) 
		
		F = numpy.fft.fft(R)
		
		dt = (R_axis[1] - R_axis[0]) * 632/299.792458
		
		F_axis = croc.Resources.Mathematics.make_ft_axis(len(R_axis), dt, undersampling = 0, normalized_to_period = 0, zero_in_middle = False)
		
		F = F[:len(F)/2]
		F_axis = F_axis[:len(F)]	
	
		plt.figure()
		plt.plot(F_axis, F)

	plt.show()			
		
def fast_PEM(laser_file_n, vibrations, n_runs):
	
	n_shots = 1000
	last_bin = 4000
	
	B_exists = False
	
	for i in range(n_runs):
		
		speed_profile = "sinsquare"
		
		if i > 0:
			print(len(B_count) - len(B_count[numpy.where(B_count)]), "unfilled")
		
		if i == n_runs - 1:
			print("slow run!")
			speed_variables = [5,0.05]
			n_shots = 2000
		else:
			speed_variables = [20,0.05]
		
		# determine the position
		T_fs, T_bin = LS.position(n_shots, speed_profile = speed_profile, variables = speed_variables)	
		
		print("last bin:", T_bin[-1])
	
		# import the laser
		I = import_laser(n = laser_file_n + i)
		I = -I[:n_shots]
		
		S = numpy.zeros(n_shots)
		for j in range(len(vibrations)):
			S += LS.signal(T_fs, vibrations[j][0], vibrations[j][1], vibrations[j][2])
			
		S = LS.signal_and_laser(S, I)
		
		S, M = LS.add_phase_modulation(S, phase_mod_profile = "pem")
		
		temp_b, temp_b_count, temp_b_axis = LS.binning(S, T_bin, M, last_bin)
				
		if B_exists:
			B += temp_b
			B_count += temp_b_count
			B_axis = temp_b_axis
		else:
			B = temp_b
			B_count = temp_b_count
			B_axis = temp_b_axis	
			B_exists = True
		
	R, R_axis = LS.construct_r(B, B_count, B_axis, M) 
	
	F = numpy.fft.fft(R)
	
	dt = (R_axis[1] - R_axis[0]) * 632/299.792458
	
	F_axis = croc.Resources.Mathematics.make_ft_axis(len(R_axis), dt, undersampling = 0, normalized_to_period = 0, zero_in_middle = False)
	
	F = F[:len(F)/2]
	F_axis = F_axis[:len(F)]	

	plt.figure()
	plt.plot(F_axis, F)

	plt.show()			

def fast_none(laser_file_n, vibrations, n_runs):
	
	n_shots = 1000
	last_bin = 4000
	
	B_exists = False
	
	for i in range(n_runs):
		
		speed_profile = "sinsquare"
		
		if i > 0:
			print(len(B_count) - len(B_count[numpy.where(B_count)]), "unfilled")
		
		if i == n_runs - 1:
			print("slow run!")
			speed_variables = [5,0.05]
			n_shots = 2000
		else:
			speed_variables = [10,0.05]
		
		# determine the position
		T_fs, T_bin = LS.position(n_shots, speed_profile = speed_profile, variables = speed_variables)	
		
		print("last bin:", T_bin[-1])
	
		# import the laser
		I = import_laser(n = laser_file_n + i)
		I = -I[:n_shots]
		
		S = numpy.zeros(n_shots)
		for j in range(len(vibrations)):
			S += LS.signal(T_fs, vibrations[j][0], vibrations[j][1], vibrations[j][2])
			
		S = LS.signal_and_laser(S, I)
		
		S, M = LS.add_phase_modulation(S, phase_mod_profile = "pem")
		
		temp_b, temp_b_count, temp_b_axis = LS.binning(S, T_bin, M, last_bin)
				
		if B_exists:
			B += temp_b
			B_count += temp_b_count
			B_axis = temp_b_axis
		else:
			B = temp_b
			B_count = temp_b_count
			B_axis = temp_b_axis	
			B_exists = True
		
	R, R_axis = LS.construct_r(B, B_count, B_axis, M) 
	
	F = numpy.fft.fft(R)
	
	dt = (R_axis[1] - R_axis[0]) * 632/299.792458
	
	F_axis = croc.Resources.Mathematics.make_ft_axis(len(R_axis), dt, undersampling = 0, normalized_to_period = 0, zero_in_middle = False)
	
	F = F[:len(F)/2]
	F_axis = F_axis[:len(F)]	

	plt.figure()
	plt.plot(F_axis, F)


def make_run(laser_file_n, vibrations, n_runs, speed_profile, speed_variables, n_shots, last_bin, phase_mod_profile, n_shots_slow = 0, n_slow_runs = 0, speed_variables_slow = [], plot_all = False):

	B_exists = False
	
	for i in range(n_runs):
		
		if i >= n_runs - n_slow_runs:
			print("slow run!")
			n_shots = n_shots_slow
			speed_var = speed_variables_slow
		else:
			speed_var = speed_variables
			
		if i > 0:
			print(len(B_count) - len(B_count[numpy.where(B_count)]), "unfilled bins")

		# determine the position
		T_fs, T_bin = LS.position(n_shots, speed_profile = speed_profile, variables = speed_var)	
		
		print("last bin:", T_bin[-1])
	
		# import the laser
		I = import_laser(n = laser_file_n + i)
		I = -I[:n_shots]
		
		S = numpy.zeros(n_shots)
		for j in range(len(vibrations)):
			S += LS.signal(T_fs, vibrations[j][0], vibrations[j][1], vibrations[j][2])
			
		S = LS.signal_and_laser(S, I)
		
		S, M = LS.add_phase_modulation(S, phase_mod_profile = phase_mod_profile)
		
		temp_b, temp_b_count, temp_b_axis = LS.binning(S, T_bin, M, last_bin)
				
		if B_exists:
			B += temp_b
			B_count += temp_b_count
			B_axis = temp_b_axis
		else:
			B = temp_b
			B_count = temp_b_count
			B_axis = temp_b_axis	
			B_exists = True
		
	R, R_axis = LS.construct_r(B, B_count, B_axis, M) 
	
	F = numpy.fft.fft(R)
	
	dt = (R_axis[1] - R_axis[0]) * 632/299.792458
	
	F_axis = croc.Resources.Mathematics.make_ft_axis(len(R_axis), dt, undersampling = 0, normalized_to_period = 0, zero_in_middle = False)
	
	F = numpy.real(F[:len(F)/2])
	F_axis = F_axis[:len(F)]	

	plt.figure()
	plt.plot(F_axis, F)
	plt.show()





if __name__ == "__main__": 

	vibrations = [
		[1600, 1000, 0.01],
		[1700, 800, 0.005]
	]

#	medium_PEM(2, vibrations, 4, plot_all = False)
#	fast_PEM(2, vibrations, 10)
	
	laser_file_n = 2
	n_runs = 4
	speed_profile = "sinsquare"
	speed_variables = [4,0.05]
	n_shots = 6000
	last_bin = 4000
	phase_mod_profile = "pem"
	n_shots_slow = 0
	n_slow_runs = 0
	speed_variables_slow = []
	plot_all = False
	
	
	



	make_run(laser_file_n, vibrations, n_runs, speed_profile, speed_variables, n_shots, last_bin, phase_mod_profile, n_shots_slow, n_slow_runs, speed_variables_slow, plot_all)




	
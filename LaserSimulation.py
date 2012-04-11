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

def check_speed_profile(laser_file_n, vibrations, n_runs, speed_profile, speed_variables, n_shots, last_bin, phase_mod_profile, n_shots_slow = 0, n_slow_runs = 0, speed_variables_slow = [], flag_plot = False, title = ""):

	B_exists = False
	
	for i in range(n_runs):
		
		if i >= n_runs - n_slow_runs:
			print("slow run!")
			n_shots = n_shots_slow
			speed_var = speed_variables_slow
		else:
			speed_var = speed_variables
			
		if i > 0:
			sum_bins = numpy.sum(B_count, axis=1)			
			print(len(sum_bins) - len(sum_bins[numpy.where(sum_bins)]), "unfilled bins")

		# determine the position
		T_fs, T_bin = LS.position(n_shots, speed_profile = speed_profile, variables = speed_var)	
		
		x, y = croc.Resources.Mathematics.derivative(numpy.arange(n_shots), T_fs)
		
		#print(T_fs[0], T_bin[0], T_fs[-1], T_bin[-1])
		
		plt.figure()
		plt.plot(numpy.arange(n_shots), T_bin)
		plt.show()
		
		plt.figure()
		plt.plot(x, y)
		plt.title("Speed profile")
		plt.xlabel("Shots")
		plt.ylabel("Time change per shot (fs)")
		plt.show()		

def make_run(laser_file_n, vibrations, n_runs, speed_profile, speed_variables, n_shots, last_bin, phase_mod_profile, n_shots_slow = 0, n_slow_runs = 0, speed_variables_slow = [], flag_plot = False, title = ""):

	B_exists = False
	
	for i in range(n_runs):
		
		if i >= n_runs - n_slow_runs:
			print("  slow run!")
			n_shots = n_shots_slow
			speed_var = speed_variables_slow
		else:
			speed_var = speed_variables
			
		# determine the position
		T_fs, T_bin = LS.position(n_shots, speed_profile = speed_profile, variables = speed_var)	

#		print("last bin:", T_bin[-1])
	
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

	sum_bins = numpy.sum(B_count, axis=1)			
	print("  " + str(len(sum_bins) - len(sum_bins[numpy.where(sum_bins)])) + " unfilled bins")
		
	R, R_axis = LS.construct_r(B, B_count, B_axis, M) 
	
	plt.figure()
	plt.plot(R_axis, R)
	plt.show()
	
	R -= numpy.mean(R)
	
	F = croc.Resources.Mathematics.fourier(R, zero_in_middle = False, first_correction = True, zeropad_to = last_bin * zeropad_by, window_function = "none", window_length = 0, flag_plot = False)
		
	dt = (R_axis[1] - R_axis[0]) * 632/299.792458
	
	F_axis = croc.Resources.Mathematics.make_ft_axis(len(F), dt, undersampling = 0, normalized_to_period = 0, zero_in_middle = False)
	
	F = numpy.real(F[:len(F)/2])
	F_axis = F_axis[:len(F)]	

	if flag_plot:
		plt.figure()
		plt.plot(F_axis, F)
		plt.title(title)
#		plt.xlim(1500, 1800)
		plt.show()


def medium_PEM(laser_file_n, vibrations):
	n_runs = 2
	speed_profile = "mostly_uniform"
	speed_variables = [0.45, 0.05, 0.0002, 0.0001]
	n_shots = 8500
	last_bin = 1000
	phase_mod_profile = "pem"
	n_shots_slow = 0
	n_slow_runs = 0
	speed_variables_slow = []
	flag_plot = True
	
	title = "Top speed: " + str(speed_variables[0]) + " fs/shot, with PEM"
	print(title)

	make_run(laser_file_n, vibrations, n_runs, speed_profile, speed_variables, n_shots, last_bin, phase_mod_profile, n_shots_slow, n_slow_runs, speed_variables_slow, flag_plot, title)	


def fast_10_PEM(laser_file_n, vibrations):
	n_runs = 5
	speed_profile = "mostly_uniform"
	speed_variables = [10, 0.05, 0.05, 0.05]
	n_shots = 550
	last_bin = 1000
	phase_mod_profile = "pem"
	n_shots_slow = 8500
	n_slow_runs = 1
	speed_variables_slow = [0.45, 0.05, 0.0002, 0.0001]
	flag_plot = True

	title = "Top speed: " + str(speed_variables[0]) + " fs/shot, with PEM"
	print(title)

	make_run(laser_file_n, vibrations, n_runs, speed_profile, speed_variables, n_shots, last_bin, phase_mod_profile, n_shots_slow, n_slow_runs, speed_variables_slow, flag_plot, title)	

def fast_10_none(laser_file_n, vibrations):
	n_runs = 5
	speed_profile = "mostly_uniform"
	speed_variables = [10, 0.05, 0.05, 0.05]
	n_shots = 550
	last_bin = 1000
	phase_mod_profile = "ones"
	n_shots_slow = 8500
	n_slow_runs = 1
	speed_variables_slow = [0.45, 0.05, 0.0002, 0.0001]
	flag_plot = True

	title = "Top speed: " + str(speed_variables[0]) + " fs/shot, without PEM"
	print(title)

	make_run(laser_file_n, vibrations, n_runs, speed_profile, speed_variables, n_shots, last_bin, phase_mod_profile, n_shots_slow, n_slow_runs, speed_variables_slow, flag_plot, title)


def fast_5_PEM(laser_file_n, vibrations):
	n_runs = 5
	speed_profile = "mostly_uniform"
	speed_variables = [5, 0.05, 0.05, 0.05]
	n_shots = 550
	last_bin = 1000
	phase_mod_profile = "pem"
	n_shots_slow = 8500
	n_slow_runs = 1
	speed_variables_slow = [0.45, 0.05, 0.0002, 0.0001]
	flag_plot = True

	title = "Top speed: " + str(speed_variables[0]) + " fs/shot, with PEM"
	print(title)

	make_run(laser_file_n, vibrations, n_runs, speed_profile, speed_variables, n_shots, last_bin, phase_mod_profile, n_shots_slow, n_slow_runs, speed_variables_slow, flag_plot, title)	

def fast_5_none(laser_file_n, vibrations):
	n_runs = 5
	speed_profile = "mostly_uniform"
	speed_variables = [5, 0.05, 0.05, 0.05]
	n_shots = 550
	last_bin = 1000
	phase_mod_profile = "ones"
	n_shots_slow = 8500
	n_slow_runs = 1
	speed_variables_slow = [0.45, 0.05, 0.0002, 0.0001]
	flag_plot = True
	
	title = "Top speed: " + str(speed_variables[0]) + " fs/shot, without PEM"
	print(title)

	make_run(laser_file_n, vibrations, n_runs, speed_profile, speed_variables, n_shots, last_bin, phase_mod_profile, n_shots_slow, n_slow_runs, speed_variables_slow, flag_plot, title)


if __name__ == "__main__": 

	global zeropad_by
	zeropad_by = 4

	vibrations = [
		[1600, 300, 0.1],
		[1700, 500, 0.05]
	]

	laser_file_n = 2
	
#	medium_PEM(laser_file_n, vibrations)
	fast_10_PEM(laser_file_n, vibrations)
#	fast_10_none(laser_file_n, vibrations)
#	fast_5_PEM(laser_file_n, vibrations)
#	fast_5_none(laser_file_n, vibrations)

	




	
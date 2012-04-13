from __future__ import print_function
from __future__ import division

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import Mathematics as M
import Equations as E

reload(M)
reload(E)

global hene_fringe 
hene_fringe = 632/299.792458 #fs



#
#def position_bin(n_shots, n_bins, speed_profile = "mostly_uniform", variables = []):
#	
#	t_array = numpy.zeros(n_shots)
#	c_array = numpy.zeros(n_shots)
#	
#	if speed_profile == "mostly_uniform":
#		
#		speed_max = variables[0]
#		
#		flag_finished = False
#		
#		while flag_finished == False:
#		
#			# number of shots needed for acceleration and deceleration
#			n_shots_acc = speed_max // variables[2] + 1
#			n_shots_dec = speed_max // variables[3] + 1
#			
#			if n_shots_acc * 
#			
#			
#			bins = 0
#			
#			for i in range(n_acc):
#				bins += variables[2] * i
#			
#			for i in range(n_dec):
#				bins += variables[3] * i
#			
#			if bins > n_bins:
#				
#				
#				
#			else:
#				remaining = n_bins - bins
#				shots_needed = remaining // speed_max
#				flag_finished = True
#			
			
			
		
	
		
	
	
	





def position(n_shots, speed_profile = "uniform", variables = []):
	
	"""
	calculates the time and the bin
	
	speed_profile options and variables:
	- uniform: speed, variation
	- mostly uniform: speed, variation, speed increase, speed decrease (increase in fs/shot per shot)
	- sinsquare: max speed, variation
	- stepped: n_steps, stepsize (in bins), shots (per bin)
	speed is in fs/shot
	
	t_array is the result in fs
	c_array is the counter value, starting at 0 (not 4000)
	
	"""

	t_array = numpy.zeros(n_shots)
	c_array = numpy.zeros(n_shots)
	
	if speed_profile == "sinsquare":
		
		if variables == []:
			variables = [4, 0.05]
		speed_max = variables[0] * (1-variables[1]*numpy.random.rand(1)) 
		speed = speed_max * numpy.sin(numpy.pi*numpy.arange(n_shots)/n_shots)**2

		for i in range(n_shots-1):
			t_array[i+1] = t_array[i] + speed[i] 
			c_array[i+1] = numpy.floor((t_array[i+1]+1.055)/hene_fringe)   

	
	elif speed_profile == "stepped":
	
		if variables == []:
			variables = [28, 12, 100]		 
		n_steps = variables[0]
		stepsize = variables[1]
		n_shots_per_step = variables[2]
		
		t_array = numpy.zeros(n_shots_per_step * n_steps)
		c_array = numpy.zeros(n_shots_per_step * n_steps)
		
		bin = 0
		for i in range(n_steps):
			for j in range(n_shots_per_step):
				t_array[i*n_shots_per_step+j] = bin
				c_array[i*n_shots_per_step+j] = bin * hene_fringe
			bin = bin + variables[1]   
	
	elif speed_profile == "mostly_uniform":
		if variables == []:
			variables = [1, 0.05, 0.1, 0.1]

		speed_max = variables[0] * (1-variables[1]*numpy.random.rand(1))
		acc = variables[2] * (1-variables[1]*numpy.random.rand(1))
		dec = variables[3] * (1-variables[1]*numpy.random.rand(1))
		
		if speed_max//acc + speed_max//dec + 2 > n_shots:
			acc_del_len = speed_max//acc + speed_max//dec + 10
			speed_max = speed_max * n_shots / acc_del_len
			print("oops, too short, reduce speed_max to:", speed_max, "fs/shot")
			
		speed = numpy.ones(n_shots) * speed_max

		for i in range(speed_max//acc+1):
			speed[i] = 0 + acc * i
		
		for i in range(speed_max//dec+1):
			speed[-1-i] = 0 + dec * i
		
		for i in range(n_shots-1):
			t_array[i+1] = t_array[i] + speed[i] 
			c_array[i+1] = numpy.floor((t_array[i+1]+1.055)/hene_fringe)		 
		   
	elif speed_profile == "uniform":   
		if variables == []:
			variables = [2, 0.05]		
		speed = variables[0] * (1-variables[1]*numpy.random.rand(1))
		for i in range(n_shots):
			t_array[i] = i * speed
			c_array[i] = numpy.floor((t_array[i]+1.055)/hene_fringe)	
	
	else:
		print("Speed profile not recognized, using uniform")
		if variables == []:
			variables = [2, 0.05] 
		speed = variables[0] * (1-variables[1]*numpy.random.rand(1))
		for i in range(n_shots):
			t_array[i] = i * speed
			c_array[i] = numpy.floor((t_array[i]+hene_fringe/2)/hene_fringe) 
	
	return t_array, c_array


def laser_intensity(n_shots, k, I0 = 10):
	"""
	Calculates the noise per shot
	
	CHANGELOG:
	201201xx/RB: started function as separate script
	20120224/RB: integrated it into croc
	
	INPUT:
	- k: 1/correlation time, in shots
	- I0: start intensity (a bit of randomness is added)
	
	"""
	
	I = numpy.zeros(n_shots)
	
	sigma = 2/numpy.sqrt(2*k)
	I[0] = 10 * numpy.random.randn(1) * sigma * k
	for i in range(n_shots-1):
		I[i+1] = I[i] * (1-k) + numpy.random.randn(1) * sigma * k
	
	return I + I0



def signal(time_array, w_cm, tau_fs, amplitude):
	"""
	Where t is an array with the time steps that need to be calculated.
	"""
	array = numpy.zeros(len(time_array))
	
	w_fs = 1e13 / (w_cm * 3e8)
	
	for i in range(len(time_array)):
		array[i] = amplitude * numpy.cos(2*numpy.pi * time_array[i] / w_fs) * numpy.exp(-time_array[i]/tau_fs)
		
	return array


def signal_and_laser(signal, laser_intensity):
	return signal * laser_intensity + laser_intensity




def add_phase_modulation(signal_array, phase_mod_profile = "none"):
	
	
	if phase_mod_profile == "chopper":
		temp = [0,1]
  
	elif phase_mod_profile == "pem":
		temp = [-1,1]
	
	elif phase_mod_profile == "zero":
		temp = [0]
	
	elif phase_mod_profile == "ones":
		temp = [1]
		
	else:
		print("phase_mod_profile not recognized, using no modulation")
		temp = [1]

	if numpy.random.rand(1) < 0.5:
		if len(temp) > 1:
			temp = [temp[1], temp[0]]

	temp = numpy.array(temp)
	
	chopper_array = numpy.resize(temp, len(signal_array))	   

	modulated_signal_array = chopper_array * signal_array

	return modulated_signal_array, chopper_array







def binning(signal_array, bin_array, chopper_array, last_bin):
	"""
	signal_array: the signal, modified and with noise etc
	bin_array: the bin for each element in signal_array
	chopper_array: the state of the chopper for each element in signal_array
	last_bin: the maximum number of bins
	"""
	
	print("  binning")
	
	states = numpy.unique(chopper_array)
	n_states = len(states) 
	
	b = numpy.reshape(numpy.zeros(n_states * last_bin), (last_bin, n_states))
	b_count = numpy.reshape(numpy.zeros(n_states * last_bin), (last_bin, n_states))
	b_axis = numpy.arange(last_bin)
	
	if bin_array[-1] > last_bin:
		signal_array = signal_array[numpy.where(bin_array < last_bin)]
		print("    cut off " + str(bin_array[-1] - last_bin) + " bins")
	
	for i in range(len(signal_array)):
		b[bin_array[i], numpy.where(states == chopper_array[i])] += signal_array[i] 
		b_count[bin_array[i], numpy.where(states == chopper_array[i])] += 1
	
	return b, b_count, b_axis	
	

def construct_r(b, b_count, b_axis, chopper_array):
	
	print("  construct r")
	
	last_bin = b_axis[-1]
	
	states = numpy.unique(chopper_array)
	n_states = len(states) 

	r = numpy.zeros(last_bin)
	r_axis = numpy.arange(last_bin)
	
	zero_bin_count = 0
	
	for i in range(last_bin):
		for j in range(n_states):
			if b_count[i,j] != 0:
				r[i] += states[j] * b[i,j] / b_count[i,j]
			else:
				r[i] += 0
	
	non_zero = numpy.where(r)	

	return r, r_axis
				
	
	
	
				




	


def average_runs(b, max_bins):
    
    flag_bins_filled = False
    
    states, n_bins, width = numpy.shape(b[0])
    
    data = numpy.reshape(numpy.zeros(states * max_bins * width), (states, max_bins, width))
    
    max_bins_too_long_flag = True
    
    for i in range(runs):
        states, n_bins, temp = numpy.shape(b[i])
        if n_bins < max_bins:
            length = n_bins
        else:
            length = max_bins
            max_bins_too_long_flag = False
            
        for j in range(length):
            data[:,j,:] = data[:,j,:] + b[i][:,j,:]
    
    no_count = 0 
    
    for i in range(states): 
        for j in range(max_bins): 
            if data[i,j,1] != 0:
                data[i,j,2] = data[i,j,0] / data[i,j,1] 
            else: 
                data[i,j,2] = 0
                no_count += 1
    
    if no_count == 0:   
        flag_bins_filled = True

    if max_bins_too_long_flag:
        print("End of range not reached")
    else:
        print("The whole range has been scanned")

    if no_count:
        print(no_count, "bins unfilled")
    else:
        print("All bins filled")
        
    return data	
	
		
		  
	
	



if __name__ == "__main__": 
	
	n_shots = 2500
	k = 1/100
	speed_profile = "sinsquare" # "uniform" # "mostly_uniform"	# "stepped" # 
	variables = [2, 0.05]
	
	n_runs = 5
	
	b = [0]*n_runs
	b_count = [0]*n_runs
	b_axis = [0]*n_runs
	
	for i in range(n_runs):
		out_t, out_b = position(n_shots, speed_profile)
		out_I = laser_intensity(n_shots, k)
		
		out_s = signal(out_t, 1600, 900, 1) + signal(out_t, 1700, 1000, 0.3)
		
		out_sn = add_noise_to_signal(out_s, out_I)
		
		out_snm, out_c = add_phase_modulation(out_sn, phase_mod_profile = "pem")
		
		b[i], b_count[i], b_axis[i] = binning(out_snm, out_b, out_c, speed_profile)
		
		
	
	out_r = average_runs(b, b_count, b_axis, n_runs, 200)
	

	
#	 plt.figure()
#	 plt.plot(out_b[0])
#	 plt.plot(signal_with_noise)
#	 plt.plot(10*signal)
#	 plt.plot(out_x)
#	 plt.show()
		
	
	
	
#	 corr_I = M.correlation_fft(out_laser_intensity)
#	 
#	 A_start = [0.9,50,0.1,1000]
#	 
#	 t = numpy.arange(n_shots)
#	 
#	 t_short = t[:500]
#	 corr_I_short = corr_I[:500]
#	 
#	 A_out = M.fit(t_short, corr_I_short, E.double_exp, A_start)
#	 
#	 print(A_out)
#	 
#	 
#	 plt.figure()
#	 plt.plot(t, corr_I)
#	 plt.plot(t_short, E.double_exp(A_out, t_short))
#	 plt.show()












#def laser_intensity(n_shots, k, I0 = 0):
#	 """
#	 Calculates the noise per shot
#	 
#	 CHANGELOG:
#	 201201xx/RB: started function as separate script
#	 20120224/RB: integrated it into croc
#	 
#	 INPUT:
#	 - k: 1/correlation time, in shots
#	 - I0: start intensity (a bit of randomness is added)
#	 
#	 """
#	 
#	 I = numpy.zeros(n_shots)
#	 
#	 sigma = 2/numpy.sqrt(2*k)
#	 I[0] = I0 + 10 * numpy.random.randn(1) * sigma * k
#	 for i in range(n_shots-1):
#		 I[i+1] = I[i] * (1-k) + numpy.random.randn(1) * sigma * k
#	 
#	 return I
#
#def laser_intensity_2(n_shots, a, t1, b, t2, I0 = 0):
#	 """
#	 Calculates the noise per shot
#	 
#	 CHANGELOG:
#	 201201xx/RB: started function as separate script
#	 20120224/RB: integrated it into croc
#	 
#	 INPUT:
#	 - k: 1/correlation time, in shots
#	 - I0: start intensity (a bit of randomness is added)
#	 
#	 """
#	 
#	 I = numpy.zeros(n_shots)
#	 
#	 k1 = 1/t1
#	 k2 = 1/t2
#	 
#	 sig1 = 2/numpy.sqrt(2*k1)
#	 sig2 = 2/numpy.sqrt(2*k2)
#	 I[0] = I0 + 10 * a * numpy.random.randn(1) * sig1 * k1 + 10 * b * numpy.random.randn(1) * sig2 * k2 
#	 for i in range(n_shots-1):
#		 I[i+1] = I[i] * (1 - a*k1 - b*k2) + numpy.random.randn(1) * sig1 * k1 + numpy.random.randn(1) * sig2 * k2 
#	 
#	 return I











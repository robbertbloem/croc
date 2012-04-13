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




def shots_for_n_bins(n_bins, speed_profile = "mostly_uniform", variables = []):

	if speed_profile == "mostly_uniform":
		
		v_max = variables[0] #fs
		
		t_max = n_bins * hene_fringe #fs
		
		# calculate number shots accelerating/decelerating
		n_s_a = v_max / variables[2]
		n_s_d = v_max / variables[3]
		
		# calculate time moved (ie bins)
		n_t_a = n_s_a * v_max / 2.0
		n_t_d = n_s_d * v_max / 2.0
		
		# sum
		shots_sum = n_s_a + n_s_d
		t_sum = n_t_a + n_t_d
		
		# just accelerating gives to many bins, reduce max speed
		if t_sum >= t_max:
			v_max = numpy.sqrt((2 * t_max * variables[2] * variables[3])/(variables[2] + variables[3]))
			
			n_s_a = v_max / variables[2]
			n_s_d = v_max / variables[3]
			
			n_shots = n_s_a + n_s_d
			
		# we need some more bins, run at full speed
		else:
			
			t_at_vmax = t_max - t_sum
			n_s_vmax = t_at_vmax / v_max
	
			n_shots =  shots_sum + n_s_vmax
		
		return int(n_shots * 1.02)
	else:
		return False
			
				
			
			
			
			
			
		
	
		
	
	
	





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
#			print("oops, too short, reduce speed_max to:", speed_max, "fs/shot")
			
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
		print("    " + str(int(bin_array[-1] - last_bin)) + " bins extra")
	else:
		print("    " + str(int(last_bin - bin_array[-1])) + " bins missing")
	
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
				
	
	




if __name__ == "__main__": 

	n_shots = 8000
	speed_profile = "mostly_uniform"
	speed_variables = [0.45, 0.05, 0.0002, 0.0001]
	n_bins = 1000

	shots_for_n_bins(n_bins, speed_profile = "mostly_uniform", variables = speed_variables)



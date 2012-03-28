CROCODILE README 
A collection of code to process measurements.


0. DISCLAIMER:
This software comes without warranty. 


1. INSTALLATION/SETUP:
- make sure you have Numpy, Scipy, Matplotlib and ipython installed. This is done most conveniently using the "Enthought Python Distribution" (Google it). There is an academic license and versions for Windows, Mac and Linux. 
- copy everything to a convenient place
- add that place to the PYTHONPATH in for example .bash_profile: 
export PYTHONPATH=$HOME/Developer:$HOME/Developer/croc:$PYTHONPATH 
- run the following commands from ipython:
>> import croc
>> import croc.Tests.Tests
>> croc.Tests.Tests.PE1()
This should result in a 2D spectrum.


2. STRUCTURE:

The code is split in two parts. First, there is the code to calculate spectra. They use a common data class structure and some mathematical and plotting stuff. Second, there are some scripts to calculate stuff. Since it uses a lot of the mathematical and plotting stuff of the first part (but not the class-structure), I decided to include it here as well. 

The highest classes are in Resources/DataClasses.py. This file contains mess_data which contains basic data structure and some functions for writing/reading/printing the data. All classes are fairly abstract and the file shouldn't be changed.

The actual code to calculate spectra is contained in sub classes: Pe.py, Ftir.py. These contain code specific for those classes. 

In Resources/ the more general functions are collected. There are important diferences between Mathematics.py, Equations.py and Functions.py.
- Mathematics.py: contains Fourier Transform stuff, fitting stuff etc. 
- Equations.py: mathematical equations. They are used for fitting (and are formatted that the fitting procedure can use them) but can also be used for plotting. New equations can be added, but be careful when changing and/or removing. 
- Functions.py: functions called by the scripts. This is probably the only file where you should make changes.

Other files in Resources/ are. 
- Constants.py contains some constants
- Debug.py sets the debug_flag. Leave it at False for everyday use. It also sets the reload_flag. If you make changes to the code, set this to True.
- Plotting.py contains plotting functions. At the end of the day, these plotting functions are wrappers around Matplotlib functions.
- GVD_Materials.py contains data of different materials.
- IOMethods.py has methods to import data. They are derived from the DataClasses methods, but don't use the DataClasses.

The directory Tests contains some stuff for testing. In the file Tests there are several methods that will test a certain subject. 


3. USAGE:

See croc.Tests.Tests for several examples of how the routines can be used. This file is mainly for testing code and some of it is therefore slightly convoluted, but it should help you on the way. 

3.1 croc.DataClasses.mess_data

mess_data contains the default structure and is initialized when you initialize a particular class (photon echo, ftir etc). 

3.1.1 Naming conventions:
- measurements are the rephasing and non-rephasing diagrams for 2DIR. FTIR has 1 diagram, 3DIR 4. Each diagram is an independent measurement.
- dimensions are the number of axis. For a 2DIR measurement this is 3: t1 or w1, t2 and w3. Note that dimensions don't need to have the same unit.

- self.r[measurements] is the time domain. 
- self.f[measurements] is the fourier transformed spectrum for individual diagrams
- self.s is the purely absorptive spectrum in frequency domain. 
- self.b[measurements * chopper_states] (fast scanning only) are the bins. 

There are variables/arrays that give a description of this data. The start with the same letter.
- self.x_axis[dimensions]: the axis for x in all dimensions. For a 2DIR measurement this means .r_axis[0] contains all time steps of t1, self.r_axis[1] has the population time and self.r_axis[2] the frequencies of the detector. Note that the rephasing and non-rephasing diagram are assumed to be identical. If the number of steps or step size is different, it will return something unreliable.
- self.x_units[dimensions]: the units of the axes.
- self.x_resolution[dimensions]: the resolution of the axes.


3.1.2 Semi-protected names
Some names are semi-protected. For example, to write the phase, you will write
>> self.phase_degrees = 90
But you don't call the variable, you call a function that will write to self._phase_degrees and will also calculate the phase in radians and writes it to self._phase_rad. When you need the phase in radians 
>> self.phase_rad
>1.57
You can write directly to self._phase_degrees, but then the value in radians will not be set. 
It also contains some methods to save the data as a pickle and to print it nicely.


3.2 croc.Pe.pe

This is the general class for photon echo experiments. It contains some plotting functions.


3.2.1 croc.Pe.pe_exp

This is a subclass of croc.Pe.pe for experimental photon echo experiments. It should be used for stepped scan measurements. It really should have its own class, but that would break things.


3.2.2 croc.Pe.pefs

This is a subclass of croc.Pe.pe_exp for fast scanning. It contains methods to import the data, reconstruct the fringes and bin the data. After the data is binned, the spectrum can be calculated.

There are three ways to import data:
1. Call all the individual functions, described in 3.2.2.1. 
2. Call croc.Pe.pefs.add_data(), which does all the functions described in 3.2.2.1 automatically.
3. Call croc.Pe.import_FS(), which calls add_data() for a whole array of measurements and saving them.

I hope the hierarchy is clear: in normal circumstances you only need to do (3). For special circumstances you can do (2) and if you need something really custom do (1).

 

3.2.2.1 importing Fast Scanning data, or: croc.Pe.pefs.add_data()

The measurement produces 4 files: 2x rephasing, 2x non-rephasing. The function add_data() contains everything that is needed to import a single scan, ie those 4 files.

First, add_data() will check if a scan is already imported. If not, the four files are imported, one file at a time. The two control-fringes at the end of the file are returned as "fringes", the data as the variable "m", which has the shape of n_channels x n_shots. It is large and has to be processed first.

The function croc.Pe.pefs.reconstruct_counter will reproduce the fringe counting using self.x_channel and self.y_channel. Its output it "m_axis": the fringe for every shot, "counter": the last fringe and "correct_count": if beginning and end fringes are given (they are in "add_data") it will return whether the two counts are the same.

If the count is correct, the data will be binned into "self.b". The count for every bin is recorded in "self.b_count". At the moment the shape of "b" is 4 x channels x (self.n_fringes + self.extra_fringes).
- The 4 is for: rephasing diagram and pem (chopper) state low; rephasing and pem state high; non-rephasing and pem state low; non-rephasing and pem state high. If there are more chopper/pem states, this should be increased. The state of the PEM is read from "self.chopper_channel" in "m". (Note that the 4 here has nothing to do with the 4 files with measurements).
- The variable "self.n_fringes" is determined from the meta file or the data. "self.extra_fringes" is to account for overshooting. 

Finally "self.r" can be constructed. "r" is the time domain data (and will be Fourier Transformed to "self.s", the spectrum) and has the shape n_pixels x n_fringes. 
- First it will divide the bins by their count. If a count is zero, the result is zero. The result is "temp" (shape: 4 x (self.n_fringes + self.extra_fringes) x self.n_channels)
- Second it will select only the part we want: 4 x self.n_fringes x self.n_pixels. 
- It will make self.r_axis[0] out of self.b_axis times the HeNe-wavelength.
- It will calculate this:
    self.r[diagram] = -log_10 { 1 + 2 * (temp[diagram][pem_state:high] - temp[diagram][pem_state:low]) / self.reference }
- Note that construct_r can be run at any time. For large import-jobs it is usually better to run this function once at the end instead of hundreds of times during the importing. 


3.2.2.2 croc.Pe.import_FS()

import_FS is to streamline the importing of files. You feed it with two arrays: "mess_array" and "scan_array" (you also need to supply it with mess_date, to construct the directories where to find the data). It will import the files you want and saves them. 
- mess_array: an array that contains vitals for the scans: object-identifier (this needs to be unique), file base name, population time, time stamp. This needs to be in this order!
- scan_array: the different options are explained in the documentation of the function, but this will determine which files will be imported. Note that add_data is designed to not re-import scans. 

import_FS looks if there is already a pickle present and if so, imports it (see also 3.2.2.2.1 below). It will then run add_data(). For every 50 successful imports it will save a pickle. If it crashes you can run import_FS again (without the need to change mess_array, since it won't re-import scans). Finally it will save the pickle.


3.2.2.2.1 Regarding additions/deletions to mess_array:
Say you run import_FS with three objects: A, B, C first. The next time you run import_FS:
- with a changed scan_array: it will import the scans that were not imported yet.
- with object D added to mess_array: it will add this new object
- with object B removed from mess_array: it will not import object B, but it should not remove it from the pickle either. It is best to be conservative with this though. 





4. PYTHON PECULIARITIES:

Python is very flexible in the assignment of data types to variables. Contrary to C they don't have to be pre-declared. 
In C you would write:
    int var;
Now "var" is always an integer.
In Python you can write:
    var = 1
and "var" is an integer. When you write
    var = "a string"
"var" is a string. 
This has advantages and disadvantages. For example "base_filename" (declared in croc.DataClasses.mess_data) is usually a string. For some methods (notably croc.Ftir) we need more filenames and "base_filename" will become an array. The advantage is the flexibility, the disadvantage is that the methods need to be able to deal with this flexibility. 
Normally axes are an array with for example the times or frequencies. Python will not warn you though, when you assign an integer. When you want to calculate the something with the axes and it expects an array, it will give an error when it is presented with an integer. 
The variables declared in croc.DataClasses.mess_data are suggestions that you can decide to deviate from. However, the rest of the methods expect the default behavior and it is wise to stick to them as close as possible.




5. KNOWN ISSUES:
- -


6. CHANGELOG:
20110912/RB: started the readme
20120222/RB: made major changes in the organization of files
























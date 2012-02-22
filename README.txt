CROCODILE README 
A collection of code to process measurements.


0. DISCLAIMER:
This software comes without warranty. 


1. INSTALLATION/SETUP:
- make sure you have Numpy, Scipy, Matplotlib and ipython installed. This is done most conveniently using the "Enthought Python Distribution" (Google it). There is an academic license. 
- copy everything to a convenient place
- add that place to the PATH
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
























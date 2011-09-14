CROCODILE README 
A collection of code to process measurements.


0. DISCLAIMER:
This software comes without warranty. 


1. INSTALLATION/SETUP:
- make sure you have Numpy, Scipy, Matplotlib and ipython installed. This is done most conveniently using the "Enthought Python Distribution" (Google it). There is an academic license. 
- copy everything to a convenient place
- add that place to the PATH
- run the following commands from ipython:
    > import croc
    > import croc.Tests.Tests
    > croc.Tests.Tests.PE1()
This should result in a 2D spectrum.


2. STRUCTURE:

The highest classes are in DataClasses. This file contains mess_data which contains basic data structure and some functions for writing/reading/printing the data. All classes are fairly abstract and the file shouldn't be changed.

Some files contain functions. 
- Absorptive.py contains stuff related to Fourier Transform calculations. The name comes from the intention to write a general method to calculate the absorptive spectrum.
- Constants.py contains some constants
- Debug.py sets the debug_flag. Leave it at False for everyday use. It also sets the reload_flag. If you make changes to the code, set this to True.
- Plotting.py contains plotting functions. At the end of the day, these plotting functions are wrappers around Matplotlib functions.

Some files contain routines for specific situations:
- pe.py contains methods related to photon echo/four wave mixing/2DIR. 
    - pe_exp contains stuff to calculate a spectrum from experimental data. Some of the functions are very specific (like importing etc). 
    - pe_sub is for calculating and plotting subtractions of two spectra
- ftir is for calculating ftir spectra.

The directory Tests contains some stuff for testing. In the file Tests there are several methods that will test a certain subject. 


3. USAGE:

See croc.Tests.Tests for several examples of how the routines can be used. This file is mainly for testing code and some of it is therefore slightly convoluted, but it should help you on the way. 


3.1 croc.DataClasses.mess_data

mess_data contains the most default information. 






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
20110912 RB: started the readme
























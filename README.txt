CROCODILE README 
A collection of code to process measurements.


DISCLAIMER:
This software comes without warranty. 


INSTALLATION/SETUP:
- make sure you have Numpy, Scipy, Matplotlib and ipython installed. This is done most conveniently using the "Enthought Python Distribution" (Google it). There is an academic license. 
- copy everything to a convenient place
- add that place to the PATH
- run the following commands from ipython:
    > import croc
    > import croc.Tests.Tests
    > croc.Tests.Tests.PE1()
This should result in a 2D spectrum.


STRUCTURE:

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


USAGE:

See croc.Tests.Tests for several examples of how the routines can be used. This file is mainly for testing code and some of it is therefore slightly convoluted, but it should help you on the way. 


KNOWN ISSUES:
- -


CHANGELOG:
20110912 RB: started the readme
























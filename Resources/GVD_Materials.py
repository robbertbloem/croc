"""
This file contains the material properties used in GroupVelocityDispersion.py

To add a new material, make a new "if materialname == etc". Each material has two entries: 
- n: a numpy-array with the wavelenght in micron and the index of refraction.
- SellmeierCoefficients: a normal array with the Sellmeier coefficients. The equation looks like 
n^2(L) = A + (B_1 * L^2)/(L^2 - C_1) + (B_2 * L^2)/(L^2 - C_2) + (B_3 * L^2)/(L^2 - C_3), where L is the wavelength in micron.
The order of the coefficients is: B_1, C_1, B_2, C_2, B_3, C_3, A
In most cases A = 0. If B_3 and C_3 are not given, set B_3 to 0.
Note that some websites give the C-values as the square root. 
- either of them can be ignored by writing 'n = []'

SOURCES:
RI: http://refractiveindex.info -> WARNING: C coefficients need to be squared SOMETIMES!
MG: http://www.cvimellesgriot.com

"""



from __future__ import print_function
from __future__ import division

import numpy

def MaterialProperties(material):

# CaF2 ###################
    if material == 'caf2':
        # CaF2, MG
        n = numpy.array([
            [0.193, 1.501],
            [0.248, 1.468],
            [0.257, 1.465],
            [0.266, 1.462],
            [0.308, 1.453],
            [0.355, 1.446],
            [0.486, 1.437],
            [0.587, 1.433],
            [0.65, 1.432],
            [0.7, 1.431],
            [1.0, 1.428],
            [1.5, 1.426],
            [2.0, 1.423],
            [2.5, 1.421],
            [3.0, 1.417],
            [4.0, 1.409],
            [5.0, 1.398],
            [6.0, 1.385],
            [7.0, 1.369],
            [8.0, 1.349]
        ])
        
        # CaF2, MG
        SellmeierCoefficients = [0.5675888, 0.00252643, 0.4710914, 0.01007833, 3.8484723, 1200.5560, 1]
        
        return n, SellmeierCoefficients

# ZnSe ###################          
    elif material == 'znse':
        # ZnSe, MG
        n = numpy.array([
            [2.58, 2.440],
            [2.75, 2.439], 
            [3.00, 2.438], 
            [3.42, 2.436], 
            [3.50, 2.435],
            [4.36, 2.432], 
            [5.00, 2.430], 
            [6.00, 2.426], 
            [6.24, 2.425], 
            [7.50, 2.420],
            [8.66, 2.414], 
            [9.50, 2.410], 
            [9.72, 2.409]
        ])
        
        # ZnSe, RI
        SellmeierCoefficients = [4.2980149, 0.1920630**2, 0.62776557, 0.37878260**2, 2.8955633, 46.994595**2, 1]
    
        return n, SellmeierCoefficients

# Fused Silica ###################    
    elif material == 'fusedsilica':
        
        n = []
        # Fused Silica, MG
        SellmeierCoefficients = [0.6961663, 0.00467914826, 0.4079426, 0.0135120631, 0.897479400, 97.9340025, 1]
        
        return n, SellmeierCoefficients

# Ge ###################          
    elif material == 'ge':
        # Ge
        n = []
        # Ge, RI
        SellmeierCoefficients = [6.72880, 0.44105, 0.21307, 3870.1, 0, 1, 9.28156]
    
        return n, SellmeierCoefficients


# BaF2 ###################          
    elif material == 'baf2':
        # BaF2
        n = []
        # BaF2, RI
        SellmeierCoefficients = [0.643356, 0.057789**2, 0.506762, 0.10968**2, 3.8261, 46.3864**2, 1]
    
        return n, SellmeierCoefficients


# MgF2 ###################          
    elif material == 'mgf2':
        # MgF2
        n = []
    
        # MgF2, RI
        SellmeierCoefficients = [0.48755108, 0.04338408**2, 0.39875031, 0.09461442**2, 2.3120353, 23.793604**2, 1]
    
        return n, SellmeierCoefficients

    
# do not add stuff after this point ########
    else:
        n = []
        SellmeierCoefficients = []
        return n, SellmeierCoefficients

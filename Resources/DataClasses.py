"""
dataclasses.py

DESCRIPTION
    This file contains all the high-level stuff for classes


CHANGELOG
    RB 20091214 - first draft.
    RB 20110908 - combined some stuff together

"""

from __future__ import print_function
from __future__ import division

import numpy
import pylab

import time
import os.path
import shelve
import sys


##############
# CLASSTOOLS #
##############

class ClassTools(object):
    """
    A way to print the whole class in one go.
    It prints the key and the value.
    """
    def gatherAttrs(self):
        attrs=[]
        for key in sorted(self.__dict__):
            attrs.append("\t%20s  =  %s\n" % (format_key(key), format_print(getattr(self, key))))
        return " ".join(attrs)

    def __str__(self):
        return "[%s:\n %s]" % (self.__class__.__name__, self.gatherAttrs())
        
    
        


##############
# MESS CLASS #
##############

class mess_data(ClassTools):
    """
    This class stores all the data. 
    Most of the variables are lists which point to ndarrays with the real data.
    """
    
    def __init__(self, objectname, dimensions, measurements):
        """
        croc.DataClasses.messdata
        
        INPUT:
        - objectname: the name
        - dimensions: the number of axes. Linear/2D/3D = 1/2/3. If something is measured in frequency and time (certain pump-probe) the dimension is also 2.
        - measurements: number of diagrams. Is 1 for everything except 2D-PE (=2) or 3D (=4?)
        
        
        """
    
        self.objectname = objectname
        
        # file stuff
        self.path = ""
        self.base_filename = ""
        self.time_stamp = ""
        self.date = ""
        
        # organizational stuff
        self.data_type_version = ""     # for different versions of data
        self.mess_type = ""             # "sim" or "exp" for 2dir
        self.dimensions = dimensions    # t1, t2, t3 etc. so 2D -> 3 dimensions
        self.measurements = measurements        # number of diagrams or measurements etc

        # data
        self.r = [0] * measurements           # r is a collection of measurements
        self.r_domain = [0] * dimensions  # r_domain about one response function
        self.r_axis = [0] * dimensions    # r_axis are the times/frequencies

        self.r_correction = [0] * dimensions  # correction for spectrom inaccur.
        self.r_correction_applied = [0] * dimensions
        
        self.r_noise = [0] * measurements
        
        self.r_units = [""] * measurements        # the units
        self.r_resolution = [0] * measurements    # the resolution
        
        # fourier transformed data/processing
        self.f = [0] * measurements         # the fourier transformed but not yet phased data
        
        self._zeropad_to = None         # the amount of samples for zeropadding (WARNING: this is different from MATLAB), -1 indicates no zeropadding
        self._zeropad_by = 1.0          # how many times it should be zeropadded

        # spectra
        self.s = [0]                    # s is the spectrum
        self.s_domain = [0]*dimensions  # s_domain about one response function
        self.s_axis = [0]*dimensions    # s_axis are the times/frequencies
        
        self.s_units = [""] * dimensions        # the units
        self.s_resolution = [0] * dimensions    # the resolution
        
        # other experimental stuff
        self._phase_degrees = False         
        self._phase_rad = False
        self.undersampling = False
        self._comment = ""
        
        self.n_shots = 0
        self.n_steps = 0
        self.n_scans = 0
        
        self.debug = False

    # comments
    @property
    def comment(self):  
        return self._comment
    @comment.setter
    def comment(self, text):
        self._comment = self._comment + time.strftime("%d/%m/%Y %H:%M:%S: ", 
            time.localtime()) + text + "\n"
     
    # phase   
    @property
    def phase_degrees(self):
        return self._phase_degrees
    @phase_degrees.setter   
    def phase_degrees(self, phase):
        self._phase_degrees = phase
        self._phase_rad = phase*numpy.pi/180
    
    @property
    def phase_rad(self):
        return self._phase_rad
    @phase_rad.setter
    def phase_rad(self, phase):
        self._phase_rad = phase
        self._phase_degrees = phase * 180/numpy.pi
    
    # zeropadding
    @property
    def zeropad_to(self):
        return self._zeropad_to
    @zeropad_to.setter
    def zeropad_to(self, zpt):
        self._zeropad_to = int(zpt)
        self._zeropad_by = zpt / numpy.shape(self.r[0])[0]

    @property
    def zeropad_by(self):
        return self._zeropad_by
    @zeropad_by.setter
    def zeropad_by(self, zp_by):
        #print("ADVISE (croc.DataClasses.mess_data.zeropad_by.setter): The variable zeropad_by will actually set the variable zeropad_to, which is an integer. Then zeropad_by will be recalculated using that.\n")
        self.zeropad_to = int(zp_by * numpy.shape(self.r[0])[0])
        #self._zeropad_by = zp_by 
       





####################
# SHELVE FUNCTIONS #
####################

def make_db(array_of_class_instances, path_and_filename, use_shelve = False, flag_debug = False, flag_overwrite = False):
    """
    Makes a database and writes all values.
    The input should be an array with class instances, not a class instance itself! If the database already exists, it will update the values. Make sure that everything stored in the database has the same class.
    
    CHANGELOG:
    20120302 RB: tried to implement the cPickle instead of shelve (which uses pickle, which should be slower than cPickle). However, there was no notable increase in speed and it was abandoned, because it would cause confusion.
    
    """
    
    if path_and_filename[-7:] != ".pickle":
        path_and_filename += ".pickle"
    
    if flag_overwrite:
    	print("make_db: overwrite flag is True")
        flag = "n"
    else:
        flag = "c"
    
    print(path_and_filename)    
    
    if flag_debug:
        print("Saving using shelve")

    db = shelve.open(path_and_filename, flag = flag)
    
    for object in array_of_class_instances:
        db[object.objectname] = object
    
    db.close()



def import_db(path_and_filename, print_keys = False):
    """
    Imports a database. 
    The function checks for the existence of the database. It returns "False" 
        if the file doesn't exist. Otherwise, it will return an array with
        class instances.
    """

    if path_and_filename[-7:] != ".pickle":
        path_and_filename += ".pickle"
    
    
    if os.path.isfile(path_and_filename) == True:
            
        db=shelve.open(path_and_filename)
        
        array_of_class_instances = []
        
        for key in db:
            if print_keys:
                print(key)
            array_of_class_instances.append(db[key])
        
        db.close()
        
        return array_of_class_instances

    
    else:
        print("classtools.import_db: The file doesn't exist!")
        return False






####################
# HELPER FUNCTIONS #
####################

def format_print(var):
    """
    format_print is a helper function for the gatherAttrs function. 
    There are a few situations:
        1) var is not a list or an ndarray, it will print the value. This include tuples
        2) var is an ndarray, the shape will be printed
        3) var is a time. It will return a readable string with the time.
        3) the var is a list, it will do recursion to print either 1 or 2
    Examples:
        42          => 42
        "car"       => "car"
        [1,2]       => [1,2]
        ndarray     => shape
        [1,ndarray] => [1, shape]
    """
    # list
    if type(var) == list:
        typ = range(len(var))       
        for i in range(0, len(var)):
            typ[i] = (format_print(var[i]))
        return typ
    # ndarray
    elif type(var) == numpy.ndarray:
        a = numpy.shape(var)
        if len(a) == 1: 
            return str(a[0]) + " x 1"
        elif len(a) == 2:
            return str(a[0]) + " x " + str(a[1])
        elif len(a) == 3:
            return str(a[0]) + " x " + str(a[1]) + " x " + str(a[2])

        else: 
            return str(a[0]) + " x " + str(a[1]) + " x " + str(a[2]) + " x ..."
    # time
    elif type(var) == time.struct_time: 
        var = time.strftime("%a, %d %b %Y %H:%M:%S", var)
        return var
    elif type(var) == float:
        return round(var, 2)
    elif type(var) == numpy.float64:
        return round(var, 2)
    # the rest
    else:
        return var

def format_key(key):
    """
    Strips keys from _. These keys are semi-protected and should be run through the getter and setter methods.
    """
    if key[0] == "_":
        key = key[1:]
    else:
        pass
    
    return key
    
    








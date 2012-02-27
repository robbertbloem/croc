"""
IOMethods is for importing/exporting of data outside the DataClass structure.
"""

from __future__ import print_function
from __future__ import division

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import croc
import croc.Pe
from croc.Resources.DataClasses import mess_data

def import_data_FS(path_and_filename, n_shots = 30000, n_channels = 37):
    """
    This method is a derivative of croc.Pe.PeFS.import_raw_data, but without the reliance on the class structure.
    
    INPUT:
    - path_and_filename (string): where the file can be found
    - n_shots (int): number of shots
    - n_channels (int): number of channels
    
    OUTPUT:
    - m (2d ndarray): array with (channels x shots)
    - fringes (array with two elements): the begin and end fringe, as appended to the data.
    
    CHANGELOG:
    - 201110xx RB: wrote function
    - 201202xx RB: rewrote the function for wider purpose, moved it to IOMethods
    
    """
    try:
        data = numpy.fromfile(path_and_filename)
        
        # remove the two fringes at the end
        fringes = [data[-2], data[-1]]
        data = data[:-2]
        
        # construct m
        m = numpy.zeros((n_channels, n_shots), dtype = "cfloat")
        
        # order the data in a 2d array
        for i in range(n_shots):
            for j in range(n_channels):
                m[j, i] = data[j + i * n_channels] 
        
        return m, fringes
    except IOError:
        print("ERROR (croc.Resources.IOMethods.import_data_FS): Unable to import data from file " + path_and_filename)
        raise
        return 0, 0


def import_data_correlation(path, mess_array, mess_i, scan_array, scan_j, mess_date, sort = "fft"):
    
    path_and_filename = path + mess_array[mess_i] + scan_array[scan_j] + "_corr_" + sort + ".bin"
    
    data = numpy.fromfile(path_and_filename)
    
    return data


def import_data(mess_date, import_mess, import_from, import_to, mess_array, 
        data_dir = "", 
        anal_dir = "",
        pickle_name = "",
        flag_calculate_noise = False,
        flag_no_pickle = False,
        flag_overwrite_pickle = False
    ):
    """
    croc.Resources.IOMethods.import_data
    
    Imports data and saves it into a pickle. The method will import several scans from a measurement. This works best when you have fewer measurements with more scans. 
    """
    if import_from == 0 or import_to == 0:
        print("No import required...")
        return 0
    else:
    
        # first check if mess_i actually exists
        try:
            mess_array[import_mess]
            
            if anal_dir == "":
                anal_dir = os.getcwd() + "/"
            
            if data_dir == "":
                # the 'root' is removes the '/analysis/20111111/'
                data_dir = os.getcwd()[:-17] + "data/" + str(mess_date) + "/"
                
            # default name of the pickle
            # use the _fs postfix to differentiate it from other pickles
            if pickle_name == "":
                pickle_name = str(mess_date) + "_fs.pickle"

            # first, check if there is a pickle
            if flag_overwrite_pickle == False and croc.Pe.check_pickle_exists(pickle_name): 
                # found a pickle, now import it
                print("Found pickle")
                mess = croc.Resources.DataClasses.import_db(pickle_name)
            else:
                # there is no pickle, so make a new a new data structure
                print("No pickle found")
                mess = [0]
                mess[0] = croc.Pe.pefs(mess_array[0][0], mess_array[0][1], mess_array[0][2], mess_array[0][3])
                mess[0].path = data_dir + mess[0].path
            
            # see if we have to extend mess to fit with mess_array
            if len(mess) < len(mess_array):
                for i in range(len(mess_array)):
                    try:
                        # this works if mess[i] exists
                        mess[i].objectname
                    except IndexError:
                        # it fails if it does not exists, so make a new one
                        mess.append(croc.Pe.pefs(mess_array[i][0], mess_array[i][1], mess_array[i][2], mess_array[i][3]))    
                        mess[-1].path = data_dir + mess[-1].path
            
                        
            # pickle can confuse the order of measurements
            # use the unique object names to find the correct one
            for i in range(len(mess)):
                if mess[i].objectname == mess_array[import_mess][0]:
                    mess_i = i
                
            # construct the import range
            import_range = range(import_from, import_to + 1)
            
            flag_change = False
            
            # import the data
            for i in import_range:
                print("Importing object: " + mess[mess_i].objectname + ", scan:", str(i))
                result = mess[mess_i].add_data(scan = i, flag_construct_r = False, flag_calculate_noise = flag_calculate_noise)
                
                if result == True:  
                    flag_change = True
            
            if flag_no_pickle == False:
                if flag_change:
                    print("Updating pickle...")
                    croc.Resources.DataClasses.make_db(mess, pickle_name)
                else:
                    print("No need to update pickle...")
            else:
                print("flag_no_pickle == True")
        
        except IndexError:
            # mess_i does not exist
            print("ERROR (script_import.py): mess_i is outside of the range of mess_array")



















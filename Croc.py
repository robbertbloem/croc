"""
STANDARD SCRIPT TO IMPORT DATA

This file automates the import of data.



"""


from __future__ import print_function
from __future__ import division

import numpy
import matplotlib 
import matplotlib.pyplot as plt

import croc
import croc.DataClasses
import croc.Pe


reload(croc)
reload(croc.DataClasses)
reload(croc.Pe)




def import_data(mess_date, import_mess, import_from, import_to, mess_array):
    
    # first check if mess_i actually exists
    try:
        mess_array[import_mess]
        
        # default name of the pickle
        # use the _fs postfix to differentiate it from other pickles
        pickle_name = str(mess_date) + "_fs.pickle"
        
        # first, check if there is a pickle
        if croc.Pe.check_pickle_exists(pickle_name):
            # found a pickle, now import it
            print("Found pickle")
            mess = croc.DataClasses.import_db(pickle_name)
        else:
            # there is no pickle, so make a new a new data structure
            print("No pickle found")
            mess = [0]
            mess[0] = croc.Pe.pefs(mess_array[0][0], mess_array[0][1], mess_array[0][2], mess_array[0][3])
        
        # see if we have to extend mess to fit with mess_array
        if len(mess) < len(mess_array):
            for i in range(len(mess_array)):
                try:
                    # this works if mess[i] exists
                    mess[i].objectname
                except IndexError:
                    # it does not work if it does not exists
                    mess.append(croc.Pe.pefs(mess_array[i][0], mess_array[i][1], mess_array[i][2], mess_array[i][3]))
                    
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
            result = mess[mess_i].add_data(scan = i, flag_construct_r = False, flag_calculate_noise = False)
            
            if result == True:  
                flag_change = True
        
        if flag_change:
            print("Updating pickle...")
            croc.DataClasses.make_db(mess, pickle_name)
        else:
            print("No need to update pickle...")
    
    except IndexError:
        # mess_i does not exist
        print("ERROR (script_import.py): mess_i is outside of the range of mess_array")
    
    
    
    
    
    




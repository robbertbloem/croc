"""
croc.Debug

- debug_flag: will print some information during the processing of data. 

- reload_flag: a normal 'import' a module will not be re-compiled if it is changed. Set this flag to True if you want to make changes in modules. 

"""

import os

debug_flag = False

reload_flag = True

# to make distinction based on where it is run from
global FlagRunningOn

if os.uname()[1] == "pcipdc.uzh.ch":
    # linux server, special path, no plotting available
    FlagRunningOn = "server"
elif os.uname()[1] == "rbmbp.local":
    FlagRunningOn = "robbert"
else:
    FlagRunningOn = "generic" 
    
def printError(string, location = ""):
    if location == "":
        print("\033[1;31mERROR: " + string + "\033[1;m")
    else:
        print("\033[1;31mERROR (" + location + "): " + string + "\033[1;m")

def printWarning(string, location = ""):
    if location == "":
        print("\033[1;35mWARNING: " + string + "\033[1;m")
    else:
        print("\033[1;35mWARNING (" + location + "): " + string + "\033[1;m")

def printGreen(string):
    print("\033[1;32m" + string + "\033[1;m")

def printBlue(string):
    print("\033[1;34m" + string + "\033[1;m")
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

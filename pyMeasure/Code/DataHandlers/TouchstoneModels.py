#-----------------------------------------------------------------------------
# Name:        TouchstoneModels
# Purpose:     To store and manipulate touchstone files
# Author:      Aric Sanders
# Created:     3/7/2016
# License:     MIT License
#-----------------------------------------------------------------------------
""" A module dedicated to the manipulation and storage of touchstone files, such as
 .s2p or .ts files"""

#-----------------------------------------------------------------------------
# Standard Imports

#-----------------------------------------------------------------------------
# Third Party Imports
try:
    from pyMeasure.Code.Utils.Alias import *
    METHOD_ALIASES=1
except:
    print("The module pyMeasure.Code.Utils.Alias was not found")
    METHOD_ALIASES=0
    pass
try:
    from pyMeasure.Code.DataHandlers.GeneralModels import *
except:
    print("The module pyMeasure.Code.DataHandlers.GeneralModels was not found,"
          "please put it on the python path")
    raise ImportError
try:
    import numpy as np
except:
    print("The module numpy was not found,"
          "please put it on the python path")
    raise ImportError
#-----------------------------------------------------------------------------
# Module Constants
TOUCHSTONE_KEYWORDS=["Version","Number of Ports","Two-Port Order","Number of Frequencies",
                     "Number of Noise Frequencies","Reference","Matrix Format","Mixed-Mode Order",
                     "Network Data","Noise Data","End"]

#-----------------------------------------------------------------------------
# Module Functions

#-----------------------------------------------------------------------------
# Module Classes

#-----------------------------------------------------------------------------
# Module Scripts

#-----------------------------------------------------------------------------
# Module Runner
if __name__ == '__main__':
    pass
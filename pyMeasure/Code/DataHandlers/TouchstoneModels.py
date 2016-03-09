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
class s2pv1(AsciiDataTable):
    """A container for s2p files"""
    def __init__(self,file_path=None,**options):
        """Initialization of the s2p class for version 1 files,
        if a file path is specified opens the file. If the file path is not
        specified then data can be added through the s2pv1.data. It automatically changes whitespace to a single space
        for consistency.
        """
        defaults={"data_delimiter":" ",
                  "column_names_delimiter":None,
                  "specific_descriptor":'Data',
                  "general_descriptor":'Table',
                  "directory":None,
                  "extension":'s2p',
                  "comment_begin":"!",
                  "comment_end":"\n",
                  "inline_comment_begin":None,
                  "inline_comment_end":None,
                  "block_comment_begin":None,
                  "block_comment_end":None,
                  "footer_begin_line":None,
                  }
        self.options={}
        for key,value in defaults.iteritems():
            self.options[key]=value
        for key,value in options.iteritems():
            self.options[key]=value
        self.elements=['header','column_names','data','footer','inline_comments']
        AsciiDataTable.__init__(self,file_path,**options)
#-----------------------------------------------------------------------------
# Module Scripts

#-----------------------------------------------------------------------------
# Module Runner
if __name__ == '__main__':
    pass
#-----------------------------------------------------------------------------
# Name:        TouchstoneModels
# Purpose:     To store and manipulate touchstone files
# Author:      Aric Sanders
# Created:     3/7/2016
# License:     MIT License
#-----------------------------------------------------------------------------
""" A module dedicated to the manipulation and storage of touchstone files, such as
 .s2p or .ts files. Touchstone files are normally s-parameter data for multiport VNA's"""

#-----------------------------------------------------------------------------
# Standard Imports
import os
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
OPTION_LINE_PATTERN="#[\s]+(?P<Frequency_Units>\w+)[\s]+(?P<Parameter>\w+)[\s]+(?P<Format>\w+)[\s]+R[\s]+"\
        "(?P<Reference_Resistance>[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)"
COMMENT_PATTERN="!(?P<Comment>.+)\n"
FREQUENCY_UNITS=["Hz","kHz","MHz","GHz"]
PARAMETERS=["S","Y","Z","G","H"]
FORMATS=["RI","DB","MA"]
S2P_MA_COLUMN_NAMES=["Frequency","magS11","argS11","magS21","argS21","magS12","argS12","magS22","argS22"]
S2P_DB_COLUMN_NAMES=["Frequency","dbS11","argS11","dbS21","argS21","dbS12","argS12","dbS22","argS22"]
S2P_RI_COLUMN_NAMES=["Frequency","reS11","imS11","reS21","imS21","reS12","imS12","reS22","imS22"]
S2P_NOISE_PARAMETER_COLUMN_NAMES=["Frequency","NFMin","mag","arg","Rn"]

#-----------------------------------------------------------------------------
# Module Functions
def make_row_match_string(column_names,delimiter_pattern='[\s]+'):
    """Returns a regex string for matching a row given a set of column names assuming the row delimiter
    is a set of white spaces (default) or a specified delimiter pattern.
    Designed to create a regex for the input of numbers"""
    row_regex_string="[\s|.]+"
    for index,name in enumerate(column_names):
        if index == len(column_names)-1:
            row_regex_string=row_regex_string+'(?P<%s>{0})'%name
        else:
            row_regex_string=row_regex_string+'(?P<%s>{0})'%name+delimiter_pattern
    row_regex_string=row_regex_string.format(NUMBER_MATCH_STRING)
    return row_regex_string
#-----------------------------------------------------------------------------
# Module Classes
class S2PV1():
    """A container for s2p version 1 files. Files consist of comments, option line, S parameter data
     and noise parameter data"""
    def __init__(self,file_path=None,**options):
        """Initialization of the s2p class for version 1 files,
        if a file path is specified, it opens and parses the file. If the file path is not
        specified then data can be added through the s2pv1.sparameter_data. A reference to the version 1 touchstone
        format may be found at
        http://cp.literature.agilent.com/litweb/pdf/genesys200801/sim/linear_sim/sparams/touchstone_file_format.htm
        """
        defaults={"data_delimiter":"\t",
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
        self.noiseparameter_row_pattern=make_row_match_string(S2P_NOISE_PARAMETER_COLUMN_NAMES)
        self.noiseparameter_column_names=S2P_NOISE_PARAMETER_COLUMN_NAMES
        if file_path is not None:
            self.path=file_path
        self.__read_and_fix__()


    def __read_and_fix__(self):
        """Reads a s2pv1 file and fixes any problems with delimiters. Since s2p files may use
        any white space or combination of white space as data delimiters it reads the data and creates
        a uniform delimter. This means a file saved with save() will not be the same as the original if the
        whitespace is not uniform. """
        default_option_line="# GHz S RI R 50"
        in_file=open(self.path,'r')
        # to keep the logic clean we will repeatedly cycle through self.lines
        # but in theory we could do it all on the line input stage
        self.lines=[]
        for line in in_file:
            self.lines.append(line)
        # now we need to collect and extract all the inline comments
        # There should be two types ones that have char position EOL, -1 or 0
        self.comments=collect_inline_comments(self.lines,begin_token="!",end_token="\n")
        # change all of them to be 0 or -1
        if self.comments is None:
            pass
        else:
            for index,comment in enumerate(self.comments):
                if comment[2]>1:
                    self.comments[index][2]=-1
                else:
                    self.comments[index][2]=0
        # Match the option line and set the attribute associated with them
        match=re.match(OPTION_LINE_PATTERN,default_option_line)
        self.option_line=default_option_line
        for line in self.lines:
            if re.match(OPTION_LINE_PATTERN,line):
                self.option_line=line
                match=re.match(OPTION_LINE_PATTERN,line)
        for key,value in match.groupdict().iteritems():
                    self.__dict__[key.lower()]=value
        if re.match('db',self.format,re.IGNORECASE):
            self.column_names=S2P_DB_COLUMN_NAMES
            self.row_pattern=make_row_match_string(S2P_DB_COLUMN_NAMES)
        elif re.match('ma',self.format,re.IGNORECASE):
            self.column_names=S2P_MA_COLUMN_NAMES
            self.row_pattern=make_row_match_string(S2P_MA_COLUMN_NAMES)
        elif re.match('ri',self.format,re.IGNORECASE):
            self.column_names=S2P_RI_COLUMN_NAMES
            self.row_pattern=make_row_match_string(S2P_RI_COLUMN_NAMES)
        # remove the comments
        stripped_lines=strip_inline_comments(self.lines,begin_token="!",end_token="\n")
        #print stripped_lines
        self.sparameter_data=[]
        self.noiseparameter_data=[]
        for line in stripped_lines:
            if re.search(self.row_pattern,line):
                #print re.search(self.row_pattern,line).groupdict()
                row_data=re.search(self.row_pattern,line).groupdict()
                self.add_sparameter_row(row_data=row_data)
            elif re.match(self.noiseparameter_row_pattern,line):
                row_data=re.match(self.noiseparameter_row_pattern,line).groupdict()
                self.add_noiseparameter_row(row_data=row_data)
        #print self.sparameter_data
        #print self.noiseparameter_data



        # parse line by line and put anything that matches regex in the right place

    def add_sparameter_row(self,row_data):
        """Adds data to the sparameter attribute, which is a list of s-parameters. The
        data can be a list of 9 real numbers, 1 real number and 4 complex number
         or dictionary with appropriate column names, note column names are not case sensitive"""
        if type(row_data) is ListType:
            if len(row_data) == 9:
                    self.sparameter_data.append(row_data)
            else:
                print("Could not add row, the data was a list of the wrong dimension, if you desire to add multiple"
                      "rows use add_sparameter_rows")
                return
        if type(row_data) is DictionaryType:
            new_row=[]
            for column_name in self.column_names:
                #print row_data
                new_row.append(float(row_data[column_name]))
            self.sparameter_data.append(new_row)

    def add_noiseparameter_row(self,row_data):
        """Adds data to the noiseparameter_data attribute, which is a list of noise parameters. The
        data can be a list of 5 real numbers dictionary with appropriate column names,
        note column names are not case sensitive"""
        if type(row_data) is ListType:
            if len(row_data) == 5:
                    self.noiseparameter_data.append(row_data)
            else:
                print("Could not add row, the data was a list of the wrong dimension, if you desire to add multiple"
                      "rows use add_sparameter_rows")
                return
        if type(row_data) is DictionaryType:
            new_row=[]
            for column_name in self.noiseparameter_column_names:
                new_row.append(float(row_data[column_name]))
            self.noiseparameter_data.append(new_row)



    def change_frequency_units(self,new_frequency_units=None):
        """Changes the frequency units from the current to new_frequency_units. Frequency Units must be one
        of the following: 'Hz','kHz','MHz', or 'GHz'. """
        old_units=self.frequency_units
        old_prefix=old_units.replace('Hz','')
        new_prefix=new_frequency_units.replace('Hz','')
        self.change_unit_prefix('Frequency',old_prefix=old_prefix,new_prefix=new_prefix)
        self.frequency_units=new_frequency_units


    def change_data_format(self,new_format=None):
        """Changes the data format to new_format. Format must be one of the following: 'DB','MA','RI'
        standing for Decibel-Angle, Magnitude-Angle or Real-Imaginary as per the touchstone specification
        all angles are in degrees."""
        pass

    def show(self):
        """Shows the touchstone file"""
        pass

#-----------------------------------------------------------------------------
# Module Scripts
def test_option_string():
    """Tests the regex for extracting option string values"""
    match=re.search(OPTION_LINE_PATTERN,"# GHz S RI R 50")
    print match.groupdict()
    print match.groupdict()["Format"] in FORMATS

def test_s2pv1(file_path="thru.s2p"):
    """Tests the s2pv1 class"""
    os.chdir(TESTS_DIRECTORY)
    new_table=S2PV1(file_path)
    print("The Table as read in with line numbers is")
    for index,line in enumerate(new_table.lines):
        print("{0} {1}".format(index,line))
    print("-"*80)
    print("The attribute {0} is {1}".format('sparameter_data',str(new_table.sparameter_data)))
    print("-"*80)
    print("The attribute {0} is {1}".format('noiseparameter_data',str(new_table.noiseparameter_data)))
    print("-"*80)
    print("The attribute {0} is {1}".format('comments',str(new_table.comments)))
    print("-"*80)
    print("The attribute {0} is {1}".format('option_line',str(new_table.option_line)))
    print("-"*80)
    print("The attribute {0} is {1}".format('format',str(new_table.format)))
    print("-"*80)
    print("The attribute {0} is {1}".format('frequncy_units',str(new_table.frequency_units)))
#-----------------------------------------------------------------------------
# Module Runner
if __name__ == '__main__':
    #test_option_string()
    #test_s2pv1()
    test_s2pv1('TwoPortTouchstoneTestFile.s2p')
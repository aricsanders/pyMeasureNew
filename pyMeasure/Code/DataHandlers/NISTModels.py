#-----------------------------------------------------------------------------
# Name:        NISTModels
# Purpose:    To handle data generated at NIST Boulder
# Author:      Aric Sanders
# Created:     2/22/2016
# License:     MIT License
#-----------------------------------------------------------------------------
""" NISTModels is a module to handle data types found at NIST in Boulder, CO """

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
    raise
#-----------------------------------------------------------------------------
# Module Constants

#-----------------------------------------------------------------------------
# Module Functions
def calrep_to_benchmark(file_path):
    """Creates a benchmark list given a path to a calrep file, assumes column names are 2 lines after
    the occurrence of the last /"""
    in_file=open(file_path,'r')
    lines=[]
    for line in in_file:
        lines.append(line)
    block_end=re.compile('/')
    for index,line in enumerate(lines):
        if re.match(block_end,line):
            last_block_comment_line=index
    header=lines[0:last_block_comment_line+1]
    columns_line=last_block_comment_line+2
    column_names=lines[columns_line].split(' ')
    data=lines[columns_line+1:None]
    return [header,column_names,data]
#-----------------------------------------------------------------------------
# Module Classes
class OnePortModel(AsciiDataTable):
    def __init__(self,file_path,**options):
        "Intializes the CalrepModel Class"
        if file_path is not None:
            self.path=file_path

        # This is a general pattern for adding a lot of options
        defaults={"data_delimiter":None,
                  "column_names_delimiter":None,
                  "specific_descriptor":'Data',
                  "general_descriptor":'Table',
                  "directory":None,
                  "extension":'txt',
                  "comment_begin":None,
                  "comment_end":None,
                  "inline_comment_begin":None,
                  "inline_comment_end":None,
                  "block_comment_begin":None,
                  "block_comment_end":None,
                  "footer_begin_line":None,
                  "footer_end_line":None,
                  "header_begin_line":None,
                  "header_end_line":None,
                  "column_names_begin_line":None,
                  "column_names_end_line":None,
                  "data_begin_line":None,
                  "data_end_line":None,
                  "footer_begin_token":None,
                  "footer_end_token":None,
                  "header_begin_token":None,
                  "header_end_token":None,
                  "column_names_begin_token":None,
                  "column_names_end_token":None,
                  "data_begin_token":None,
                  "data_end_token":None,
                  "metadata_delimiter":None,
                  "header_line_types":None,
                  "column_types":None,
                  "column_description":None,
                  "footer_line_types":None,
                  "header":None,
                  "column_names":None,
                  "data":None,
                  "footer":None,
                  "inline_comments":None,
                  "row_formatter_string":None,
                  "empty_value":None,
                  "escape_character":None,
                  "data_table_element_separator":'\n',
                  "treat_header_as_comment":None,
                  "treat_footer_as_comment":None
                  }
        self.options={}
        for key,value in defaults.iteritems():
            self.options[key]=value
        for key,value in options.iteritems():
            self.options[key]=value
        # Define Method Aliases if they are available
        if METHOD_ALIASES:
            for command in alias(self):
                exec(command)


class SwitchTermsFR():
    pass
class SwitchTermsPort()
    pass
class NoiseCalRaw():
    pass
class ReverbChamber():
    pass
class RobotData():
    pass

#-----------------------------------------------------------------------------
# Module Scripts

#-----------------------------------------------------------------------------
# Module Runner
if __name__ == '__main__':
    pass
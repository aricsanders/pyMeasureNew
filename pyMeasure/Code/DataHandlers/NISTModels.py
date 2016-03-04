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
    raise ImportError
try:
    import numpy as np
except:
    print("The module numpy was not found,"
          "please put it on the python path")
    raise ImportError
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
        "Intializes the OnePortModel Class, it is assumed that the file is of the .asc or table type"
        # This is a general pattern for adding a lot of options
        defaults={"data_delimiter":",",
                  "column_names_delimiter":",",
                  "specific_descriptor":'One_Port',
                  "general_descriptor":'Sparameter',
                  "extension":'txt',
                  "comment_begin":"#",
                  "comment_end":"\n",
                  "column_types":['float' for i in range(11)],
                  "column_description":None,
                  "header":None,
                  "column_names":["Frequency","|Gamma|","uGb","uGa","uGd","uGg","Phase",
                                  "uPhb","uPha","uPhd","uPhg"],
                  "column_names_end_token":"\n",
                  "data":None,
                  "row_formatter_string":None,
                  "data_table_element_separator":None,
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

        if file_path is not None:
            self.path=file_path
            self.__read_and_fix__()

        if os.path.dirname(file_path) is "":
            self.options["directory"]=os.getcwd()
        else:
            self.options["directory"]=os.path.dirname(file_path)
        #build the row_formatting string, the original files have 4 decimals of precision for freq/gamma and 2 for Phase
        row_formatter=""
        for i in range(11):
            if i<6:
                row_formatter=row_formatter+"{"+str(i)+":.4f}{delimiter}"
            else:
                row_formatter=row_formatter+"{"+str(i)+":.2f}{delimiter}"
        self.options["row_formatter_string"]=row_formatter

        AsciiDataTable.__init__(self,None,**self.options)

    def __read_and_fix__(self):
        """Reads in a 1 port ascii file and fixes any issues with inconsistent delimiters, etc"""
        lines=[]
        table_type=self.path.split(".")[-1]
        in_file=open(self.path,'r')
        for line in in_file:
            lines.append(line)
        # Handle the cases in which it is the comma delimited table
        if re.match('txt',table_type,re.IGNORECASE):
            self.options["data"]=split_all_rows(row_list=lines[:-1],delimiter=",")
            self.options["header"]=["Device_Id = {0}".format(self.path.split(".")[-2])]
        elif re.match("asc",table_type,re.IGNORECASE):
            self.lines=lines
            data_begin_line=self.find_line(" TABLE")+2
            data=np.loadtxt(self.path,skiprows=data_begin_line)
            self.options["data"]=data.tolist()
            self.options["header"]=lines[:self.find_line(" TABLE")]




class SwitchTermsFR():
    pass
class SwitchTermsPort():
    pass
class NoiseCalRaw():
    pass
class ReverbChamber():
    pass
class RobotData():
    pass

#-----------------------------------------------------------------------------
# Module Scripts
def test_OnePortModel(file_path_1='700437.txt',file_path_2="700437.asc"):
    os.chdir(TESTS_DIRECTORY)
    print(" Import of {0} results in:".format(file_path_1))
    new_table_1=OnePortModel(file_path=file_path_1)
    print new_table_1
    print("-"*80)
    print("\n")

    print(" Import of {0} results in:".format(file_path_2))
    new_table_1=OnePortModel(file_path=file_path_2)
    print new_table_1
    print("{0} results in {1}:".format('new_table_1.get_column("Frequency")',new_table_1.get_column("Frequency")))


#-----------------------------------------------------------------------------
# Module Runner
if __name__ == '__main__':
    test_OnePortModel()
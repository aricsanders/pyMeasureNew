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
        defaults= {"data_delimiter": ",", "column_names_delimiter": ",", "specific_descriptor": 'One_Port',
                   "general_descriptor": 'Sparameter', "extension": 'txt', "comment_begin": "#", "comment_end": "\n",
                   "column_types": ['float' for i in range(11)],
                   "column_descriptions": {"Frequency": "Frequency in GHz", "Magnitude": "Linear magnitude",
                                           "uMb": "Uncertainty in magnitude due to standards",
                                           "uMa": "Uncertainty in magnitude due to electronics",
                                           "uMd": "Uncertainty in magnitude for repeated connects",
                                           "uMg": "Total uncertainty in magnitude",
                                           "Phase": "Phase in degrees",
                                           "uPhb": "Uncertainty in phase due to standards",
                                           "uPha": "Uncertainty in phase due to electronics",
                                           "uPhd": "Uncertainty in phase for repeated connects",
                                           "uPhg": "Total uncertainty in phase"}, "header": None,
                   "column_names": ["Frequency", "Magnitude", "uMb", "uMa", "uMd", "uMg", "Phase",
                                    "uPhb", "uPha", "uPhd", "uPhg"], "column_names_end_token": "\n", "data": None,
                   "row_formatter_string": None, "data_table_element_separator": None}
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
            elif i==10:
                row_formatter=row_formatter+"{"+str(i)+":.2f}"
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
            data=split_all_rows(lines[data_begin_line:],delimiter="")
            self.options["data"]=data.tolist()
            self.options["header"]=lines[:self.find_line(" TABLE")]

class OnePortRawModel(AsciiDataTable):
    """ Class that deals with the OnePort Raw Files after conversion to Ascii using Ron Ginley's converter.
    These files typically have header information seperated from data by !!
    Header format is:
    Line 1:		Spid$ - identification of type of system used
    Line 2:		Systemletter$ - letter name indicating which system was used
    Line 3:		Conncal$ - connector type from the system calibration
    Line 4:		Connectors$ - connector type used for the measurement
    Line 5:		Meastype$ - type of measurement (basically 1-port, 2-port or power)
    Line 6:		Datea$ - date of measurement
    Line 7:		Timea$ - time of measurement
    Line 8:		Programm$ - name of program used
    Line 9:		Rev$ - program revision
    Line 10:	Opr$ - operator
    Line 11:	Cfile$ - calibration name
    Line 12:	Cdate$ - calibration date
    Line 13:	Sport - identification of which port or direction was used for measurement
    Line 14:	Numconnects ? number of disconnect/reconnect cycles
    Line 15:	Numrepeats ? number of repeat measurements for each connect (usually 1)
    Line 16:	Nbs ? not sure
    Line 17:	Nfreq ? number of frequencies
    Line 18:	Startfreq ? data row pointer for bdat files
    Line 19:	Devicedescript$ - description of device being measured or of test being done
    Line 20:	Devicenum$ - Identifying number for device ? used for file names
    """
    def __init__(self,file_path=None,**options):
        """Initializes the OnePortRaw class, if a file_path is specified opens an existing file, else creates an
        empty container"""
        defaults= {"data_delimiter": ",", "column_names_delimiter": ",", "specific_descriptor": 'One_Port_Raw',
                   "general_descriptor": 'Sparameter', "extension": 'txt', "comment_begin": "#", "comment_end": "\n",
                   "column_types": ['float','int','int','float','float','float','float'],
                   "column_descriptions": {"Frequency":"Frequency in GHz",
                                           "Direction":"Direction of connects, may be unused",
                                           "Connect":"Connect number", "Magnitude_S11":"Linear magnitude for port 1",
                                           "Phase_S11":"Phase in degrees for port 1",
                                           "Magnitude_S22":"Linear magnitude for port 2",
                                           "Phase_S22":"Phase in degrees for port 2"}, "header": None,

                   "column_names": ["Frequency","Direction","Connect", "Magnitude_S11",
                                    "Phase_S11","Magnitude_S22",  "Phase_S22"],
                   "column_names_end_token": "\n", "data": None,
                   'row_formatter_string': "{0:.5f}{delimiter}{1}{delimiter}{2}{delimiter}{3:.4f}{delimiter}{4:.2f}{delimiter}{5:.4f}{delimiter}{5:.2f}",
                   "data_table_element_separator": None}
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
        AsciiDataTable.__init__(self,None,**self.options)
        self.structure_metadata()

    def __read_and_fix__(self):
        """Inputs in the raw OnePortRaw file and fixes any problems with delimiters,etc."""
        lines=[]
        in_file=open(self.path,'r')
        for index,line in enumerate(in_file):
            lines.append(line)
            if re.match("!!",line):
                data_begin_line=index+1
        self.lines=lines
        data=split_all_rows(lines[data_begin_line:],delimiter=", ")
        self.options["data"]=data
        self.options["header"]=lines[:data_begin_line-1]


    def structure_metadata(self):
        """Returns a dictionary of key,value pairs extracted from the header"""
        keys=["System_Id","System_Letter","Connector_Type_Calibration","Connector_Type_Measurement",
              "Measurement_Type","Measurement_Date","Measurement_Time","Progam_Used","Program_Revision","Operator",
              "Calibration_Name","Port_Used","Number_Connects","Number_Repeats","Number_Frequencies","Start_Frequency",
              "Device_Description","Device_Id"]
        self.metadata={}
        for index,key in enumerate(keys):
            self.metadata[key]=self.header[index]


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
    new_table_2=OnePortModel(file_path=file_path_2)
    print new_table_2
    print("{0} results in {1}:".format('new_table_1.get_column("Frequency")',new_table_1.get_column("Frequency")))
    print new_table_1.get_options()

def test_OnePortRawModel(file_path='OnePortRawTestFile.txt'):
    os.chdir(TESTS_DIRECTORY)
    print(" Import of {0} results in:".format(file_path))
    new_table_1=OnePortRawModel(file_path=file_path)
    print new_table_1
    print("-"*80)
    print("{0} results in {1}:".format('new_table_1.get_column("Frequency")',new_table_1.get_column("Frequency")))
    print new_table_1.get_options()
    print new_table_1.metadata
#-----------------------------------------------------------------------------
# Module Runner
if __name__ == '__main__':
    #test_OnePortModel()
    test_OnePortRawModel()
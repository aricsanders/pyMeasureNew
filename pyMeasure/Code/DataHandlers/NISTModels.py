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
    from pyMeasure.Code.DataHandlers.TouchstoneModels import *
except:
    print("The module pyMeasure.Code.DataHandlers.TouchstoneModels was not found,"
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
ONE_PORT_COLUMN_NAMES=["Frequency", "Magnitude", "uMb", "uMa", "uMd", "uMg", "Phase",
                                    "uPhb", "uPha", "uPhd", "uPhg"]
POWER_COLUMN_NAMES=['Frequency', 'Efficiency','uEs', 'uEc', 'uEe',
                    'Calibration Factor', 'uCs', 'uCc', 'uCe']
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
                   "row_formatter_string": None, "data_table_element_separator": None,"row_begin_token":None,
                   "row_end_token":None,"escape_character":None,
                   "data_begin_token":None,"data_end_token":None}
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
        if file_path is not None:
            self.path=file_path



    def __read_and_fix__(self):
        """Reads in a 1 port ascii file and fixes any issues with inconsistent delimiters, etc"""
        lines=[]
        table_type=self.path.split(".")[-1]
        in_file=open(self.path,'r')
        for line in in_file:
            if not re.match('[\s]+(?!\w+)',line):
                #print line
                lines.append(line)
        # Handle the cases in which it is the comma delimited table
        if re.match('txt',table_type,re.IGNORECASE):
            lines=strip_tokens(lines,*[self.options['data_begin_token'],
                                                    self.options['data_end_token']])
            self.options["data"]=strip_all_line_tokens(lines,begin_token=self.options["row_begin_token"],
                                            end_token=self.options["row_end_token"])
            self.options["data"]=split_all_rows(self.options["data"],delimiter=self.options["data_delimiter"],
                                     escape_character=self.options["escape_character"])
            self.options["data"]=convert_all_rows(self.options["data"],self.options["column_types"])
            #print self.options["data"]
            self.options["header"]=["Device_Id = {0}".format(self.path.split(".")[-2])]
        elif re.match("asc",table_type,re.IGNORECASE):
            self.lines=lines
            data_begin_line=self.find_line(" TABLE")+2
            data=np.loadtxt(self.path,skiprows=data_begin_line)
            self.options["data"]=data.tolist()
            self.options["header"]=lines[:self.find_line(" TABLE")]
            #print("The {0} variable is {1}".format('data.tolist()',data.tolist()))

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
                   'row_formatter_string': "{0:.5f}{delimiter}{1}{delimiter}{2}{delimiter}{3:.4f}{delimiter}{4:.2f}{delimiter}{5:.4f}{delimiter}{6:.2f}",
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
            self.__read_and_fix__(file_path)

        AsciiDataTable.__init__(self,None,**self.options)
        self.path=file_path
        self.structure_metadata()

    def __read_and_fix__(self,file_path=None):
        """Inputs in the raw OnePortRaw file and fixes any problems with delimiters,etc."""
        lines=[]
        in_file=open(file_path,'r')
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
              "Measurement_Type","Measurement_Date","Measurement_Time","Program_Used","Program_Revision","Operator",
              "Calibration_Name","calibration_date","Port_Used","Number_Connects","Number_Repeats","Nbs",
              "Number_Frequencies","Start_Frequency",
              "Device_Description","Device_Id"]
        self.metadata={}
        for index,key in enumerate(keys):
            self.metadata[key]=self.header[index]

class TwoPortCalrep():
    """TwoPortCalrep is a model that holds data output by analyzing several datafiles using the HPBasic program
    Calrep. The data is stored in 3 tables: a S11 table, a S21 table and a S22 table. The data is in linear
    magnitude and angle in degrees. There are 2 types of files, one is a single file with .asc extension
    and 3 files with .txt extension"""

    def __init__(self,file_path=None,**options):
        """Intializes the TwoPortCalrep class, if a file path is specified it opens and reads the file"""
        if file_path is None:
            pass
        elif re.match('asc',file_path.split(".")[-1],re.IGNORECASE):
            self.table_names=['header','S11','S22','S21']
            self.row_pattern=make_row_match_string(ONE_PORT_COLUMN_NAMES)
            self.path=file_path
            self.__read_and_fix__()

    def __read_and_fix__(self):
        in_file=open(self.path,'r')
        self.lines=[]
        table_locators=["Table 1","Table 2","Table 3"]
        begin_lines=[]
        for index,line in enumerate(in_file):
            self.lines.append(line)
            for table in table_locators:
                if re.search(table,line,re.IGNORECASE):
                    begin_lines.append(index)
        in_file.close()
        self.table_line_numbers=[]
        for index,begin_line in enumerate(begin_lines):
            if index == 0:
                header_begin_line=0
                header_end_line=begin_line-2
                table_1_begin_line=begin_line+3
                table_1_end_line=begin_lines[index+1]-1
                self.table_line_numbers.append([header_begin_line,header_end_line])
                self.table_line_numbers.append([table_1_begin_line,table_1_end_line])

            elif index>0 and index<(len(begin_lines)-1):
                table_begin_line=begin_line+3
                table_end_line=begin_lines[index+1]-1
                self.table_line_numbers.append([table_begin_line,table_end_line])

            elif index==(len(begin_lines)-1):
                table_begin_line=begin_line+3
                table_end_line=None
                self.table_line_numbers.append([table_begin_line,table_end_line])
        self.tables=[]
        for index,name in enumerate(self.table_names):
            self.table_lines=self.lines[self.table_line_numbers[index][0]:self.table_line_numbers[index][1]]
            self.tables.append(self.table_lines)
        for index,table in enumerate(self.table_names):
            if index==0:
                # by using parse_lines we get a list_list of strings instead of list_string
                # we can just remove end lines
                self.tables[index]=strip_all_line_tokens(self.tables[index],begin_token=None,end_token='\n')
            else:

                column_types=['float' for i in range(len(ONE_PORT_COLUMN_NAMES))]
                options={"row_pattern":self.row_pattern,"column_names":ONE_PORT_COLUMN_NAMES,"output":"list_list"}
                options["column_types"]=column_types
                self.tables[index]=parse_lines(self.tables[index],**options)

class JBSparameter(AsciiDataTable):
    """JBSparameter is a class that holds data taken and stored using Jim Booth's two port format.
     """

    def __init__(self,file_path=None,**options):
        """Initializes the JBSparameter class. JB Sparameter data is very close to s2p, but has # as a comment
         begin token, and space as a data delimiter. The first line has structured metadata that usually includes
         date and IFBW"""
        defaults={"header_begin_line":0,"data_end_line":None,"column_names_delimiter":' ',
                "column_names_begin_token":'#',"column_names_end_token":'\n',"data_table_element_separator":None,
                 "data_delimiter":' ',"comment_begin":"#",
                 "comment_end":"\n","row_end_token":'\n',"column_types":['float' for i in range(9)],
                 "column_descriptions":["Frequency in Hz",
                                        "Real part of S11",
                                        "Imaginary part of S11",
                                        "Real part of S21",
                                        "Imaginary part of S21",
                                        "Real part of S12",
                                        "Imaginary part of S12",
                                        "Real part of S22",
                                        "Imaginary part of S22"]}
        rfs=""
        for i in range(9):
            if i==8:
                rfs=rfs+"{%s:.6g}"%(str(i))
            else:
                rfs=rfs+"{%s:.6g}{delimiter}"%(str(i))
        options["row_formatter_string"]=rfs
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
            column_name_line=0
            in_file=open(file_path)
            for line in in_file:
                if line[0] is '#':
                    column_name_line+=1
            self.options["header_end_line"]=column_name_line-1
            self.options["column_names_begin_line"]=column_name_line-1
            self.options["column_names_end_line"]=column_name_line
            self.options["data_begin_line"]=column_name_line
            self.path=file_path
            AsciiDataTable.__init__(self,file_path,**self.options)
        else:
            AsciiDataTable.__init__(self,file_path,**self.options)
    def get_frequency_units(self):
        """Returns the frequency units by looking at the 0 index element of column names"""
        pattern='freq\((?P<Frequency_Units>\w+)\)'
        match=re.match(pattern,self.column_names[0])
        return match.groupdict()['Frequency_Units']




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

def test_OnePortModel_Ctable(file_path_1='700437.txt'):
    """Tests the OnePortModel on ctables from 2 port """
    os.chdir(TESTS_DIRECTORY)
    print(" Import of {0} results in:".format(file_path_1))
    new_table_1=OnePortModel(file_path=file_path_1,**{"row_end_token":",\n"})
    print new_table_1
    print("-"*80)
    print("\n")


def test_OnePortRawModel(file_path='OnePortRawTestFile.txt'):
    os.chdir(TESTS_DIRECTORY)
    print(" Import of {0} results in:".format(file_path))
    new_table_1=OnePortRawModel(file_path=file_path)
    print new_table_1
    print("-"*80)
    print("{0} results in {1}:".format('new_table_1.get_column("Frequency")',new_table_1.get_column("Frequency")))
    print new_table_1.get_options()
    print new_table_1.metadata
    print new_table_1.column_names
    print('index' in new_table_1.column_names )

def test_JBSparameter(file_path="ftest6_L1_g5_HF_air"):
    """Tests the JBSparameter class"""
    os.chdir(TESTS_DIRECTORY)
    # open an existing file
    new_table=JBSparameter(file_path=file_path)
    print new_table.column_names
    print new_table.get_frequency_units()
    old_prefix=new_table.get_frequency_units().replace('Hz','')
    #new_table.change_unit_prefix(column_selector=0,old_prefix='',new_prefix='G',unit='Hz')
    new_table.change_unit_prefix(column_selector=0,old_prefix=old_prefix,new_prefix='G',unit='Hz')
    print new_table.column_names
    print new_table.get_column(None,0)
    print new_table.get_frequency_units()
    print new_table.get_header_string()

def test_TwoPortCalrep(file_name="922729.asc"):
    """Tests the TwoPortCalrep model type"""
    pass

#-----------------------------------------------------------------------------
# Module Runner
if __name__ == '__main__':
    #test_OnePortModel()
    test_OnePortModel_Ctable(file_path_1='922729c.txt')
    #test_OnePortRawModel()
    #test_JBSparameter()
    #test_JBSparameter('QuartzRefExample_L1_g10_HF')

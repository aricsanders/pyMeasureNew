#-----------------------------------------------------------------------------
# Name:        GeneralModels
# Purpose:     To create base classes
# Author:      Aric Sanders
# Created:     2/24/2016
# License:     MIT License
#-----------------------------------------------------------------------------
""" Module that contains general data models """

#-----------------------------------------------------------------------------
# Standard Imports
from types import *
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
    from pyMeasure.Code.Utils.Names import auto_name
    DEFAULT_FILE_NAME=None
except:
    print("The function auto_name in pyMeasure.Code.Utils.Names was not found")
    print("Setting Default file name to New_Data_Table.txt")
    DEFAULT_FILE_NAME='New_Data_Table.txt'
    pass
try:
    import numpy as np
except:
    np.ndarray='np.ndarray'
    print("Numpy was not imported")
    pass
#-----------------------------------------------------------------------------
# Module Constants

#-----------------------------------------------------------------------------
# Module Functions
def string_list_collapse(list_of_strings):
    """ Makes a list of strings a single string"""
    out_string=''
    for item in list_of_strings:
        out_string=out_string+item
    return out_string

def list_to_string(row_list,data_delimiter=None,row_formatter_string=None,end='\n'):
    """Given a list of values returns a string"""
    if data_delimiter is None:
        data_delimiter=','
    string_out=""
    if row_formatter_string is None:
        for index,item in enumerate(row_list):
            if index is len(row_list)-1:
                string_out=string_out+str(item)
            else:
                string_out=string_out+str(item)+data_delimiter
    else:
        string_out=row_formatter_string.format(*row_list,delimiter=data_delimiter)
    return string_out+end

def list_list_to_string(list_lists,data_delimiter=None,row_formatter_string=None):
    "coverts a list of lists to a string"
    string_out=""
    for row in list_lists:
        string_out=string_out+list_to_string(row,data_delimiter=data_delimiter,row_formatter_string=row_formatter_string)
    return string_out

def line_comment_string(comment,comment_begin=None,comment_end=None):
    "Creates a comment optionally wrapped with comment_begin and comment_end"
    string_out=""
    if comment_begin is None:
        if comment_end is None:
            string_out=comment
        else:
            string_out=comment+comment_end
    else:
        if comment_end is None:
            string_out=comment_begin+comment
        else:
            string_out=comment_begin+comment+comment_end
    return string_out
def line_list_comment_string(comment_list,comment_begin=None,comment_end=None,block=False):
    """Creates a string with each line wrapped in comment_begin and comment_end
    or the full string wrapped with block_comment_begin and block_comment_end"""
    string_out=""
    if block:
        string_out=comment_begin+string_list_collapse(comment_list)+comment_end
    else:
        for item in comment_list:
            string_out=string_out+line_comment_string(item,comment_begin=comment_begin,comment_end=comment_end)
    return string_out


#-----------------------------------------------------------------------------
# Module Classes
class AsciiDataTable():
    """ An AsciiDatable is a generalized model of a data table with optional header,
    column names,rectangular array of data, and footer """
    def __init__(self,file_path=None,**options):
        " Initializes the AsciiDataTable class "
        # This is a general pattern for adding a lot of options
        defaults={"data_delimiter":None,
                  "column_name_delimiter":None,
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
                  "column_name_line":None,
                  "data_begin_line":None,
                  "data_end_line":None,
                  "footer_begin_token":None,
                  "footer_end_token":None,
                  "header_begin_token":None,
                  "header_end_token":None,
                  "column_name_token":None,
                  "data_begin_token":None,
                  "data_end_token":None,
                  "metadata_delimiter":None,
                  "column_types":None,
                  "header":None,
                  "column_names":None,
                  "data":None,
                  "footer":None,
                  "row_formatter_string":None,
                  "empty_value":None,
                  "escape_character":None,
                  "data_table_element_separator":'\n'
                  }
        #some of the options have the abiltiy to confilct with each other, so there has to be a
        #built-in way to determine the precedence of each option
        self.options={}
        for key,value in defaults.iteritems():
            self.options[key]=value
        for key,value in options.iteritems():
            self.options[key]=value
        # Define Method Aliases if they are available
        if METHOD_ALIASES:
            for command in alias(self):
                exec(command)
        if file_path is None:
            #create a new data table
            if DEFAULT_FILE_NAME is None:
                self.path=auto_name(self.options["specific_descriptor"],
                                    self.options["general_descriptor"],
                                    self.options["directory"],
                                    self.options["extension"])
            #Now we see if the table has been defined in the options

            self.header=self.options["header"]
            self.column_names=self.options["column_names"]
            self.data=self.options["data"]
            self.footer=self.options["footer"]

        else:
            # open the file and read it in as lines
            file_in=open(file_path,'r')
            self.lines=[]
            for line in file_in:
                self.lines.append(line)
            file_in.close()
            self.path=file_path

        self.string=""

    def __str__(self):
        "Controls the str output of AsciiDataTable"
        return self.string

    def update_model(self):
        """Updates the model after a change has been made"""
        pass

    def save(self,path=None,**options):
        """" Saves the file, to save in another ascii format specify elements in options """
        if path is None:
            path=self.path
        file_out=open(path,'w')
        file_out.write(self.string)
        file_out.close()

    def build_string(self,**options):
        "Builds a string representation of the data table based on self.options"
        for key,value in options.iteritems():
            self.options[key]=value
        string_out=""
        if self.header is None:
            pass
        else:
            string_out=self.get_header_string()+self.options['data_table_element_separator']
        if self.column_names is None:
            pass
        else:
            string_out=string_out+self.get_column_names_string()+self.options['data_table_element_separator']
        if self.data is None:
            pass
        else:
            string_out=string_out+self.get_data_string()+self.options['data_table_element_separator']
        if self.footer is None:
            pass
        else:
            string_out=string_out+self.get_footer_string()+self.options['data_table_element_separator']
        return string_out

    def get_header_string(self):
        string_out=""
        # This writes the header
        if self.header is None:
            return ""
        else:
            if type(self.header) is StringType:
                string_out=line_comment_string(self.header,
                                               comment_begin=self.options["comment_begin"],
                                               comment_end=self.options["comment_end"])
            elif type(self.header) is ListType:
                if self.options['block_comment_begin'] is None:
                    string_out=line_comment_string(string_list_collapse(self.header))
            else:
                try:
                    string_out=str(self.header)
                except:raise
        return string_out

    def get_column_names_string(self):
        "Returns the column names as a string using options"
        string_out=""
        # This writes the column_names
        if self.column_names is None:
            string_out=""
        else:
            if type(self.column_names) is StringType:
                if self.options['column_name_token'] is None:
                    string_out=self.column_names
                else:
                    if re.match(self.options['column_name_token'],self.column_names):
                        string_out=self.column_names
                    else:
                        string_out=self.options['column_name_token']+self.column_names
            elif type(self.column_names) is ListType:
                if self.options['column_name_token'] is None:
                    string_out=list_to_string(self.column_names,self.options['column_name_delimiter'],end="")
                else:
                    string_out=self.options['column_name_token']+\
                               list_to_string(self.column_names,self.options['column_name_delimiter'],end="")
            else:
                try:
                    string_out=str(self.column_names)
                except:raise
        return string_out

    def get_data_string(self):
        "Returns the data as a string"
        string_out=""
        if self.data is None:
            string_out= ""
        else:
            if type(self.data) is StringType:
                if self.options['data_begin_token'] is None:
                       if self.options['data_end_token'] is None:
                           string_out=self.data
                       else:
                           if re.search(self.options['data_end_token'],self.data):
                               string_out=self.data
                           else:
                               string_out=self.data+self.options['data_end_token']
                else:
                        if self.options['data_end_token'] is None:
                            if re.match(self.options['data_begin_token'],self.data):
                                string_out=self.data
                            else:
                                string_out=self.options['data_begin_token']+self.data
            elif type(self.data) is ListType:
                    if type(self.data[0]) is StringType:
                        if self.options['data_begin_token'] is None:
                            string_out=string_list_collapse(self.data)
                        else:
                            if re.match(self.options['data_begin_token'],self.data[0]):
                                if self.options['data_end_token'] is None:
                                    string_out=string_list_collapse(self.data)
                                else:
                                    if re.search(self.options['data_end_token'],self.data[-1]):
                                        string_out=string_list_collapse(self.data)
                                    else:
                                        string_out=string_list_collapse(self.data)+self.options['data_end_token']
                            else:
                                if self.options['data_end_token'] is None:
                                    string_out=self.options['data_begin_token']+string_list_collapse(self.data)
                                else:
                                    if re.search(self.options['data_end_token'],self.data[-1]):
                                        string_out=self.options['data_begin_token']+string_list_collapse(self.data)
                                    else:
                                        string_out=self.options['data_begin_token']+\
                                                   string_list_collapse(self.data)+\
                                                   self.options['data_end_token']
                    elif type(self.data[0]) in [ListType,np.ndarray]:
                        prefix=""
                        if self.options['data_begin_token'] is None:
                            if self.options['data_end_token'] is None:
                                string_out=list_list_to_string(self.data,data_delimiter=self.options['data_delimiter'],
                                                               row_formatter_string=self.options['row_formatter_string'])
                        else:
                            if self.options['data_end_token'] is None:
                                string_out=self.options['data_begin_token']+\
                                           list_list_to_string(self.data,data_delimiter=self.options['data_delimiter'],
                                                               row_formatter_string=self.options['row_formatter_string'])
                            else:
                                string_out=self.options['data_begin_token']+\
                                           list_list_to_string(self.data,data_delimiter=self.options['data_delimiter'],
                                                               row_formatter_string=\
                                                               self.options['row_formatter_string'])+\
                                                                self.options['data_end_token']
                    else:
                        string_out=list_to_string(self.data,data_delimiter=self.options['data_delimiter'],
                                                               row_formatter_string=self.options['row_formatter_string'])
        return string_out
    def get_footer_string(self):
        "Returns a string representation of the footer"
        # writes the footer
        string_out=""
        if self.footer is None:
            pass
        else:
            string_out=string_out+self.options["data_table_element_seperator"]
            if type(self.footer) is StringType:
                string_out=self.header
            elif type(self.footer) is ListType:
                string_out=string_list_collapse(self.footer)
            else:
                try:
                    string_out=str(self.footer)
                except:raise
        return string_out

    def __add__(self, other):
        """Controls the behavior of the addition operator, if column_names are equal it adds rows at the end
        and increments any column named index. If the column_names are different it adds columns to the table and
        fills the non-defined rows with self.options['empty_character'] which is None by default. If the headers are
        different it string adds them"""
        pass

    def is_vaid(self):
        """Returns True if ascii table conforms to its specification"""
        pass

    def add_row(self,row_data):
        """Adds a single row given row_data which can be an ordered list/tuple or a dictionary with
        column names as keys"""
        pass

    def add_column(self,column_name=None,column_type=None,**options):
        """Adds a column with column_name, and column_type"""
        pass

    def add_index(self):
        "Adds a column with name index and values that are 0 referenced indices"
        pass

    def move_footer_to_header(self):
        """Moves the DataTable's footer to the header and updates the model"""
        pass

    def add_comment(self,comment):
        "Adds a comment to the header"
        pass

    def add_inline_comment(self,comment,location=None):
        "Adds an inline in the specified location"
        pass

    def add_block_comment(self,comment,location=None):
        "Adds a block comment in the specified location"
        pass
#-----------------------------------------------------------------------------
# Module Scripts
def test_AsciiDataTable():
    options={"column_names":["a","b","c"],"data":[[0,1,2],[2,3,4]],"data_delimiter":',',
             "header":'Hello There',"column_name_token":'!'}
    new_table=AsciiDataTable(file_path=None,**options)
    print new_table.data
    print dir(new_table)
    print new_table.get_header_string()
    print new_table.get_data_string()
    print new_table.build_string()
    print new_table.path
#-----------------------------------------------------------------------------
# Module Runner
if __name__ == '__main__':
    test_AsciiDataTable()
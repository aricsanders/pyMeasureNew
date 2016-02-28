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
TESTS_DIRECTORY=os.path.join(os.path.dirname(os.path.realpath(__file__)),'Tests')
#-----------------------------------------------------------------------------
# Module Functions
def check_arg_type(arg,arg_type):
    "Checks argument and prints out a statement if arg is not type"
    if type(arg) is arg_type:
        return
    else:
        print("{0} was not {1}".format(arg,arg_type))

def string_list_collapse(list_of_strings,string_delimiter='\n'):
    """ Makes a list of strings a single string"""
    check_arg_type(list_of_strings,ListType)
    if string_delimiter is None:
        string_delimiter=""
    out_string=''
    for index,item in enumerate(list_of_strings):
        if index is len(list_of_strings)-1:
            out_string=out_string+item
        else:
            out_string=out_string+item+string_delimiter
    return out_string

def list_to_string(row_list,data_delimiter=None,row_formatter_string=None,begin=None,end='\n'):
    """Given a list of values returns a string, if row_formatter is specifed
     it uses it as a template, else uses data delimiter. Inserts data_delimiter between each list element. An optional
    begin and end wrap the resultant string. (i.e ['1','2','3']-> 'begin+'1'+','+'2'+','+'3'+'end') end defaults
    to \n"""
    check_arg_type(row_list,ListType)
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
    if end is None:
        end=""
    if begin is None:
        begin=""
    return begin+string_out+end

def list_list_to_string(list_lists,data_delimiter=None,row_formatter_string=None,line_begin=None,line_end='\n'):
    """Repeatedly calls list to string on each element of a list and string adds the result
    . ie coverts a list of lists to a string"""
    check_arg_type(list_lists,ListType)
    string_out=""
    for row in list_lists:
        string_out=string_out+list_to_string(row,data_delimiter=data_delimiter,
                                             row_formatter_string=row_formatter_string,
                                             begin=line_begin,end=line_end)
    return string_out

def line_comment_string(comment,comment_begin=None,comment_end=None):
    "Creates a comment optionally wrapped with comment_begin and comment_end, meant for a single string comment "
    check_arg_type(comment,StringType)
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
    """Creates a string with each line wrapped in comment_begin and comment_end, by repeatedly calling
    line_comment_string,
    or the full string wrapped with block_comment_begin and block_comment_end if block is set to True. Meant
    to deal with a list of comment strings"""
    check_arg_type(comment_list,ListType)
    string_out=""
    if block:
        string_out=comment_begin+string_list_collapse(comment_list)+comment_end
    else:
        for item in comment_list:
            string_out=string_out+line_comment_string(item,comment_begin=comment_begin,comment_end=comment_end)
    return string_out

def ensure_string(input_object,  list_delimiter="",  end_if_list=""):
    """Returns a string given an object. If the object is a string just returns it,
    if it is a list of strings, returns a collapsed version. If is another type of object returns str(object).
      If all else fails it returns an empty string"""
    string_out=""
    try:
        if type(input_object) in StringTypes:
            string_out=input_object
        elif type(input_object) in [ListType,np.ndarray]:
            if type(input_object[0]) in [ListType,np.ndarray]:
                string_out=list_list_to_string(input_object,data_delimiter=list_delimiter,end=end_if_list)
            else:
                string_out=list_to_string(input_object,data_delimiter=list_delimiter,end=end_if_list)
        else:
            string_out=str(input_object)
    except:
        pass
    return string_out

def strip_tokens(string_list,begin_token=None,end_token=None):
    """Strips a begin and end token from the first position in a list and the
    last positon in a list if present. Returns the list with 2 less elements if the first and last position are now
    empty. Meant to reverse the action of line_list_comment_string for a list of strings"""
    check_arg_type(string_list,ListType)
    new_string_list=string_list
    try:
        if begin_token is not None:
            new_string_list[0]=string_list[0].replace(begin_token,'')
            if new_string_list[0] is "":
                new_string_list.pop(0)
        if end_token is not None:
            new_string_list[-1]=string_list[-1].replace(end_token,'')
            if new_string_list[-1] is "":
                new_string_list.pop(-1)
    except:
        print("Strip Tokens Did not work")
        pass
    return new_string_list

def strip_line_tokens(string,begin_token=None,end_token=None):
    """Strips a begin and end token if present from an inputted string, meant to remove line_comments"""
    check_arg_type(string,StringType)
    string_out=string
    try:
        if begin_token is not None:
            string_out=string_out.replace(begin_token,'')
        if end_token is not None:
            string_out=string_out.replace(end_token,'')
    except:
        pass
    return string_out

def strip_all_line_tokens(string_list,begin_token=None,end_token=None):
    """Strips all line tokens from a list of strings, meant  to reverse the action of line_list_comment_string
    with block=false"""
    check_arg_type(string_list,ListType)
    stripped_list=[]
    for row in string_list:
        check_arg_type(row,StringType)
        stripped_list.append(strip_line_tokens(row,begin_token=begin_token,end_token=end_token))
    return stripped_list

def split_row(row_string,delimiter=None,escape_character=None):
    """Splits a row given a delimiter, and ignores any delimiters after an escape character
    returns a list. If the string is unsplit returns a list of length 1"""
    check_arg_type(row_string,StringType)
    if delimiter is None:
        row_list=[row_string]
        return row_list
    if escape_character is None:
        row_list=row_string.split(delimiter)
    else:
        temp_row_string=row_string.replace(escape_character+delimiter,'TempPlaceHolder')
        temp_row_list=temp_row_string.split(delimiter)
        for item in temp_row_list:
            item.replace('TempPlaceHolder',escape_character+delimiter)
        row_list=temp_row_list
    return row_list

def split_all_rows(row_list,delimiter=None,escape_character=None):
    """Splits all rows in a list of rows and returns a 2d list """
    if type(row_list) is not ListType:
        print("Split row argument (%s) was not a list"%str(row_list))
        return row_list
    out_list=[]
    for row in row_list:
        out_list.append(split_row(row,delimiter=delimiter,escape_character=escape_character))
    return out_list

def insert_inline_comment(list_of_strings,comment="",line_number=None,string_position=None,begin_token='(*',end_token='*)'):
    "Inserts an inline comment in a list of strings, location is determined by line_number and string_position"
    if line_number is None or string_position is None:
        print("inline comment must have both line number and string position")
        return
    if begin_token is None or end_token is None:
        print("inline comment must have both a begin and end token")
        return
    inline_comment=begin_token+comment+end_token
    list_of_strings[line_number]=list_of_strings[line_number][:string_position]+inline_comment+list_of_strings[line_number][string_position:]
    return list_of_strings

def collect_inline_comments(list_of_strings,begin_token=None,end_token=None):
    """Reads a list of strings and returns all of the inline comments in a list.
    Output form is ['comment',line_number,string_location]"""
    match=re.compile('{0}(?P<inline_comments>.+){1}'.format(re.escape(begin_token),re.escape(end_token)))
    inline_comment_list=[]
    for index,line in enumerate(list_of_strings):
        comment_match=re.search(match,line)
        if comment_match:
            inline_comment_list.append([comment_match.group('inline_comments'),index,comment_match.start()])
    return inline_comment_list

def strip_inline_comments(list_of_strings,begin_token='(*',end_token='*)'):
    "Removes inline coments from a list of strings"
    match=re.compile('{0}(?P<inline_comments>.+){1}'.format(re.escape(begin_token),re.escape(end_token)))
    out_list=[]
    for index,line in enumerate(list_of_strings):
        out_list.append(re.sub(match,'',line))
    return out_list
#-----------------------------------------------------------------------------
# Module Classes
class AsciiDataTable():
    """ An AsciiDatable is a generalized model of a data table with optional header,
    column names,rectangular array of data, and footer """
    def __init__(self,file_path=None,**options):
        " Initializes the AsciiDataTable class "
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
                  "column_types":None,
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
        #some of the options have the abiltiy to confilct with each other, so there has to be a
        #built-in way to determine the precedence of each option, for import lines first, then begin and then end
        self.options={}
        for key,value in defaults.iteritems():
            self.options[key]=value
        for key,value in options.iteritems():
            self.options[key]=value
        #Define Method Aliases if they are available
        #unqualified exec is not allowed in function '__init__' because it contains a nested function with free variables
        # This is because __init__ has nested functions
        # if METHOD_ALIASES:
        #     for command in alias(self):
        #         exec(command)
        if file_path is None:
            #create a new data table
            if DEFAULT_FILE_NAME is None:
                self.name=auto_name(self.options["specific_descriptor"],
                                    self.options["general_descriptor"],
                                    self.options["directory"],
                                    self.options["extension"])
                if self.options['directory'] is None:
                    self.path=self.name
                else:
                    self.path=os.path.join(self.options["directory"],self.name)
            #Now we see if the table has been defined in the options
            # We should reset the self.options versions to None after this so as to not recreate or we
            # can use it as a cache and add a method reset_table which either redoes the below or reloads the saved file
            self.header=self.options["header"]
            self.column_names=self.options["column_names"]
            self.data=self.options["data"]
            self.footer=self.options["footer"]
            self.inline_comments=self.options["inline_comments"]
            self.string=self.build_string()

        else:
            # open the file and read it in as lines
            # do we parse it here?
            # once parsed we should end up with the major components
            # if we are given options we should use them, if not try to autodetect them?
            # we can just return an error right now and then have an __autoload__ method
            # we can assume it is in ascii or utf-8
            self.elements=['header','column_names','data','footer','inline_comments']
            # set any attribute that has no options to None
            import_table=[]
            for item in self.elements:
                if len(filter(lambda x: None!=x,self.get_options_by_element(item).values()))==0:
                    self.__dict__[item]=None
                    #elements.remove(item)
                else:
                    self.__dict__[item]=[]
                    import_row=[self.options['%s_begin_line'%item],
                                self.options['%s_end_line'%item],
                                self.options['%s_begin_token'%item],
                                self.options['%s_end_token'%item]]
                    import_table.append(import_row)
            file_in=open(file_path,'r')
            # in order to parse the file we need to know line #'s, once we deduce them we use __parse__
            self.lines=[]
            for line in file_in:
                self.lines.append(line)
            file_in.close()
            self.path=file_path
            if self.lines_defined():
                self.__parse__()
            else:
                import_table[0][0]=0
                import_table[-1][1]=-1
                inner_element_spacing=self.options['data_table_element_seperator'].count('\n')-1
                #print import_table
                self.update_import_options(import_table=import_table)
                #self.get_options()
                if self.lines_defined():
                    #print("%s says %s"%('self.lines_defined()',str(self.lines_defined())))
                    self.__parse__()
                row_zero=[import_table[i][0] for i in range(len(import_table))]
                for index,item in enumerate(row_zero):
                    #print import_table
                    #print index,item
                    if index>0:
                        #print("Row Zero Loop Returns index={0}, item={1}".format(index,item))
                        if item is not None:
                            import_table[index-1][1]=item+inner_element_spacing
                            #print import_table
                            self.update_import_options(import_table)
                            #print self.lines_defined()
                if self.lines_defined():
                        self.__parse__()
                else:
                    row_one=[import_table[i][1] for i in range(len(import_table))]
                    for index,item in enumerate(row_one):
                        #print("Row One Loop Returns index={0}, item={1}".format(index,item))
                        if index<(len(row_one)-1):
                            #print((index+1)<len(row_one))
                            #print("Row One Loop Returns index={0}, item={1}".format(index,item))
                            if item is not None:
                                #print import_table
                                import_table[index+1][0]=item-inner_element_spacing
                                self.update_import_options(import_table)
                    if self.lines_defined():
                        self.__parse__()
                    else:
                        row_two=[import_table[i][2] for i in range(len(import_table))]
                        for index,item in enumerate(row_two):
                            if item is not None:
                                import_table[index][0]=self.find_line(item)
                        for index,item in enumerate(row_zero):
                            if index>0:
                                if item is not None:
                                    import_table[index-1][1]=item++inner_element_spacing
                                    self.update_import_options(import_table)
                        if self.lines_defined():
                            self.__parse__()
                        else:
                            row_three=[import_table[i][3] for i in range(len(import_table))]
                            for index,item in enumerate(row_three):
                                if item is not None:
                                    import_table[index][1]=self.find_line(item)
                            for index,item in enumerate(row_one):
                                if index<(len(row_one)-1):
                                    if item is not None:
                                        import_table[index+1][0]=item-inner_element_spacing
                            self.update_import_options(import_table)
                            if self.lines_defined():
                                self.__parse__()
                            else:
                                print("FAILED to import file!")
                                raise

    def find_line(self,begin_token):
        """Finds the first line that has begin token in it"""
        for index,line in enumerate(self.lines):
            if re.match(begin_token,line):
                return index

    def update_import_options(self,import_table):
        """Updates the options in the import table"""
        for index,element in enumerate(self.elements):
            if self.__dict__[element] is not None:
                [self.options['%s_begin_line'%element],
                                self.options['%s_end_line'%element],
                                self.options['%s_begin_token'%element],
                                self.options['%s_end_token'%element]]=import_table[index][:]
                #self.get_options_by_element(element)

    def lines_defined(self):
        """If begin_line and end_line for all elements that are None are defined returns True"""
        truth_table=[]
        output=False
        for index,element in enumerate(self.elements):
            if self.__dict__[element] is not None:
                try:
                    if not None in [self.options['%s_begin_line'%element],self.options['%s_end_line'%element]]:
                        truth_table.append(True)
                    else:
                         truth_table.append(False)
                except:
                    return False
        #print truth_table
        if False in truth_table:
            output=False
        else:
            output=True
        #print output
        return output

    def __parse__(self):
        """Parses self.lines into its components once all the relevant begin and end lines have been set. It assumes
         that the self.__dict__[self.element[i]]=None for elements that are not defined"""
        if self.inline_comments is None:
            pass
        else:
            self.lines=strip_inline_comments(self.inline_comments,
                                             begin_token=self.options['inline_comment_begin'],
                                             end_token=self.options['inline_comment_end'])
        for index,element in enumerate(self.elements.remove('inline_comments')):
            if self.__dict__[element] is not None:
                try:
                    if not None in [self.options['%s_begin_line'%element],self.options['%s_end_line'%element]]:
                        content_list=self.lines[
                                            self.options['%s_begin_line'%element]:self.options['%s_end_line'%element]]
                        self.__dict__[element]=content_list
                        #print("The result of parsing is self.{0} = {1}".format(element,content_list))
                except:
                    raise
        for index,element in enumerate(self.elements.remove('inline_comments')):
            if self.__dict__[element] is not None:
                        content_list=strip_tokens(self.__dict__[element],
                                            begin_token=self.options['%s_begin_token'%element],
                                                            end_token=self.options['%s_end_token'%element])
                        content_list=strip_all_line_tokens(content_list,end_token='\n')
                        self.__dict__[element]=content_list
                        #print("The result of parsing is self.{0} = {1}".format(element,content_list))
        if self.header is not None:
            self.header=strip_all_line_tokens(self.header,begin_token=self.options['comment_begin'],
                                              end_token=self.options['comment_end'])
        if self.column_names is not None:
            self.column_names=strip_all_line_tokens(self.column_names,begin_token=self.options['column_names_begin_token'],
                                              end_token=self.options['column_names_end_token'])
            #print("The result of parsing is self.{0} = {1}".format('column_names',self.column_names))
            self.column_names=split_all_rows(self.column_names,delimiter=self.options["column_names_delimiter"],
                                        escape_character=self.options["escape_character"])
            self.column_names=self.column_names[0]
            #print("The result of parsing is self.{0} = {1}".format('column_names',self.column_names))


        if self.data is not None:
            self.data=split_all_rows(self.data,delimiter=self.options["data_delimiter"],
                                     escape_character=self.options["escape_character"])
        if self.footer is not None:
            self.footer=strip_all_line_tokens(self.footer,begin_token=self.options['comment_begin'],
                                              end_token=self.options['comment_end'])



    def get_options_by_element(self,element_name):
        """ returns a dictionary
         of all the options that have to do with element. Element must be header,column_names,data, or footer"""
        keys_regarding_element=filter(lambda x: re.search(element_name,str(x),re.IGNORECASE),self.options.keys())
        out_dictionary={key:self.options[key] for key in keys_regarding_element}
        #print out_dictionary
        return out_dictionary

    def __str__(self):
        "Controls the str output of AsciiDataTable"
        self.string=self.build_string()
        return self.string

    def update_index(self):
        """ Updates the index column if it exits, otherwise exits quietly
        """
        if 'index' not in self.column_names:
            return
        else:
            try:
                #This should be 0 but just in case
                index_column_number=self.column_names.index('index')
                for i in range(len(self.data)):
                    self.data[i][index_column_number]=i
            except:
                pass

    def update_model(self):
        """Updates the model after a change has been made. If you add anything to the attributes of the model,
        or change this updates the values. If the model has an index column it will make sure the numbers are correct.
        In addition, it will update the options dictionary to reflect added rows, changes in deliminators etc.  """
        if 'index' in self.column_names:
            self.update_index()
        self.string=self.build_string()
        self.lines=self.string.split('\n')

    def save(self,path=None,**temp_options):
        """" Saves the file, to save in another ascii format specify elements in temp_options, the options
        specified do not permanently change the object's options. If path is supplied it saves the file to that path. """
        original_options=self.options
        for key,value in temp_options.iteritems():
            self.options[key]=value
        out_string=self.build_string(**temp_options)
        if path is None:
            path=self.path
        file_out=open(path,'w')
        file_out.write(out_string)
        file_out.close()
        self.options=original_options

    def build_string(self,**temp_options):
        """Builds a string representation of the data table based on self.options, or temp_options.
        Passing temp_options does not permanently change the model"""
        # store the original options to be put back after the string is made
        original_options=self.options
        for key,value in temp_options.iteritems():
            self.options[key]=value
        string_out=""
        between_section=""
        if self.options['data_table_element_separator'] is not None:
            between_section=self.options['data_table_element_separator']
        if self.header is None:
            pass
        else:
            if self.data is None and self.column_names is None and self.footer is None:
                string_out=self.get_header_string()
            else:
                string_out=self.get_header_string()+between_section
        if self.column_names is None:
            pass
        else:
            if self.data is None and self.footer is None:
                string_out=string_out+self.get_column_names_string()
            else:
                string_out=string_out+self.get_column_names_string()+between_section
        if self.data is None:
            pass
        else:
            if self.footer is None:
                string_out=string_out+self.get_data_string()
            else:
                string_out=string_out+self.get_data_string()+between_section
        if self.footer is None:
            pass
        else:
            string_out=string_out+self.get_footer_string()
        # set the options back after the string has been made
        if self.inline_comments is None:
            pass
        else:
            lines=string_out.split('\n')
            for comment in self.inline_comments:
                lines=insert_inline_comment(lines,comment=comment[0],line_number=comment[1],string_position=comment[2])
            string_out=string_list_collapse(lines,string_delimiter='\n')
        self.options=original_options
        return string_out

    def get_header_string(self):
        """Returns the header using options in self.options. If block comment is specified, and the header is a
        list it will block comment out the header. If comment_begin and comment_end are specified it will use
        those to represent each line of the header. If header_begin_token and/or header_end_token are specified it
         will wrap the header in those.
        """
        string_out=""
        header_begin=""
        header_end=""
        if self.options["header_begin_token"] is None:
            header_begin=""
        else:
            header_begin=self.options["header_begin_token"]
        if self.options["header_end_token"] is None:
            header_end=""
        else:
            header_end=self.options["header_end_token"]
        # This writes the header
        if self.header is None:
            string_out= ""
        elif self.options['treat_header_as_comment'] is None:
            # Just happens if the user has set self.header manually
            if type(self.header) is StringType:
                string_out=line_comment_string(self.header,
                                               comment_begin=self.options["comment_begin"],
                                               comment_end=self.options["comment_end"])
            elif type(self.header) is ListType:
                if self.options['block_comment_begin'] is None:
                    if self.options['comment_begin'] is None:
                        string_out=string_list_collapse(self.header)

                    else:
                        string_out=line_list_comment_string(self.header,comment_begin=self.options['comment_begin'],
                                                        comment_end=self.options['comment_end'])
                else:
                    string_out=line_list_comment_string(self.header,comment_begin=self.options['block_comment_begin'],
                                                        comment_end=self.options['block_comment_end'],block=True)
        else:
            string_out=ensure_string(self.header)
        return header_begin+string_out+header_end

    def get_column_names_string(self):
        "Returns the column names as a string using options"
        string_out=""
        # This writes the column_names
        column_name_begin=""
        column_name_end=""
        if self.options["column_names_begin_token"] is None:
            column_name_begin=""
        else:
            column_name_begin=self.options["column_names_begin_token"]
        if self.options["column_names_end_token"] is None:
            column_name_end=""
        else:
            column_name_end=self.options["column_names_end_token"]

        if self.column_names is None:
            string_out=""
        else:
            if type(self.column_names) is StringType:
                string_out=self.column_names

            elif type(self.column_names) is ListType:
                string_out=list_to_string(self.column_names,
                                          data_delimiter=self.options["column_names_delimiter"],end="")
                #print("{0} is {1}".format('string_out',string_out))
            else:

                string_out=ensure_string(self.column_names)

        #print column_name_begin,string_out,column_name_end
        return column_name_begin+string_out+column_name_end

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
            elif type(self.data) in [ListType,np.ndarray]:
                try:
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

                except IndexError:
                    pass
            else:
                string_out=ensure_string(self.data)
        return string_out

    def get_footer_string(self):
        """Returns the footer using options in self.options. If block comment is specified, and the footer is a
        list it will block comment out the footer. If comment_begin and comment_end are specified it will use
        those to represent each line of the footer. If footer_begin_token and/or footer_end_token are specified it
         will wrap the footer in those.
        """
        string_out=""
        footer_begin=""
        footer_end=""
        if self.options["footer_begin_token"] is None:
            footer_begin=""
        else:
            footer_begin=self.options["footer_begin_token"]
        if self.options["footer_end_token"] is None:
            footer_end=""
        else:
            footer_end=self.options["footer_end_token"]
        # This writes the footer
        if self.footer is None:
            string_out= ""
        elif self.options['treat_footer_as_comment']:
            if type(self.footer) is StringType:
                string_out=line_comment_string(self.footer,
                                               comment_begin=self.options["comment_begin"],
                                               comment_end=self.options["comment_end"])
            elif type(self.footer) is ListType:
                if self.options['block_comment_begin'] is None:
                    string_out=line_list_comment_string(self.footer,comment_begin=self.options['comment_begin'],
                                                        comment_end=self.options['comment_end'])
                else:
                    string_out=line_list_comment_string(self.footer,comment_begin=self.options['block_comment_begin'],
                                                        comment_end=self.options['block_comment_end'],block=True)
            else:
                try:
                    string_out=str(self.footer)
                except:raise
        else:
            string_out=ensure_string(self.footer)
        return footer_begin+string_out+footer_end
    # our current definition of add is not reversible !!!!!!!!!
    # def __radd__(self, other):
    #     "Controls the behavior of radd to use the sum function it is required"
    #     if other==0:
    #         return self
    #     else:
    #         return self.__add__(other)

    def __add__(self, other):
        """Controls the behavior of the addition operator, if column_names are equal it adds rows at the end
        and increments any column named index. If the column_names are different it adds columns to the table and
        fills the non-defined rows with self.options['empty_character'] which is None by default. If the headers are
        different it string adds them"""
        if self==other:
            return
        if self.column_names is other.column_names:
            for row in other.data:
                self.add_row(row)
        else:
            for column in other.column_names:
                self.add_column(column)
            for row in other.data:
                data=[self.options['empty_value'] for i in self.column_names]
                self.add_row(data.append(row))

        if self.header is not other.header:
            self.header=self.header+other.header

        if self.header is not other.header:
            self.header=self.header+other.header
        return self

    def is_valid(self):
        """Returns True if ascii table conforms to its specification given by options"""
        self.update_model()
        self.string=self.build_string()
        self.lines=self.string.split("\n")
        newtable=AsciiDataTable()
        newtable.lines=self.lines
        newtable.options=self.options
        newtable.__parse__()
        return self==newtable
        # create a clone and then parse the clone and compare it to the
        # original. If they are equal then it is valid
        #self.add_inline_comments()

    def __eq__(self, other):
        """Defines what being equal means for the AsciiDataTable Class"""
        compare_elements=['options','header','column_names','data','footer']
        truth_table=[]
        output=False
        for item in compare_elements:
            if self.__dict__[item]==other.__dict__[item]:
                truth_table.append(True)
            else:
                truth_table.append(False)
        if False in truth_table:
            output=False
        else:
            output=True
        #print(truth_table)
        return output

    def __ne__(self,other):
        """Defines what being not equal means for the AsciiDataTable Class"""
        compare_elements=['options','header','column_names','data','footer']
        truth_table=[]
        output=True
        for item in compare_elements:
            if self.__dict__[item]==other.__dict__[item]:
                truth_table.append(True)
            else:
                truth_table.append(False)
        if False in truth_table:
            output=True
        else:
            output=False
        return output

    def add_row(self,row_data):
        """Adds a single row given row_data which can be an ordered list/tuple or a dictionary with
        column names as keys"""
        if len(row_data) not in [len(self.column_names),len(self.column_names)]:
            print(" could not add the row")
            return
        if type(row_data) in [ListType,np.ndarray]:
            self.data.append(row_data)
        elif type(row_data) in [DictionaryType]:
            data_list=[row_data[column_name] for column_name in self.column_names]
            self.data.append(data_list)


    def add_column(self,column_name=None,column_type=None,column_data=None):
        """Adds a column with column_name, and column_type. If column data is supplied and it's length is the
        same as data(same number of rows) then it is added, else self.options['empty_character'] is added in each
        spot"""
        original_column_names=self.column_names
        try:
            self.column_names.append(column_name)
            if len(column_data) is len(self.data):
                for index,row in enumerate(self.data):
                    row.append(column_data[index])
            else:
                for index,row in enumerate(self.data):
                    row.append(self.options['empty_value'])
                    if column_data is not None:
                        for item in column_data:
                            empty_row=[self.options['empty_value'] for column in original_column_names]
                            self.add_row(empty_row.append(item))
        except:
            self.column_names=original_column_names
            print("Could not add columns")
            pass

    def add_index(self):
        """Adds a column with name index and values that are 0 referenced indices, does nothing if there is
        already a column with name index, always inserts it at the 0 position"""
        if 'index' in self.column_names:
            print("Add Index passed")
            pass
        else:
            self.column_names.insert(0,'index')
            for index,row in enumerate(self.data):
                self.data[index].insert(0,index)
            if self.options['column_types']:
                self.options['column_types'].insert(0,'int')
            if self.options['row_formatter_string']:
                self.options['row_formatter_string']='{0}{delimiter}'+self.options['row_formatter_string']

    def move_footer_to_header(self):
        """Moves the DataTable's footer to the header and updates the model"""
        # check to see if the footer is defined
        if self.footer is None:
            return
        try:
          for item in self.footer:
              self.header.append(item)
        except:
          self.header=ensure_string(self.header)+ensure_string(self.footer)
        self.footer=None

    # This actually operated on self.lines before parsing and not directly on self.header
    def add_comment(self,comment):
        "Adds a line comment to the header"
        new_comment=line_comment_string(comment,comment_begin=self.options["comment_begin"],
                                               comment_end=self.options["comment_end"])
        self.header=self.header.append(new_comment)

    def add_inline_comment(self,comment="",line_number=None,string_position=None):
        "Adds an inline in the specified location"
        try:
            self.inline_comments.append([comment,line_number,string_position])
        except:pass

    def add_block_comment(self,comment,element=None,location=None):
        "Adds a block comment in the specified location"
        pass

    def get_options(self):
        "Prints the option list"
        for key,value in self.options.iteritems():
            print("{0} = {1}".format(key,value))

    def get_column(self,column_name=None,column_index=None):
        """Returns a column as a list given a column name or column index"""
        if column_name is None:
            if column_index is None:
                return
            else:
                column_selector=column_index
        else:
            column_selector=self.column_names.index(column_name)
        out_list=[self.data[i][column_selector] for i in range(len(self.data))]
        return out_list
#-----------------------------------------------------------------------------
# Module Scripts
def test_AsciiDataTable():
    options={"column_names":["a","b","c"],"data":[[0,1,2],[2,3,4]],"data_delimiter":'\t',
             "header":['Hello There\n',"My Darling"],"column_names_begin_token":'!',"comment_begin":'#',
             "directory":TESTS_DIRECTORY}
    new_table=AsciiDataTable(file_path=None,**options)
    print new_table.data
    #print dir(new_table)
    for key,value in new_table.options.iteritems():
        print("{0} = {1}".format(key,value))
    print new_table.get_header_string()
    print new_table.get_data_string()
    print new_table.build_string()
    print new_table.path
    new_table.save()
    print("Test add_index")
    new_table.add_index()
    new_table.add_index()
    new_table.add_index()
    print new_table
    new_table.data[1][0]=4
    print new_table
    new_table.update_index()
    print new_table
def test_open_existing_AsciiDataTable():
    # options={"data_delimiter":'\t','column_names_delimiter':',',
    #          "column_names_begin_token":'!',"comment_begin":'#',
    #          "directory":TESTS_DIRECTORY,'header_begin_line':0,'header_end_line':2,'column_names_begin_line':2,
    #          'column_names_end_line':3,'data_begin_line':3,'data_end_line':5}
    # os.chdir(TESTS_DIRECTORY)
    # new_table=AsciiDataTable(file_path="Data_Table_20160225_001.txt",**options)
    # #print new_table.string
    # print new_table.lines
    # print new_table.header
    # print new_table.get_header_string()
    # print new_table.column_names
    # print new_table.get_column_names_string()
    # print new_table.data
    # print new_table.get_data_string()
    # print new_table.footer
    # print new_table.get_footer_string()
    # options={"data_delimiter":'\t','column_names_delimiter':',',
    #          "column_names_begin_token":'!',"comment_begin":'#',
    #          "directory":TESTS_DIRECTORY,'header_begin_line':0,'column_names_begin_line':2,
    #          'data_begin_line':3}
    # os.chdir(TESTS_DIRECTORY)
    # new_table=AsciiDataTable(file_path="Data_Table_20160225_001.txt",**options)
    # new_table.get_options_by_element('columns')
    # print new_table.lines
    # print new_table.header
    # print new_table.get_header_string()
    # print new_table.column_names
    # print new_table.get_column_names_string()
    # print new_table.data
    # print new_table.get_data_string()
    # print new_table.footer
    # print new_table.get_footer_string()
    options={"data_delimiter":'\t','column_names_delimiter':',',
             "column_names_begin_token":'!',"comment_begin":'#',
             "directory":TESTS_DIRECTORY,'header_end_line':2,'column_names_end_line':3,
             'data_end_line':-1}
    os.chdir(TESTS_DIRECTORY)
    new_table=AsciiDataTable(file_path="Data_Table_20160225_001.txt",**options)
    new_table.get_options_by_element('columns')
    print new_table.lines
    print new_table.header
    print new_table.get_header_string()
    print new_table.column_names
    print new_table.get_column_names_string()
    print new_table.data
    print new_table.get_data_string()
    print new_table.footer
    print new_table.get_footer_string()
    print new_table
    temp_options={"data_delimiter":',','column_names_delimiter':',',
             "column_names_begin_token":'#',"comment_begin":'#',"comment_end":'\n',
             "directory":TESTS_DIRECTORY,'header_begin_token':'BEGIN HEADER\n',
                  'header_end_token':'END HEADER','data_begin_token':'BEGIN DATA\n','data_end_token':"END DATA"}
    new_table.save('new_test_table.txt',**temp_options)
def test_AsciiDataTable_equality():
    options={"column_names":["a","b","c"],"data":[[0,1,2],[2,3,4]],"data_delimiter":'\t',
             "header":['Hello There\n',"My Darling"],"column_names_begin_token":'!',"comment_begin":'#',
             "directory":TESTS_DIRECTORY}
    new_table=AsciiDataTable(file_path=None,**options)
    print new_table.data
    new_table_2=AsciiDataTable()
    new_table_2.options=new_table.options
    new_table_2.header=new_table.header
    new_table_2.column_names=new_table.column_names
    new_table_2.data=[[0,1,2],[2,3,4]]
    print new_table==new_table_2
    print new_table!=new_table_2
    new_table_2.data[0][0]=9

    print new_table.data==new_table_2.data
    print new_table==new_table_2
    print new_table_2
    print new_table
def test_inline_comments():
    options={"column_names":["a","b","c"],"data":[[0,1,2],[2,3,4]],"data_delimiter":'\t',
             "header":['Hello There\n',"My Darling"],"column_names_begin_token":'!',"comment_begin":'#',
             "directory":TESTS_DIRECTORY,'inline_comment_begin':'(*','inline_comment_end':'*)',
             'inline_comments':[["My Inline Comment",0,5]]}
    new_table=AsciiDataTable(**options)
    print new_table
def test_add_row():
    options={"column_names":["a","b","c"],"data":[[0,1,2],[2,3,4]],"data_delimiter":'\t',
             "header":['Hello There\n',"My Darling"],"column_names_begin_token":'!',"comment_begin":'#',
             "directory":TESTS_DIRECTORY}
    new_table=AsciiDataTable(**options)
    print "Table before add row"
    print new_table
    print "Add the row 0,1,3"
    new_table.add_row([0,1,3])
    print new_table
def test_add_index():
    options={"column_names":["a","b","c"],"data":[[0,1,2],[2,3,4]],"data_delimiter":'\t',
             "header":['Hello There\n',"My Darling"],"column_names_begin_token":'!',"comment_begin":'#',
             "directory":TESTS_DIRECTORY,'treat_header_as_comment':False}
    new_table=AsciiDataTable(**options)
    print "Table before add row"
    print "*"*80
    print new_table
    print "Add the row 0,1,3"
    print "*"*80
    new_table.add_row([0,1,3])
    print new_table
    print "Add an index"
    print "*"*80
    new_table.add_index()
    print new_table
    print "Now Get the index column"
    print new_table.get_column(column_name='index')

#-----------------------------------------------------------------------------
# Module Runner
if __name__ == '__main__':
    #test_AsciiDataTable()
    #test_open_existing_AsciiDataTable()
    #test_AsciiDataTable_equality()
    #test_inline_comments()
    #test_add_row()
    test_add_index()
#-----------------------------------------------------------------------------
# Name:        Translations
# Purpose:     To translate from one data form to another
# Author:      Aric Sanders
# Created:     3/3/2016
# License:     MIT License
#-----------------------------------------------------------------------------
""" Translations.py holds the functions that map from one form to another"""

#-----------------------------------------------------------------------------
# Standard Imports
import timeit
#-----------------------------------------------------------------------------
# Third Party Imports
try:
    from pyMeasure.Code.DataHandlers.GeneralModels import *
except:
    print("The module pyMeasure.Code.DataHandlers.GeneralModels was not found,"
          "please put it on the python path")
    raise ImportError
try:
    from pyMeasure.Code.DataHandlers.XMLModels import *
except:
    print("The module pyMeasure.Code.DataHandlers.XMLModels was not found,"
          "please put it on the python path")
    raise ImportError
try:
    from pyMeasure.Code.DataHandlers.NISTModels import *
except:
    print("The module pyMeasure.Code.DataHandlers.NISTModels was not found,"
          "please put it on the python path")
    raise ImportError
try:
    import pandas
except:
    print("The module pandas was not found,"
          "please put it on the python path")
    raise ImportError
#-----------------------------------------------------------------------------
# Module Constants

#-----------------------------------------------------------------------------
# Module Functions
def AsciiDataTable_to_XMLDataTable(ascii_data_table,**options):
    """Takes an AsciiDataTable and returns a XMLDataTable with **options"""
    defaults={"specific_descriptor":ascii_data_table.options["specific_descriptor"],
                     "general_descriptor":ascii_data_table.options["general_descriptor"],
                      "directory":ascii_data_table.options["directory"],
              "style_sheet":"../XSL/ONE_PORT_STYLE.xsl"
                     }
    XML_options={}
    for key,value in defaults.iteritems():
        XML_options[key]=value
    for key,value in options.iteritems():
        XML_options[key]=value
    data_description={}
    if ascii_data_table.options["column_descriptions"] is not None:
        for key,value in ascii_data_table.options["column_descriptions"].iteritems():
            data_description[key]=value
    if ascii_data_table.header is not None:
        for index,line in enumerate(ascii_data_table.header):
            key="Header_{0:0>3}".format(index)
            data_description[key]=line
    if ascii_data_table.footer is not None:
        for index,line in enumerate(ascii_data_table.footer):
            key="Footer_{0:0>3}".format(index)
            data_description[key]=line
    data_dictionary={"Data_Description":data_description,"Data":ascii_data_table.get_data_dictionary_list()}
    XML_options["data_dictionary"]=data_dictionary
    new_xml_data_table=DataTable(None,**XML_options)
    return new_xml_data_table

def AsciiDataTable_to_DataFrame(ascii_data_table):
    """Converts an AsciiDataTable to a pandas.DataFrame
    discarding any header or footer information"""
    data_frame=pandas.DataFrame(data=ascii_data_table.data,columns=ascii_data_table.column_names)
    return data_frame

def AsciiDataTable_to_Excel(ascii_data_table,file_path=None):
    """Converts an AsciiDataTable to an excel spreadsheet using pandas"""
    if ascii_data_table.header:
        data_frame=pandas.DataFrame(data=ascii_data_table.data,columns=ascii_data_table.column_names)


#-----------------------------------------------------------------------------
# Module Classes

#-----------------------------------------------------------------------------
# Module Scripts
def test_AsciiDataTable_to_XMLDataTable(input_file="700437.asc"):
    os.chdir(TESTS_DIRECTORY)
    one_port=OnePortModel(input_file)
    XML_one_port=AsciiDataTable_to_XMLDataTable(one_port)
    print XML_one_port
    XML_one_port.save()

def test_AsciiDataTable_to_DataFrame(input_file="700437.asc"):
    os.chdir(TESTS_DIRECTORY)
    one_port=OnePortModel(input_file)
    data_frame=AsciiDataTable_to_pandas(one_port)
    data_frame.to_excel('one_port.xlsx', sheet_name='Sheet1')
    #print data_frame

def timeit_script(script='test_AsciiDataTable_to_XMLDataTable()',
                  setup="from __main__ import test_AsciiDataTable_to_XMLDataTable",n_loops=10):
    print timeit.timeit(script,setup=setup,number=n_loops)/n_loops
#-----------------------------------------------------------------------------
# Module Runner
if __name__ == '__main__':
    test_AsciiDataTable_to_XMLDataTable()
    #test_AsciiDataTable_to_pandas()
    #timeit_script()
    #timeit_script(script="test_AsciiDataTable_to_pandas()",
     #             setup="from __main__ import test_AsciiDataTable_to_pandas",n_loops=10)
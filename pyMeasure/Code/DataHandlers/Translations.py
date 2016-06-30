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
    from pyMeasure.Code.DataHandlers.TouchstoneModels import *
except:
    print("The module pyMeasure.Code.DataHandlers.TouchstoneModels was not found,"
          "please put it on the python path")
    raise ImportError
try:
    import pandas
except:
    print("The module pandas was not found,"
          "please put it on the python path")
    raise ImportError
try:
    import odo
except:
    print("The module odo was not found,"
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
        if type(ascii_data_table.options["column_descriptions"]) is DictionaryType:
            for key,value in ascii_data_table.options["column_descriptions"].iteritems():
                data_description[key]=value
        elif type(ascii_data_table.options["column_descriptions"]) is ListType:
            for index,value in enumerate(ascii_data_table.options["column_descriptions"]):
                key=ascii_data_table.column_names[index]
                data_description[key]=value

    if ascii_data_table.metadata is not None:
        for key,value in ascii_data_table.metadata.iteritems():
            data_description[key]=value
    else:
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
        data_frame=pandas.DataFrame(data=ascii_data_table.data,columns=ascii_data_table.column_names,index=False)

def S2PV1_to_XMLDataTable(s2p,**options):
    """Transforms a s2p's sparameters to a XMLDataTable. Converts the format to #GHz DB first"""
    defaults={"specific_descriptor":s2p.options["specific_descriptor"],
                     "general_descriptor":s2p.options["general_descriptor"],
                      "directory":s2p.options["directory"],
              "style_sheet":"../XSL/S2P_DB_STYLE.xsl"
                     }
    XML_options={}
    for key,value in defaults.iteritems():
        XML_options[key]=value
    for key,value in options.iteritems():
        XML_options[key]=value
    data_description={}
    if s2p.options["column_descriptions"] is not None:
        for key,value in s2p.options["column_descriptions"].iteritems():
            data_description[key]=value
    if s2p.metadata is not None:
        for key,value in s2p.metadata.iteritems():
            data_description[key]=value
    else:
        if s2p.comments is not None:
            for index,line in enumerate(s2p.comments):
                key="Comments_{0:0>3}".format(index)
                data_description[key]=line[0]
    s2p.change_data_format(new_format='DB')
    s2p.change_frequency_units('GHz')
    data_dictionary={"Data_Description":data_description,"Data":s2p.get_data_dictionary_list()}
    XML_options["data_dictionary"]=data_dictionary
    new_xml_data_table=DataTable(None,**XML_options)
    return new_xml_data_table

def S1PV1_to_XMLDataTable(s1p,**options):
    """Transforms a s1p's sparameters to a XMLDataTable. Converts the format to RI first"""
    defaults={"specific_descriptor":s1p.options["specific_descriptor"],
                     "general_descriptor":s1p.options["general_descriptor"],
                      "directory":s1p.options["directory"],
              "style_sheet":"../XSL/S1P_STYLE.xsl"
                     }
    XML_options={}
    for key,value in defaults.iteritems():
        XML_options[key]=value
    for key,value in options.iteritems():
        XML_options[key]=value
    data_description={}
    if s1p.options["column_descriptions"] is not None:
        for key,value in s1p.options["column_descriptions"].iteritems():
            data_description[key]=value
    if s1p.metadata is not None:
        for key,value in s1p.metadata.iteritems():
            data_description[key]=value
    else:
        if s1p.comments is not None:
            for index,line in enumerate(s1p.comments):
                key="Comments_{0:0>3}".format(index)
                data_description[key]=line[0]
    s1p.change_data_format(new_format='RI')
    s1p.change_frequency_units('GHz')
    data_dictionary={"Data_Description":data_description,"Data":s1p.get_data_dictionary_list()}
    XML_options["data_dictionary"]=data_dictionary
    new_xml_data_table=DataTable(None,**XML_options)
    return new_xml_data_table

def TwoPortCalrep_to_XMLDataTable(two_port_calrep_table,**options):
    """Converts the 2-port calrep model to xml"""
    table=two_port_calrep_table.joined_table
    defaults={"specific_descriptor":table.options["specific_descriptor"],
                     "general_descriptor":table.options["general_descriptor"],
                      "directory":table.options["directory"],
              "style_sheet":"../XSL/TWO_PORT_CALREP_STYLE.xsl"
                     }
    XML_options={}
    for key,value in defaults.iteritems():
        XML_options[key]=value
    for key,value in options.iteritems():
        XML_options[key]=value
    new_xml=AsciiDataTable_to_XMLDataTable(table,**XML_options)
    return new_xml

#-----------------------------------------------------------------------------
# Module Classes

#-----------------------------------------------------------------------------
# Module Scripts
def test_AsciiDataTable_to_XMLDataTable(input_file="700437.asc"):
    """Tests a one port ascii data table to an XMLDataTable transformation
    and saves the result in the tests directory. The one port file should be the output
    of Calrep7.1 or similar."""
    os.chdir(TESTS_DIRECTORY)
    one_port=OnePortRawModel(input_file)
    XML_one_port=AsciiDataTable_to_XMLDataTable(one_port)
    print XML_one_port
    XML_one_port.save()
    XML_one_port.save_HTML()

def test_OnePortRaw_to_XMLDataTable(input_file="OnePortRawTestFile.txt"):
    """Tests a one port raw ascii data table to an XMLDataTable transformation
    and saves the result in the tests directory. The one port file should be the output
    of Meas HP Basic program or similar. Average time without print is 7.2 ms for 10 loops."""
    os.chdir(TESTS_DIRECTORY)
    one_port=OnePortRawModel(input_file)
    options={"style_sheet":"../XSL/ONE_PORT_RAW_STYLE.xsl"}
    XML_one_port=AsciiDataTable_to_XMLDataTable(one_port,**options)
    #print XML_one_port
    XML_one_port.save()
    XML_one_port.save_HTML()

def test_AsciiDataTable_to_DataFrame(input_file="700437.asc"):
    os.chdir(TESTS_DIRECTORY)
    one_port=OnePortCalrepModel(input_file)
    data_frame=AsciiDataTable_to_DataFrame(one_port)
    data_frame.to_excel('one_port.xlsx', sheet_name='Sheet1')
    #print data_frame

def test_S2P_to_XMLDataTable(file_path="thru.s2p"):
    os.chdir(TESTS_DIRECTORY)
    s2p_file=S2PV1(file_path)
    XML_s2p=S2PV1_to_XMLDataTable(s2p_file)
    XML_s2p.save()
    #print XML_s2p

def timeit_script(script='test_AsciiDataTable_to_XMLDataTable()',
                  setup="from __main__ import test_AsciiDataTable_to_XMLDataTable",n_loops=10):
    """Returns the mean time from running script n_loops time. To import a script, put a string
    import statement in setup"""
    print timeit.timeit(script,setup=setup,number=n_loops)/n_loops

def test_S2P_to_XMLDataTable_02(file_path="thru.s2p",**options):
    os.chdir(TESTS_DIRECTORY)
    s2p_file=S2PV1(file_path)
    XML_s2p=S2PV1_to_XMLDataTable(s2p_file,**options)
    #XML_s2p.save()
def test_TwoPortCalrep_to_XMLDataTable(file_path='922729.asc',**options):
    """Test's the conversion of the TwoPortCalrep to XMLDataTable"""
    os.chdir(TESTS_DIRECTORY)
    two_port=TwoPortCalrepModel(file_path)
    two_port.joined_table.save()
    xml=TwoPortCalrep_to_XMLDataTable(two_port,**options)
    xml.save()
    xml.save_HTML()

#-----------------------------------------------------------------------------
# Module Runner
if __name__ == '__main__':
    #test_AsciiDataTable_to_XMLDataTable()
    #test_OnePortRaw_to_XMLDataTable()
    #test_AsciiDataTable_to_pandas()
    #timeit_script()
    #timeit_script(script="test_AsciiDataTable_to_pandas()",
     #             setup="from __main__ import test_AsciiDataTable_to_pandas",n_loops=10)
    # timeit_script(script="test_OnePortRaw_to_XMLDataTable()",
    #               setup="from __main__ import test_OnePortRaw_to_XMLDataTable",n_loops=10)
    #test_S2P_to_XMLDataTable()
    #test_S2P_to_XMLDataTable('TwoPortTouchstoneTestFile.s2p')
    #test_S2P_to_XMLDataTable('20160301_30ft_cable_0.s2p')
    #test_S2P_to_XMLDataTable_02('20160301_30ft_cable_0.s2p',**{"style_sheet":"../XSL/S2P_STYLE_02.xsl"})
    test_TwoPortCalrep_to_XMLDataTable(r'C:\Share\ascii.dut\000146a.txt')
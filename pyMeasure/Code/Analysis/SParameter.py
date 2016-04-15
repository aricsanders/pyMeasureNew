#-----------------------------------------------------------------------------
# Name:        SParameter.py
# Purpose:    Tools to analyze SParameter Data
# Author:      Aric Sanders
# Created:     4/13/2016
# License:     MIT License
#-----------------------------------------------------------------------------
""" Sparameter is a module with tools for analyzing Sparameter data """
#-----------------------------------------------------------------------------
# Standard Imports

#-----------------------------------------------------------------------------
# Third Party Imports
try:
    import numpy as np
except:
    np.ndarray='np.ndarray'
    print("Numpy was not imported")
    pass
try:
    from pyMeasure.Code.DataHandlers.NISTModels import *
except:
    print("The module pyMeasure.Code.DataHandlers.NISTModels was not found,"
          "please put it on the python path")
    raise ImportError
#-----------------------------------------------------------------------------
# Module Constants

#-----------------------------------------------------------------------------
# Module Functions
def average_one_port_sparameters(table_list,**options):
    """Returns a table that is the average of the Sparameters in table list. The new table will have all the unique
    frequency values contained in all of the tables. Tables must be in Real-Imaginary format or magnitude-angle format
    do not try to average db-angle format. """
    defaults={"frequency_selector":0,"frequency_column_name":"Frequency"}
    average_options={}
    for key,value in defaults.iteritems():
        average_options[key]=value
    for key,value in options.iteritems():
        average_options[key]=value
    frequency_list=[]
    average_data=[]
    for table in table_list:
        frequency_list=frequency_list+table.get_column("Frequency")
    unique_frequency_list=sorted(list(set(frequency_list)))
    for frequency in unique_frequency_list:
        new_row=[]
        for table in table_list:
            data_list=filter(lambda x: x[average_options["frequency_selector"]]==frequency,table.data)
            table_average=np.mean(np.array(data_list),axis=0)
            new_row.append(table_average)
            #print new_row
        average_data.append(np.mean(new_row,axis=0).tolist())
    return average_data

#-----------------------------------------------------------------------------
# Module Classes

#-----------------------------------------------------------------------------
# Module Scripts
def test_average_one_port_sparameters():
    os.chdir(TESTS_DIRECTORY)
    table_list=[OnePortRawModel('OnePortRawTestFileAsConverted.txt') for i in range(3)]
    out_data=average_one_port_sparameters(table_list)
    out_table=OnePortRawModel(None,**{"data":out_data})
    #table_list[0].show()
    #out_table.show()
    fig, (ax0, ax1) = plt.subplots(nrows=2, sharex=True)
    ax0.plot(out_table.get_column('Frequency'),out_table.get_column('magS11'),'k--')
    ax0.plot(table_list[0].get_column('Frequency'),table_list[0].get_column('magS11'),'bx')
    ax0.set_title('Magnitude S11')
    ax1.plot(out_table.get_column('Frequency'),out_table.get_column('argS11'),'ro')
    ax1.plot(table_list[0].get_column('Frequency'),table_list[0].get_column('argS11'),'bx')
    ax1.set_title('Phase S11')
    plt.show()
    print out_table

#-----------------------------------------------------------------------------
# Module Runner
if __name__ == '__main__':
    test_average_one_port_sparameters()
    
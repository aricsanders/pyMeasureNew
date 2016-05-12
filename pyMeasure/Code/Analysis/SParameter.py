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
    import pandas
except:
    print("Pandas was not imported")
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
    #This will work on any table that the data is stored in data, need to add a sparameter version
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

def two_port_comparision_plot_with_residuals(two_port_raw,mean_frame,difference_frame):
    """Creates a comparision plot given a TwoPortRawModel object and a pandas.DataFrame mean frame"""
    fig, axes = plt.subplots(nrows=3, ncols=2, sharex='col',figsize=(8,6),dpi=80)
    measurement_date=two_port_raw.metadata["Measurement_Date"]
    ax0,ax1,ax2,ax3,ax4,ax5 = axes.flat
    compare_axes=[ax0,ax1,ax2,ax3,ax4,ax5]
    diff_axes=[]
    for ax in compare_axes:
        diff_axes.append(ax.twinx())
    #diff_axes=[diff_ax0,diff_ax1,diff_ax2,diff_ax3,diff_ax4,diff_ax5]
    column_names=['Frequency','magS11','argS11','magS21','argS21','magS22','argS22']
    for index,ax in enumerate(diff_axes):
        ax.plot(difference_frame['Frequency'].tolist(),difference_frame[column_names[index+1]].tolist(),'r-x')
        ax.set_ylabel('Difference',color='red')
        if re.search('mag',column_names[index+1]):
            ax.set_ylim(-.02,.02)
        #ax.legend_.remove()
    for index, ax in enumerate(compare_axes):
        ax.plot(two_port_raw.get_column('Frequency'),two_port_raw.get_column(column_names[index+1]),
                'k-o',label=measurement_date)
        ax.plot(mean_frame['Frequency'].tolist(),mean_frame[column_names[index+1]].tolist(),'gs',label='Mean')
        ax.set_title(column_names[index+1])
        ax.legend(loc=1,fontsize='8')
        #ax.xaxis.set_visible(False)
        if re.search('arg',column_names[index+1]):
            ax.set_ylabel('Phase(Degrees)',color='green')
        elif re.search('mag',column_names[index+1]):
            ax.set_ylabel(r'|${\Gamma} $|',color='green')
        #ax.sharex(diff_axes[index])
    ax4.set_xlabel('Frequency(GHz)',color='k')
    ax5.set_xlabel('Frequency(GHz)',color='k')
    fig.subplots_adjust(hspace=0)
    fig.suptitle(two_port_raw.metadata["Device_Id"]+"\n",fontsize=18,fontweight='bold')
    plt.tight_layout()
    plt.show()

def two_port_difference_frame(two_port_raw,mean_frame):
    """Creates a difference pandas.DataFrame given a two port raw file and a mean pandas.DataFrame"""
    difference_list=[]
    for row in two_port_raw.data[:]:
        #print row[0]
        mean_row=mean_frame[abs(mean_frame["Frequency"]-row[0])<abs(.01)].as_matrix()
        #print mean_row
        try:
            mean_row=mean_row[0]
            difference_row=[row[i+2]-mean_row[i] for i in range(1,len(mean_row))]
            difference_row.insert(0,row[0])
            difference_list.append(difference_row)
        except:pass
    column_names=['Frequency','magS11','argS11','magS21','argS21','magS22','argS22']
    diff_data_frame=pandas.DataFrame(difference_list,columns=column_names)
    return diff_data_frame

def two_port_mean_frame(device_id,system_id=None,history_data_frame=None):
    """Given a Device_Id and a pandas data frame of the history creates a mean data_frame"""
    device_history=history_data_frame[history_data_frame["Device_Id"]==device_id]
    if system_id is not None:
        device_history=device_history[device_history["System_Id"]==system_id]
    column_names=['Frequency','magS11','argS11','magS21','argS21','magS22','argS22']
    unique_frequency_list=device_history["Frequency"].unique()
    mean_array=[]
    for index,freq in enumerate(unique_frequency_list):
        row=[]
        for column in column_names:
            values=np.mean(device_history[device_history["Frequency"]==unique_frequency_list[index]][column].as_matrix())
            #print values
            mean_value=np.mean(values)
            row.append(mean_value)
        mean_array.append(row)
    mean_frame=pandas.DataFrame(mean_array,columns=column_names)
    return mean_frame
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
    
#-----------------------------------------------------------------------------
# Name:        XMLModels.py
# Purpose:     To define XML models
# Author:      Aric Sanders
# Created:     2/21/2016
# License:     MIT License
#-----------------------------------------------------------------------------
""" XMLModels is dedicated to handling xml based models,
requires lxml to be installed. """

#-----------------------------------------------------------------------------
# Standard Imports
import os
import xml.dom                                     # Xml document handling
import xml.dom.minidom                             # For xml parsing
from xml.dom.minidom import getDOMImplementation   # Making blank XML documents
import datetime
#-----------------------------------------------------------------------------
# Third Party Imports
# For XLST transformations of the data
try:
    from lxml import etree
    XSLT_CAPABLE=1
except:
    print("Transformations using XSLT are not available please check the lxml module")
    XSLT_CAPABLE=0
    pass
# For auto generation of common method aliases
try:
    from pyMeasure.Code.Utils.Alias import *
    METHOD_ALIASES=1
except:
    print("The module pyMeasure.Code.Utils.Alias was not found")
    METHOD_ALIASES=0
    pass
# For Auto-naming of files if path is not specified
try:
    from pyMeasure.Code.Utils.Names import auto_name
    DEFAULT_FILE_NAME=None
except:
    print("The function auto_name in pyMeasure.Code.Utils.Names was not found")
    print("Setting Default file name to New_XML.xml")
    DEFAULT_FILE_NAME='New_XML.xml'
    pass
#-----------------------------------------------------------------------------
# Module Constants
XSLT_REPOSITORY='../XSL'
TESTS_DIRECTORY=os.path.join(os.path.dirname(os.path.realpath(__file__)),'Tests')
#-----------------------------------------------------------------------------
# Module Functions

#-----------------------------------------------------------------------------
# Module Classes
class XMLBase():
    """ The XMLBase Class is designed to be a container for xml data
    """
    def __init__(self,file_path=None,**options):
        "Initializes the XML Base Class "
        if file_path is not None:
            self.path=file_path
        # This is a general pattern for adding a lot of options
        # The next more advanced thing to do is retrieve defaults from a settings file
        defaults={"root":"root",
                  "style_sheet":os.path.join(XSLT_REPOSITORY,'DEFAULT_STYLE.xsl').replace('\\','/'),
                  "specific_descriptor":'XML',
                  "general_descriptor":'Document',
                  "directory":None,
                  "extension":'xml'
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
        #if the file path is not supplied create a new xml sheet
        if file_path is None:
            impl=getDOMImplementation()
            self.document=impl.createDocument(None,self.options['root'],None)
            # Should be a relative path for
            new_node=self.document.createProcessingInstruction('xml-stylesheet',
            u'type="text/xsl" href="%s"'%self.options['style_sheet'])
            self.document.insertBefore(new_node,self.document.documentElement)
            if DEFAULT_FILE_NAME is None:
                self.path=auto_name(self.options["specific_descriptor"],
                                    self.options["general_descriptor"],
                                    self.options["directory"],
                                    self.options["extension"])
            else:
                # Just a backup plan if the python path is messed up
                self.path=DEFAULT_FILE_NAME
        else:
            file_in=open(file_path,'r')
            self.document=xml.dom.minidom.parse(file_in)
            file_in.close()
            self.path=file_path

    def save(self,path=None):
        """" Saves as an XML file"""
        if path is None:
            path=self.path
        file_out=open(path,'w')
        file_out.write(self.document.toprettyxml())
        file_out.close()

    if XSLT_CAPABLE:
        def to_HTML(self,XSLT=None):
            """ Returns HTML string by applying a XSL to the XML document"""
            if XSLT is None:
                # For some reason an absolute path tends to break here, maybe a spaces in file names problem
                XSLT=self.options['style_sheet']
            XSL_data=etree.parse(XSLT)
            XSL_transform=etree.XSLT(XSL_data)
            HTML=XSL_transform(etree.XML(self.document.toxml()))
            return HTML
    def __str__(self):
        "Controls how XMLBAse is returned when a string function is called"
        return self.document.toxml()
class Log(XMLBase):
    """ Data container for a general Log"""
    def __init__(self,file_path=None,**options):
        """ Intializes the Log"""
        # We add the defaults for the log pass and the options along
        defaults={"root":'Log',
                  'style_sheet':os.path.join(XSLT_REPOSITORY,'DEFAULT_LOG_STYLE.xsl').replace('\\','/'),
                  'entry_style_sheet':os.path.join(XSLT_REPOSITORY,'DEFAULT_LOG_STYLE.xsl').replace('\\','/'),
                  'specific_descriptor':'Log','general_descriptor':'XML'}
        self.options={}
        for key,value in defaults.iteritems():
            self.options[key]=value
        for key,value in options.iteritems():
            self.options[key]=value
        XMLBase.__init__(self,file_path,**self.options)
        # TODO: Check how scalable a dictionary of nodes is
        self.Index_node_dictionary=dict([(str(node.getAttribute('Index')),
        node) for node in \
        self.document.getElementsByTagName('Entry')])   
        self.current_entry={}
                   
    def add_entry(self,entry=None):
        """ Adds an entry element to the current log"""
        root=self.document.documentElement
        if entry is None:
            new_entry=self.document.createElement('Entry')
            value=''
        elif type(entry) is str:
            if re.search('<Entry>(.)+</Entry>',entry):
                new_document=xml.dom.minidom.parseString(new_entry)
                new_entry=new_document.documentElement
            else:
                new_document=xml.dom.minidom.parseString('<Entry>'
                +entry+'</Entry>')
                new_entry=new_document.documentElement
        else:
            new_entry=entry
        # Find the max of Index's and add 1 to make a new Index
        if len(self.Index_node_dictionary)==0:
            new_Index='1'
        else:
            max_Index=max([int(Index) for Index in self.Index_node_dictionary.keys()])
            new_Index=str(max_Index+1)
        # Add the Index attribute to the new entry
        Index_attribute=self.document.createAttribute('Index')
        new_entry.setAttributeNode(Index_attribute)
        new_entry.setAttribute('Index',str(new_Index))
        if new_entry.getAttribute('Date'):
            pass
        else:
            # Add the Date attribute, this is the time when the entry was logged
            date=datetime.datetime.utcnow().isoformat()
            Date_attribute=self.document.createAttribute('Date')
            new_entry.setAttributeNode(Date_attribute)
            new_entry.setAttribute('Date',str(date))
        # Now append the new Child        
        root.appendChild(new_entry)
        self.update_Index_node_dictionary()
        
        try:
            value=new_entry.childNodes[0].data
        except:
            value=''
             
        self.current_entry={'Tag':'Entry','Value':value,'Index':new_entry.getAttribute('Index'),
        'Date':new_entry.getAttribute('Date')} 
        
    def edit_entry(self,old_Index,new_value=None,new_Index=None,new_Date=None):
        """Edits and existing entry by replacing the existing values with new ones"""
        node=self.get_entry(str(old_Index))
        if not new_value is None:
            new_text_node=self.document.createTextNode(new_value)
            try:
                old_text_node=node.childNodes[0]
                node.removeChild(old_text_node)
            except: pass
            node.appendChild(new_text_node)
            
        elif not new_Index is None:
            node.setAttribute('Index',new_Index)
        elif not new_Date is None:
            node.setAttribute('Date',new_Date)
        self.current_entry={'Tag':'Entry','Value':node.childNodes[0].data,'Index':node.getAttribute('Index'),
        'Date':node.getAttribute('Date')}    
                
    def get_entry(self,Index):
        """ Returns the entry selcted by Index"""
        return self.Index_node_dictionary[str(Index)]
    
    def set_current_entry(self,Index=-1):
        """Sets self.current_entry """
        entry=self.Index_node_dictionary[str(Index)]
        try:
            value=entry.childNodes[0].data
        except:
            value=''
        self.current_entry={'Tag':'Entry','Value':value,'Index':entry.getAttribute('Index'),
        'Date':entry.getAttribute('Date')}            
    def remove_entry(self,Index):
        """ Removes the entry using the Index attribute"""
        root=self.document.documentElement
        root.removeChild(self.Index_node_dictionary[Index])
        self.update_Index_node_dictionary()
        
    def add_description(self,description=None):
        """ Adds an entry with Index='-1' which holds data about the log itself"""
        root=self.document.documentElement
        new_entry=self.document.createElement('Entry')
        if not description is None:
            text_node=self.document.createTextNode(description)
            new_entry.appendChild(text_node)
        # Add the Index attribute to the new entry
        Index_attribute=self.document.createAttribute('Index')
        new_entry.setAttributeNode(Index_attribute)
        new_entry.setAttribute('Index',str(-1))
        # Add the Date attribute, this is the time when the entry was logged
        date=datetime.datetime.utcnow().isoformat()
        Date_attribute=self.document.createAttribute('Date')
        new_entry.setAttributeNode(Date_attribute)
        new_entry.setAttribute('Date',str(date))
        # Now append the new Child        
        root.appendChild(new_entry)
        self.update_Index_node_dictionary()
            
    def update_Index_node_dictionary(self):
        """ Re-creates the attribute self.Index_node_dictionary, using the current
        definition of self.document"""
        self.Index_node_dictionary=dict([(str(node.getAttribute('Index')),
        node) for node in \
        self.document.getElementsByTagName('Entry')])
    # if the XSLT engine loaded then define a transformation to HTML    
    if XSLT_CAPABLE:
        def current_entry_to_HTML(self,XSLT=None):
            """ Returns HTML string by applying a XSL to the XML document"""
            if XSLT is None:
                XSLT=self.options['entry_style_sheet']
            XSL_data=etree.parse(XSLT)
            XSL_transform=etree.XSLT(XSL_data)
            current_entry_XML=self.Index_node_dictionary[self.current_entry['Index']]
            HTML=XSL_transform(etree.XML(current_entry_XML.toxml())) 
            return HTML         
    
    # TODO: Make show and display function work well
    def previous_entry(self):
        """Sets current entry to the one before"""
        if len(self.current_entry)>0:
            Index=int(self.current_entry['Index'])
        else:
            return
        new_Index=Index-1
        try:
            self.set_current_entry(new_Index)
        except KeyError:
            Indexs=map(lambda x:int(x),self.Index_node_dictionary.keys()) 
            if min(Indexs)<Index:
               Indexs.sort()
               new_Index=Indexs[Indexs.index(Index)-1]
            else:
                Indexs.remove(Index)
                if len(Indexs)>0:
                    new_Index=max(Indexs)
                else:
                    new_Index=Index
        self.set_current_entry(new_Index)
   
    def next_entry(self):
        """Sets current entry to the one after"""
        if len(self.current_entry)>0:
            Index=int(self.current_entry['Index'])
        else:
            return
        new_Index=Index+1
        try:
            self.set_current_entry(new_Index)
        except KeyError:
            Indexs=map(lambda x:int(x),self.Index_node_dictionary.keys()) 
            if max(Indexs)>Index:
               Indexs.sort()
               new_Index=Indexs[Indexs.index(Index)+1]
            else:
                Indexs.remove(Index)
                new_Index=min(Indexs)
        self.set_current_entry(new_Index)

    def show(self,mode='text'):
        """ Displays a Log either as formatted text in the command line or in a 
        window (using wx)"""
        def tag_to_tagName(tag):
            tagName=tag.replace('<','')
            tagName=tagName.replace('/','')
            tagName=tagName.replace('>','')
            return tagName
        if mode in ['text','txt','cmd line','cmd']:
            for node in self.document.getElementsByTagName('Entry'):
                print 'Entry Index: %s \tDate: %s'%(node.getAttribute('Index'),
                node.getAttribute('Date'))
                print node.firstChild.nodeValue
        elif re.search('xml',mode,re.IGNORECASE):
            for node in self.document.getElementsByTagName('Entry'):
                print node.toprettyxml()
        elif re.search('Window|wx',mode,re.IGNORECASE):
            try:
                import wx
                import wx.html
            except:
                print 'Cannot locate wx, please add to sys.path'
            app = wx. wx.App(False)
            frame=wx.Frame(None)
            html_window=wx.html.HtmlWindow(frame)
            html_window.SetPage(str(self.to_HTML()))
            frame.Show()
            app.MainLoop()

    def __add__(object,right):
        """Controls Behavior of two Logs added using the + operator"""
        new_log=object
        for entry in right.document.getElementsByTagName('Entry'):
            if entry.getAttribute('Index')=='-1':
                pass    
            else:
                new_log.add_entry(entry)
        return new_log
class ChangeLog(Log):
    """ A Log for storing changes to a program"""
    def __init__(self,path=None,program_name=None):
        Log.__init__(self,path)
        # set the description element if it is a new log
        if path is None:
            self.add_ChangeLog_description(program_name)
            
    def add_ChangeLog_description(self,program_name=None):
        """ Adds a description of the change log as element Index=-1"""
        if program_name is None:
            program_name='a program'
        description="""This is a change log for %s. It consists of entries with
        a date attribute, an Index attribute that is a simple integer, and text 
        describing the changes made to %s."""%(program_name,program_name)
        self.add_description(description)
class EndOfDayLog(Log):
    """ A Log for storing notes about daily activities"""
    def __init__(self,path=None):
        options={"style_sheet":os.path.join(XSLT_REPOSITORY,'DEFAULT_STYLE.xsl').replace('\\','/')}
        Log.__init__(self,path,**options)
        if path is None:
            self.add_EndOfDayLog_description()
        self.information_tags=['Actions','Who_Did','Who_Suggested','Why','Conclusion','Data_Location']
    def add_entry_information(self,Index=None,**entry):
        """ Adds a log specific entry takes a dicitionary in the form 
        {'tag':value,..} this does not add atributes"""
        if Index is None:
            self.add_entry()
            Index=self.current_entry['Index']
            
        try:
            node=self.get_entry(Index)
        except:
            raise
        for tag,value in entry.iteritems():
            new_element=self.document.createElement(tag)
            new_text=self.document.createTextNode(str(value))
            new_element.appendChild(new_text)
            node.appendChild(new_element)
    def add_EndOfDayLog_description(self,program_name=None):
        """ Adds a description of the log as element Index=-1"""
        description="""This is a End of day log. It consists of entries with
        a date attribute, an Index attribute that is a simple integer, and xml tags 
        describing daily activities""" 
        self.add_description(description)
    
class ErrorLog(Log):
    """ A Log for storring errors generated by a program """
    def __init__(self,path=None):
        Log.__init__(self,path) 
        
class ServiceLog(Log):
    """ A Log for servicing an instrument or experiment """
    def __init__(self,path=None,instrument_name=None):
        Log.__init__(self,path)     
#-----------------------------------------------------------------------------
# Module Scripts
def test_XMLModel(test_new=True,test_existing=False):
    """ a test of the XMLBase class
    """
    if test_new:
        print("Begin Test of a New XML sheet \n")
        os.chdir(TESTS_DIRECTORY)
        new_xml=XMLBase(None,**{'style_sheet':'../XSL/DEFAULT_STYLE.xsl'})
        print("The New Sheet has been created as new_xml \n")
        print('*'*80)
        print("The New File Path is {0}".format(os.path.join(TESTS_DIRECTORY,new_xml.path)))
        print('*'*80)
        print("The result of print new_xml")
        print(new_xml)
        print('*'*80)
        print("The result of new_xml.to_HTML()")
        print new_xml.to_HTML()
        print('*'*80)
        print("The result of new_xml.options")
        print new_xml.options
        print('*'*80)
        print("The new_xml has been saved")
        new_xml.save()
    if test_existing:
        print("Begin Test of a Preexisting XML sheet \n")
        os.chdir(TESTS_DIRECTORY)
        new_xml=XMLBase('Data_Table_021311_1.xml',**{'style_sheet':'../XSL/DEFAULT_STYLE.xsl'})
        print("The New Sheet has been created as new_xml \n")
        print('*'*80)
        print("The New File Path is {0}".format(os.path.join(TESTS_DIRECTORY,new_xml.path)))
        print('*'*80)
        print("The result of print new_xml")
        print(new_xml)
        print('*'*80)
        print("The result of new_xml.to_HTML()")
        print new_xml.to_HTML()
        print('*'*80)
        print("The result of new_xml.options")
        print new_xml.options
        print('*'*80)
        print("The new_xml has been saved")
        new_xml.save()
def test_Log():
    print('Creating New Log..\n')
    os.chdir(TESTS_DIRECTORY)
    new_log=Log()
    print('Log Contents Upon Creation: using print new_log')
    print(new_log)
    print('\n')
    print('The New Log\'s path is %s'%new_log.path)
    print('Add an entry using new_log.add_entry("This is a test")')
    new_log.add_entry("This is a test")
    print('Log Contents: using print new_log')
    new_log.save()
    print(new_log)

def test_log_addition():
    """ Script to develop test the __add__ attribute for the class Log"""
    # First we want to know how a copy works
    os.chdir(TESTS_DIRECTORY)
    import time
    log_1=Log()
    log_1.add_entry("I am Log Number One")
    time.sleep(.3)
    log_2=Log()
    log_2.add_entry("I am Log Number 2")
    print('Log_1 Contents: using print')
    print log_1
    print('Log_2 Contents: using print')
    print log_2
    print('Log_1+Log_2 Contents: using print')
    print log_1+log_2
def test_EndOfDayLog():
    """ Script to test that daily logs work properly"""
    os.chdir(TESTS_DIRECTORY)
    print('Creating New Log..\n')
    new_log=EndOfDayLog()
    print('Log Contents Upon Creation: using print new_log')
    print(new_log)
    print('\n')
    print('The New Log\'s path is %s'%new_log.path)
    print('Add an entry using new_log.add_entry("This is a test")')
    new_log.add_entry("This is a test")
    print('Add an entry using new_log.add_entry_information(1,dictionary)')
    dictionary={'Actions':'I tested EndofDayLog()','Who_Did':'Aric Sanders'
    ,'Who_Suggested':'Small Green Man','Why':'To make sure it works!',
    'Conclusion':'It Does!','Data_Location':'In front of your face'}
    new_log.add_entry_information(0,**dictionary)
    print('Log Contents: using print new_log')
    new_log.save()
    print(new_log)
    #new_log.show('wx')
def test_show():
    os.chdir(TESTS_DIRECTORY)
    new_log=Log()
    print 'New Log Created...'
    print 'The Result of Show() is:'
    print '*'*80
    entries=['1','2','Now I see!', 'Today was a good day']
    for entry in entries:
        new_log.add_entry(entry)
    print new_log.show()
    print '\n'*4
    print 'The Result of Log.show(xml) is:'
    print '*'*80
    print new_log.show('xml')
    #the window version
    new_log.show('wx')
def test_to_HTML():
    os.chdir(TESTS_DIRECTORY)
    new_log=Log()
    print 'New Log Created...'
    print 'The Result of Show() is:'
    print '*'*80
    entries=['1','2','Now I see!', 'Today was a good day']
    for entry in entries:
        new_log.add_entry(entry)
    print new_log.show()
    print '\n'*4
    print 'The Result of Log.to_HTML(xml) is:'
    print '*'*80
    print new_log.to_HTML()

#-----------------------------------------------------------------------------
# Module Runner
if __name__=='__main__':
    test_XMLModel()
    #test_Log()
    #test_log_addition()
    #test_EndOfDayLog()
    #test_show()
    #test_to_HTML()
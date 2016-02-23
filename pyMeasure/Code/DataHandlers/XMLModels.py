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
import urlparse                                    # To form proper URLs
import socket                                      # To determine IPs and Hosts
from types import *                                # For Data Type testing

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
# For retrieving metadata
try:
    from pyMeasure.Code.Utils.Names import auto_name
    DEFAULT_FILE_NAME=None
except:
    print("The function auto_name in pyMeasure.Code.Utils.Names was not found")
    print("Setting Default file name to New_XML.xml")
    DEFAULT_FILE_NAME='New_XML.xml'
    pass
try:
    from pyMeasure.Code.Utils.GetMetadata import *
except:
    print "Can not find the module GetMetadata, please add it to sys.path"
    print "Anything that uses the functions from GetMetadata will be broken"
    pass
#-----------------------------------------------------------------------------
# Module Constants
XSLT_REPOSITORY='../XSL'
TESTS_DIRECTORY=os.path.join(os.path.dirname(os.path.realpath(__file__)),'Tests')
DRIVER_FILE_EXTENSIONS=['sys','SYS','drv','DRV']
NODE_TYPE_DICTIONARY={'1':'ELEMENT_NODE', '2':'ATTRIBUTE_NODE', '3':'TEXT_NODE',
    '4':'CDATA_SECTION_NODE', '6':'ENTITY_NODE', '7':'PROCESSING_INSTRUCTION_NODE',
    '8':'COMMENT_NODE','9':'DOCUMENT_NODE','10':'DOCUMENT_TYPE_NODE',
    '12':'NOTATION_NODE'}
#-----------------------------------------------------------------------------
# Module Functions
def dictionary_to_xmlchunk(dictionary, level='attribute'):
    "returns a string formatted as xml when given a python dictionary"
    if type(dictionary) is not dict:raise
    if re.match('attr',level,re.IGNORECASE):
        prefix="<Tuple "
        postfix=" />"
        inner=""
        for key,value in dictionary.iteritems():
            inner=inner+"%s='%s' "%(key,value)
        xml_out=prefix+inner+postfix

    if re.match('tag',level,re.IGNORECASE):
        xml_out=""
        for key,value in dictionary.iteritems():
            xml_out=xml_out+"<"+str(key)+">"+str(value)+"</"+str(key)+">"
    return xml_out

def dictionary_list_to_xmlchunk(list_of_dictionaries,level='attribute'):
    """returns a string of xml given a list of dictionaries, level says if keys become attribute names or tag names"""
    if type(list_of_dictionaries) is not list:raise
    xml_out=""
    for item in list_of_dictionaries:
        xml_out=xml_out+dictionary_to_xmlchunk(item,level)+"\n"
    return xml_out

def get_XML_text(tag_name,path=None,text=None):
    """ Returns the text in the first tag found with tag name """
    if text is None:
        f=open(path,'r')
        text=f.read()
    tag_match=re.search(
    '<%s>(?P<XML_text>\w+)</%s>'%(tag_name,tag_name),
     text)
    return tag_match.group('XML_text')

def URL_to_path(URL,form='string'):
    """Takes an URL and returns a path as form.
    Argument form may be 'string' or 'list'"""
    path=urlparse.urlparse(URL)[2]
    if form in ['string', 'str', 's']:
        return path
    elif form in ['list','ls','li']:
        path_list=path.split('/')
        return path_list

def condition_URL(URL):
    """ Function that makes sure URL's have a / format and assigns host as
    local host if there is not one. Also gives paths a file protocol."""
    parsed_URL=urlparse.urlparse(URL.replace('\\','/'))
    if not (parsed_URL[0] in ['file','http','ftp']):
        parsed_URL=urlparse.urlparse('file:'+URL.replace('\\','/'))
    return str(urlparse.urlunparse(parsed_URL).replace('///',''))
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
        return self.document.toprettyxml()
class Log(XMLBase):
    """ Data container for a general Log"""
    def __init__(self,file_path=None,**options):
        """ Intializes the Log"""
        # We add the defaults for the log pass and the options along
        defaults={"root":'Log',
                  'style_sheet':os.path.join(XSLT_REPOSITORY,'DEFAULT_LOG_STYLE.xsl').replace('\\','/'),
                  'entry_style_sheet':os.path.join(XSLT_REPOSITORY,'DEFAULT_LOG_STYLE.xsl').replace('\\','/'),
                  'specific_descriptor':'XML','general_descriptor':'Log'}
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
            Indices=map(lambda x:int(x),self.Index_node_dictionary.keys()) 
            if min(Indices)<Index:
               Indices.sort()
               new_Index=Indices[Indices.index(Index)-1]
            else:
                Indices.remove(Index)
                if len(Indices)>0:
                    new_Index=max(Indices)
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
            Indices=map(lambda x:int(x),self.Index_node_dictionary.keys()) 
            if max(Indices)>Index:
               Indices.sort()
               new_Index=Indices[Indices.index(Index)+1]
            else:
                Indices.remove(Index)
                new_Index=min(Indices)
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
class DataTable(XMLBase):
    """ This is a XML data table class with an optional description"""
    def __init__(self,file_path=None,**options):
        """ Intializes the DataTable Class. Passing **{'data_table':[mylist]} creates a
        table with x1 and x2 as column names. Passing **{'data_dictionary':{'Data_Description':{'Tag':'Text',etc},
        'Data':[{'x':1,'y':2},{'x':2,'y':3}]
         """
        # the general idea is <Data_Description/><Data><Tuple i=''/></Data>

        # This is a general pattern for adding a lot of options
        # The next more advanced thing to do is retrieve defaults from a settings file
        defaults={"root":"Data_Table",
                  "style_sheet":os.path.join(XSLT_REPOSITORY,'DEFAULT_MEASUREMENT_STYLE.xsl').replace('\\','/'),
                  "specific_descriptor":'Data',
                  "general_descriptor":'Table',
                  "directory":None,
                  "extension":'xml'
                  }
        self.options={}
        for key,value in defaults.iteritems():
            self.options[key]=value
        for key,value in options.iteritems():
            self.options[key]=value
        XMLBase.__init__(self,file_path,**self.options)

        try:
            data_table=self.options['data_table']
            if len(data_table)>0:
                data_node=self.list_to_XML(data_table)
                self.document.documentElement.appendChild(data_node)
        except: pass
        try:
            data_dictionary=self.options['data_dictionary']
            if len(data_dictionary)>0:
                for key,value in data_dictionary.iteritems():
                    # This hanldes Tag:Text dictionaries
                    if re.search('Description',key):
                        new_entry=self.document.createElement(key)
                        for tag,element_text in value.iteritems():
                            new_tag=self.document.createElement(tag)
                            new_text=self.document.createTextNode(element_text)
                            new_tag.appendChild(new_text)
                            new_entry.appendChild(new_tag)
                        self.document.documentElement.appendChild(new_entry)
                    if re.search('Data',key) and not re.search('Description',key):
                        new_entry=self.list_to_XML(value)
                        self.document.documentElement.appendChild(new_entry)
        except:pass

    def list_to_XML(self,data_list):
        """ Converts a list to XML document"""
        data_node=self.document.createElement('Data')
        #self.document.documentElement.appendChild(data_node)
        for row in data_list:
            if type(row) in [ListType,TupleType]:
                new_entry=self.document.createElement('Tuple')
                for j,datum in enumerate(row):
                    x_attribute=self.document.createAttribute('X%s'%j)
                    new_entry.setAttributeNode(x_attribute)
                    new_entry.setAttribute('X%s'%j,str(datum))
                data_node.appendChild(new_entry)
            elif type(row) is DictionaryType:
                new_entry=self.document.createElement('Tuple')
                for key,datum in row.iteritems():
                    x_attribute=self.document.createAttribute(key)
                    new_entry.setAttributeNode(x_attribute)
                    new_entry.setAttribute(key,str(datum))
                data_node.appendChild(new_entry)
        return data_node

    def get_attribute_names(self):
        """ Returns the attribute names in the first tuple element in the 'data' element """
        attribute_names=[]
        data_nodes=self.document.getElementsByTagName('Data')
        first_tuple_node=data_nodes[0].childNodes[1]
        text=first_tuple_node.toprettyxml()
        text_list=text.split(' ')
        #print text_list
        for item in text_list:
            try:
                match=re.search('(?P<attribute_name>\w+)=',item)
                name=match.group('attribute_name')
                #print name
                attribute_names.append(name)
            except:pass

        return attribute_names

    def to_list(self,attribute_name):
        """ Outputs the data as a list given a data column (attribute) name"""
        try:
            node_list=self.document.getElementsByTagName('Tuple')
            data_list=[node.getAttribute(attribute_name) for node in node_list]
            return data_list
        except:
            return None

    def to_tuple_list(self,attribute_names):
        """ Returns a list of tuples for the specified list of attribute names"""
        try:
            node_list=self.document.getElementsByTagName('Tuple')
            data_list=[tuple([node.getAttribute(attribute_name) for
            attribute_name in attribute_names]) for node in node_list]
            return data_list
        except:
            return None

    def get_header(self,style='txt'):
        """ Creates a header from the data description if there is one"""
        try:
            node_list=self.document.getElementsByTagName('Data_Description')
            data_description=node_list[0]
            out=''
            if style in ['txt','text','ascii']:
                for child in data_description.childNodes:
                    try:
                        out=out+'%s: %s'%(child.nodeName,child.firstChild.nodeValue)+'\n'
                    except:pass
                return out
            elif re.search('xml',style,flags=re.IGNORECASE):
                out=data_description.toprettyxml()
                return out
        except:
            raise
class FileRegister(XMLBase):
    """ The base class for arbitrary database, which processes the
    File Register XML File."""

    def __init__(self,file_path=None,**options):
        """ Initializes the File Register Class."""

        # This is a general pattern for adding a lot of options
        # The next more advanced thing to do is retrieve defaults from a settings file
        defaults={"root":"File_Registry",
                  "style_sheet":os.path.join(XSLT_REPOSITORY,'FR_STYLE.xsl').replace('\\','/'),
                  "specific_descriptor":'Resource',
                  "general_descriptor":'Registry',
                  "directory":None,
                  "extension":'xml'
                  }
        self.options={}
        for key,value in defaults.iteritems():
            self.options[key]=value
        for key,value in options.iteritems():
            self.options[key]=value
        XMLBase.__init__(self,file_path,**self.options)

        self.Id_dictionary=dict([(str(node.getAttribute('URL')),
            str(node.getAttribute('Id'))) for node in
            self.document.getElementsByTagName('File')])

    def create_Id(self,URL):
        """ Creates or returns the existing Id element of a URL"""
        parsed_URL=urlparse.urlparse(condition_URL(URL))
        try: # Look in self.Id_dictionary, if it is not there catch
             # the exception KeyError and generate an Id.
            return self.Id_dictionary[URL.replace('///','')]
        except KeyError:
            # The Id is not in the existing list so start buliding Id.
            # Determine the IP Address of the host in the URL
            if parsed_URL[1] in ['',u'']: #if it is empty assume local host
                IP_address=socket.gethostbyaddr(socket.gethostname())[2][0]
            else:
                IP_address= socket.gethostbyaddr(parsed_URL[1])[2][0]
            Id_cache={}
            # We begin with all the entries with the same IP address
            for (key,value) in self.Id_dictionary.iteritems():
                if value.startswith(IP_address):
                        Id_cache[key]=value
            # If the Id_cache is empty then we just assign the number
            temp_Id=IP_address
            path_list=parsed_URL[2].split('/')
            file_extension=path_list[-1].split('.')[-1]
            if len(Id_cache) is 0:
                for index,part in enumerate(path_list):
                    if index<len(path_list)-1:
                        temp_Id=temp_Id+'.'+'11'
                    elif index==len(path_list)-1:
                        if (file_extension in DRIVER_FILE_EXTENSIONS):
                            temp_Id=temp_Id+'.'+'31'
                        elif os.path.isdir(parsed_URL[2]):
                            temp_Id=temp_Id+'.'+'11'
                        else:
                            temp_Id=temp_Id+'.'+'21'
                return temp_Id
            # if it is not empty we have to a little work
            # remove the information about IP address
            place=0
            #print path_list
            while place<=len(path_list):
              # If the Id_cache is empty assign the rest of the Id.
               if len(Id_cache) is 0:
                    for index,part in enumerate(path_list[place:]):
                        if index<len(path_list[place:])-1:
                            temp_Id=temp_Id+'.'+'11'
                        elif index==len(path_list[place:])-1:
                            if (file_extension in DRIVER_FILE_EXTENSIONS):
                                temp_Id=temp_Id+'.'+'31'
                            elif os.path.isdir(parsed_URL[2]):
                                temp_Id=temp_Id+'.'+'11'
                            else:
                                temp_Id=temp_Id+'.'+'21'
                    return temp_Id

                # If the Id_cache is not empty
               else:
                    path_cache=dict([(URL,URL_to_path(URL,form='list'))
                        for URL in Id_cache.keys()])
                    print Id_cache
                    part_cache=dict([(URL,[path_cache[URL][place],
                        Id_cache[URL].split('.')[place+4]])
                        for URL in Id_cache.keys()])
                    parts_list=[part_cache[URL][0]for URL in Id_cache.keys()]
                    node_number=max([int(Id_cache[URL].split('.')[place+4][1:])
                        for URL in Id_cache.keys()])
                # If it is the last place
                    if place==len(path_list)-1:
                        new_node_number=node_number+1
                        if (file_extension in DRIVER_FILE_EXTENSIONS):
                            new_node_type='3'
                        elif os.path.isdir(parsed_URL[2]):
                            new_node_type='1'
                        else:
                            new_node_type='2'
                        temp_Id=temp_Id+'.'+new_node_type+str(new_node_number)
                        return temp_Id
                # If it is not the last place assume it is a directory
                    else:
                        new_node_type='1'
                        # Check to see if it is already in the FR
                        if path_list[place] in parts_list:
                            for URL in Id_cache.keys():
                                if part_cache[URL][0]==path_list[place]:
                                    new_node=part_cache[URL][1]

                        # If not add one to node
                        else:
                            new_node_number=node_number+1
                            new_node=new_node_type+str(new_node_number)
                        temp_Id=temp_Id+'.'+new_node
                        # Update the Id_cache for the next round, and the place
                        for URL in Id_cache.keys():
                            try:
                                if not part_cache[URL][0]==path_list[place]:
                                    del(Id_cache[URL])
                                Id_cache[URL].split('.')[place+5]
                            except KeyError:
                                pass
                            except IndexError:
                                #print Id_cache,URL
                                del(Id_cache[URL])
                        place=place+1

    def add_entry(self,URL):
        """ Adds an entry to the current File Register """
        URL=condition_URL(URL)
        if URL in self.Id_dictionary.keys():
            print 'Already there'
            return
        # the xml entry is <File Date="" Host="" Type="" Id="" URL=""/>
        File_Registry=self.document.documentElement
        new_entry=self.document.createElement('File')
        # Make all the new attributes
        attributes=['Id','Host','Date','URL','Type']
        new_attributes=dict([(attribute,
        self.document.createAttribute(attribute)) for attribute in \
        attributes])
        # Add the new attributes to the new entry
        for attribute in attributes:
            new_entry.setAttributeNode(new_attributes[attribute])
        # Now assign the values
        attribute_values={}
        attribute_values['URL']=URL
        attribute_values['Id']=self.create_Id(URL)
        attribute_values['Date']=datetime.datetime.utcnow().isoformat()
        type_code=attribute_values['Id'].split('.')[-1][0]
        if type_code in ['1',u'1']:
            attribute_values['Type']="Directory"
        elif type_code in ['2',u'2']:
            attribute_values['Type']="Ordinary"
        elif type_code in ['3',u'3']:
            attribute_values['Type']="Driver"
        else:
            attribute_values['Type']="Other"
        parsed_URL=urlparse.urlparse(condition_URL(URL))
        if parsed_URL[1] in ['',u'']: #if it is empty assume local host
            attribute_values['Host']= socket.gethostbyaddr(socket.gethostname())[0]
        else:
            attribute_values['Host']= parsed_URL[1]

        # Now set them all in the actual attribute
        for (key,value) in attribute_values.iteritems():
            new_entry.setAttribute(key,value)
        File_Registry.appendChild(new_entry)
        # Finally update the self.Id_dictionary
        # Added boolean switch to speed up adding a lot of entries

        self.Id_dictionary=dict([(str(node.getAttribute('URL')),
            str(node.getAttribute('Id'))) for node in
            self.document.getElementsByTagName('File')])
    # TODO : Add an input filter that guesses at what you inputed

    def add_tree(self,root,**options):
        """ Adds a directory and all sub folders and sub directories, **options
        provides a way to {'ignore','.pyc|etc'} or {'only','.png|.bmp'}"""

        # Deal with the optional parameters, these tend to make life easier
        default_options={'ignore':None,'only':None,'print_ignored_files':True,
        'directories_only':False,'files_only':False}
        tree_options=default_options
        for option,value in options.iteritems():
            tree_options[option]=value
        #print tree_options
        #condition the URL
        root_URL=condition_URL(root)
        path=URL_to_path(root_URL)
        # now we add the files and directories that jive with the options
        try:

            for (home,directories,files) in os.walk(path):
                #print (home,directories,files)
                for directory in directories:# had to change this, used to be first element in list
                    try:
                        if tree_options['files_only']:
                            if tree_options['print_ignored_files']:
                                print "ignoring %s because it is not a file"%file
                            raise
                        if tree_options['ignore'] is not None and re.search(tree_options['ignore'],directory):
                            if tree_options['print_ignored_files']:
                                print "ignoring %s because it does not match the only option"%directory
                            raise
                        elif tree_options['only'] is not None and not re.search(tree_options['only'],directory):
                            if tree_options['print_ignored_files']:
                                print "ignoring %s because it does not match the only option"%directory
                            raise
                        else:
                            self.add_entry(condition_URL(os.path.join(home,directory)))
                            self.save()
                    except:pass
                for file in files: # had to change this 12/2012, used to be Second element in list
                    try:
                        if tree_options['directories_only']:
                            if tree_options['print_ignored_files']:
                                print "ignoring %s because it is not a directory"%file
                            raise
                        if tree_options['ignore'] is not None and re.search(tree_options['ignore'],file):
                            if tree_options['print_ignored_files']:
                                print "ignoring %s because it matches the ignore option"%file
                            raise
                        elif tree_options['only'] is not None and not re.search(tree_options['only'],file):
                            if tree_options['print_ignored_files']:
                                print "ignoring %s because it does not match the only option"%file
                            raise
                        else:
                            #print (home,file)
                            self.add_entry(condition_URL(os.path.join(home,file)))
                            self.save()
                    except:raise
        except:
            raise
        #After all the files are added update the Id_dictionary
        self.Id_dictionary=dict([(str(node.getAttribute('URL')),
            str(node.getAttribute('Id'))) for node in
            self.document.getElementsByTagName('File')])

    def remove_entry(self,URL=None,Id=None):
        """ Removes an entry in the current File Register """
        File_Registry=self.document.documentElement
        if not URL is None:
            URL=condition_URL(URL)
            URL_FileNode_dictionary=dict([(node.getAttribute('URL'),
            node) for node in self.document.getElementsByTagName('File')])
            File_Registry.removeChild(URL_FileNode_dictionary[URL])
        else:
            Id_FileNode_dictionary=dict([(node.getAttribute('Id'),
            node) for node in self.document.getElementsByTagName('File')])
            File_Registry.removeChild(Id_FileNode_dictionary[Id])
        # Finally update the self.Id_dictionary
        self.Id_dictionary=dict([(str(node.getAttribute('URL')),
        str(node.getAttribute('Id'))) for node in \
        self.document.getElementsByTagName('File')])

class Metadata(XMLBase):
    """ Metadata holds the metadata tags for a FileRegistry, If it already exists
    and the parser gives an error check the xml file for special characters like &#30;"""

    def __init__(self,file_path=None,**options):#FileRegistry,Metadata_File=None)
        """ Intializes the class Metadata"""
        # This is a general pattern for adding a lot of options
        # The next more advanced thing to do is retrieve defaults from a settings file
        defaults={"root":"Metadata_Registry",
                  "style_sheet":os.path.join(XSLT_REPOSITORY,'METADATA_STYLE.xsl').replace('\\','/'),
                  "specific_descriptor":'Metadata',
                  "general_descriptor":'Registry',
                  "directory":None,
                  "extension":'xml',
                  "metadata_file":None
                  }
        self.options={}
        for key,value in defaults.iteritems():
            self.options[key]=value
        for key,value in options.iteritems():
            self.options[key]=value
        FileRegistry=self.options['file_registry']
        Metadata_File=self.options['metadata_file']
        # Process the file register
        if type(FileRegistry) is InstanceType:
            self.FileRegister=FileRegistry
        elif type(FileRegistry) in StringTypes:
            self.FileRegister=FileRegister(FileRegistry)



        # Process or create the Metadata File
        if Metadata_File is None:
            # Make the metadata file based on the file register
            FileRegister_path=self.FileRegister.path.replace('\\','/')
            FileRegister_name=FileRegister_path.split('/')[-1]
            FileRegister_ext=FileRegister_name.split('.')[-1]
            Metadata_name=FileRegister_name.replace('.'+FileRegister_ext,
            '_Metadata.'+FileRegister_ext)
            self.path=FileRegister_path.replace(FileRegister_name,Metadata_name)
            self.document=self.FileRegister.document
            # delete old processing instructions
            for node in self.document.childNodes:
                if node.nodeType is 7:
                    self.document.removeChild(node)
                    node.unlink()
            # add in the default xsl
            new_node=self.document.createProcessingInstruction(
                'xml-stylesheet',
                u'type="text/xsl" href="%s"'%self.options['style_sheet'])
            self.document.insertBefore(new_node,self.document.documentElement)
            # make sure there is a fileregister reference
            FR_Path=self.FileRegister.path
            new_node=self.document.createProcessingInstruction(\
            'xml-FileRegistry',\
            'href=\"%s\"'%(self.FileRegister.path))
            self.document.insertBefore(new_node,self.document.documentElement)

        else:
            # The metadata file exists as a saved file or an instance
            if type(Metadata_File) is InstanceType:
                self.document=Metadata_File.document
                self.path=Metadata_File.path
            elif type(Metadata_File) in StringTypes:
                XMLBase.__init__(self,file_path,**self.options)


        # TODO: This dictionary of nodes worries me-- it may not scale well
        self.node_dictionary=dict([(str(node.getAttribute('URL')),
            node) for node in
            self.document.getElementsByTagName('File')])

        self.URL_dictionary=dict([(str(node.getAttribute('Id')),
            str(node.getAttribute('URL'))) for node in
            self.document.getElementsByTagName('File')])

        self.name_dictionary=dict([(Id,os.path.split(self.URL_dictionary[Id])[1])
            for Id in self.URL_dictionary.keys()])

        self.current_node=self.node_dictionary.values()[0]

    def search_name(self,name=None,re_flags=re.IGNORECASE):
        """ Returns a list of URL's that have an element matching name"""
        try:
            if re_flags in [None,'']:
                urls=filter(lambda x: re.search(name,x),
                self.URL_dictionary.values())
                return urls
            else:
                urls=filter(lambda x: re.search(name,x,flags=re_flags),
                self.URL_dictionary.values())
                return urls

        except:
            raise


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

    def get_file_node(self,URL=None,Id=None):
        """ Returns the file node specified by URL or Id"""
        if not URL is None:
            URL=condition_URL(URL)
            self.current_node=self.node_dictionary[URL]
            return self.current_node
        elif not Id is None:
            self.current_node=self.node_dictionary[self.URL_dictionary[Id]]
            return self.current_node
    def set_current_node(self,URL=None,Id=None):
        """ Sets the current file node to the one specified by URL or Id"""
        if not URL is None:
            URL=condition_URL(URL)
            self.current_node=self.node_dictionary[URL]
        elif not Id is None:
            self.current_node=self.node_dictionary[self.URL_dictionary[Id]]

    def add_element_to_current_node(self,XML_tag=None,value=None,node=None,**Atributes):
        """Adds a metadata element to the current file node"""
        if node is None:
            new_element=self.document.createElement(XML_tag)
        else:
            new_element=node
        if not value is None:
            new_text=self.document.createTextNode(str(value))
            new_element.appendChild(new_text)

        attributes=[key for key in Atributes.keys()]
        new_attributes=dict([(attribute,
        self.document.createAttribute(attribute)) for attribute in \
        attributes])

        for (key,value) in Atributes.iteritems():
            new_element.setAttribute(key,str(value))
        self.current_node.appendChild(new_element)
    def remove_element_in_current_node(self,element_name):
        """Removes all metadata elements with the same tagname
         in the current file node"""
        nodes_to_remove=self.current_node.getElementsByTagName(element_name)
        try:
            for node in nodes_to_remove:
                self.current_node.removeChild(node)
        except:pass

    if XSLT_CAPABLE:
        def current_node_to_HTML(self,XSLT=None):
            """Returns a HTML document from the current node"""
            if XSLT is None:
                # For some reason an absolute path tends to break here, maybe a spaces in file names problem
                XSLT=self.options['style_sheet']
            XSL_data=etree.parse(XSLT)
            XSL_transform=etree.XSLT(XSL_data)
            HTML=XSL_transform(etree.XML(self.current_node.toxml()))
            return HTML

    def print_current_node(self):
        """ Prints the current node """
        print self.current_node.toxml()
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
    "Tests the show() method of the Log class"
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
    "Tests the to_HTML method of the Log class"
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

def test_DataTable():
    """ Tests the DataTable Class"""
    test_data=[tuple([2*i+j for i in range(3)]) for j in range(5)]
    test_options={'data_table':test_data}
    new_table=DataTable(None,**test_options)
    print new_table
    test_dictionary={'Data_Description':{'x':'X Distance in microns.',
    'y':'y Distance in microns.','Notes':'This data is fake'},'Data':[[1,2],[2,3]]}
    test_dictionary_2={'Data_Description':{'x':'x Distance in microns.',
    'y':'y Distance in microns.'},'Data':[{'x':1,'y':2},{'x':2,'y':3}]}
    test_options_2={'data_dictionary':test_dictionary}
    test_options_3={'data_dictionary':test_dictionary_2}
    new_table_2=DataTable(**test_options_2)
    new_table_3=DataTable(**test_options_3)
    print new_table_2
    print new_table_3
    print new_table_3.to_list('x')
    print new_table_3.to_tuple_list(['x','y'])
    print new_table_3.path
    new_table_3.get_header()

def test_get_header():
    """ Test of the get header function of the DataTable Class """
    test_dictionary={'Data_Description':{'x':'X Distance in microns.',
    'y':'y Distance in microns.','Notes':'This data is fake'},'Data':[[1,2],[2,3]]}
    new_table=DataTable(**{'data_dictionary':test_dictionary})
    header=new_table.get_header()
    print header
    print new_table.get_header('xml')

def test_open_measurement(sheet_name='Data_Table_021311_1.xml'):
    """Tests opening a sheet"""
    os.chdir(TESTS_DIRECTORY)
    measurement=DataTable(sheet_name)
    print("The file path is {0}".format(measurement.path))
    #print measurement
    print measurement.get_header()

def test_get_attribute_names(sheet_name='Data_Table_021311_1.xml'):
    "Tests the get_attribute_name method of the DataTable Class"
    os.chdir(TESTS_DIRECTORY)
    measurement=DataTable(sheet_name)
    names=measurement.get_attribute_names()
    print 'the names list is:',names
    print 'Using the names list to create a data table:'
    print '*'*80+'\n'+'%s   %s  %s'%(names[0], names[1], names[2])+'\n'+'*'*80
    for index,item in enumerate(measurement.to_list(names[0])):
        row=''
        for name in names:
            row=measurement.to_list(name)[index] +'\t'+row
        print row

def test_FileRegister():
    "Tests the FileRegister Class"
    os.chdir(TESTS_DIRECTORY)
    new_file_register=FileRegister()
    new_file_register.add_tree(os.getcwd())
    print new_file_register

def test_Metadata(File_Registry=None,Metadata_File=None):
    os.chdir(TESTS_DIRECTORY)
    if File_Registry is None:
        File_Registry=os.path.join(TESTS_DIRECTORY,'Resource_Registry_20160222_001.xml')
    options={'file_registry':File_Registry}
    new_Metadata=Metadata(None,**options)
    print new_Metadata.current_node_to_HTML()
    new_Metadata.save()

#-----------------------------------------------------------------------------
# Module Runner
if __name__=='__main__':
    #test_XMLModel()
    #test_Log()
    #test_log_addition()
    #test_EndOfDayLog()
    #test_show()
    #test_to_HTML()
    #test_DataTable()
    #test_get_header()
    #test_open_measurement()
    #test_get_attribute_names()
    #test_FileRegister()
    test_Metadata()
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
                  "style_sheet":os.path.join(XSLT_REPOSITORY,'DEFAULT_STYLE.xsl').replace('\\','/')}
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
                self.path=auto_name('XML','Document')
            else:
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
#-----------------------------------------------------------------------------
# Module Runner
if __name__=='__main__':
    test_XMLModel()
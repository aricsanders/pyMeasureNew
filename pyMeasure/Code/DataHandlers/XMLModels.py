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
    from pyMeasure.Code.Utils.Names import
#-----------------------------------------------------------------------------
# Module Constants
XSLT_REPOSITORY=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'XSL')
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
        defaults={"root":"root","style_sheet":os.path.join(XSLT_REPOSITORY,'DEFAULT_STYLE.xsl')}
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
            self.path=os.path.join(os.getcwd(),'New_XML.xml')# TODO: Change to autoname
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
                XSLT=self.options['style_sheet']
            XSL_data=etree.parse(XSLT)
            XSL_transform=etree.XSLT(XSL_data)
            HTML=XSL_transform(etree.XML(self.document.toxml()))
            return HTML
#-----------------------------------------------------------------------------
# Module Scripts

#-----------------------------------------------------------------------------
# Module Runner
if __name__=='__main__':
    pass
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

#-----------------------------------------------------------------------------
# Third Party Imports
try:
    import lxml
except:
    print("Install lxml or put it on the python path")
    pass
# For auto generation of common method aliases
try:
    from pyMeasure.Code.Utils.Alias import * #TODO : Determine if I have to rename pyMeasure
    METHOD_ALIASES=1
except:
    print("The module pyMeasure.Code.Utils.Alias was not found")
    METHOD_ALIASES=0
    pass
#-----------------------------------------------------------------------------
# Module Constants
XSLT_REPOSITORY=os.path.join(os.path.dirname(os.path.realpath(pyMeasure.__file__))
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
        defaults={}
        self.options={}
        for key,value in defaults.iteritems():
            self.options[key]=value
        for key,value in options.iteritems():
            self.options[key]=value
        # Define Method Aliases if they are available
        if METHOD_ALIASES:
            for command in alias(self):
                exec(command)

    def save(self,path=None):
        """" Saves as an XML file"""
        if path is None:
            path=self.path
        file_out=open(path,'w')
        file_out.write(self.document.toprettyxml())
        file_out.close()

    def to_HTML(self,XSLT=None):
        """ Returns HTML string by applying a XSL to the XML document"""
        if XLST is None:
            XLST=os.path.join()
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
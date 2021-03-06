#-----------------------------------------------------------------------------
# Name:        HPBasicUtils
# Purpose:     To manage legacy HP Basic Files
# Author:      Aric Sanders
# Created:     2/22/2016
# License:     MIT License
#-----------------------------------------------------------------------------
""" This module handles HPBasic code when it has already been converted to .txt (DOS ASCII).
 To convert from native format to DOS ASCII, install HPBasic, Run HP Basic and
  type: SAVE CONFIGURE ASCII OFF
  Then
  LOAD "My_File"
  SAVE "My_ASCII_File"
  """

#-----------------------------------------------------------------------------
# Standard Imports
import os
#-----------------------------------------------------------------------------
# Third Party Imports
from pyMeasure.Code.Utils.Names import auto_name
#-----------------------------------------------------------------------------
# Module Constants
HTML_PREFIX="""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>%s</title>
    <link href="prism.css" rel="stylesheet" />
</head>
<body>
<h1> A highlighted Plain Text version of %s Basic Program</h1>
<pre><code class="language-basic"><script>"""
HTML_POSTFIX="""</script>

</code></pre>

<script src="prism.js" data-default-language="markup"></script>
</body>
</html>"""
#-----------------------------------------------------------------------------
# Module Functions
def HPBasic_to_HTML(file_name,file_path_output=None):
    """Converts HP BASIC code in DOS ASCII to a highlighted HTML file, requires prism.js"""
    # Default is to put the file in the current working directory under a different name
    # I should use pyMeasure.Code.Utils.Names.auto_name here
    if file_path_output is None:
        file_path_output=auto_name(file_name,'HPBasic_HTML',None,'html')
    in_lines=[]
    in_file=open(file_name,'r')
    for line in in_file:
        in_lines.append(line)
    out_file=open(file_path_output,'w')
    out_file.write(HTML_PREFIX%(file_name,file_name))
    for line in in_lines:
        out_file.write(line)
    out_file.write(HTML_POSTFIX)
    out_file.close()
#-----------------------------------------------------------------------------
# Module Classes
class HPBasicCode():
    """ This Class Serves a container for HPBasic Code that has been converted to DOS Compatible ASCII.
    """
    def __init__(self,file_path=None,**options):
        "Intializes the HPBasicCode Class"
        if file_path is None:
            print("Please Do Not Write Any More HP Basic Code!!")
            raise
        self.path=file_path
        self.code=[]
        in_file=open(self.path,'r')
        for line in in_file:
            self.code.append(line)
        # Code to set options
        defaults={}
        self.options={}
        for key,value in defaults.iteritems():
            self.options[key]=value
        for key,value in options.iteritems():
            self.options[key]=value
#-----------------------------------------------------------------------------
# Module Scripts
#TODO: Write Test Script
#-----------------------------------------------------------------------------
# Module Runner
if __name__ == '__main__':
    pass
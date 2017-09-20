# Written by Dennis Eldridge
#This delete any dimension styles whose name is strictly a number

# import clr
# this is the common runtime language
import clr

# Import DocumentManager and TransactionManager
clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# Import RevitAPI
clr.AddReference("RevitAPI")
import Autodesk
from Autodesk.Revit.DB import *

# this allows us to process strings
import sys
sys.path.append("C:\Python27\Lib")
from string import ascii_letters

# get the document
doc = DocumentManager.Instance.CurrentDBDocument

# Use a filtered element collector to gather all the dimension styles in the project.
collector = Autodesk.Revit.DB.FilteredElementCollector(doc).OfClass(DimensionType)

# this will collect all the dimension styles
dimensions_to_delete = []

# iterate through all the dimension types
for dim in collector:
	
	# find the name of the dimension style	
	name = dim.LookupParameter("Type Name").AsString()
	
	# This will remove spaces (" ") by replacing them with # an empty string ("")
	# then if the check if the resulting string can be converted to an integer
	if name.replace(" ", "").isdigit(): 
		dimensions_to_delete.append(dim)
		
# start a transaction to modify the model
t = Transaction(doc, 'Removing dimension styles')
t.Start()
 
# delete the dimension styles we don't want
for dim in dimensions_to_delete:
	doc.Delete(dim.Id)

# finish the transaction and dispose of it
t.Commit()
t.Dispose()

# output a list of the dim styles we deleted.
OUT = dims




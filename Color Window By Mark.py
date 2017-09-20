# Written by Dennis Eldridge
# This will change the color of a window based on it's mark

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


# import the ironpython library so for the next library
import sys
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)


# import the random module for colors
import random
from random import randint


#this fuction creates a color randomly
def randColor():
	rand_color = Color(random.randrange(0, 256), random.randrange(0, 256), random.randrange(0, 256))
	return rand_color

# get the current open document
doc = DocumentManager.Instance.CurrentDBDocument

# create filtered element collectors for walls and curtain panels
wall_collector = FilteredElementCollector(doc).OfClass(Wall)

# create an empty list to collect windows and each unique mark
windows = []
unique_marks = []

# checks the marks of the walls, and adds them to a list if they have a mark
for wall in wall_collector:

	# check if the wall type is a curtain wall
	type = doc.GetElement(wall.GetTypeId())
	if type.Kind == WallKind.Curtain:

		# check if the wall type has a mark
		mark_parameter = wall.LookupParameter("Mark")

		if mark_parameter.HasValue == True or mark_parameter.AsString != None:
			windows.append(wall)

			# if this mark is not yet used, add it to the list
			if mark_parameter.AsString() not in unique_marks:
				unique_marks.append(mark_parameter.AsString())



# create filtered element collectors for walls and curtain panels
curtain_panel_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_CurtainWallPanels)

# checks the marks of the windows, and adds them to a list if they have a mark
for curtain_panel in curtain_panel_collector:
		
	# check if the curtain panel type has a mark
	mark_parameter = curtain_panel.LookupParameter("Mark")
	if mark_parameter != None:
    
		if mark_parameter.HasValue == True:
			windows.append(curtain_panel)

			# if this mark is not yet used, add it to the list
			if mark_parameter.AsString() not in unique_marks:
				unique_marks.append(mark_parameter.AsString())



# this will collect all the colors we'll use
graphics_overrides = {}
colors = []

# get the input hatch pattern
solid_fill = UnwrapElement(IN[0])

#checks the marks of all walls and creates a color if it does not exist
for mark in unique_marks:

	# generate a color with the random function
	color = randColor()
	
	# creates a grahpics override element for each color
	graphics_overrides[mark] = OverrideGraphicSettings()
	graphics_overrides[mark].SetProjectionFillColor(color)
	graphics_overrides[mark].SetProjectionFillPatternId(solid_fill.Id)


# Start a new transaction
t = Transaction(doc, 'Override the window colors')
t.Start()

# gets the current view
view = doc.ActiveView

# assigns the appropriate color to each window
for window in windows:
	mark = window.LookupParameter("Mark").AsString()

	# applies the color to the element based on it's mark
	view.SetElementOverrides(window.Id, graphics_overrides[mark])

		
# commit and dispose of the transaction
t.Commit()
t.Dispose()
	
OUT = windows






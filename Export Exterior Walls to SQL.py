#This will export the walls to a database along with their proerties
import clr


# Import RevitAPI
clr.AddReference("RevitAPI")
import Autodesk
from Autodesk.Revit.DB import *
clr.AddReference("RevitAPIUI")
from Autodesk.Revit.UI import *
# Import DocumentManager and TransactionManager
clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application


import sys
#sys.setdefaultencoding('utf_32')
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
import System
from string import ascii_letters

sys.path.append("C:\Python27\Lib")
from string import ascii_letters
clr.AddReferenceToFileAndPath('C:\\Program Files (x86)\\IronPython 2.7\\DLLs\\IronPython.SQLite.dll')
import sqlite3

# Determines the data type of the input parameter
def GetDataType(param):
	storage = param.StorageType
	if storage == StorageType.Integer:
		return "INTEGER"
	elif storage == StorageType.String:
		return "STRING"
	elif storage == StorageType.Double:
		return "DOUBLE"
	elif storage == StorageType.ElementId:
		return "ID"

	return ""

# gets lines from the input geometry.
# input a geometry class and an id
def GetGeometry(edges, id):

	edge_iterator = edges.ForwardIterator()
	edge_iterator.MoveNext()

	# iterate through all the edge curves
	for x in range(1, edges.Size):
		line = edge_iterator.Current.AsCurve()
		sp = line.GetEndPoint(0)
		ep = line.GetEndPoint(1)

		# add the geometry to the database
		return "INSERT INTO Furniture_Geometry (furn_id, id, start_x, start_y, start_z, end_x, end_y, end_z) VALUES (" + str(i) + ", " + str(id) + ", " + str(sp.X) + ", " + str(sp.Y) + ", " + str(sp.Z) +  ", " + str(ep.X) + ", " + str(ep.Y) + ", " + str(ep.Z) +  ")"



#Creates an object that can collect / find elements of the wall calss
furn_collector = Autodesk.Revit.DB.FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Furniture)
furn_param_collector = Autodesk.Revit.DB.FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Furniture)

# Options for exporting geometry.  The default is fine.
options = Options()

# create the database
conn = sqlite3.connect('C:\\temp\\walls12.sqlite')
#conn.text_factory = lambda x: str(x, 'utf-32')
cur = conn.cursor()

# remove the existing table if it exists
cur.execute(u'DROP TABLE IF EXISTS Furniture')
cur.execute(u"CREATE TABLE Furniture (id INTEGER UNIQUE)")

# create the geometry table
cur.execute(u'DROP TABLE IF EXISTS Furniture_Geometry')
cur.execute(u"CREATE TABLE Furniture_Geometry (furn_id INTEGER, id INTEGER UNIQUE, start_x DOUBLE, start_y DOUBLE, start_z DOUBLE, end_x DOUBLE, end_y DOUBLE, end_z DOUBLE)")

# a dictionary of parameters and their associated data type
params = {}

# get the list of parameters
for furn in furn_param_collector:
	for param in furn.GetOrderedParameters():


		# find the storage type
		storage = GetDataType(param)

		# replace element ids with integers
		if storage == "ID":
			storage = "INTEGER"

		# get the name of the parameter, and replace spaces with underscores.
		name = param.Definition.Name.replace(" ", "_").replace("-", "")


		# create map the parameter name to it's storage type
		if name not in params.keys():
			params[name] = storage




# get the parameters so we can create a table
#TaskDialog.Show("hi", str(params.keys()))
add_col  = 'ALTER TABLE Furniture ADD COLUMN '

for param in params.keys():
	try:
		cur.execute(add_col + param + " " + params[param])
	except:
		try:
			TaskDialog.Show("hi", unicode(add_col + param + " " + params[param], error='ignore', encode='utf-8'))
		except:
			params[param] = ""


# counters for the wall id and geometry id
i = 0
g = 0

# iterate through teh walls and add them to the database
for furn in furn_collector.OfClass(FamilyInstance):

	# an empty list for the geometry of each wall
	glist = []

	# this will construct the database entry
	q = u'INSERT INTO Furniture (id, '
	v = str(i) + ", "


	# get the wall properties
	for param in furn.GetOrderedParameters():
		name = param.Definition.Name.replace(" ", "_").replace("-", "")

		if params[name] != "":


			# determine the datatype of the parameter
			if params[name] == "STRING":
				value = param.AsString()
			elif params[name] == "INTEGER":

				# get element ids
				if GetDataType(param) == "ID":
					value = str(param.AsElementId().IntegerValue)
				else:
					value = str(param.AsInteger())

			elif params[name] == "DOUBLE":
				value = str(param.AsDouble())
				# for as yet unsupported data types
			else:
				value = ""

			# try to generate the entire list of values
			try:
				if value != "" and type(value) != type(None) and name in params.keys():
						q += name + ", "
						v += value + ", "
			except:
				pass


	# get the type properties
	type = doc.GetElement(furn.GetTypeId())
	for param in type.GetOrderedParameters():
		name = param.Definition.Name.replace(" ", "_").replace("-", "")

		if params[name] != "":


			try:
				# find the datatype of the property
				if params[name] == "STRING":
					value = param.AsString()
				elif params[name] == "INTEGER":


					# get element ids
					if GetDataType(param) == "ID":
						value = str(param.AsElementId().IntegerValue)
					else:
						value = str(param.AsInteger())

				elif params[name] == "DOUBLE":
					value = str(param.AsDouble())
				# for as yet unsupported data types
				else:
					value = ""
			except:
				pass

			# try to add the values to the list.
			try:
				if value != "" and type(value) != type(None) and name in params.keys() and value != "None":
					q += name + ", "
					v += value + ", "
			except:
				pass


	# remove extra commas
	q = q[:-2]
	v = v[:-2]


	# add the elements to the database
	try:
		cur.execute(unicode(q + ") VALUES (" + v + ")", encoding='utf-8'))

	except:
		pass

	# add geometry
	for solid in furn.Geometry[options]:

		try:
			# get the edges of each solid
			edges = solid.Edges

			geo = GetGeometry(edges, g)
			cur.execute(geo)

			g += 1
			glist.append(str(g))

		except:
			try:
				solids = solid.GetInstanceGeometry()

				for solid in solids:
					if solid.SurfaceArea &gt; 0:
						edges = solid.Edges

						geo = GetGeometry(edges, g)
						cur.execute(geo)

						g += 1
						glist.append(str(g))
			except:
				pass

	# increment the wall id
	i += 1


# commit the changes to the database and close it.
conn.commit()
cur.close()

#Assign your output to the OUT variable.
OUT = 0

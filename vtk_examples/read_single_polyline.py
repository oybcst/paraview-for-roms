#!/usr/bin/env vtkpython
# 2022-03-03 Mark Van Moer, NCSA

# Tested with VTK 9.1, VTK has breaking API changes at major number
# releases, e.g., 8.x to 9.x.

# reading data from a VTK XML PolyData (.vtp)
# vtk.org/doc/nightly/html/classes.html is the best resource
# for digging into classes once one gets a little bit of
# familiarity.

# another handy thing is to do this in the Python interpreter
# and use dir() and help() on objects

import vtk

reader = vtk.vtkXMLPolyDataReader()

# assuming data is in same directory
reader.SetFileName('single_polyline.vtp')

# normally VTK pipeline stages don't execute until
# it reaches a step that requires data. So at this point, the file
# hasn't actually been read. We can force that with Update()

reader.Update()

# The actual dataset, this is the geometry, scalars, vectors, connectivity
# info, etc.
polydata = reader.GetOutput()

# this will give an outline of the data members in the class. At lot of
# what's printed is more for debugging and can usually be ignored
# The main things to note are:
# Number of Points: 11 - number of points in the polyline
# Nubmer of Cells: 1 - each poly line is a single VTK_CELL
# (side note: in VTK a "point" is a x,y,z triple while a "vertex" is
# a vtk cell data type with extra attributes
print(polydata)

# There are Cell Data and Point Data sections. The data we want is
# in the Point Data. Idiomatic VTK is to start chaining method calls
# instead of grabbing objects explicitly.

# should be 2, the dummy_var I created in ParaView and another that
# got automatically added by ParaView
print(polydata.GetPointData().GetNumberOfArrays())

# Note that the Python API is automatically generated from the C++
# source and so __iter__ doesn't get defined (I think) and so looping
# has to be over indices instead of over lists.
for i in range(polydata.GetPointData().GetNumberOfArrays()):
    print(polydata.GetPointData().GetArrayName(i))

# GetArray() is overloaded to take either the index or the name if known
dummy_data = polydata.GetPointData().GetArray('dummy_var')

# dummy_data is a vtkDoubleArray. VTK predates the C++ STL, so these
# are essentially std::vector<double> with extra VTK stuff
# data are stored in "tuples" which terminology predates the Python
# interface, not 100% certain that one always gets a Python tuple, but
# usually do. In C++ you get a VTK_TUPLE object or something.
for i in range(dummy_data.GetNumberOfTuples()):
    print(dummy_data.GetTuple(i)[0])

# to get the x,y,z point coordinates:
for i in range(polydata.GetNumberOfPoints()):
    print(polydata.GetPoint(i))


# it is also possible to grab all of this into numpy arrays which might work
# better when integrating with other codes.

import numpy as np
from vtk.util import numpy_support

dummy_np = numpy_support.vtk_to_numpy(polydata.GetPointData().GetArray('dummy_var'))

print(dummy_np)

# This is tricky, polydata.GetPoints() returns an object of type vtkPoints.
# vtkPoints has a GetPoints() method, but that's not what we want in Python
# (would be okay in C++ with an array pointer), instead GetData() returns
# the coords as a Nx3 nparray
coords_np = numpy_support.vtk_to_numpy(polydata.GetPoints().GetData())
print(np.shape(coords_np))
print(coords_np)

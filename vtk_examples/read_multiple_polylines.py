#!/usr/bin/env vtkpython
# 2022-03-03 Mark Van Moer, NCSA

# same as read_single_polyline.py except now the .vtp file contains 
# multiple polylines. This data set is some arbitrary streamlines 
# (not pathlines), but the techniques should be the same. The entire
# collection of polylines is a single vtkPolyData object. The individual
# lines are not directly accessible, they have to be accessed through a
# vtkCellArray member which is an interleaved list of
# ...| N_1 | p1 | p2 | ... | pN_1 | ... | N_2 | ...
# where N is the number of points in the current polyline and
# p# is the index into the vtkPoints object holding the x,y,z triples.

# This is a little tricky because from the VTK standpoint, it's like
# trying to access individual triangles in a triangle mesh. It can be
# done, but usually that's done internally to a method and most user
# applications just work with the entire mesh.

import vtk
import numpy as np
from vtk.util import numpy_support

reader = vtk.vtkXMLPolyDataReader()

# assuming data is in same directory
reader.SetFileName('multiple_polylines.vtp')
reader.Update()

polydata = reader.GetOutput()

# Each polyline is considered a VTK cell, so 1187 cells
# means there are 1187 streamlines (polylines) in the data.
# I don't think one can count on the indexing being consistent
# from one timestep to the next. E.g., I don't think polyline 0
# in step 0 is guaranteed to be polyline 0 in step 1. Especially as
# pathlines get created and destroyed each timestep.
print(polydata)

# get all the polylines as one object.
polylines = polydata.GetLines()

# how to iterate over a cell array - the recommended way is through
# iterator objects. Instantiate the iterator, move it to the first 
# cell, then loop until done. Kind of clunky.
iter = polylines.NewIterator()
iter.GoToFirstCell()
while not iter.IsDoneWithTraversal():
    current = iter.GetCurrentCellId()
    polyline = iter.GetCurrentCell()
    print('pts in polyline {}: {}'.format(current, polyline.GetNumberOfIds()))
    iter.GoToNextCell()

# The data is stored at the data set level in arrays. 
for i in range(polydata.GetPointData().GetNumberOfArrays()):
    print(polydata.GetPointData().GetArrayName(i))

# GetArray() is overloaded to take either the index or the name if known
vel = polydata.GetPointData().GetArray('velocity')

# these two numbers should be equal
print(polydata.GetNumberOfPoints() == vel.GetNumberOfTuples())

# Okay, so the geometry is organized as cells, but the data is as points.
# A polyline (singular) is really a vtkIdList, which should be the indices
# in to the vtkPoints coordinates and should also be the same index into
# the data. Eyeballing this in ParaView using a find data query this seems
# to be a correct assumption. 

iter.GoToFirstCell()
while not iter.IsDoneWithTraversal():
    current = iter.GetCurrentCellId()
    polyline = iter.GetCurrentCell()
    # since vtkIdList is just a flat array of ints, no iterator object
    for i in range(polyline.GetNumberOfIds()):
        ptId = polyline.GetId(i)
        ptVel = vel.GetTuple(ptId)
        print('velocity at pt {}: {}'.format(ptId, ptVel))
    iter.GoToNextCell()
    
# So at this point, if you need the polylines as separate python lists
# or numpy arrays, I'd probably build them up element by element in 
# something like the above loop. There might be a clever way to use
# list slicing to grab things as chunks.

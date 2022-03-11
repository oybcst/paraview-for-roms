# paraview-for-roms
ParaView and VTK scripts for visualizing ROMS output

merge_netcdfs/ contains a Python script to merge a ROMS netCDF data file with a netCDF containing a mesh with lat, lon coords.

vtk_examples/ contains two VTK Python scripts showing how to read a .vtp (VTK XML PolyData file) containing pathline geometry exported from ParaView.

pvbatch/ contains a ParaView Python script which reads in a ROMS netcdf and exports pathline geometry as .vtps.

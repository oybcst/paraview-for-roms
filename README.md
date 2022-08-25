# paraview-for-roms
ParaView and VTK scripts for visualizing ROMS output

export_pathlines/ contains a ParaView Python script which reads in a ROMS netcdf and exports pathline geometry as .vtps.

merge_netcdfs/ contains a Python script to merge a ROMS netCDF data file with a netCDF containing a mesh with lat, lon coords; a SLURM job file; a BASH wrapper script for use with the job file.

render_scalars/workstation/ contains a pvbatch script to render a single scalar on a slice plane and two BASH scripts showing examples of how to call it over multiple inputs.

vtk_examples/ contains two VTK Python scripts showing how to read a .vtp (VTK XML PolyData file) containing pathline geometry exported from ParaView.

render_scalars/expanse/ contains a SLURM job file and a pvbatch script to render multiple netcdfs on Expanse.

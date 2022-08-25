Two example SLURM job files used on Expanse, a BASH wrapper, and a Python script to merge ROMS NetCDF4 output with a separate NetCDF with lat, lon info, and also calculate Z on the rho points from sigma.

- hari-merge-parallel.job
- zhilong-merge-parallel.job

These use gnu parallel to launch jobs as doing the merge is embarassingly parallel. 

runmerge.sh

This is a wrapper around the python call and also moves the merged output to project space on Expanse.

merge_grid_data.py

This is the Python code that actually does the merge and writes the new NetCDF.

There could stand to be some clean up of how file names are handled in runmerge.sh and merge_grid_data.py

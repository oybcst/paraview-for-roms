# 2022-03-11 Mark Van Moer, NCSA
# This script merges a netcdf4 time-series data file in index space
# with a static netcdf4 lat,lon,depth coordinate file.
# This replaces the R ncdf4 script which produced files that both
# ParaView and VisIt could load spatially, but only ParaView could
# understand the time series. I believe this is because with ncdf4 there
# was no way to write the ocean_time:field attribute.

import netCDF4

# mimicing the R script
# 1. open the grid file and get the lat,lon as 1D arrays from the
# lon_rho and lat_rho variables

# note that netCDF4.Dataset() doesn't support tilde expansion for $HOME
datapath = '/home/mvanmoer/Vis/projects/lowe-esrt/data/original/'
outpath = '/home/mvanmoer/Vis/projects/lowe-esrt/data/derived/'
gridfile = 'mobile_whole_grid05032021.nc'
datafile = 'roms_mobile_bay_output.nc'

lonlatgrid = netCDF4.Dataset(datapath+gridfile, 'r', format='NETCDF4')
print(lonlatgrid.data_model)
#lonlatgrid.close()

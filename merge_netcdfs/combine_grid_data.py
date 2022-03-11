# 2022-03-11 Mark Van Moer, NCSA
# This script merges a netcdf4 time-series data file in index space
# with a static netcdf4 lat,lon,depth coordinate file.
# This replaces the R ncdf4 script which produced files that both
# ParaView and VisIt could load spatially, but only ParaView could
# understand ocean_time. I believe this is because with ncdf4 there
# was no way to write the ocean_time:field attribute. The python API
# allows copying of all the variable attrs, though.

# The idea is that in the merged data set the longitude and latitude
# are 1D dimensions AND variables. We want this so that we can then
# in PV or VisIt convert degrees to meters to match the velocity units.

import netCDF4

# note that netCDF4.Dataset() doesn't support tilde expansion for $HOME
datapath = '/home/mvanmoer/Vis/projects/lowe-esrt/data/original/'
outpath = '/home/mvanmoer/Vis/projects/lowe-esrt/data/derived/'
gridfile = 'mobile_whole_grid05032021.nc'
datafile = 'roms_mobile_bay_output.nc'

# the grid data
grid = netCDF4.Dataset(datapath+gridfile, 'r', format='NETCDF4')

# get unique lons
lons = grid['lon_rho'][0,:]

# get unique lats
lats = grid['lat_rho'][:,0]

# the actual data 
romsdata = netCDF4.Dataset(datapath+datafile, 'r', format='NETCDF4')

# the merged output
merged = netCDF4.Dataset(outpath+'merged.nc', 'w', format='NETCDF4')

# createDimension(name, size) - size=None means unlimited
# replaces xi_rho
merged.createDimension('lon_rho', lons.size)
# replaces eta_rho
merged.createDimension('lat_rho', lats.size)
merged.createDimension('ocean_time', None)
merged.createDimension('s_rho', None)

# copy variables from romsdata to merged... but not all, just the
# data which has dims (ocean_time, s_rho, 840, 600)
# Note that there is now w_rho, so there still won't be a 3D velocity
# vector, just the vector in the uv plane at each rho point
wantedshape = tuple([romsdata['ocean_time'].size,
                   romsdata['s_rho'].size,
                   lats.size,
                   lons.size])

for name, var in romsdata.variables.items():
    if var.shape == wantedshape:
        merged.createVariable(name, var.dtype,
                ('ocean_time', 's_rho', 'lat_rho', 'lon_rho'))
        # copy the attrs
        merged[name].setncatts(romsdata[name].__dict__)
        # copy the data
        merged[name][:] = romsdata[name][:]

# copy lon, lat vars from grid, but just as the already extracted
# 1D lons and lats vars
merged.createVariable('lon_rho', grid['lon_rho'].dtype, ('lon_rho'))
merged['lon_rho'][:] = lons

merged.createVariable('lat_rho', grid['lat_rho'].dtype, ('lat_rho'))
merged['lat_rho'][:] = lats

grid.close()
romsdata.close()
merged.close()

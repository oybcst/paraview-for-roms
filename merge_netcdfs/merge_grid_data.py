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

# We assume that the lat, lon, depth and data are all at the rho pts
# and have the same dimensions.

# We assume the data is ROMS output. This script has not been tested
# with data from other simulation packages.

import netCDF4
import argparse
import sys

def merge(meshfile, datafile):

    mesh = netCDF4.Dataset(meshfile, 'r', format='NETCDF4')

    # the actual data 
    data = netCDF4.Dataset(datafile, 'r', format='NETCDF4')
    
    # the merged output
    merged = netCDF4.Dataset('./merged.nc', 'w', format='NETCDF4')

    merged.createDimension('s_rho', data.dimensions['s_rho'].size)
    merged.createDimension('eta_rho', data.dimensions['eta_rho'].size)
    merged.createDimension('xi_rho', data.dimensions['xi_rho'].size)
    # doing a straight copy gives the current size (12) not UNLIMITED, which
    # causes problems when being read by a vis app.
    merged.createDimension('ocean_time', None)

    # copy variables from data to merged... but not all, just the
    # data which has dims (ocean_time, s_rho, 840, 600)
    # Note that there is no w_rho, so there still won't be a 3D velocity
    # vector, just the vector in the uv plane at each rho point
    wantedshape = tuple([data.dimensions['ocean_time'].size,
                   data.dimensions['s_rho'].size,
                   data.dimensions['eta_rho'].size,
                   data.dimensions['xi_rho'].size])

    for name, var in data.variables.items():
        if var.shape == wantedshape:
            merged.createVariable(name, var.dtype,
                ('ocean_time', 's_rho', 'eta_rho', 'xi_rho'))
            # copy the attrs
            merged[name].setncatts(data[name].__dict__)
            # copy the data
            merged[name][:] = data[name][:]

    # However, that omits the ocean_time variable (not dimension) which
    # is 1D, so we must explicitly add it.
    merged.createVariable('ocean_time', data['ocean_time'].dtype, ('ocean_time'))
    merged['ocean_time'].setncatts(data['ocean_time'].__dict__)
    merged['ocean_time'][:] = data['ocean_time'][:]

    # additionally, ocean_time goes from 5061747600 to 5061787200 (with dt of
    # 3600) which gets exported from ParaView in scientific notation and a
    # loss of precision
    merged['ocean_time'][:] = [x - min(merged['ocean_time'][:]) for x in merged['ocean_time'][:]] 

    # copy lon, lat vars from mesh, but these are (eta_rho, xi_rho) size
    # 1D lons and lats vars. In the Mobile Bay mesh these are 2D variables,
    # it is unclear if they should also be so in the merged file. It appears
    # to be topologically orthogonal...
    merged.createVariable('lon_rho', mesh['lon_rho'].dtype, ('eta_rho', 'xi_rho'))
    merged['lon_rho'].setncatts(mesh['lon_rho'].__dict__)
    merged['lon_rho'][:] = mesh['lon_rho'][:]

    merged.createVariable('lat_rho', mesh['lat_rho'].dtype, ('eta_rho', 'xi_rho'))
    merged['lat_rho'].setncatts(mesh['lat_rho'].__dict__)
    merged['lat_rho'][:] = mesh['lat_rho'][:]

    # copy s_rho var from data
    merged.createVariable('s_rho', data['s_rho'].dtype, ('s_rho'))
    merged['s_rho'].setncatts(data['s_rho'].__dict__)
    merged['s_rho'][:] = data['s_rho'][:]

    mesh.close()
    data.close()
    merged.close()

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='''merge NetCDF file with lon,lat,
            depth to NetCDF file with data, assumes all on rho-points''')
    parser.add_argument('meshfile', help='path to NetCDF file with lon, lat, depth')
    parser.add_argument('datafile', help='path to NetCDF file with data')
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()

    merge(args.meshfile, args.datafile)

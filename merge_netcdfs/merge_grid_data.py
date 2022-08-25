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

# 2022-06-08 update
# Adapting a Matlab script from Zhilong Liu to calculate z from sigma.

# 2022-06-30 update
# Adapting for Expanse

import netCDF4
import argparse
import sys
import numpy as np
import os.path
import re

# rho-pt vars we want to write out
outvars = ('oxyg', 'temp', 'salt')

def sigma2z(h, zeta):
    '''h is a 2D array of dims (eta_rho, xi_rho)
    z0 is a 3D matrix of (eta_rho, xi_rho, N)
    zeta is a 3D matrix of (ocean_time, eta_rho, xi_rho)
    z is a 4D matrix of (ocean_time, eta_rho, xi_rho, N)
    '''
    N = 16 # number of layers in data grid
    hc = 5
    # in matlab these are column vectors, unsure that's
    # needed here
    # (16,1)
    sc_r = np.array(
            [[-0.96875,
              -0.90625,
              -0.84375,
              -0.78125,
              -0.71875,
              -0.65625,
              -0.59375,
              -0.53125,
              -0.46875,
              -0.40625,
              -0.34375,
              -0.28125,
              -0.21875,
              -0.15625,
              -0.09375,
              -0.03125]]
            ).T
    # (16,1)
    Cs_r = np.array(
                [[-0.92933179349998 ,
                  -0.794253635024853,
                  -0.669491858922906,
                  -0.556502457784762,
                  -0.455881998797214,
                  -0.367584280625179,
                  -0.291122750769323,
                  -0.225741484043665,
                  -0.170549537487751,
                  -0.124620529843704,
                  -0.0870626773619712,
                  -0.0570655714349174,
                  -0.0339297340269769,
                  -0.0170841262376474,
                  -0.00609572801830117,
                  -0.000674269832677419]]
                ).T

    # need to go through here an grab all the netCDF4 vars as numpy and
    # then convert back
    h_np = mesh['h'][:] # can't scalar add to netCDF4 variable
    dividend = ((hc * sc_r)[:, None] + (Cs_r[:,None] * h_np))
    divisor = hc + h_np
    z0 = dividend/divisor
    print('z0 shape: {}'.format(z0.shape))
    zeta_np = data['zeta'][:]
    tmpA = (zeta_np + h_np)[:,None] # (12,840,600)
    tmpB = tmpA * z0 # (12,16,840,600)
    z = zeta_np[:,None] + tmpB
    print('z shape: {}'.format(z.shape))
    return z

def merge(mesh, data, datafile):

    # the merged output
    # on Expanse, we're doing some munging to get names of the form:
    # YYYYMMDD.nc
    # the path is often of the form /path/to/data_YYYYMM/ but not always
    # the nc files appear to always be of the form .*DD\.nc
    path,base = os.path.split(datafile)
    yyyymm = re.search(r'([0-9]{6})',path)
    mergedname = f'merged-{yyyymm.group(1)}{base[-5:]}'
    merged = netCDF4.Dataset(mergedname, 'w', format='NETCDF4')

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
        if var.shape == wantedshape and name in outvars:
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

    # For the use case of eventually exporting geometry and a .pvd file from
    # ParaView, ocean_time needs to be shifted, because Modified Julian Day
    # times will get exported in scientific notation, losing precision!
    # for a single .nc, this can be done with the following line:
    # merged['ocean_time'][:] = [x - min(merged['ocean_time'][:]) for x in merged['ocean_time'][:]]
    
    # However, for a series of .nc's, then the time to be subtracted is the earliest
    # time in the entire series. This could possibly be probed for, but hard-coding
    # suffices if this is run infrequently.
    # earliest time in 201811/mobile_g01_his_00001.nc 
    earliest = 5047747200
    merged['ocean_time'][:] = [x - earliest for x in merged['ocean_time'][:]]
    
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

    # finally, we want z_rho with real bathmetry
    z_rho = sigma2z(mesh, data)
    merged.createVariable('z_rho', z_rho.dtype, ('ocean_time', 's_rho', 'eta_rho', 'xi_rho'))
    merged['z_rho'].setncattr('long_names', 'z-coordinate derived from sigma at rho-points')
    merged['z_rho'][:] = z_rho
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

    mesh = netCDF4.Dataset(args.meshfile, 'r', format='NETCDF4')
    data = netCDF4.Dataset(args.datafile, 'r', format='NETCDF4')
    # commented while testing
    #sigma2z(mesh,data)
    merge(mesh, data, args.datafile)
    mesh.close()
    data.close()

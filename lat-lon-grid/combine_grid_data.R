# Mark Van Moer, NCSA, University of Illinois at Urbana-Champaign
# 2022-02-18
# Combines a netcdf containing data over time with a netcdf containing
# a static mesh.
library(tidyverse)
library(ncdf4)

datapath <- "~/Vis/projects/lowe-esrt/data/original/"
outpath <- "~/Vis/projects/lowe-esrt/data/derived/"
gridfile <- "mobile_whole_grid05032021.nc"
datafile <- "roms_mobile_bay_output.nc"

# Working on the mesh
lonlatgrid <- nc_open(str_c(datapath, gridfile))

# want to grab lat_rho, lon_rho and extract them, these are 2D tuples
# at every rho point
lon_rho <- ncvar_get(lonlatgrid, "lon_rho")
lat_rho <- ncvar_get(lonlatgrid, "lat_rho")

# what we actually want are 1D lists of lon and lat, similar to
# vtkRectilinearData
lons <- lon_rho[,1] # 600x1
lats <- lat_rho[1,] # 840x1

# working on the data
romsdata <- nc_open(str_c(datapath, datafile))
times <- ncvar_get(romsdata, "ocean_time")

# for testing, just grab NO3, this is 4D 600 x 840 x 16 x 12
# in x, y, z, time
# data list: chlorophyll, LdetritusC, LdetritusN, NH4, NO3, oxyg,
# phytoplankton, SdetritusC, SdetritusN, Talk, TIC, zooplankton,
# temp, salinity, u_eastward, v_northward
# The proper way to do this is to make a list of strings, then user
# higher order functions, but that'll have to wait for a minute
cholorphyll <- ncvar_get(romsdata, "chlorophyll")
LdetritusC <- ncvar_get(romsdata, "LdetritusC")
LdetritusN <- ncvar_get(romsdata, "LdetritusN")
NH4 <- ncvar_get(romsdata, "NH4")
NO3 <- ncvar_get(romsdata, "NO3")
oxyg <- ncvar_get(romsdata, "oxyg")
phytoplankton <- ncvar_get(romsdata, "phytoplankton")
SdetritusC <- ncvar_get(romsdata, "SdetritusC")
SdetritusN <- ncvar_get(romsdata, "SdetritusN")
Talk <- ncvar_get(romsdata, "Talk")
TIC <- ncvar_get(romsdata, "TIC")
zooplankton <- ncvar_get(romsdata, "zooplankton")
temp <- ncvar_get(romsdata, "temp")
salt <-ncvar_get(romsdata, "salt")
u_eastward <- ncvar_get(romsdata, "u_eastward")
v_northward <- ncvar_get(romsdata, "v_northward")

# is top z == 1 or z == 16? 16, by inspection
topidx <- 16
topcholorphyll <- cholorphyll[,,topidx,]
topLdetritusC <- LdetritusC[,,topidx,]
topLdetritusN <- LdetritusN[,,topidx,]
topNH4 <- NH4[,,topidx,]
topNO3 <- NO3[,,topidx,]
topoxyg <- oxyg[,,topidx,]
topphytoplankton <- phytoplankton[,,topidx,]
topSdetritusC <- SdetritusC[,,topidx,]
topSdetritusN <- SdetritusN[,,topidx,]  
topTalk <- Talk[,,topidx,]
topTIC <- TIC[,,topidx,]
topzooplankton <- zooplankton[,,topidx,]
toptemp <- temp[,,topidx,]
topsalt <- salt[,,topidx,]
topu_eastward <- u_eastward[,,topidx,]
topv_northward <- v_northward[,,topidx,]

# define dimensions
londim <- ncdim_def("longitude", "degrees_east", as.double(lons))
latdim <- ncdim_def("latitude", "degrees_north", as.double(lats))
timedim <- ncdim_def("ocean_time", "seconds since 1858-11-17 00:00:00", 
                     as.double(times), unlim=TRUE, 
                     calendar="proleptic_gregorian")

# must have coordinate vars of same name
lonvar <- ncvar_def("longitude", "degrees_east", londim, NULL, 
                    longname="longitude", prec="double")
latvar <- ncvar_def("latitude", "degress_north", latdim, NULL, 
                    longname="latitude", prec="double")
timevar <- ncvar_def("ocean_time", "seconds since 1858-11-17 00:00:00", 
                     timedim, NULL, longname="time since initialization")

fillval <- 1e37 # from ROMS
combofile <- "top_slice_test.nc"

chlorophylldef <- ncvar_def("chlorophyll", "milligrams_chlorophyll meter-3", list(londim, latdim, timedim), fillval)
LdetritusCdef <- ncvar_def("LdetritusC", "millimole_carbon meter-3", list(londim, latdim, timedim), fillval)
LdetritusNdef <- ncvar_def("LdetritusN", "millimole_nitrogen meter-3", list(londim, latdim, timedim), fillval)
NH4def <- ncvar_def("NH4", "millimole_NH4 meter-3", list(londim, latdim, timedim), fillval)
NO3def <- ncvar_def("NO3", "millimole_N03 meter-3", list(londim, latdim, timedim), fillval)
oxygdef <- ncvar_def("oxyg", "millimole_O2 meter-3", list(londim, latdim, timedim), fillval)
phytoplanktondef <- ncvar_def("phytoplankton", "millimole_nitrogen meter-3", list(londim, latdim, timedim), fillval)
SdetritusCdef <- ncvar_def("SdetritusC", "millimole_carbon meter-3", list(londim, latdim, timedim), fillval)
SdetritusNdef <- ncvar_def("SdetritusN", "millimole_nitrogen meter-3", list(londim, latdim, timedim), fillval)
Talkdef <- ncvar_def("Talk", "millimole meter-3", list(londim, latdim, timedim), fillval)
TICdef <- ncvar_def("TIC", "millimole_carbon meter-3", list(londim, latdim, timedim), fillval)
zooplanktondef <- ncvar_def("zooplankton", "millimole_nitrogen meter-3", list(londim, latdim, timedim), fillval)
tempdef <- ncvar_def("temp", "Celsius", list(londim, latdim, timedim), fillval)
saltdef <- ncvar_def("salt",'',list(londim, latdim, timedim), fillval)
u_eastwarddef <- ncvar_def("u_eastward", "meter second-1", list(londim, latdim, timedim), fillval)
v_northwarddef <- ncvar_def("v_northward", "meter second-1", list(londim, latdim, timedim), fillval )

ncout <- nc_create(str_c(outpath, combofile), 
                   list(chlorophylldef, LdetritusCdef, LdetritusNdef, NH4def, NO3def,
                        oxygdef, phytoplanktondef, SdetritusCdef, SdetritusNdef, Talkdef,
                        TICdef, zooplanktondef, tempdef, saltdef, u_eastwarddef, v_northwarddef), force_v4 = TRUE, verbose=TRUE)

ncvar_put(ncout, chlorophylldef, topcholorphyll)
ncvar_put(ncout, LdetritusCdef, topLdetritusC)
ncvar_put(ncout, LdetritusNdef, topLdetritusN)
ncvar_put(ncout, NH4def, topNH4)
ncvar_put(ncout,NO3def,topNO3)
ncvar_put(ncout, oxygdef, topoxyg)
ncvar_put(ncout, phytoplanktondef, topphytoplankton)
ncvar_put(ncout, SdetritusCdef, topSdetritusC)
ncvar_put(ncout, SdetritusNdef, topSdetritusN)
ncvar_put(ncout, Talkdef, topTalk)
ncvar_put(ncout, TICdef, topTIC)
ncvar_put(ncout, zooplanktondef, topzooplankton)
ncvar_put(ncout, tempdef, toptemp)
ncvar_put(ncout, saltdef, topsalt)
ncvar_put(ncout, u_eastwarddef, topu_eastward)
ncvar_put(ncout, v_northwarddef, topv_northward)
nc_close(ncout)

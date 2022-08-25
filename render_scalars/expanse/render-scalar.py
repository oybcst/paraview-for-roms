from datetime import date
import sys
import re
import json

# There's a bug not fixed until PV 5.9.0 where argv needs to be parsed 
# before the paraview.simple import
# would rather have these in a YAML or JSON file...
scalar = sys.argv[1]
zslice = int(sys.argv[2])
scalarMin = float(sys.argv[3])
scalarMax = float(sys.argv[4])
colormap = sys.argv[5]
pngbase = sys.argv[6]
ncfile = sys.argv[7]


from paraview.simple import *
paraview.simple._DisableFirstRenderCameraReset()

# This is an unfortunate workaround section. For unknown reasons, ParaView on 
# Expanse will not load every colormap available. The following two lines will 
# print a list of all the colormaps ("lookup tables" or LUTs) that it thinks 
# it sees.
#
# availmaps = GetLookupTableNames()
# print(availmaps)
#
# in particular, the Viridis and Plasma colormaps are listed, but using them 
# further below the resulting images are in the Cool to Warm colormap. The 
# workaround is to export the desired colormaps as JSON from a local ParaView, 
# upload to Expanse, and load with the json module. 

# check if the colormap string passed has a json extension
cmapre = re.search('json$', colormap)
cmapjson = []
cmaprgbpts = []
if cmapre:
    with open(colormap) as json_file:
        cmapjson = json.load(json_file)
        cmapRGBpts = cmapjson[0]['RGBPoints']

# original showing entire bay
#winW = 1920 // 3
#winH = 1080

# for closeup found by inspection in Adobe AE and ParaView
winW = 896
winH = 773

# output images need to be named with sequential numbering so that
# animation software will recognize them as a series. We use hours
# since 2019-01-01T00:00:00 as the image index.
YYYYMMDD = ncfile[-11:-3]
start = date(2019, 1, 1)
curr =  date(int(YYYYMMDD[:4]),int(YYYYMMDD[4:6]),int(YYYYMMDD[6:]))
dt = curr - start
dthrs = dt.days * 24

# Data is on the rho points
nc = NetCDFReader(FileName=[ncfile])
nc.Dimensions = '(s_rho, eta_rho, xi_rho)'
nc.SphericalCoordinates = 0    # don't use spherical coords
nc.ReplaceFillValueWithNan = 1 # DO replace fill (-9999) with NaN 
nc.OutputType = 'Automatic'

# extract z slice plane, indices go from 0-15, 0 is bottom
extractZ = ExtractSubset(Input=nc)
# for the whole domain
#extractZ.VOI = [0, 599, 0, 839, zslice, zslice]
# for the closeup subdomain
extractZ.VOI = [0, 599, 60, 577, zslice, zslice]

# Convert from lat, lon to meters. s_rho is meters, this
# constant was found via googling.
# the longitude range is -88.4987 to -87.6684
# the latitude range is 29.7902 to 31.088
deg2mfactor = 111139.0
latlon2m = Transform(Input=extractZ)
latlon2m.Transform = 'Transform'
latlon2m.Transform.Scale = [deg2mfactor, deg2mfactor, 1.0]

renderView = GetActiveViewOrCreate('RenderView')
renderView.ViewSize = [winW, winH]
renderView.OrientationAxesVisibility = 0

ncDisplay = GetDisplayProperties(latlon2m, view=renderView)
ncDisplay.Representation = 'Surface'
ncDisplay.SetScaleArray = ['POINTS', scalar]

LUT = GetColorTransferFunction(scalar)

if cmapre:
    # if the colormap was loaded from a json, just set the attr
    LUT.RGBPoints = cmapRGBpts
else:
    LUT.ApplyPreset(colormap, True)
LUT.NanOpacity = 0.0

ColorBy(ncDisplay, ('POINTS', scalar))

# WARNING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# this MUST be called after ColorBy(), despite what the python trace does
# otherwise it will have NO effect!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
LUT.RescaleTransferFunction(scalarMin, scalarMax)

# for troubleshooting
#ncDisplay.SetScalarBarVisibility(renderView, True)

# center the camera over the center, centrally...
xmin,xmax,ymin,ymax,zmin,zmax = latlon2m.GetDataInformation().GetBounds()

#camZ = 300 * 1000 # 300KM up for full data
camZ = 150 * 1000 # 150KM up for closeup
renderView.CameraPosition = [(xmin+xmax)/2.0, (ymin+ymax)/2.0, camZ]
renderView.CameraFocalPoint = [(xmin+xmax)/2.0, (ymin+ymax)/2.0, -100]

# Using SaveScreenshot because SaveAnimation doesn't honor the 
# RescaleTransferFunction call!
# 24 hrs in a day, one day per file.
for i in range(24):
    times = nc.TimestepValues
    view = GetActiveView()
    view.ViewTime = times[i]
    Render()
    pngfile = '{}.{:04d}.png'.format(pngbase, dthrs + i)
    print(f'Saving: {pngfile}...')
    # another workaround - ParaView on Expanse doesn't seem to honor different
    # background colors 
    # (which are set in ~/.config/ParaView/ParaView-UserSettings.json IIUC)
    # but setting TransparentBackground works. Fix in the compositing program
    SaveScreenshot(pngfile, renderView, 
            ImageResolution=[winW, winH], TransparentBackground=1)

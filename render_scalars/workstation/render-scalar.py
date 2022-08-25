from datetime import date
import sys

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

winW = 1920 // 3
winH = 1080

YYYYMMDD = ncfile[-11:-3]
# hours since start of ROMS data which is 2018-11-01
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

extractZ = ExtractSubset(Input=nc)
extractZ.VOI = [0, 599, 0, 840, zslice, zslice]

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

# might be better to have this in lat, lon degrees and then convert to
# meters.
# by inspection in ParaView
#renderView.CameraPosition = [-9789519.81600239, 3382974.081183975, 353675.63746335817]
#renderView.CameraFocalPoint = [-9789519.81600239, 3382974.08113975, -81642.97223371016]
xmin,xmax,ymin,ymax,zmin,zmax = latlon2m.GetDataInformation().GetBounds()
renderView.CameraPosition = [(xmin+xmax)/2.0, (ymin+ymax)/2.0, 300 * 1000]
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
    SaveScreenshot(pngfile, renderView, ImageResolution=[winW, winH])

from paraview.simple import *
from datetime import date
import sys

paraview.simple._DisableFirstRenderCameraReset()

#projpath = '/home/mvanmoer/Vis/projects/lowe-esrt/'
#ncpath = projpath + 'data/derived/expanse_download/'
#ncfile = ncpath + 'merged-20190601.nc'

ncfile = sys.argv[1]

YYYYMMDD = ncfile[-11:-3]
# hours since start of ROMS data
start = date(2018, 11, 1)
curr =  date(int(YYYYMMDD[:4]),int(YYYYMMDD[4:6]),int(YYYYMMDD[6:]))
dt = curr - start
dthrs = dt.days * 24


nc = NetCDFReader(FileName=[ncfile])
nc.Dimensions = '(s_rho, eta_rho, xi_rho)'
nc.SphericalCoordinates = 0
nc.ReplaceFillValueWithNan = 1
nc.OutputType = 'Automatic'

latlon2m = Transform(Input=nc)
latlon2m.Transform = 'Transform'
latlon2m.Transform.Scale = [111139.0, 111139.0, 1.0]

renderView = GetActiveViewOrCreate('RenderView')
renderView.ViewSize = [660, 1080]

ncDisplay = GetDisplayProperties(latlon2m, view=renderView)
ncDisplay.Representation = 'Surface'
ncDisplay.SetScaleArray = ['POINTS', 'oxyg']

oxygLUT = GetColorTransferFunction('oxyg')
oxygLUT.ApplyPreset('Black, Blue and White', True)
oxygLUT.NanOpacity = 0.0

ColorBy(ncDisplay, ('POINTS', 'oxyg'))

# WARNING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# this MUST be called after ColorBy(), despite what the python trace does
# otherwise it will have NO effect!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
oxygLUT.RescaleTransferFunction(0.0, 500.0)

# for troubleshooting
#ncDisplay.SetScalarBarVisibility(renderView, True)

# might be better to have this in lat, lon degrees and then convert to
# meters.
renderView.CameraPosition = [-9789519.81600239, 3382974.081183975, 353675.63746335817]
renderView.CameraFocalPoint = [-9789519.81600239, 3382974.08113975, -81642.97223371016]

# 24 hrs in a day, one day per file.
for i in range(24):
    times = nc.TimestepValues
    view = GetActiveView()
    view.ViewTime = times[i]
    Render()
    pngfile = 'parallel-test.{:04d}.png'.format(dthrs + i)
    print(f'Saving: {pngfile}...')
    SaveScreenshot(pngfile, renderView, ImageResolution=[660, 1080])


# SaveAnimation doesn't honor the RescaleTransferFunction call!
#SaveAnimation('./from-scratch-test.png',
#        renderView,
#        ImageResolution=[660, 1080],
#        FrameWindow=[0,23],
#        SuffixFormat='.%04d')

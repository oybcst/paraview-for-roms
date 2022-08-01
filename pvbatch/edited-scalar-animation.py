# 2022-07-29 edited from ParaView trace by Mark Van Moer, NCSA
# This approach assumes a pvsm has been saved with all the desired options,
# camera placement, colorbars, etc.

# pvbatch version MUST match the version of ParaView that exported the pvsm, 5.8.0


#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

import glob

# 1920x1080 is HD1080
imgW = 1920
imgH = 1080

# 0-719 is 24*30 hours in June 2019 test data
startT = 0
endT = (24 * 30) - 1 

statefile = '/home/mvanmoer/Vis/projects/lowe-esrt/data/assets/2019-06-01-oxyg-test-8.pvsm'

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')
# uncomment following to set a specific view size
renderView1.ViewSize = [imgW, imgH]

# get layout
layout1 = GetLayout()

# destroy renderView1
Delete(renderView1)
del renderView1

# load state
# This state file is based on setting options for merged-20190601.nc
# we glob the files instead of listing them explicitly
mergedncpath = '/home/mvanmoer/Vis/projects/lowe-esrt/data/derived/expanse_download/'
mergedncs = glob.glob(mergedncpath+'merged-*.nc')
print(f'MVM: {mergedncs}')
LoadState(statefile,
        LoadStateDataFileOptions='Choose File Names',
        DataDirectory='/home/mvanmoer/Vis/projects/lowe-esrt/data/assets',
        OnlyUseFilesInDataDirectory=0,
        merged20190601ncFileName=mergedncs)

# get animation scene
animationScene1 = GetAnimationScene()

# get the time-keeper
timeKeeper1 = GetTimeKeeper()

# find view
renderView1 = FindViewOrCreate('RenderView1', viewtype='RenderView')

# get layout
layout1_1 = GetLayoutByName("Layout #1")

# set active view
SetActiveView(renderView1)

# current camera placement for renderView1
# These are magic numbers from exporting the PVSM from ParaView, can be thought of as meters.
renderView1.CameraPosition = [-9789520.0, 3382974.125, 285047.43203943904]
renderView1.CameraFocalPoint = [-9789520.0, 3382974.125, -45749.11660845035]
renderView1.CameraParallelScale = 85616.44684425622

# save animation
# odd API, IMNSHO, the first argument is what the name would be if this was saving only a single PNG
# however, the actual output will be a series of PNGs of the form filename.####.png
basepngname = '/home/mvanmoer/Vis/projects/lowe-esrt/renders/frames/2019-06-01-oxyg-test-13.png'
SaveAnimation(basepngname,
        renderView1, 
        ImageResolution=[imgW,imgH],
        FrameWindow=[startT,endT])

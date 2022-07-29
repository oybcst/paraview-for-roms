# 2022-07-29 edited from ParaView trace by Mark Van Moer, NCSA
# This approach assumes a pvsm has been saved with all the desired options,
# camera placement, colorbars, etc.
# trace generated using paraview version 5.8.0

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')
# uncomment following to set a specific view size
renderView1.ViewSize = [1920, 1080]

# get layout
layout1 = GetLayout()

# destroy renderView1
Delete(renderView1)
del renderView1

# load state
LoadState('/home/mvanmoer/Vis/projects/lowe-esrt/data/assets/2019-06-01-oxyg-test-8.pvsm', LoadStateDataFileOptions='Use File Names From State',
    DataDirectory='/home/mvanmoer/Vis/projects/lowe-esrt/data/assets',
    OnlyUseFilesInDataDirectory=0,
    merged20190601ncFileName=['/home/mvanmoer/Vis/projects/lowe-esrt/data/derived/expanse_download/merged-20190601.nc'])

# get animation scene
animationScene1 = GetAnimationScene()

# get the time-keeper
timeKeeper1 = GetTimeKeeper()

# find view
renderView1 = FindViewOrCreate('RenderView1', viewtype='RenderView')
# uncomment following to set a specific view size
# renderView1.ViewSize = [1920, 1080]

# get layout
layout1_1 = GetLayoutByName("Layout #1")

# set active view
SetActiveView(renderView1)

# current camera placement for renderView1
renderView1.CameraPosition = [-9789520.0, 3382974.125, 285047.43203943904]
renderView1.CameraFocalPoint = [-9789520.0, 3382974.125, -45749.11660845035]
renderView1.CameraParallelScale = 85616.44684425622

# save animation
SaveAnimation('/home/mvanmoer/Vis/projects/lowe-esrt/renders/frames/2019-06-01-oxyg-test-8a.png', renderView1, ImageResolution=[1920, 1080],
    FontScaling='Scale fonts proportionally',
    OverrideColorPalette='',
    StereoMode='No change',
    TransparentBackground=0,
    FrameRate=1,
    FrameWindow=[0, 23], 
    # PNG options
    CompressionLevel='5',
    SuffixFormat='.%04d')

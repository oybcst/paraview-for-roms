# 2022-03-03 Mark Van Moer, NCSA
# edit of trace generated using paraview version 5.9.1
# !!! be sure to set the datapath variable appropriately !!!
# !!! be sure to set the ouputpath variable appropriately !!!

#### import the simple module from the paraview
from paraview.simple import *

# to grab input merged mesh + ROMS output NetCDF from cmdline
import sys

#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# create a new 'NetCDF Reader'
ncfile = sys.argv[1]
nc = NetCDFReader(registrationName=ncfile, FileName=[ncfile])
nc.Dimensions = '(s_rho, lat_rho, lon_rho)'

# get animation scene
animationScene1 = GetAnimationScene()

# update animation scene based on data timesteps
animationScene1.UpdateAnimationUsingDataTimeSteps()

# Properties modified on nc
# "spherical coordinates" has a particular meaning for how the data is
# projected in the client GUI, turn off.
nc.SphericalCoordinates = 0
# need to change fill value to NaNs or ParaView will think the fill value is data
nc.ReplaceFillValueWithNan = 1

# get active view
# Even though we're not rendering, we have to have a view established
# so we can hide the geometry we don't want to export.
renderView1 = GetActiveViewOrCreate('RenderView')

# slice the top surface, we don't have a w velocity component
# at the rho points, so no point in having anything but a slice
slice1 = Slice(registrationName='Slice1', Input=nc)
slice1.SliceType = 'Plane'
slice1.SliceType.Origin = [-88.08356907460802, 30.439126530406817, 15.0]
slice1.SliceType.Normal = [0.0, 0.0, 1.0]

# create a new 'Transform'
transform1 = Transform(registrationName='Transform1', Input=slice1)
transform1.Transform = 'Transform'

# Properties modified on transform1.Transform
# I found these values googling "convert lon,lat to meters"
transform1.Transform.Scale = [111139.0, 111139.0, 1.0]

# create a new 'Calculator'
calculator1 = Calculator(registrationName='Calculator1', Input=transform1)
calculator1.Function = ''

# Properties modified on calculator1
calculator1.ResultArrayName = 'uv_velocity'
calculator1.Function = 'u_eastward*iHat+v_northward*jHat'

# create a new 'Plane'
plane1 = Plane(registrationName='Plane1')

# Properties modified on plane1
# Arbitrary values chosen for visual effect
plane1.Origin = [-9788270.0, 3358210.0, 15.0]
plane1.Point1 = [-9783510.0, 3358210.0, 15.0]
plane1.Point2 = [-9788270.0, 3363310.0, 15.0]
plane1.XResolution = 50
plane1.YResolution = 50

# create a new 'ParticleTracer'
particleTracer1 = ParticleTracer(registrationName='ParticleTracer1', Input=calculator1,
    SeedSource=plane1)
particleTracer1.SelectInputVectors = ['POINTS', 'uv_velocity']

# Properties modified on particleTracer1
# Static seeds because the Plane source never changes 
particleTracer1.StaticSeeds = 1

# State mesh because the netcdf mesh never changes geometry
particleTracer1.StaticMesh = 1

# completely arbitrary for visual effect
particleTracer1.ForceReinjectionEveryNSteps = 5

# might save some compute time
particleTracer1.ComputeVorticity = 0

# create a new 'Temporal Particles To Pathlines'
temporalParticlesToPathlines1 = TemporalParticlesToPathlines(registrationName='TemporalParticlesToPathlines1', Input=particleTracer1,
    Selection=None)

# Properties modified on temporalParticlesToPathlines1

# This means every 23rd point is shown. I picked a prime number to try
# and avoid an obvious pattern in the seeds.
temporalParticlesToPathlines1.MaskPoints = 23

# These next two attributes have to be played around with to see how they behave
# The maxtracklength is that as a patline evolves, it will never be more than 
# that length.
temporalParticlesToPathlines1.MaxTrackLength = 5

# If a particle is advected more than this distance it will be discarded, I think
temporalParticlesToPathlines1.MaxStepDistance = [10000.0, 10000.0, 1.0]

# There are many options to ID the particles, this a good default, but
# it's worth looking at in the GUI to see what's available.
temporalParticlesToPathlines1.IdChannelArray = 'ParticleId'

# show data in view
temporalParticlesToPathlines1Display = Show(temporalParticlesToPathlines1, renderView1, 'GeometryRepresentation')

# get color transfer function/color map for 'TrailId'
trailIdLUT = GetColorTransferFunction('TrailId')

# All visible geometry will get exported, so we need to make sure everything is hidden 
# except the Pathlines object hanging off the TemporalParticlesToPathlines filter


# hide data in view
Hide(nc, renderView1)
Hide(transform1, renderView1)
Hide(calculator1, renderView1)
Hide(plane1, renderView1)
Hide(particleTracer1, renderView1)

# TemporalParticlesToPathlines1 has two downstream objects
# 0 - the pathlines
# 1 - the particles
Hide(OutputPort(temporalParticlesToPathlines1, 1), renderView1)

outputpath = './'

# the output is just the name of the .pvd, but there will be a subdirectory
# with .vtps
# The pvd will have munged timesteps for this particular data because 
# ParaView will write them in scientific notation, rounded. (sigh.)
output = 'pvbatch_pathline_output_all_vars.pvd'

# To save all the variables along the pathlines, use SaveData() instead of
# WriteAnimationGeometry() which only saves visible geometry/data.
SaveData(outputpath + output, 
         proxy=temporalParticlesToPathlines1, 
         PointDataArrays=['ErrorCode', 
             'InjectedPointId', 
             'InjectionStepId', 
             'LdetritusC', 
             'LdetritusN', 
             'NH4', 
             'NO3', 
             'ParticleAge', 
             'ParticleId', 
             'ParticleSourceId', 
             'SdetritusC', 
             'SdetritusN', 
             'TIC', 
             'Talk', 
             'TrackLength', 
             'TrailId', 
             'chlorophyll', 
             'oxyg', 
             'phytoplankton', 
             'salt', 
             'temp', 
             'u_eastward', 
             'v_northward', 
             'velocity', 
             'zooplankton'],
    WriteTimeSteps=1)

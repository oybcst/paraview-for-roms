#!/bin/bash

# NOTE: This will NOT run if there is an existing rendering.log file in pwd!

module load ParaView/5.8.0-prebuilt

SLURM_NTASKS=18
NCDIR=/home/mvanmoer/Vis/projects/lowe-esrt/data/derived/expanse_download/

# get all the .nc's as a spaced-delimited list for piping into parallel
readarray -d '' NCS < <(find $NCDIR -name "*.nc" -print0)

parallel="time -p parallel --delay 0.2 -j $SLURM_NTASKS --joblog rendering.log --resume"

# eventually want to have this args in an config file instead.
#renderscript="render-scalar.py salt 0 0 40 \"Viridis (matplotlib)\" salt"
renderscript="render-scalar.py oxyg 0 0 500 \"Black, Blue and White\" oxygen"
#renderscript="render-scalar.py temp 15 10 35 Plasma temperature-plasma"
#renderscript="render-scalar.py temp 15 10 35 \"Cool to Warm\" temperature-cool-to-warm"
#renderscript="render-scalar.py temp 15 10 35 \"Cold and Hot\" temperature-cold-and-hot"

# this one outputs Plasma?!
#renderscript="render-scalar.py temp 15 10 35 \"Cool to Warm \(Extended\)\" temperature-cool-to-warm-extended"

#renderscript="render-scalar.py temp 15 10 35 \"Spectral_lowBlue\" temperature-spectral-lowblue"

#renderscript="render-scalar.py temp 15 10 35 \"Rainbow Uniform\" temperature-rainbow-uniform"
printf '%s\n' "${NCS[@]}" | $parallel "pvbatch $renderscript {} > render.log.{#}"

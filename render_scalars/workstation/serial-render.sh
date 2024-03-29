#!/bin/bash

module load ParaView/5.8.0-prebuilt

NCDIR=/home/mvanmoer/Vis/projects/lowe-esrt/data/derived/expanse_download/

# get all the .nc's as a list
readarray -d '' NCS < <(find $NCDIR -name "*.nc" -print0)

renderscript=render-scalar.py
for nc in ${NCS[@]}; do
    echo "rendering $nc"
    #pvbatch $renderscript oxyg 0 0 500 'Black, Blue and White' oxygen $nc
    #pvbatch $renderscript temp 15 10 35 Plasma temperature $nc
    pvbatch $renderscript salt 0 0 40 'Viridis (matplotlib)' salt $nc
done

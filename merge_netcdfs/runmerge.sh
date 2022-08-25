#!/bin/bash

# Python/NetCDF script that does the actual merge of lat-lon grid
# to ROMS output netcdf - only rho-points values get copied.
MERGESCRIPT=$HOME/Vis/projects/lowe-esrt/bin/merge_grid_data.py

GRIDNC=$1
DATANC=$2

echo "merging $GRIDNC with $DATANC"
python $MERGESCRIPT $GRIDNC $DATANC

# the merged files will have an output file name in the for
# form of: 
# merged-YYYYMMDD.nc
# there is not entirely consistent naming of the ROMS output, so
# regex's are used to grab the YYYYMM and the DD, respectively.

DATADIR=$(dirname $DATANC)
yyyymmre='([0-9]{6})'
if [[ $DATADIR =~ $yyyymmre ]] ; then
	YYYYMM=${BASH_REMATCH[1]}
fi
BASEDATANC=$(basename $DATANC)
ddncre='mobile_g01_his_000([0-9]{2}.\nc)'
if [[ $BASEDATANC =~ $ddncre ]] ; then
	DDNC=${BASH_REMATCH[1]}
fi

MERGEDNC="merged-$YYYYMM$DDNC"
echo "mv'ing $MERGEDNC"
if [ ! -f $MERGEDNC ]; then
	echo "$MERGEDNC not found"
	echo "MVM: pwd call: $PWD"
	echo "$(ls)"
else
	mv $MERGEDNC /expanse/lustre/projects/ncs124/$USER
fi

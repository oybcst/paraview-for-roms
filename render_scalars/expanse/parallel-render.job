#!/bin/bash
#SBATCH --job-name="gnu-parallel-render"
#SBATCH --output="gnu-parallel-render.%j.%N.out"
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --mem=128G
#SBATCH --account=ncs124
#SBATCH --export=None
#SBATCH --mail-user=mvanmoer@illinois.edu
#SBATCH --mail-type=ALL
#SBATCH -t 00:40:00

# NOTE: This will NOT run if there is are existing rendering log files in pwd!

export SLURM_EXPORT_ENV=ALL
module purge
module load cpu/0.15.4
module load gcc/10.2.0
module load openmpi/4.0.4
module load paraview/5.8.0-openblas
module load parallel
module load slurm

# contains the merged NetCDFS
NCDIR=/expanse/lustre/projects/ncs124/mvanmoer/zhilong/
BINDIR=$HOME/Vis/projects/lowe-esrt/bin/rendering/

cd /scratch/$USER/job_$SLURM_JOB_ID

# get all the .nc's as a space-delimited list for piping into parallel
readarray -d '' NCS < <(find $NCDIR -name "*.nc" -print0)

# currently render a scalar per job at a particular k-index/z-slice
# comment/uncomment as needed. This could be better handled by putting
# into config file
# OXYGEN
#var=oxyg
#zslice=15
#min=0
#max=500
#colormap="\"Black, Blue and White\""
#name=${var}_${zslice}_closeup

# SALT
#var=salt
#zslice=15
#min=0
#max=40
#colormap=$HOME/Vis/projects/lowe-esrt/data/assets/viridis_export.json
#name=${var}_${zslice}_closeup

# TEMPERATURE
var=temp
zslice=0
min=10
max=35
colormap=$HOME/Vis/projects/lowe-esrt/data/assets/plasma_export.json
name=${var}_${zslice}_closeup

srun="srun --exclusive -N1 -n1"
parallel="time -p parallel --delay 0.2 -j $SLURM_NTASKS --joblog $name.log --resume"

renderscript="render-scalar.py $var $zslice $min $max $colormap $name"

printf '%s\n' "${NCS[@]}" | $parallel "$srun pvbatch $BINDIR/$renderscript {} > $name.log.{#}"

# there will be 8760 png's and 366 log files per run, so they need to be
# tar'd or lustre will be unhappy.
tar cvf $name.tar $name*png
mv $name.tar /expanse/lustre/projects/ncs124/$USER/renders/frames
rm -rf $name*png

tar cvf logs-$name.tar $name.log*
mv logs-$name.tar /expanse/lustre/projects/ncs124/$USER/renders/frames
rm -rf $name.log*

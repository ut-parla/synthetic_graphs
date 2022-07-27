#!/bin/bash

#SBATCH -J dg2           # Job name
#SBATCH -o dg2.o%j       # Name of stdout output file
#SBATCH -e dg2.e%j       # Name of stderr error file
#SBATCH -p small           # Queue (partition) name
#SBATCH -N 1               # Total # of nodes (must be 1 for serial)
#SBATCH -n 1               # Total # of mpi tasks (should be 1 for serial)
#SBATCH -t 05:00:00        # Run time (hh:mm:ss)
#SBATCH -A ASC21002        # Project/Allocation name (req'd if you have more than 1)

source /scratch1/06081/wlruys/miniconda3/etc/profile.d/conda.sh
conda activate rap

# Any other commands must follow all #SBATCH directives...
module list
pwd
date

n=1000

for rep in 1 2 3 4 5
do
    for gil in 500 1000 2500 5000 10000 25000 40000
    do
        size=$((50000-gil))
        for work in $(seq 1 1 4; seq 5 5 50);
        do
            python_output=`python dask_thread.py -workers ${work} -time ${size} -n ${n} -gtime ${gil}`
            echo "$gil, $python_output"
        done
    done
done

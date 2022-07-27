#!/bin/bash

#SBATCH -J dpsc           # Job name
#SBATCH -o dpsc.o%j       # Name of stdout output file
#SBATCH -e dpsc.e%j       # Name of stderr error file
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

for rep in 1 2 3 4 5
do
    for n in $(seq 100 100 5000);
    do
        first=0
        for size in 0
        do
            for work in 20;
            do
                python_output=`python dask_process.py -workers ${work} -time ${size} -n ${n}`
                last=`echo ${python_output} | awk -F "," '{print $NF}'`
                echo "$n, $python_output"
            done
        done
    done
done

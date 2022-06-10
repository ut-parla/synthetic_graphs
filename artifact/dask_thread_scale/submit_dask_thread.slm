#!/bin/bash

#SBATCH -J dtsc           # Job name
#SBATCH -o dtsc.o%j       # Name of stdout output file
#SBATCH -e dtsc.e%j       # Name of stderr error file
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
    for n in $(seq 100 100 5000);
    do
        first=0
        for size in 0
        do
            for work in 20;
            do
                python_output=`python dask_thread.py -workers ${work} -time ${size} -n ${n}`
                last=`echo ${python_output} | awk -F "," '{print $NF}'`
                echo "$n, $python_output"

                if [ $work -eq "1" ]; then
                    first=$last
                fi

                if (( $(echo "$last > $first" |bc -l) )); then
                    break
                fi
                
            done
        done
    done
done

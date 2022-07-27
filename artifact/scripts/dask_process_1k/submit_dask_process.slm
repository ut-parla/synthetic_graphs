#!/bin/bash

#SBATCH -J dp1k           # Job name
#SBATCH -o dp1k.o%j       # Name of stdout output file
#SBATCH -e dp1k.e%j       # Name of stderr error file
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
    first=0
    for size in 800 1600 3200 6400 12800 25600 51200 102400
    do
        for work in $(seq 1 1 4; seq 5 5 55);
        do
            python_output=`python dask_process.py -workers ${work} -time ${size} -n ${n}`
            last=`echo ${python_output} | awk -F "," '{print $NF}'`
            echo $python_output

            if [ $work -eq "1" ]; then
                first=$last
            fi

            if (( $(echo "$last > $first" |bc -l) )); then
                break
            fi
            
        done
    done
done

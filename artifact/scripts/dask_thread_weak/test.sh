#!/bin/bash

per=50
for rep in 1 2 3 4 5
do
    first=0
    for size in 800 1600 3200 6400 12800 25600 51200 102400
    do
        for work in $(seq 1 1 4; seq 5 5 55);
        do
            n=$((per*work))
            python_output=`python dask_thread.py -workers ${work} -time ${size} -n ${n}`
            last=`echo ${python_output} | awk -F "," '{print $NF}'`
            echo $python_output

            if [ $work -eq "1" ]; then
                first=`echo $last*20 | bc`
            fi

            if (( $(echo "$last > $first" |bc -l) )); then
                break
            fi
            
        done
    done
done

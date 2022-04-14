#!/bin/bash

delim="_gpu_"
OUTPUT="parsed_results.out"

rm $OUTPUT

INPUT=$1

for fpath in $INPUT/*; do
  IFS="/"
  read -a fname <<< "$fpath"
  fname=${fname[1]}
  IFS="."
  read -a etype <<< "${fname}"
  unset IFS
  afname=$etype
  if [[ $etype == *"_gpu_"* ]]; then
    afname=( "${etype%%"$delim"*}" ) #random_l
    etype=${etype#*"$delim"}
    IFS="_" # 100KB_1g_eagerdm
    read -a etype <<< "${etype}"
    dsize=${etype[0]}
    etype=${etype[1]}
    IFS="g"
    read -a num_gpu <<< $etype # 
    afname=( "${afname%%"_"$num_gpu"g"*}" )
    afname+="_gpu.gph."$num_gpu".analysis"
    unset IFS
  else
    afname+=".gph.analysis"
  fi
#commands="python parser.py -actual "$fpath" -expect inputs/"$afname" -output="$OUTPUT
  commands="python parser_median.py -actual "$fpath" -expect inputs/"$afname" -output="$OUTPUT" -branch=$2 -policy=$3"
#commands="python parser_withoutexp.py -actual "$fpath" -output="$OUTPUT
#echo $commands
  $commands
done

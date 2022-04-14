#!/bin/bash

GRAPH_INPUT_DIR="inputs"

export PYTHONPATH=../Parla.py

for gpath in ${GRAPH_INPUT_DIR}/*.gph; do
  num_gpu=""
  if [[ $gpath == *"_gpu"* ]]; then
    for g in 1 2 4; do
      commands="python viz.py -graph "$gpath" -data 1 -p "$g
      echo $commands
      $commands > $gpath"."$g".analysis"
    done
  else
    commands="python viz.py -graph "$gpath" -data 1 --no-plot True"
    echo $commands
    $commands > $gpath".analysis"
  fi
done

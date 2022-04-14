GRAPH_GENERATORS=( "generate_serial_graph.py" "generate_independent_graph.py"
                   "generate_random_graph.py" "generate_reduce_graph.py" )

#GRAPH_GENERATORS=( "generate_serial_graph.py" )
GRAPH_TYPES=( "serial" "independent" "random" "reduce" )
#GRAPH_TYPES=( "serial" )
#SLEEP_KNOBS=( 50000 5000 500 50 )
#SLEEP_KNOBS=( 50000 )
SLEEP_KNOBS=( 16000 )
#COMPUTATION_TYPE=( "l" "m" "ms" "s" )
#COMPUTATION_TYPE=( "l" )
COMPUTATION_TYPE=( "80%" )
# 0 = CPU, 1 = GPU
#ARCH_TYPE=( "0" "1" )
ARCH_TYPE=( "1" )
#ARCH_NAME=( "cpu" "gpu" )
ARCH_NAME=( "gpu" )
TASK_WIDTH=150
GIL_COUNT=1
GIL_TIME=100
NVAL=6250
NUM_PARTITIONS=2

export PYTHON_PATH="../Parla.py/"

for gen_idx in "${!GRAPH_GENERATORS[@]}"; do
  GRAPH_TYPE=${GRAPH_TYPES[$gen_idx]}
  FLAGS=""
  # Construct commands for each script.
  if [[ ${GRAPH_TYPES[$gen_idx]} == *"independent"* ]]; then
    FLAGS+=" -overlap 0 -width 300"
  elif [[ ${GRAPH_TYPES[$gen_idx]} == *"serial"* ]]; then
    FLAGS+=" -overlap 1 -levels 150"
  elif [[ ${GRAPH_TYPES[$gen_idx]} == *"random"* ]]; then
    FLAGS+=" -levels 4 -width 30 -min_read 1 -max_read 1 "
  elif [[ ${GRAPH_TYPES[$gen_idx]} == *"reduce"* ]]; then
    FLAGS+=" -overlap 1 -levels 8 -branch 2"
  fi
  FLAGS+=" -N "$NVAL" -gil_count "$GIL_COUNT" -gil_time "$GIL_TIME

  for compute_idx in ${!SLEEP_KNOBS[@]}; do
    COMPUTE_WEIGHT=${SLEEP_KNOBS[$compute_idx]}
    COMPUTE_WEIGHT_TYPE=${COMPUTATION_TYPE[$compute_idx]}
    for arch_idx in ${!ARCH_TYPE[@]}; do
      ARCH_NO=${ARCH_TYPE[$arch_idx]}
      ARCH=${ARCH_NAME[$arch_idx]}
      OUTPUT_FNAME=${GRAPH_TYPE}"_"${COMPUTE_WEIGHT_TYPE}"_"${ARCH}."gph"
      OUTPUT_DIR="inputs/"
      ARCH_FLAGS=" -location "$ARCH_NO
      FULL_COMMANDS="python graphs/${GRAPH_GENERATORS[$gen_idx]} "${FLAGS}${ARCH_FLAGS}" -weight "$COMPUTE_WEIGHT" -output "$OUTPUT_DIR$OUTPUT_FNAME
      echo $FULL_COMMANDS  >> used_generating_commands.out
      $FULL_COMMANDS
    done
  done
done

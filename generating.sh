GRAPH_GENERATORS=( "generate_serial_graph.py" "generate_independent_graph.py" 
                   "generate_reduce_graph.py" )
GRAPH_TYPES_STR=( "serial" "independent" "reduce" )
#GRAPH_GENERATORS=( "generate_reduce_graph.py" )
#GRAPH_TYPES_STR=( "reduce" )

#GRAPH_GENERATORS=( "generate_serial_graph.py" "generate_independent_graph.py" )
#GRAPH_TYPES_STR=( "serial" "independent" )


#NUM_TASKS_SET=( 300 500 1000 2000 )
NUM_TASKS_SET=( 300 )
#LEVELS=( 8 16 )
LEVELS=( 8 )
#SLEEP_KNOBS=( 3000 5000 10000 16000 20000 )
SLEEP_KNOBS=( 16000 )
#FD_DATA_KNOBS=( 6250 62500 625000 6250000 )
FD_DATA_KNOBS=( 6250 )
#SD_DATA_KNOBS=( 1 2 )
SD_DATA_KNOBS=( 2 )
# 0 = CPU, 1 = GPU
ARCH_TYPE=( "1" )
NUM_GPUS_SET=( "1" "2" "3" "4")
CUDA_VISIBLE_DEVICES_SET=( "0" "0,1" "0,1,2" "0,1,2,3" )
USER_CHOSEN_PLACEMENT_SET=( "0" "1" )
GIL_COUNT=1
GIL_TIME=0

DATA_MOVE_MODES=( 0 1 2 )

GRAPH_DIR="graphs"

GRAPH_INPUT_DIR="sc23_inputs"
rm -rf $GRAPH_INPUT_DIR
mkdir $GRAPH_INPUT_DIR

OUTPUT_DIR="sc23_outputs"
rm -rf $OUTPUT_DIR
mkdir $OUTPUT_DIR

for gen_idx in "${!GRAPH_GENERATORS[@]}"; do
  GRAPH_TYPE=${GRAPH_TYPES_STR[$gen_idx]}
  for computation_time in "${SLEEP_KNOBS[@]}"; do
    for fd_data_knob in "${FD_DATA_KNOBS[@]}"; do
      for sd_data_knob in "${SD_DATA_KNOBS[@]}"; do 
        for user_chosen_placement in "${USER_CHOSEN_PLACEMENT_SET[@]}"; do
          if [[ ${GRAPH_TYPE} == *"reduce"* ]]; then
            for level in "${LEVELS[@]}"; do
              for num_gpus in "${!NUM_GPUS_SET[@]}"; do
                for data_move_mode in "${DATA_MOVE_MODES[@]}"; do
                  FLAGS=" -weight "${computation_time}" -gil_count "$GIL_COUNT" -gil_time "$GIL_TIME" -user "$user_chosen_placement" -location 1"
                  FLAGS+=" -overlap 1 -level "${level}" -branch 2 "
                  output_prefix="${GRAPH_TYPE}_${fd_data_knob}_${sd_data_knob}_${computation_time}_${user_chosen_placement}_${level}_$((num_gpus+1))_${data_move_mode}"
                  graph_generation_commands="python ${GRAPH_DIR}/${GRAPH_GENERATORS[$gen_idx]} "${FLAGS}" -output ${GRAPH_INPUT_DIR}/${output_prefix}.gph"
                  commands="python run.py -graph ${GRAPH_INPUT_DIR}/${output_prefix}.gph "
                  commands+=" -d "${sd_data_knob}" -data_move "${data_move_mode}" -user "${user_chosen_placement}" -weight "${computation_time}
                  output_fname=${output_prefix}.log
                  echo $graph_generation_commands
                  $graph_generation_commands
                  echo $commands
                  PYTHONPATH="../Parla.py" CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES_SET[$num_gpus]} $commands > $OUTPUT_DIR/${output_fname}
                  mean_time=$(grep "Graph Execution Time:: " $OUTPUT_DIR/$output_fname)
                  mean_time=${mean_time#*"Median = "}
                  user_chosen_bool="False"
                  if [[ ${user_chosen_placement} == 1 ]]; then
                    user_chosen_bool="True"
                  fi
                  results_line="old_parla,reduction,2-"${level}","$((num_gpu+1))","${user_chosen_bool}","${fd_data_knob}","${data_move_mode}","$mean_time
                  echo $results_line
                  echo $results_line >> $OUTPUT_DIR/result.log
                done
              done
            done
          else
            for num_task in "${NUM_TASKS_SET[@]}"; do
              for num_gpus in "${!NUM_GPUS_SET[@]}"; do
                for data_move_mode in "${DATA_MOVE_MODES[@]}"; do
                  FLAGS=" -weight "${computation_time}" -gil_count "$GIL_COUNT" -gil_time "$GIL_TIME" -user "$user_chosen_placement" -location 1"
                  if [[ ${GRAPH_TYPE} == *"independent"* ]]; then
                    FLAGS+=" -overlap 0 -width "${num_task}
                  elif [[ ${GRAPH_TYPE} == *"serial"* ]]; then
                    FLAGS+=" -overlap 1 -levels "${num_task}
                  fi
                  output_prefix="${GRAPH_TYPE}_${fd_data_knob}_${sd_data_knob}_${computation_time}_${user_chosen_placement}_${num_task}_$((num_gpus+1))_${data_move_mode}.out"
                  graph_generation_commands="python ${GRAPH_DIR}/${GRAPH_GENERATORS[$gen_idx]} "${FLAGS}" -output ${GRAPH_INPUT_DIR}/${output_prefix}.gph"
                  commands="python run.py -graph ${GRAPH_INPUT_DIR}/${output_prefix}.gph "
                  commands+=" -d "${sd_data_knob}" -data_move "${data_move_mode}" -user "${user_chosen_placement}" -weight "${computation_time}
                  output_fname=${output_prefix}.log
                  echo $output_prefix
                  echo $graph_generation_commands
                  $graph_generation_commands
                  echo $commands
                  PYTHONPATH="../Parla.py" CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES_SET[$num_gpus]} $commands > $OUTPUT_DIR/${output_fname}
                  mean_time=$(grep "Graph Execution Time:: " $OUTPUT_DIR/$output_fname)
                  mean_time=${mean_time#*"Median = "}
                  user_chosen_bool="False"
                  if [[ ${user_chosen_placement} == 1 ]]; then
                    user_chosen_bool="True"
                  fi
                  results_line="old_parla,"${GRAPH_TYPE}","${num_task}","$((num_gpu+1))","${user_chosen_bool}","${fd_data_knob}","${data_move_mode}","$mean_time
                  echo $results_line
                  echo $results_line >> $OUTPUT_DIR/result.log
                done
              done
            done
          fi
        done
      done
    done
  done
done

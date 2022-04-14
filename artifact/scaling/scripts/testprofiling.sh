#!/bin/bash

GPU_COMBS=( "0" "0,1" "0,1,2,3" )
NUM_GPUS=( "1g" "2g" "4g" )
#DEPTHS=( "2000" )
#INPUT_SIZES=( "100MB" )
DEPTHS=( "2" )
INPUT_SIZES=( "100KB" )
INPUT_DIR="inputs"
DATE=`date +"%Y_%m%d"`
echo $DATE
OUTPUT_DIR="profiling_results_$DATE"

export PYTHONPATH="../Parla.py"

rm -rf $OUTPUT_DIR
mkdir $OUTPUT_DIR

for depth_idx in "${!DEPTHS[@]}"; do
  DEPTH=${DEPTHS[$depth_idx]}
  INPUT_SIZE=${INPUT_SIZES[$depth_idx]}
  for gpath in ${INPUT_DIR}/*; do
    if [[ $gpath == *".analysis"* ]]; then
      continue
    fi
    if [[ $gpath == *"indepenent"* ]]; then
      continue
    elif [[ $gpath == *"random"* ]]; then
      continue
    elif [[ $gpath == *"reduce"* ]]; then
      continue
    fi
    commands="python run.py -graph "$gpath" -d ${DEPTH} --verbose -loop 20" 
    IFS="/"
    read -a gpath_split <<< "$gpath"
    IFS="."
    read -a gfname <<< "${gpath_split[1]}"
    unset IFS 
    for data_move_mode in 1 2; do
      echo "data mode is tested:" $data_move_mode
      data_move_flag=""
      out_fname_post=""
      if [[ (($data_move_mode == 2)) ]]; then
        echo "eager data mode is enabled:" $data_move_mode
        out_fname_post="_eagerdm"
        data_move_flag=" --check"
      else
        echo "lazy data mode is enabled:" $data_move_mode
        out_fname_post="_lazydm"
        data_move_flag=" --check"
      fi
      if [[ $gpath == *"_gpu."* ]]; then
        for exp_type in "${!NUM_GPUS[@]}"; do
          GPU_PREFIX=${GPU_COMBS[$exp_type]}
          export CUDA_VISIBLE_DEVICES=$GPU_PREFIX
          echo $GPU_PREFIX
          final_commands=${commands}" -data_move "${data_move_mode}${data_move_flag}
          out_fname=${gfname}"_"${INPUT_SIZE}"_"${NUM_GPUS[$exp_type]}${out_fname_post}".out"
          echo "$final_commands"
          echo "$final_commands > "$out_fname >> ${OUTPUT_DIR}"/run_commands.out"
          $final_commands > ${OUTPUT_DIR}"/"${out_fname}
        done
      else
        out_fname=${gfname}"_"${INPUT_SIZE}"_cpu_"${out_fname_post}".out"
        final_commands=${commands}" -data_move "${data_move_mode}${data_move_flag}
        echo "$final_commands"
        echo "$final_commands > "$out_fname >> ${OUTPUT_DIR}"/run_commands.out"
        $final_commands  > ${OUTPUT_DIR}"/"${out_fname}
      fi
    done
  done
done

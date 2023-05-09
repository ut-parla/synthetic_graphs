import numpy as np
import argparse

"""

Generates a reduction-scatter tree of tasks:

x x x x x x x x 
\ | | | | | | /
      x
/ | | | | | | \
x x x x x x x x 

Options:
    -levels : how many levels to generate
    -branch : whats the branching factor
    -overlap:
        0: Each task reads/writes a separate block of data
        1: Each task reads the data of the parents and writes itself

    -weight: how long the computation runs
    -gil_count: how many gil locks
    -gil_time: length of gil lock

"""

def fstr(template, **kwargs):
        return eval(f"f'{template}'", kwargs)

parser = argparse.ArgumentParser(description='Create inverted tree [reduction] graph')
parser.add_argument('-levels', metavar='width', type=int, help='how many levels in the reduction tree', default=4)
parser.add_argument('-overlap', metavar='overlap', type=int, help='type of data read. e.g are the buffers shared. options = (False=0, True=1)', default=1)
parser.add_argument('-output', metavar='output', type=str, help='name of output file containing the graph', default="reduce.gph")
parser.add_argument('-weight', metavar='weight', type=int, help='time (in microseconds) that the computation of the task should take', default=50000)
parser.add_argument('-coloc', metavar='coloc', type=int, help=' x tasks can run on a device concurrently', default=1)
parser.add_argument('-location', metavar='location', type=int, help="valid runtime locations of tasks. options=(CPU=0, GPU=1, Both=3)", default=1)
parser.add_argument('-gil_count', metavar='gil_count', type=int, help="number of (intentional) additional gil accesses in the task", default=1)
parser.add_argument('-gil_time', metavar='gil_time', type=int, help="time (in microseconds) that the gil is held", default=200)
parser.add_argument('-N', metavar='N', type=int, help='total width of data block', default=2**19)
parser.add_argument('-user', metavar='user', type=int, help='whether to specify optimal manual placment', default=1)
parser.add_argument('-num_gpus', metavar='num_gpus', type=int, help='number of GPUs', default=4)
parser.add_argument('-num_tasks', metavar='num_tasks', type=int, help='total number of tasks', default=10)
args = parser.parse_args()
N = args.N

output = args.output

# Level starts from 1
levels = args.levels
width = 1
length = 1

overlap = args.overlap
weight = args.weight
loc = args.location
coloc = args.coloc
gil_count = args.gil_count
gil_time = args.gil_time
num_gpus = args.num_gpus
num_tasks = args.num_tasks

# Calculate the number of bridge tasks in the graph
num_bridge_tasks = levels // 2
num_bridge_tasks += 1 if (levels % 2 > 0) else 0
# Calculate the number of bulk tasks in the graph
num_bulk_tasks = (num_tasks - num_bridge_tasks)
# Calculate the number of levels for bulk tasks
num_levels_for_bulk_tasks = levels // 2 + 1
# Calculate the number of bulk tasks per level
num_bulk_tasks_per_level = num_bulk_tasks // num_levels_for_bulk_tasks
# All the remaining bulk tasks are added to the last level
num_bulk_tasks_last_level = (num_bulk_tasks % num_levels_for_bulk_tasks) + \
                            num_bulk_tasks_per_level
num_bulk_tasks_per_gpu = (num_bulk_tasks_per_level) // num_gpus

with open(output, 'w') as graph:
    if overlap == 1:
        # Each bulk task takes an individual (non-overlapped) data block.
        # A bridge task reduces all data blocks from the bulk tasks in the previous level.
        single_data_block_size = N
        for d in range(num_bulk_tasks_last_level):
            if d > 0:
                graph.write(", ")
            graph.write(f"{single_data_block_size}")
    else:
        raise NotImplementedError(
            "[ReductionScatter] Data patterns not implemented")
    graph.write("\n")            

    task_id = 0
    # Any GPU 
    bridge_task_dev_id = 3 if args.user else 1
    last_bridge_task_id_str = ""
    last_bridge_task_id = 0
    for l in range(levels + 1):
        # If the last level has a bridge task, the previous level should take all
        # remaining bulk tasks.
        if levels % 2 > 0:
            l_num_bulk_tasks = num_bulk_tasks_per_level if l < (levels - 1) \
                               else num_bulk_tasks_last_level
        else:
            l_num_bulk_tasks = num_bulk_tasks_per_level if l < levels \
                               else num_bulk_tasks_last_level
        if l % 2 > 0: # Bridge task condition
            dependency_block = ""
            inout_data_block = ""
            for d in range(l_num_bulk_tasks):
                inout_data_block += f"{d}"
                if l == 1:
                    dependency_block += f"{d + last_bridge_task_id}"
                else:
                    dependency_block += f"{d + last_bridge_task_id + 1}"
                if d != (l_num_bulk_tasks - 1):
                    inout_data_block += ","
                    dependency_block += " : "
            graph.write(f"{task_id} | {weight}, {coloc}, {bridge_task_dev_id}, {gil_count}, {gil_time} | {dependency_block} | : : {inout_data_block}\n")
            if args.user:
                bridge_task_dev_id += 1
                if bridge_task_dev_id == num_gpus + 3:
                    bridge_task_dev_id = 3
            last_bridge_task_id_str = f"{task_id}"
            last_bridge_task_id = int(task_id)
            task_id += 1
        else:
            bulk_task_id_per_gpu = 0
            bulk_task_dev_id = 3 if args.user else 1
            for bulk_task_id in range(l_num_bulk_tasks):
                inout_data_block = f"{bulk_task_id}"
                graph.write(f"{task_id} | {weight}, {coloc}, {bulk_task_dev_id}, {gil_count}, {gil_time} | {last_bridge_task_id_str} | : : {inout_data_block}\n")
                l_num_bulk_tasks_per_gpu = l_num_bulk_tasks // num_gpus
                if args.user:
                    if l_num_bulk_tasks % num_gpus >= (bulk_task_dev_id - 3):
                        l_num_bulk_tasks_per_gpu += 1
                    bulk_task_id_per_gpu += 1
                    if bulk_task_id_per_gpu == l_num_bulk_tasks_per_gpu:
                        bulk_task_id_per_gpu = 0
                        bulk_task_dev_id += 1
                        if bulk_task_dev_id == num_gpus + 3:
                            bulk_task_dev_id = 3
                task_id += 1

print(f"Wrote graph to {args.output}.")

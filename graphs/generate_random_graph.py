import numpy as np
import argparse

import random


"""

Generates a level-by-level random graph of tasks:

x x x x x x
| | |/|  / |
x x x x /  x x
|   |  /   |
x x x x    x x

Each task will randomly connect between (min_depend, max_depend) tasks of previous levels from level-1 to level-back.
per_level balances connections per level
//DEPRECIATED IDEA: per_level determines if at least 1 connection per level is required.


Each task 'owns' # partitions data blocks
Each task will update a # update of these data blocks per task (chosen randomly)
Each task will randomly chose its data dependencies from its dependencies between (min_data, max_data)

Options:
    -levels : how many levels to generate
    -width  : how many tasks in a level
    -min_depend : how many tasks to depend on (min)
    -max_depend : how many tasks to depend on (max)
    -min_data : how many data blocks to depend on (min)
    -max_data : how many data blocks to depend on (max)
    -per_level : attempt to balance dependencies per level (round robin)
    -partitions: how many data blocks in each task space
    -update: how many owned data blocks are written to
    -back : how many levels back to possibly link
    -weight: how long the computation runs
    -gil_count: how many gil locks
    -gil_time: length of gil lock

"""

def fstr(template, **kwargs):
        return eval(f"f'{template}'", kwargs)

parser = argparse.ArgumentParser(description='Create iterations of a random graph')
parser.add_argument('-levels', metavar='levels', type=int, help='the number of levels to generate', default=4)
parser.add_argument('-width', metavar='width', type=int, help='the number of tasks in each level', default=4)

parser.add_argument('-overlap', metavar='overlap', type=int, help='type of data read. e.g are the buffers shared. options = (False=0, True=1)', default=0)
parser.add_argument('-output', metavar='output', type=str, help='name of output file containing the graph', default="random.gph")
parser.add_argument('-weight', metavar='weight', type=int, help='time (in microseconds) that the computation of the task should take', default=50000)
parser.add_argument('-coloc', metavar='coloc', type=int, help=' x tasks can run on a device concurrently', default=1)
parser.add_argument('-location', metavar='location', type=int, help="valid runtime locations of tasks. options=(CPU=0, GPU=1, Both=3)", default=1)
parser.add_argument('-gil_count', metavar='gil_count', type=int, help="number of (intentional) additional gil accesses in the task", default=1)
parser.add_argument('-gil_time', metavar='gil_time', type=int, help="time (in microseconds) that the gil is held", default=200)
parser.add_argument('-N', metavar='N', type=int, help='total width of data block', default=2**19)
\
parser.add_argument('-min_depend', metavar='min_depend', type=int, help='how many tasks to depend on (min)', default=1)
parser.add_argument('-max_depend', metavar='max_depend', type=int, help='how many tasks to depend on (max)', default=1)
parser.add_argument('-per_level', metavar='per_level', type=int, help='require tasks in each level back', default=0)
parser.add_argument('-back', metavar='back', type=int, help='how many levels back to link', default=1)
parser.add_argument('-seed', metavar='seed', type=int, help='random seed', default=1)

parser.add_argument('-partitions', metavar='partitions', help='max number of data partitions per task space', default=2)

parser.add_argument('-min_read', metavar='min_read', type=int, help='how many data to read on (min)', default=1)
parser.add_argument('-max_read', metavar='max_read', type=int, help='how many data to read on (max)', default=1)

parser.add_argument('-min_write', metavar='min_write', type=int, help='how many data to write on (min)', default=1)
parser.add_argument('-max_write', metavar='max_write', type=int, help='how many data to write on (max)', default=1)

args = parser.parse_args()
N = args.N

output = args.output

level = args.levels
width = args.width

overlap = args.overlap
weight = args.weight
loc = args.location
coloc = args.coloc
gil_count = args.gil_count
gil_time = args.gil_time

random.seed(args.seed)
np.random.seed(args.seed)

#All tasks in the chain need separate data
n_partitions = width * args.partitions

with open(output, 'w') as graph:

    #setup data information
    #assume equipartition
    #TODO: Change this to uneven sizes for "ghost points"?

    n_local = N//n_partitions
    for i in range(n_partitions):
        graph.write(f"{n_local}")
        if i+1 < n_partitions:
            graph.write(", ")

    graph.write("\n")

    self_index = 0
    #setup task information
    for i in range(level):
        for j in range(width):

            valid_levels = min(args.back, i)

            # number of connections
            n_dep = np.random.randint(args.min_depend, args.max_depend+1)
            dep_count = n_dep

            dep_list = []

            #chose dependency connections
            if args.per_level and i:
                for k in range(valid_levels):

                    n_choice = n_dep // level + n_dep % level
                    #chose at least 1 from each level

                    idx_list = np.random.choice(args.width, n_choice, replace=False)

                    for idx in idx_list:
                        dep_list.append((i-valid_levels, idx))

                    dep_count -= n_choice

                assert(dep_count == 0)
            elif i:
                n_poss = args.width * valid_levels
                idx_list = np.random.choice(n_poss, n_dep, replace=False)


                for idx in idx_list:
                    k_l = idx//width
                    k_o = idx % width

                    dep_list.append((i - 1 - k_l, k_o))

            #chose read list
            #read from a random fraction of possible input
            read_list = []
            n_reads = np.random.randint(args.min_read, args.max_read+1)
            for dep in dep_list:
                #get global index
                global_index = dep[1]*args.partitions

                for k in range(args.partitions):
                    if k == i % args.partitions:
                        continue
                    else:
                        read_list.append(global_index+k)

            if i:
                read_list = random.sample(read_list, n_reads)

            #chose write list
            #write to a random fraction of owned datapoints
            self_list = []
            for k in range(args.partitions):
                self_list.append(j*args.partitions+k)

            read_list = list(set(read_list))

            write_list = self_list

            n_writes = np.random.randint(args.min_write, args.max_write+1)
            write_list = [write_list[i%args.partitions]] #random.sample(write_list, n_writes)

            if i >= args.partitions:
                dep_list.append((i - args.partitions, j))
            dep_list = list(set(dep_list))

            read_list = list(set(read_list).difference(write_list))

            #build task_dep string
            task_dep = ' : '.join([ f"{dep[0]}, {dep[1]}" for dep in dep_list])

            #build task_read string
            task_read = ', '.join([f"{read}" for read in read_list] )

            #build task_write string
            task_write = ', '.join([f"{write}" for write in write_list])


            self_index += 1

            graph.write(f"{i}, {j} | {weight}, {coloc}, {loc}, {gil_count}, {gil_time} | {task_dep} | {task_read} : : {task_write} \n")

print(f"Wrote graph to {args.output}.")

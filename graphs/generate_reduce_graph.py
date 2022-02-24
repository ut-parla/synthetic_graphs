import numpy as np
import argparse

"""

Generates a reduction tree of tasks:

x x x x
|/  |/
x   x
|  /
| /
x

Options:
    -levels : how many levels to generate
    -branch : whats the branching factor
    -overlap:
        0: Each task reads/writes a separate block of data
        1: Each task reads the data of the parents and writes itself
    -constant:
        0: Doubling work per task
        1: Constant work per task

    -weight: how long the computation runs
    -gil_count: how many gil locks
    -gil_time: length of gil lock

"""

def fstr(template, **kwargs):
        return eval(f"f'{template}'", kwargs)

parser = argparse.ArgumentParser(description='Create inverted tree [reduction] graph')
parser.add_argument('-levels', metavar='width', type=int, help='how many levels in the reduction tree', default=4)
parser.add_argument('-overlap', metavar='overlap', type=int, help='type of data read. e.g are the buffers shared. options = (False=0, True=1)', default=0)
parser.add_argument('-output', metavar='output', type=str, help='name of output file containing the graph', default="reduce.gph")
parser.add_argument('-weight', metavar='weight', type=int, help='time (in microseconds) that the computation of the task should take', default=50000)
parser.add_argument('-coloc', metavar='coloc', type=int, help=' x tasks can run on a device concurrently', default=1)
parser.add_argument('-location', metavar='location', type=int, help="valid runtime locations of tasks. options=(CPU=0, GPU=1, Both=3)", default=1)
parser.add_argument('-gil_count', metavar='gil_count', type=int, help="number of (intentional) additional gil accesses in the task", default=1)
parser.add_argument('-gil_time', metavar='gil_time', type=int, help="time (in microseconds) that the gil is held", default=200)
parser.add_argument('-N', metavar='N', type=int, help='total width of data block', default=2**19)
parser.add_argument('-branch', metavar='branch', type=int, help='the branching factor of the tree', default=2)
parser.add_argument('-constant', metavar='constant', type=int, help='Keep the work per task constant (1) or doubled (0)')
#parser.add_argument('-n_partitions', metavar='n_partitions', help='max number of partitions')

args = parser.parse_args()
N = args.N

output = args.output

level = args.levels
width = 1
length = 1

overlap = args.overlap
weight = args.weight
loc = args.location
coloc = args.coloc
gil_count = args.gil_count
gil_time = args.gil_time

constant = args.constant
branch = args.branch

#All tasks in the chain need separate data
n_partitions = branch**(level+1)
N = N * n_partitions

with open(output, 'w') as graph:

    #setup data information
    n_local = N//n_partitions
    level_count = 0
    count = 0
    for i in range(level, 0, -1):
        for j in range(branch**i):
            if count > 0:
                graph.write(", ")
            graph.write(f"{n_local}")
            count += 1
        level_count += 1
        #if <some condition>:
        #    n_local = n_local * branch

    graph.write("\n")

    global_index = 0
    level_count = 0
    #setup task information
    for i in range(level, -1, -1):
        for j in range(branch**i):

            if level_count:
                task_dep = " "
                for k in range(branch):
                    task_dep += f"{level_count-1}, {branch*j + k}"
                    if k+1 < branch:
                        task_dep += " : "
            else:
                task_dep = " "

            if overlap and level_count:
                start_index = branch**(level+1) - branch**(i+2)
                start_index = start_index // (branch -1)

                read_dep = " "
                for k in range(branch):
                    read_dep += f"{start_index + branch*j + k}"
                    if k+1 < branch:
                        read_dep += " , "
            else:
                read_dep = " "

            graph.write(f"{level_count}, {j} | {weight}, {coloc}, {loc}, {gil_count}, {gil_time} | {task_dep} | {read_dep} : : {global_index} \n")


            global_index += 1
        level_count += 1







print(f"Wrote graph to {args.output}.")



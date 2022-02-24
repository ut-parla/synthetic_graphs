import numpy as np
import argparse

"""

Generates a tree of tasks:

x
| \
x   x
|\  | \
x x x x

Options:
    -levels : how many levels to generate
    -branch : whats the branching factor
    -overlap:
        0: Each task reads/writes a separate block of data
        1: Each task reads the data of the parent and reads/writes itself
    -weight: how long the computation runs
    -gil_count: how many gil locks
    -gil_time: length of gil lock

"""


def fstr(template, **kwargs):
        return eval(f"f'{template}'", kwargs)


parser = argparse.ArgumentParser(description='Create tree graph')
parser.add_argument('-levels', metavar='levels', type=int, help='the number of levels in the tree', default=4)
parser.add_argument('-overlap', metavar='overlap', type=int, help='type of data read. e.g are the buffers shared. options = (False=0, True=1)', default=0)
parser.add_argument('-output', metavar='output', type=str, help='name of output file containing the graph', default="tree.gph")
parser.add_argument('-weight', metavar='weight', type=int, help='time (in microseconds) that the computation of the task should take', default=50000)
parser.add_argument('-coloc', metavar='coloc', type=int, help=' x tasks can run on a device concurrently', default=1)
parser.add_argument('-location', metavar='location', type=int, help="valid runtime locations of tasks. options=(CPU=0, GPU=1, Both=3)", default=1)
parser.add_argument('-gil_count', metavar='gil_count', type=int, help="number of (intentional) additional gil accesses in the task", default=1)
parser.add_argument('-gil_time', metavar='gil_time', type=int, help="time (in microseconds) that the gil is held", default=200)
parser.add_argument('-N', metavar='N', type=int, help='total width of data block', default=2**19)
parser.add_argument('-branch', metavar='branch', type=int, help='the branching factor of the tree', default=2)
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

branch = args.branch

#All tasks in the chain need separate data
n_partitions = branch**(level+1)
N = N * n_partitions

with open(output, 'w') as graph:

    #setup data information
    #assume equipartition
    #TODO: Change this to decaying size?
    #TODO: Add index sets to split nodes when supported

    n_local = N//n_partitions
    for i in range(n_partitions):
        graph.write(f"{n_local}")
        if i+1 < n_partitions:
            graph.write(", ")

    graph.write("\n")

    global_index = 0
    #setup task information
    for i in range(level):
        for j in range(branch**i):
            parent_index = (j)//branch


            if global_index:
                parent_dep = f"{i-1}, {parent_index}"
            else:
                parent_dep = " "


            if overlap and global_index:
                read_dep = str((global_index-1)//branch)
            else:
                read_dep = " "

            graph.write(f"{i}, {j} | {weight}, {coloc}, {loc}, {gil_count}, {gil_time} | {parent_dep} | {read_dep} : : {global_index} \n")


            global_index += 1








print(f"Wrote graph to {args.output}.")

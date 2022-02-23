import numpy as np
import argparse

"""
Generates an independent set of tasks:
    | | | | |
    x x x x x

    Options:
        -width: how many tasks to generate
        -overlap:
            0: each task reads the same data
            1: each task reads a separate data block
"""







parser = argparse.ArgumentParser(description='Create embarassingly parallel graph')
parser.add_argument('-width', metavar='width', type=int, help='the width of the task graph', default=10)
parser.add_argument('-overlap', metavar='overlap', type=int, help='type of data read. e.g are the buffers shared. options = (False=0, True=1)', default=0)
parser.add_argument('-output', metavar='output', type=str, help='name of output file containing the graph', default="independent.gph")
parser.add_argument('-weight', metavar='weight', type=int, help='time (in microseconds) that the computation of the task should take', default=50000)
parser.add_argument('-coloc', metavar='coloc', type=int, help=' x tasks can run on a device concurrently', default=1)
parser.add_argument('-location', metavar='location', type=int, help="valid runtime locations of tasks. options=(CPU=0, GPU=1, Both=3)", default=1)
parser.add_argument('-gil_count', metavar='gil_count', type=int, help="number of (intentional) additional gil accesses in the task", default=1)
parser.add_argument('-gil_time', metavar='gil_time', type=int, help="time (in microseconds) that the gil is held", default=200)
parser.add_argument('-N', metavar='N', type=int, help='total width of data block', default=2**23)
#parser.add_argument('-n_partitions', metavar='n_partitions', help='max number of partitions')

args = parser.parse_args()

output = args.output

level = 1
width = args.width
length = 1

overlap = args.overlap
weight = args.weight
loc = args.location
coloc = args.coloc
gil_count = args.gil_count
gil_time = args.gil_time

if overlap:
    n_partitions = 1
    N = N//width
else:
    n_partitions = width

with open(output, 'w') as graph:

    #setup data information
    #assume equipartition
    n_local = N//n_partitions
    for i in range(n_partitions):
        graph.write(f"{n_local}")
        if i+1 < n_partitions:
            graph.write(", ")

    graph.write("\n")

    #setup task information
    for i in range(level):
        for j in range(width):
            for k in range(length):

                if overlap == 1:
                    #All tasks read the same datablock
                    index = 0
                else:
                    #All tasks read a different datablock
                    index = j

                graph.write(f"{j} | {weight}, {coloc}, {loc}, {gil_count}, {gil_time} | | {index} \n")









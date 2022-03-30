import numpy as np
import argparse


"""

Generates a chain of tasks:

x -> x -> x -> x -> x

Options:
    -levels : how many tasks to generate
    -back : how many depenencies to generate (Default 1 back)
    -overlap:
        0: Each task reads/writes a separate block of data
        1: Each task reads/writes the same block of data
    -weight: how long the computation runs
    -gil_count: how many gil locks
    -gil_time: length of gil lock

"""

def fstr(template, **kwargs):
        return eval(f"f'{template}'", kwargs)

parser = argparse.ArgumentParser(description='Create serial chain graph')

parser.add_argument('-levels', metavar='levels', type=int, help='Length of the task chain', default=10)
parser.add_argument('-overlap', metavar='overlap', type=int, help='type of data read. e.g are the buffers shared. options = (False=0, True=1)', default=0)
parser.add_argument('-output', metavar='output', type=str, help='name of output file containing the graph', default="serial.gph")
parser.add_argument('-weight', metavar='weight', type=int, help='time (in microseconds) that the computation of the task should take', default=50000)
parser.add_argument('-coloc', metavar='coloc', type=int, help=' x tasks can run on a device concurrently', default=1)
parser.add_argument('-location', metavar='location', type=int, help="valid runtime locations of tasks. options=(CPU=0, GPU=1, Both=3)", default=1)
parser.add_argument('-gil_count', metavar='gil_count', type=int, help="number of (intentional) additional gil accesses in the task", default=1)
parser.add_argument('-gil_time', metavar='gil_time', type=int, help="time (in microseconds) that the gil is held", default=200)
parser.add_argument('-N', metavar='N', type=int, help='total width of data block', default=2**23)
parser.add_argument('-back', metavar='back', type=int, help='how many redundant dependencies to include', default=1)
#parser.add_argument('-n_partitions', metavar='n_partitions', help='max number of partitions')

parser.add_argument('-user', metavar='user', type=int, help='whether to specify optimal manual placment', default=0)
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

back = args.back+1

if overlap == 1:
    #All tasks in the chain read/write the same data
    n_partitions = 1
    N = N
else:
    #All tasks in the chain read/write different data
    n_partitions = level
    N = N * level

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

        if overlap == 1:
            #All tasks read the same datablock
            index = 0
        else:
            #All tasks read a different datablock
            index = i

        dependency = " "
        limit = min(i+1, back)
        for j in range(1, limit):
            dependency += "{" + f"i - {j}" + "}"
            if j+1 < limit:
                dependency += " : "

        dependency = fstr(dependency, i=i)

        if args.user:
            device = 3 #gpu 0
        else:
            device = 1 #any gpu

        graph.write(f"{i} | {weight}, {coloc}, {loc}, {gil_count}, {gil_time} | {dependency} | : : {index} \n")








print(f"Wrote graph to {args.output}.")

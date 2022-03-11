import numpy as np
import argparse

"""

Generates a tree of tasks:

x x x x x x
|/|/|/|/|/|
x x x x x x
|/|/|/|/|/|
x x x x x x

Options:
    -levels : how many levels to generate
    -depend : how many neighbors to depend on
    -weight: how long the computation runs
    -gil_count: how many gil locks
    -gil_time: length of gil lock

"""

def fstr(template, **kwargs):
        return eval(f"f'{template}'", kwargs)

parser = argparse.ArgumentParser(description='Create iterations of a domain decomposition-like graph')
parser.add_argument('-levels', metavar='levels', type=int, help='the number of iterations', default=4)
parser.add_argument('-width', metavar='width', type=int, help='the length of the task chain', default=4)
parser.add_argument('-overlap', metavar='overlap', type=int, help='type of data read. e.g are the buffers shared. options = (False=0, True=1)', default=0)
parser.add_argument('-output', metavar='output', type=str, help='name of output file containing the graph', default="1D_stencil.gph")
parser.add_argument('-weight', metavar='weight', type=int, help='time (in microseconds) that the computation of the task should take', default=50000)
parser.add_argument('-coloc', metavar='coloc', type=int, help=' x tasks can run on a device concurrently', default=1)
parser.add_argument('-location', metavar='location', type=int, help="valid runtime locations of tasks. options=(CPU=0, GPU=1, Both=3)", default=1)
parser.add_argument('-gil_count', metavar='gil_count', type=int, help="number of (intentional) additional gil accesses in the task", default=1)
parser.add_argument('-gil_time', metavar='gil_time', type=int, help="time (in microseconds) that the gil is held", default=200)
parser.add_argument('-N', metavar='N', type=int, help='total width of data block', default=2**19)
parser.add_argument('-branch', metavar='branch', type=int, help='the branching factor of the tree', default=2)
parser.add_argument('-depend', metavar='depend', type=int, help='how many neighbors to depend on', default=1)
#parser.add_argument('-n_partitions', metavar='n_partitions', help='max number of partitions')

args = parser.parse_args()
N = args.N

output = args.output

level = args.levels
width = args.width
length = 1

overlap = args.overlap
weight = args.weight
loc = args.location
coloc = args.coloc
gil_count = args.gil_count
gil_time = args.gil_time

depends = args.depend

#All tasks in the chain need separate data
n_partitions = width * depends

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

    global_index = 0
    #setup task information
    for i in range(level):
        for j in range(width):

            lbound = -1
            rbound = width

            task_dep = " "
            valid = 1
            if i > 0:
                task_dep += f"{i-1}, {j}"

                for k in range(1, depends):

                    side = k % 2
                    inc = (k+1) // 2

                    #print("k", k, side, inc, rbound, lbound, i, j)

                    if side:
                        if j + inc < rbound:
                            if valid:
                                task_dep += " : "
                                valid -= 1
                            task_dep += f"{i-1}, {j+inc}"
                            valid = 1
                    else:
                        if (j - inc) > lbound:
                            if valid:
                                task_dep += " : "
                                valid -= 1
                            task_dep += f"{i-1}, {j-inc}"
                            valid = 1


            self_index = depends*j
            read_dep = ""
            valid = 0
            for k in range(1, depends):
                side = k % 2
                inc = (k+1) // 2

                if side:
                    if j + inc < rbound:
                        if valid:
                            valid -= 1
                            read_dep += ", "
                        read_dep += f"{(j+inc)*depends + inc}"
                        valid = 1
                else:
                    if (j - inc) > lbound:
                        if valid:
                            valid -= 1
                            read_dep += ", "
                        read_dep += f"{(j-inc)*depends + (depends - inc)}"
                        valid = 1


            write_dep = ""
            #Note can only write to "center", cant update ghost points unless more dependencies are added (concurrent reads/writes aren't possible without coherency "versions")
            #TODO: Change this back when we support versions
            for k in range(0, 1):
                write_dep += f"{(j)*depends + k}"

                if k+1 < depends:
                    write_dep += ", "

            #print(read_dep)

            graph.write(f"{i}, {j} | {weight}, {coloc}, {loc}, {gil_count}, {gil_time} | {task_dep} | {read_dep} : : {write_dep} \n")


print(f"Wrote graph to {args.output}.")

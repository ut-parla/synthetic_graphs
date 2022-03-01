import time

import numpy as np
from sleep.core import *

from parla import Parla
from parla.cpu import cpu

import argparse

from synthetic.core_old import *

parser = argparse.ArgumentParser(description='Launch graph file in Parla')
parser.add_argument('-d', metavar='N', type=int, help='The dimension of data segments >=2 (Increase to make movement more expensive)', default=2)
parser.add_argument('-data_move', metavar='data_move', type=int, help='type of data movement. options=(None=0, Lazy=1, Eager=2)', default=0)
parser.add_argument('-graph', metavar='graph', type=str, help='the input graph file to run', required=True, default='graph/independent.gph')
parser.add_argument('--verbose', metavar='verbose', nargs='?', const=True, type=str2bool, default=False, help='Activate verbose mode (required for verifying output)')
parser.add_argument('-loop', metavar='loop', default=1, help='How many times to repeat the graph execution')
parser.add_argument('--check_data', metavar='check_data', dest='check', nargs='?', const=True, type=str2bool, default=False, help='Activate data check mode (required for verifying movement output output)')


execution_times = []

args = parser.parse_args()
task_space = TaskSpace("Graph Iterations")

def main_parla(iteration, G, array, verbose=False):

    dep = [task_space[iteration-1]] if iteration > 0 else [] 

    @spawn(task_space[iteration], dependencies=dep, placement=cpu)
    async def main_task():
        start_internal = time.perf_counter()
        await create_tasks(G, array, args.data_move, verbose, args.check)
        end_internal = time.perf_counter()

        graph_elapsed = end_internal - start_internal
        execution_times.append(graph_elapsed)
        print(f"Iteration {iteration} | Graph Execution Time: ", graph_elapsed, "seconds", flush=True)
        

def main():

    if args.data_move:
        print(f"move=({args.data_move})")

    if args.verbose:
        print(f"dim=({args.d})")

    G = read_graph(args.graph)
    array = setup_data(G, args.d, data_move=args.data_move)

    start = time.perf_counter()

    with Parla():
        for iteration in range(args.loop):
            start_internal = time.perf_counter()
            main_parla(iteration, G, array, args.verbose)
            end_internal = time.perf_counter()

    end = time.perf_counter()

    print("Total Elapsed: ", end - start, "seconds", flush=True)

    if args.verbose:
        print("Time to Spawn Main Task: ", end_internal - start_internal, "seconds", flush=True)


if __name__ == '__main__':
    #Estimate GPU frequency for busy wait timing
    #global cycles_per_second
    #cycles_per_second = estimate_frequency(50, ticks=10**8)

    #Launch experiment
    main()

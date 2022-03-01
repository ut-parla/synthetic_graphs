import time

import copy

import numpy as np
from sleep.core import *

from parla import Parla
from parla.cpu import cpu

import argparse

from synthetic.core import *

parser = argparse.ArgumentParser(description='Launch graph file in Parla')
parser.add_argument('-d', metavar='N', type=int, help='The dimension of data segments >=2 (Increase to make movement more expensive)', default=2)
parser.add_argument('-data_move', metavar='data_move', type=int, help='type of data movement. options=(None=0, Lazy=1, Eager=2)', default=0)
parser.add_argument('-graph', metavar='graph', type=str, help='the input graph file to run', required=True, default='graph/independent.gph')
parser.add_argument('--verbose', metavar='verbose', nargs='?', const=True, type=str2bool, default=False, help='Activate verbose mode (required for verifying output)')
parser.add_argument('-loop', metavar='loop', default=1, type=int, help='How many times to repeat the graph execution')
parser.add_argument('-outerloop', metavar='outerloop', default=1, type=int, help='How many times to repeat to whole experiment')
parser.add_argument('-reinit', metavar='reinit', default=0, type=int, help='Reinitialize the data on CPU at each inner loop (0=False, 1=True)')
parser.add_argument('--check_data', metavar='check_data', dest='check', nargs='?', const=True, type=str2bool, default=False, help='Activate data check mode (required for verifying movement output output)')

data_execution_times = []
graph_execution_times = []
parla_execution_times = []

args = parser.parse_args()


def main_parla(task_space, iteration, G, array, verbose=False):

    dep = [task_space[iteration-1]] if iteration > 0 else []

    @spawn(task_space[iteration], dependencies=dep, placement=cpu)
    async def main_task():
        start_internal = time.perf_counter()
        await create_tasks(G, array, args.data_move, verbose, args.check)
        end_internal = time.perf_counter()

        graph_elapsed = end_internal - start_internal
        graph_execution_times.append(graph_elapsed)
        print(f"Iteration {iteration} | Graph Execution Time: ", graph_elapsed, "seconds \n", flush=True)


def main():

    if args.data_move:
        print(f"move=({args.data_move})")

    if args.verbose:
        print(f"dim=({args.d})")


    G = read_graph(args.graph)

    data_config = G.pop(0)

    array = setup_data(data_config, args.d, data_move=args.data_move)


    for outer in range(args.outerloop):

        task_space = TaskSpace("Graph Iterations")

        #NOTE: INCLUDES DATA SETUP TIME IF ARGS.REINIT=TRUE
        start = time.perf_counter()

        with Parla():
            for iteration in range(args.loop):

                if args.reinit:
                    start_data = time.perf_counter()
                    array = setup_data(data_config, args.d, data_move=args.data_move)
                    end_data = time.perf_counter()


                start_internal = time.perf_counter()
                main_parla(task_space, iteration, G, array, args.verbose)
                end_internal = time.perf_counter()

        end = time.perf_counter()

        parla_total_elapsed = end - start
        parla_execution_times.append(parla_total_elapsed)
        print(f"Outer Iteration: {outer} | Total Elapsed: ", parla_total_elapsed, "seconds", flush=True)

        if args.reinit:
            data_elapsed = end_data - start_data
            data_execution_times.append(data_elapsed)
            print(f"Outer Iteration: {outer} | Time to Reconfigure Data: ", data_elapsed, "seconds", flush=True)

        #Note: This isn't really useful info but its there if you're curious
        #if args.verbose:
        #    print(f"Outer Iteration: {outer} | Time to Spawn Main Task: ", end_internal - start_internal, "seconds", flush=True)

        print("---------------")

    graph_mean = np.mean(np.array(graph_execution_times))
    graph_median = np.median(np.array(graph_execution_times))

    parla_mean = np.mean(np.array(parla_execution_times))
    parla_median = np.median(np.array(parla_execution_times))

    print(f"Graph Execution Time:: Average = {graph_mean} | Median = {graph_median}")
    print(f"Parla Total Time    :: Average = {parla_mean} | Median = {parla_median}")

    if args.reinit:
        data_mean = np.mean(np.array(data_execution_times))
        data_median = np.median(np.array(data_execution_times))
        print(f"----Data ReInit Time:: Average = {data_mean} | Median = {data_median}")
        print("Note: Data ReInit Time is included in Parla Total Time (subtract out as necessary)")


if __name__ == '__main__':
    #Estimate GPU frequency for busy wait timing
    #global cycles_per_second
    #cycles_per_second = estimate_frequency(50, ticks=10**8)

    #Launch experiment
    main()

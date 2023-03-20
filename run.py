import time

import copy

import numpy as np
#from sleep.core import *

from parla import Parla
from parla.cpu import cpu

from parla.RL.util import ReplayMemory

try:
    from parla.cuda import summarize_memory, clean_memory
except (ImportError, AttributeError):
    def summarize_memory():
        pass
    def log_memory():
        pass
    def clean_memory():
        pass


try:
    import cupy as cp
except ImportError:
    cp = None

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
parser.add_argument('-user', metavar='user', type=int, help='type of placement. options=(None=0, User=1)', default=0)
parser.add_argument('-weight', metavar='weight', type=int, help='length of task compute time', default=None)
parser.add_argument('-threads', metavar='threads', type=int, help='Number of workers', default=None)
parser.add_argument('-n', metavar='n', type=int, help='maximum number of tasks', default=None)
parser.add_argument('-gweight', metavar='gweight', type=int, help="length of task gil time", default=None)
parser.add_argument('-use_gpu', metavar='use_gpu', type=int, help="Use any GPUs?", default=1)
parser.add_argument('-training', metavar='training', type=int, help="Enable training mode?", default=0)
parser.add_argument('-random_type', type=int,
                    help="Use random generator for execution time: disable: 0, general: 1, gaussian distribution: 2, poisson distribution: 3", default=0)
parser.add_argument('-variance', type=int, help="", default=0)
parser.add_argument('-shuffling', type=int, help="1 if shuffling is enabled", default=0)

data_execution_times = []
graph_execution_times = []
parla_execution_times = []

args = parser.parse_args()

if cp is not None:
    n_gpus = cp.cuda.runtime.getDeviceCount()
else:
    n_gpus = 0

first_taskspace = TaskSpace("Demarcation_First")
last_taskspace = TaskSpace("Demarcation_Last")

replay_memory = ReplayMemory(10000)

def main_parla(it, exec_mode, random_type, variance, shuffling, data_config, task_space, iteration, G, verbose=False, reinit=False):
    #dep = [task_space[iteration-1]] if iteration > 0 else []

    @spawn(placement=cpu)
    async def main_task():

        start_data = time.perf_counter()
        array = setup_data(data_config, args.d, data_move=args.data_move,
                           use_gpu=args.use_gpu)
        end_data = time.perf_counter()

        data_elapsed = end_data - start_data
        data_execution_times.append(data_elapsed)

        device_id = get_current_devices()[0].index
        #print("Running on device", device_id, flush=True)

        for i in range(iteration):
            #print("Starting Iteration 1", flush=True)

            data_elapsed = 0
            if reinit and (i != 0):

                start_data = time.perf_counter()

                if args.data_move == 2 and reinit==2:

                    print("Resetting Data through PArray movement")
                    #Reset parray to modified on starting device
                    rs = TaskSpace("Reset")
                    for k in range(len(array)):
                        data = array[k]
                        if k == 0:
                            @spawn(rs[k], dependencies=[], placement=gpu(k%n_gpus), inout=[data])
                            def reset():
                                noop = 1
                        else:
                            @spawn(rs[k], dependencies=[rs[k-1]], placement=gpu(k%n_gpus), inout=[data])
                            def reset():
                                noop = 1

                    await rs[k]

                    #set to shared state
                    #ts = TaskSpace("Touch")
                    #for k in range(len(array)):
                    #    data = array[k]
                    #    @spawn(ts[k], placement=gpu(k%n_gpus), input=[data])
                    #    def reset():
                    #        noop = 1
                    #await ts

                elif args.data_move == 1 or reinit==1:
                    print("Resetting by creating new PArrays")
                    del array
                    array = setup_data(data_config, args.d,
                                       data_move=args.data_move, use_gpu=args.use_gpu)
                else:
                    noop = 1

                end_data = time.perf_counter()

                data_elapsed = end_data - start_data
                data_execution_times.append(data_elapsed)
            #print(f"Outer Iteration: {outer} | Time to Reconfigure Data: ", data_elapsed, "seconds", flush=True)

            #for l in range(len(array)):
            #    states = array[l]._coherence._local_states
            #    for device, val in states.items():
            #        if val == 2:
            #            array[l]._coherence._local_states[device] = 1
            #
            #    print(array[l]._coherence._local_states)
            # TODO(hc): print("----")
            start_internal = time.perf_counter()
            # TODO(hc): print("internal:", start_internal)

            @spawn(first_taskspace)
            def first_task():
                pass
            await create_tasks(G, array, first_taskspace, exec_mode, it, args.data_move, verbose, args.check,
                               args.user, random_type, variance, shuffling,
                               ndevices=args.threads, ttime=args.weight, limit=args.n,
                               gtime=args.gweight, use_gpu=args.use_gpu)
            @spawn(last_taskspace)
            def last_task():
                pass
            await last_taskspace

            end_internal = time.perf_counter()
            graph_elapsed = end_internal - start_internal
            graph_execution_times.append(graph_elapsed)

            # TODO(hc): print(f"Iteration {i} | Time: {graph_elapsed}", flush=True)
            #print(f"{args.weight}, {args.threads}, {graph_elapsed}")

            #if reinit and (i!= 0):
            #    noop = 1
            #    print(f"Iteration {i} | Data Reset Time: ", data_elapsed, "seconds \n", flush=True)



def main():

    #if args.data_move:
    #    print(f"move=({args.data_move})")
    #
    #if args.verbose:
    #    print(f"dim=({args.d})")


    G = read_graph(args.graph)

    data_config = G.pop(0)

    #array = setup_data(data_config, args.d, data_move=args.data_move)

    exec_mode = "test" if args.training == 0 else "training" if args.training == 1 else "disabled"
    random_type = args.random_type 
    variance = args.variance
    shuffling = args.shuffling
    print("exec mode:", exec_mode, " random type:", random_type, " variance:", variance, " shuffling:", shuffling)

    print("Exec mode:", exec_mode, flush=True)

    for outer in range(args.outerloop):

        task_space = TaskSpace("Graph Iterations")

        #NOTE: INCLUDES DATA SETUP TIME IF ARGS.REINIT=TRUE
        start = time.perf_counter()

        with Parla(replay_memory, exec_mode, outer):
            start_internal = time.perf_counter()
            main_parla(outer, exec_mode, random_type, variance, shuffling, data_config, task_space, args.loop, G, args.verbose, reinit=args.reinit)
            end_internal = time.perf_counter()

        end = time.perf_counter()

        parla_total_elapsed = end - start
        parla_execution_times.append(parla_total_elapsed)
        #print(f"Outer Iteration: {outer} | Total Elapsed: ", parla_total_elapsed, "seconds", flush=True)


            #Note: This isn't really useful info but its there if you're curious
            #if args.verbose:
            #    print(f"Outer Iteration: {outer} | Time to Spawn Main Task: ", end_internal - start_internal, "seconds", flush=True)

        summarize_memory()
        #Reset memory counter on outer loop
        clean_memory()
        #print("--------------- \n")


    #print("Summary: ")
    if len(graph_execution_times) > 1:
        start_index = 1
    else:
        start_index = 0
    graph_mean = np.mean(np.array(graph_execution_times)[start_index:])
    graph_median = np.median(np.array(graph_execution_times)[start_index:])

    parla_mean = np.mean(np.array(parla_execution_times))
    parla_median = np.median(np.array(parla_execution_times))

    # TODO(hc): print(f"Graph Execution Time:: Average = {graph_mean} | Median = {graph_median}")
    # TODO(hc): print(f"Parla Total Time    :: Average = {parla_mean} | Median = {parla_median}")


    if args.reinit:
        data_mean = np.mean(np.array(data_execution_times))
        data_median = np.median(np.array(data_execution_times))
        print(f"----Data ReInit Time:: Average = {data_mean} | Median = {data_median}")
        #print("Note: Data ReInit Time is included in Parla Total Time (subtract out as necessary)")


if __name__ == '__main__':
    """
    #Estimate GPU frequency for busy wait timing
    device_info = GPUInfo()
    cycles_per_second = estimate_frequency(100, ticks=0.05*1910*10**6)
    print("Cycle per second:", cycles_per_second, flush=True)
    device_info.update(cycles_per_second)
    """

    #Launch experiment
    main()

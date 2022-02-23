import time

import numpy as np
from sleep.core import *

from parla import Parla
from parla.cpu import cpu

import argparse

from synthetic.core import *

parser = argparse.ArgumentParser(description='Launch graph file in Parla')
parser.add_argument('-d', metavar='N', type=int, help='The dimension of data segments. (Increase to make movement more expensive)', default=10)
parser.add_argument('-data_move', metavar='data_move', type=int, help='type of data movement. options=(None=0, Lazy=1, Eager=2)', default=0)
parser.add_argument('-graph', metavar='graph', type=str, help='the input graph file to run', required=True, default='graph/independent.gph')
parser.add_argument('-verbose', metavar='verbose', type=bool, default=False)

args = parser.parse_args()

def main_parla(G, array):
    @spawn(placement=cpu)
    async def main_task():
        start_internal = time.perf_counter()
        await create_tasks(G, array)
        end_internal = time.perf_counter()

        print("Elapsed Internal Main Task: ", end_internal - start_internal, "seconds", flush=True)

def main():

    G = read_graph(args.graph)
    array = setup_data(G, args.d, args.verbose)

    start = time.perf_counter()

    with Parla():
        start_internal = time.perf_counter()
        main_parla(G, array, args.verbose)
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

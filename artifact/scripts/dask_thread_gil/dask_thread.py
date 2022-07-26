import time
import dask
from dask.distributed import Client, LocalCluster
from concurrent.futures import ThreadPoolExecutor
from sleep.core import bsleep, sleep_with_gil

import argparse

parser = argparse.ArgumentParser(description='Launch graph file in Parla')
parser.add_argument('-workers', type=int, default=1)
parser.add_argument('-time', type=int, default=51200)
parser.add_argument('-n', type=int, default=100)
parser.add_argument('-gtime', type=int, default=0)
args = parser.parse_args()


@dask.delayed
def sleep(dummy):
    bsleep(args.time)
    sleep_with_gil(args.gtime)

def end(dummy):
    pass

if __name__ == '__main__':
    with dask.config.set(pool=ThreadPoolExecutor(args.workers)):
        start_t = time.perf_counter()
        a = []
        for i in range(args.n):
            a.append(sleep(1))
        dask.compute(*a)
        end_t = time.perf_counter()
        print(args.time, ",", args.workers, ",", end_t - start_t)



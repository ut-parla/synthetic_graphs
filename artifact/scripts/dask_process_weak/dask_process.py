import time
import dask
from dask.distributed import Client, LocalCluster
from concurrent.futures import ThreadPoolExecutor
from sleep.core import bsleep

import argparse

parser = argparse.ArgumentParser(description='Launch graph file in Parla')
parser.add_argument('-workers', type=int, default=1)
parser.add_argument('-time', type=int, default=51200)
parser.add_argument('-n', type=int, default=100)
args = parser.parse_args()

def sleep(dummy):
    bsleep(args.time)

def end(dummy):
    pass

if __name__ == '__main__':

    cluster = LocalCluster(n_workers=args.workers, threads_per_worker=1, processes=True)
    client = Client(cluster)
    start_t = time.perf_counter()
    L = client.map(sleep, range(args.n))
    results = client.gather(L)
    end_t = time.perf_counter()
    print(args.time, ",", args.workers, ",", end_t - start_t)



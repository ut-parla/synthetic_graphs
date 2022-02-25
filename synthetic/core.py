import time
import re

import numpy as np
from sleep.core import *

from parla import Parla
from parla.cpu import cpu
from parla.array import copy, clone_here

try:  # if the system has no GPU
    import cupy as cp
    from parla.cuda import gpu
except (ImportError, AttributeError):
    cp = np
    gpu = cpu


from parla.tasks import get_current_devices
from parla.tasks import spawn, TaskSpace

from parla.device import Device

from parla.function_decorators import specialized

from parla.parray import asarray_batch


def get_dimension(file):
    with open(file, mode='r') as f:
        lines = f.readlines()

        for line in lines:
            is_dim = bool(re.search("dim", line))
            info = re.search("\(.*\)", line)
            info = None if info is None else info.group(0)

            if is_dim and info:
                #unpack tuple
                d = eval(info)
                d = d[0]
                return d


def get_movement_type(file):
    with open(file, mode='r') as f:
        lines = f.readlines()

        for line in lines:
            is_move = bool(re.search("dim", line))
            info = re.search("\(.*\)", line)
            info = None if info is None else info.group(0)

            if is_move and info:
                #unpack tuple
                move = eval(info)
                move = move[0]
                return move


def get_data_locations(file, launch_graph, locations):
    pass


def get_execution_info(file):
    
    G_time = dict()
    G_loc = dict()

    with open(file, mode='r') as f:
        lines = f.readlines()

        for line in lines:

            is_started = bool(re.search("\+Task", line))

            is_finished = bool(re.search("\-Task", line))

            task_id = re.search("\(.*\)", line)
            task_id = None if task_id is None else task_id.group(0)


            info = re.search("\[.*\]", line)
            info = None if info is None else info.group(0).strip("[]")

            #print(is_started, is_finished, task_id, info)

            if is_started and (info is not None) and (task_id is not None):
                #This is device information
                G_loc[task_id] = info

            if is_finished and (info is not None) and (task_id is not None):
                #This is time information
                G_time[task_id] = info

    return G_time, G_loc



def verify(file, G):
    G = G[0]
    correct = True
    started_tasks = []
    finished_tasks = []

    with open(file, mode='r') as f:
        lines = f.readlines()

        for line in lines:

            is_started = bool(re.search("\+Task", line))
            is_finished = bool(re.search("-Task", line))
            task_id = re.search("\(.*\)", line)
            task_id = None if task_id is None else task_id.group(0)

            if task_id is not None:
                task_id = eval(task_id)

                if is_started:
                    started_tasks.append(task_id)
                if is_finished:
                    finished_tasks.append(task_id)

                if is_started:
                    #Search for dependencies in is finished
                    deps = G[task_id]
                    check = [dep in finished_tasks for dep in deps]

                    correct = all(check)

    return correct

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


#approximate average on frontera RTX
cycles_per_second = 1919820866.3481758

def estimate_frequency(n_samples= 10, ticks=cycles_per_second):

    stream = cp.cuda.get_current_stream()
    cycles = ticks
    device_id = 0

    print(f"Starting GPU Frequency benchmark.")
    times = np.zeros(n_samples)
    for i in range(n_samples):

        start = time.perf_counter()
        gpu_sleep(device_id, cycles, stream)
        stream.synchronize()
        end = time.perf_counter()
        print(f"...collected frequency sample {i}")

        times[i] = (end-start)

    elapsed = np.sum(times)
    estimated_speed = (cycles*n_samples/elapsed)
    median_speed = cycles/np.median(times)

    print("Finished Benchmark.")
    print("Estimated GPU Frequency: Mean: ", estimated_speed, ", Median: ", median_speed, flush=True)
    return estimated_speed

def setup_data(G, d = 10, verbose=False, device_list=None, data_move=1):
    """
    Setup data into blocks of data specified by the graph config.
    At the moment all data will be initialized on the CPU.
    """
    data_config = G.pop(0)

    data = []
    count = 0
    for segment in data_config:
        array = np.zeros([segment, d], dtype=np.float32)+count
        data.append(array)
        count += 1

    #If data move is 'Eager'
    if data_move == 2:
        data = asarray_batch(data)

    return data

def read_graph(filename):
    G = []

    with open(filename, 'r') as graph:
        lines = graph.readlines()

        #Unpack data setup information (data sizes)
        config = lines.pop(0)
        config = config.split(",")

        G.append(np.zeros(len(config), dtype=np.int32))

        for i in range(len(config)):
            G[0][i] = int(config[i])

        #Unpack task information
        for line in lines:


            task = line.split("|")

            #Section 0: Self Id
            #Cannot be empty (Not checked)

            #print("First Segment: ", task[0])
            values = task[0].split(",")
            task_ids = np.zeros(len(values), dtype=np.int32)

            for i in range(len(values)):
                task_ids[i] = int(values[i])

            #Section 1: Self Info
            #Cannot be empty (Not checked)

            #print("Second Segment: ", task[1])
            values = task[1].split(",")
            task_info = np.zeros(len(values), dtype=np.int32)

            for i in range(len(values)):
                task_info[i] = int(values[i])


            if len(task) > 2:
                #Section 2: Dependency Info
                #print("Third Segment: ", task[2])
                deps = task[2].split(":")

                if (len(deps) > 0) and (not deps[0].isspace()):
                    task_deps = []

                    for i in range(len(deps)):
                        if not deps[i].isspace():
                            ids = deps[i].split(",")
                            task_deps.append(np.zeros(len(ids), dtype=np.int32))

                            for j in range(len(ids)):
                                if not ids[j].isspace():
                                    task_deps[-1][j] = int(ids[j])
                else:
                    task_deps = [None]
            else:
                task_deps = [None]


            if len(task) > 3:
                #Section 3: Data Info
                types = task[3].split(":")
                #print("Fourth Segment: ", task[3])

                check = [not t.isspace() for t in types]

                if any(check):
                    task_data = [None, None, None]
                    for i in range(len(types)):
                        data = types[i].split(",")
                        if not data[0].isspace():
                            task_data[i] = np.zeros(len(data), dtype=np.int32)
                            for j in range(len(data)):
                                if not data[j].isspace():
                                    task_data[i][j] = int(data[j])
                else:
                    task_data = None

            else:
                task_data = None

            task_tuple = (task_ids, task_info, task_deps, task_data)

            G.append(task_tuple)

    return G

def convert_to_dict(G):
    #print(G)

    depend_dict = dict()
    write_dict = dict()
    read_dict = dict()

    for task in G:
        ids, info, dep, data = task

        tuple_dep = [tuple(ids)] if dep[0] is None else [tuple(idx) for idx in dep]
        depend_dict[tuple(ids)] = tuple_dep

        list_in = [] if data[0] is None else [k for k in data[0]]
        list_out = [] if data[1] is None else [k for k in data[1]]
        list_inout = [] if data[2] is None else [k for k in data[2]]

        read_dict[tuple(ids)] = list_in+list_inout
        write_dict[tuple(ids)] = list_out + list_inout

    return depend_dict, read_dict, write_dict

def bfs(graph, node, target, writes):
    queue = []
    visited = []
    visited.append(node)
    queue.append(node)

    while queue:
        s = queue.pop(0)

        for neighbor in graph[s]:

            writes_to = writes[neighbor]

            if target in writes_to:
                return neighbor if neighbor != node else None

            if neighbor not in visited:
                visited.append(neighbor)
                queue.append(neighbor)

    return None


def find_data_edges(dicts, data_sizes=None, location_filter=None):
    depend_dict, read_dict, write_dict = dicts

    data_dict = dict()
    weight_dict = dict()
    target_dict = dict()

    for task, deps in depend_dict.items():
        reads = read_dict[task]
        writes = write_dict[task]
        #touches = set(reads+writes)
        touches = set(reads)

        data_deps = []

        for target in touches:
            last = bfs(depend_dict, task, target, write_dict)
            if last is None:
                last = f"D{target}"

                if location_filter is not None:
                    #All data starts initialized on the CPU
                    #TODO: Change this assumption
                    location_filter[last] = -1

                data_deps.append(last)
            else:
                data_deps.append(last)

            if data_sizes is not None:
                edge_id = str(last)+"-"+str(task)
                weight = data_sizes[target]

                if location_filter is not None:

                    #task that last used
                    loc_target = location_filter[target]
                    loc_last = location_filter[target]

                    if loc_target == loc_last:
                        weight = 0

                weight_dict[edge_id] = weight_dict.get(edge_id, []) + [weight]
                target_dict[edge_id] = target_dict.get(edge_id, []) + [target]

        data_dict[task] = data_deps

    return (data_dict, weight_dict, target_dict)


@specialized
def waste_time(ids, weight, gil, verbose=False):

    if verbose:
        print(f"+Task {ids} running on Device[-1] CPU", f"for {weight} total milliseconds", flush=True)

    gil_count, gil_time = gil

    for i in range(gil_count):
        weight_per_loop = weight//gil_count
        bsleep(weight_per_loop)
        sleep_with_gil(gil_time)


@waste_time.variant(gpu)
def waste_time_gpu(ids, weight, gil, verbose=False):
    """
    Busy wait function for GPU.
    Keep in mind that when decreasing kernel weight that synchronization and kernel launch times become a factor. Please run estimate frequency with 'ticks' near the desired experiment to get an estimate of the speed when these effects are factored in.
    """

    gil_count, gil_time = gil

    device_id = get_current_devices()[0].index
    stream = cp.cuda.get_current_stream()
    ticks = int((weight/(10**6))*cycles_per_second)

    if verbose:
        print(f"+Task {ids} running on Device[{device_id}] GPU for {ticks} total cycles", flush=True)

    for i in range(gil_count):

        ticks_per_loop = ticks//gil_count
        gpu_sleep(device_id, ticks, stream)

        #Optional Sync (Prevents overlap with GIL lock, if that behavior is wanted)
        stream.synchronize()

        sleep_with_gil(gil_time)


def create_task_lazy(launch_id, task_space, ids, deps, place, IN, OUT, INOUT, cu, weight, gil, array, data, verbose=False, check=False):

    ids = tuple(ids)

    @spawn(task_space[ids], placement=place, dependencies=deps, vcus=cu)
    def busy_sleep():
        start = time.perf_counter()

        local = dict()
        if data[0] is not None:
            for in_data in data[0]:
                block = array[in_data]
                where = -1 if isinstance(block, np.ndarray) else block.device.id
                arr = clone_here(block)
                local[in_data] = arr
                old = None if not check else np.copy(arr[0, 1])
                arr[0, 1] = -launch_id
                if verbose:
                    print(f"Task {ids} moved Data[{in_data}] from Device[{where}]. Block={arr[0, 0]} | Value={arr[0,1]}, {old}", flush=True)

        if data[2] is not None:
            for inout_data in data[2]:
                block = array[inout_data]
                where = -1 if isinstance(block, np.ndarray) else block.device.id
                arr = clone_here(block)
                local[inout_data] = arr
                old = None if not check else np.copy(arr[0, 1])
                arr[0,1] = -launch_id
                if verbose:
                    print(f"Task {ids} moved Data[{inout_data}] from Device[{where}]. Block={arr[0, 0]} | Value={arr[0, 1]}, {old}", flush=True)

        waste_time(ids, weight, gil, verbose)

        #Update location of data to this copy?
        #Should this be a copy back to where it was
        if data[1] is not None:
            for out_data in data[1]:
                array[out_data] = local[out_data]

        if data[2] is not None:
            for inout_data in data[2]:
                array[inout_data] = local[inout_data]

        end = time.perf_counter()

        if verbose:
            print(f"-Task {ids} elapsed: [{end - start}] seconds", flush=True)

def create_task_eager(launch_id, task_space, ids, deps, place, IN, OUT, INOUT, cu, weight, gil, array, data, verbose=False, check=False):

    ids = tuple(ids)

    @spawn(task_space[ids], placement=place, dependencies=deps, input=IN, output=OUT, inout=INOUT, vcus=cu)
    def busy_sleep():

        if data[0] is not None:
            for in_data in data[0]:
                block = array[in_data]
                block = block.array
                where = -1 if isinstance(block, np.ndarray) else block.device.id
                old = None if not check else np.copy(block[0, 1])
                block[0, 1] = -launch_id
                if verbose:
                    print(f"Task {ids} :: Auto Move.. Data[{in_data}] is on Device[{where}]. Block={block[0, 0]} | Value={block[0,1]}, {old}", flush=True)

        if data[2] is not None:
            for inout_data in data[2]:
                block = array[inout_data]
                block = block.array
                where = -1 if isinstance(block, np.ndarray) else block.device.id
                old = None if not check else np.copy(block[0, 1])
                block[0, 1] = -launch_id
                if verbose:
                    print(f"Task {ids} :: Auto Move.. Data[{inout_data}] is on Device[{where}]. Block={block[0, 0]} | Value={block[0,1]}, {old}", flush=True)

        start = time.perf_counter()

        waste_time(ids, weight, gil, verbose)

        end = time.perf_counter()

        if verbose:
            print(f"-Task {ids} elapsed: [{end - start}] seconds", flush=True)


def create_task_no(launch_id, task_space, ids, deps, place, IN, OUT, INOUT, cu, weight, gil, verbose=False):
    ids = tuple(ids)
    @spawn(task_space[ids], dependencies=deps, placement=place, vcus=1)
    def busy_sleep():

        start = time.perf_counter()

        waste_time(ids, weight, gil, verbose)

        end = time.perf_counter()
        print(f"-Task {ids} elapsed: [{end - start}] seconds", flush=True)

def create_tasks(G, array, data_move=0, verbose=False, check=False):

    task_space = TaskSpace('TaskSpace')

    launch_id = 0
    for task in G:
        ids, info, dep, data = task

        #Generate data list
        INOUT = [] if data[0] is None else [array[f] for f in data[0]]
        IN = [] if data[1] is None else [array[f] for f in data[1]]
        OUT = [] if data[2] is None else [array[f] for f in data[2]]

        #Generate dep list
        deps = [] if dep[0] is None else [task_space[tuple(idx)] for idx in dep]

        #Generate task weight
        weight = info[0]
        vcus = 1/info[1]
        gil_count = info[2]
        gil_time = info[3]
        gil = (gil_count, gil_time)

        #Generate placement list
        if info[2] == 0:
            place = cpu
        elif info[2] == 1:
            place = gpu
        else:
            place = [cpu, gpu]

        #print(ids, deps, place, IN, OUT, INOUT, vcus, weight)

        if data_move == 0:
            create_task_no(launch_id, task_space, ids, deps, place, IN, OUT, INOUT, vcus, weight, gil, verbose)
        if data_move == 1:
            create_task_lazy(launch_id, task_space, ids, deps, place, IN, OUT, INOUT, vcus, weight, gil, array, data, verbose, check)
        if data_move == 2:
            create_task_eager(launch_id, task_space, ids, deps, place, IN, OUT, INOUT, vcus, weight, gil, array, data, verbose, check)

        launch_id += 1

    return task_space

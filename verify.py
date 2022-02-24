
import time

import re

import numpy as np
import argparse

from synthetic.core import *

import networkx as nx
import pydot 
import matplotlib.image as mpimg
import io 
from networkx.drawing.nx_agraph import graphviz_layout, to_agraph

import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='Verify graph execution order')
parser.add_argument('-input', metavar='input', type=str, help='the output from the parla run', required=True, default='output.txt')
parser.add_argument('-graph', metavar='graph', type=str, help='the input graph file to run', required=True, default='graph/independent.gph')
args = parser.parse_args()

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

if __name__ == '__main__':
    #Throwaway data information
    G = read_graph(args.graph)

    G.pop(0)
    depend_dict = convert_to_dict(G)

    result = verify(args.input, depend_dict)

    if result:
        print("Ordering: VALID")
    else:
        print("Ordering: INCORRECT")
    



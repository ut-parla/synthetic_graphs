
import time


import numpy as np
import argparse

from synthetic.core import *

parser = argparse.ArgumentParser(description='Verify graph execution order')
parser.add_argument('-input', metavar='input', type=str, help='the output from the parla run', required=True, default='output.txt')
parser.add_argument('-graph', metavar='graph', type=str, help='the input graph file to run', required=True, default='graph/independent.gph')
args = parser.parse_args()


if __name__ == '__main__':
    #Throwaway data information
    G = read_graph(args.graph)

    data_sizes = G.pop(0)
    depend_dict = convert_to_dict(G)

    G_time, G_loc = get_execution_info(args.input)

    result = verify(args.input, depend_dict, location=G_loc)

    if result:
        print("Task Ordering: VALID")
    else:
        print("Task Ordering: INCORRECT")

    data_dict = find_data_edges(depend_dict, data_sizes)
    data_dep, weight_dict, target_dict = data_dict

    movement_obs = load_movement(args.input, depend_dict, verify=True)
    #verify_movement(movement_obs, depend_dict, data_dict)
    print(movement_obs)






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

    G.pop(0)
    depend_dict = convert_to_dict(G)

    result = verify(args.input, depend_dict)

    if result:
        print("Ordering: VALID")
    else:
        print("Ordering: INCORRECT")




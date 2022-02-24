
import time

import numpy as np
import argparse

from synthetic.core import *

import networkx as nx
import pydot 
import matplotlib.image as mpimg
import io 
from networkx.drawing.nx_agraph import graphviz_layout, to_agraph

import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='Plot graph file')
parser.add_argument('-data', metavar='data', type=int, default=0, help="Bool: whether to include data dependencies in plot")
parser.add_argument('-backend', metavar='backend', type=int, default=0, help='What plotting backed to use. networkx=0, pydot=1')
parser.add_argument('-graph', metavar='graph', type=str, help='the input graph file to run', required=True, default='graph/independent.gph')
parser.add_argument('-output', metavar='output', type=str, help='the output png file name', required=False, default='graph_output.png')
args = parser.parse_args()

def plot_graph_nx(depend_dict, data_dict, plot_isolated=True, plot=True):
    G = nx.DiGraph()

    dep_dict = depend_dict[0]

    for target, deps in dep_dict.items():
        for source in deps:
            is_isolated = all( [target[i] == source[i] for i in range(len(target))])
            if is_isolated and plot_isolated:
                #G.add_edge(source, target, color='black', style='dotted')
                G.add_node(source)
            elif not is_isolated:
                G.add_edge(source, target, color='black')

    if args.data:
        for target, deps in data_dict.items():
            for source in deps:
                G.add_edge(source, target, color='red')

    #nx.draw(G, with_labels=True, font_weight='bold')
    #plt.show()

    if plot:
        pg = nx.drawing.nx_pydot.to_pydot(G)
        
        png_str = pg.create_png(prog="dot")
        sio = io.BytesIO()
        sio.write(png_str)
        sio.seek(0)
        img = mpimg.imread(sio)

        implot = plt.imshow(img, aspect='equal')
        plt.show()

        pg.write_png(args.output)

    if plot_isolated:
        critical_path = nx.dag_longest_path(G)
        generations = nx.topological_generations(G)
        gen_size = np.array([len(g) for g in generations])

        print()
        print("Graph analysis:")
        print("--------------")
        print(f"The longest path in the DAG is: {len(critical_path)}")
        print(f"Generation Sizes. Min: {np.min(gen_size)}, Mean: {np.mean(gen_size)}, Max: {np.max(gen_size)}")

        return (len(critical_path), np.max(gen_size))

    return None
    #A = to_agraph(G)
    #A.layout('dot')
    #A.draw('output.png')


def plot_graph_pydot(depend_dict, data_dict):
    G = pydot.Dot("graph", graph_type="graph")

    dep_dict = depend_dict[0]

    for target, deps in dep_dict.items():
        target = str(target)
        for source in deps:
            source = str(source)
            G.add_edge(pydot.Edge(source, target, color='black'))

    for target, deps in data_dict.items():
        target = str(target)
        for source in deps:
            source = str(source)
            G.add_edge(pydot.Edge(source, target, color='red'))

    #G.write_png("output.png")


if __name__ == '__main__':
    #Throwaway data information
    G = read_graph(args.graph)
    if args.data:
       print("Generating graph plot with data movement.")
    else:
       print("Generating graph plot without data movement.")
    

    G.pop(0)
    depend_dict = convert_to_dict(G)


    if args.data:
        data_dict = find_data_edges(depend_dict)
    else:
        data_dict = dict()
    
    info = plot_graph_nx(depend_dict, data_dict)

    if info is not None:
        depth, width = info
        task = G[0]
        task_info = task[1]
        compute_time = task_info[0]
        gil_count = task_info[3]
        gil_time = task_info[4]
        task_time = compute_time + gil_count * gil_time
        task_time = task_time / 10**6
        
        p = 1

        serial = task_time * len(G)
        est = max(serial/p, (depth*task_time))
        print("Assuming equal sized tasks and no data movement:")
        print("Degree of Parallelism =", width)
        print("Task Size: ", task_time)
        print("Lower bound estimate: ", est)
        print("Serial Time: ", serial)




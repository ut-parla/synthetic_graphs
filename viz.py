
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
parser.add_argument('-p', metavar='p', type=int, help='the number of devices to run', default=4)
parser.add_argument('--no-plot', dest='plot', type=str2bool, nargs='?', default=False, help='Toggle generate plots (default=True)')
parser.add_argument('--data-nodes', dest='data_nodes', type=str2bool, nargs='?', default=False, help='Toggle generate of data nodes (default=False)')
parser.add_argument('--merge', dest='merge', type=str2bool, nargs='?', default=False, help='Toggle merging of data nodes (default=False)')
parser.add_argument('-input', metavar='input', type=str, help="Read Parla log to view mapping and execution time in graph")
parser.add_argument('--maximum-set', dest='maximum', type=str2bool, help="Compute maximal independent set. WARNING NP-COMPLETE", default=False, nargs='?')
args = parser.parse_args()

def plot_graph_nx(depend_dict, data_dict, plot_isolated=True, plot=True, weights=None, data_task=(False, False), location=None, times=None):
    G = nx.DiGraph()

    data_dict, target_dict = data_dict
    dep_dict = depend_dict[0]

    skip_data_end = True

    data_task, merge = data_task

    show_weights = True

    if weights is None:
        default_weight = 1
        show_weights = False
    else:
        default_weight = 0
        show_weights = True

    if not data_task:
        show_weights = False


    for target, deps in dep_dict.items():
        for source in deps:
            is_isolated = all( [target[i] == source[i] for i in range(len(target))])

            #print("Initial Nodes", source, target)
            if is_isolated and plot_isolated:
                #G.add_edge(source, target, color='black', style='dotted')
                G.add_node(source)
            elif not is_isolated:
                if show_weights:
                    G.add_edge(source, target, color='black', weight=default_weight)
                else:
                    G.add_edge(source, target, color='black', weight=default_weight)

            if location:
                G.nodes[source]['loc'] = location[str(source)]
                G.nodes[target]['loc'] = location[str(target)]

            if times:
                G.nodes[source]['time'] = times[str(source)]
                G.nodes[target]['time'] = times[str(target)]

    if args.data:
        for target, deps in data_dict.items():
            for source in deps:
                edge_w = default_weight
                edge_id = str(source)+"-"+str(target)


                if data_task:
                    if merge:
                        if weights is not None:
                            edge_w = np.sum(weights[edge_id])

                        #print("merge", source, edge_id, target)

                        if show_weights:
                            if not skip_data_end or ("D" not in source):
                                G.add_edge(source, edge_id, color='red', weight=edge_w, label=edge_w)
                                edge_w = 0
                            G.add_edge(edge_id, target, color='red', weight=edge_w, label=edge_w)
                        else:
                            if not skip_data_end or ("D" not in source):
                                G.add_edge(source, edge_id, color='red', weight=edge_w)
                                edge_w = 0
                            G.add_edge(edge_id, target, color='red', weight=edge_w)

                        if location:
                            #TODO: Update this to be compatible with MSI
                            G.nodes[edge_id]['loc'] = location[str(target)]

                    else:
                        d_idx = 0
                        for d in target_dict[edge_id]:
                            temp_id = edge_id+" Data ["+str(d)+"]"

                            if weights is not None:
                                edge_w = weights[edge_id][d_idx]

                            #print("nm", source, temp_id, target, d)
                            if show_weights:
                                if not skip_data_end or ("D" not in source):
                                    G.add_edge(source, temp_id, color='red', weight=edge_w, label=edge_w)
                                    edge_w = 0

                                G.add_edge(temp_id, target, color='red', weight=edge_w, label=edge_w)
                            else:
                                if not skip_data_end or ("D" not in source):
                                    G.add_edge(source, temp_id, color='red', weight=edge_w)
                                    edge_w = 0
                                G.add_edge(temp_id, target, color='red', weight=edge_w)

                            if location:
                                #TODO: Update this to be compatible with MSI
                                G.nodes[temp_id]['loc'] = location[str(target)]

                        d_idx += 1

                else:
                    #print("No Data Task", source, target)
                    if show_weights:
                        G.add_edge(source, target, color='red', weight=edge_w, label=edge_w)
                    else:
                        G.add_edge(source, target, color='red', weight=edge_w)


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
        critical_path = nx.dag_longest_path(G, weight=1)
        #print(critical_path)
        generations = nx.topological_generations(G)
        gen_size = np.array([len(g) for g in generations])

        #TODO: Why is this broken for args.maximum? (undirected is not equivalent)
        #uG = G.to_undirected()
        #if args.maximum:
        #    width = nx.algorithms.approximation.maximum_independent_set(G)
        #else:
        #   width = nx.algorithms.mis.maximal_independent_set(uG)

        #width = len(width)

        print()
        print("Graph analysis:")
        print("--------------")
        print(f"The longest path in the DAG is: {len(critical_path)}")
        print(f"Generation Sizes. Min: {np.min(gen_size)}, Mean: {np.mean(gen_size)}, Max: {np.max(gen_size)}")
        #print(f"ERROR: BUG HERE. --> Approximate size of independent set: {width}")

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


    data_sizes = G.pop(0)
    depend_dict = convert_to_dict(G)

    if args.input is not None:
        G_time, G_loc = get_execution_info(args.input)
    else:
        G_time = None
        G_loc = None

    #print(G_loc)

    if args.data:
        data_dict = find_data_edges(depend_dict, data_sizes)
    else:
        data_dict = (dict(), None, None)

    data_dict, weight_dict, target_dict = data_dict
    data_dict = data_dict, target_dict
    info = plot_graph_nx(depend_dict, data_dict, weights=weight_dict, data_task=(args.data_nodes,args.merge), location=G_loc, times=G_time)

    #Compute runtime estimates
    if info is not None:
        depth, width = info
        task = G[0]
        task_info = task[1]
        compute_time = task_info[0]
        gil_count = task_info[3]
        gil_time = task_info[4]
        task_time = compute_time + gil_count * gil_time
        task_time = task_time / 10**6

        p = args.p

        serial = task_time * len(G)
        est = max(serial/p, (depth*task_time))
        print("Assuming equal sized tasks and no data movement:")
        print("Degree of Parallelism in Generational Ordering =", width)
        print("Average Task Size: ", task_time, "seconds ")
        print("Lower bound estimate: ", est, " seconds")
        print("Serial Time: ", serial, " seconds")




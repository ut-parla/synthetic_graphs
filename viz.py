
import time

import numpy as np
import argparse

from synthetic.core import *
from synthetic.bandwidth import *

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

def check_movement(data_idx, to_id, from_id, location, movement=None):

    if movement is not None:
        #Get task id that last t1ouched the data this read from
        try:
            from_id = movement[to_id][data_idx]
        except KeyError:
            print("Looking for", to_id, data_idx)
            print(movement)
        #print("Data came from Task: ", from_id)

    to_id = str(to_id)
    from_id = str(from_id)


    #print(to_id, from_id, location.keys())
    if "D" in from_id and (location[to_id] == -1):
        #print("Initial Read from CPU TO CPU")
        return (False, -1)
    elif "D" in from_id:
        #print("Initial read from CPU to Device")
        return (True, -1)
    else:
        #print("Read: (from, to)", location[from_id], location[to_id])
        return ((location[to_id] != location[from_id]), location[from_id])

def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def make_graph_nx(depend_dict, data_dict, plot_isolated=True, plot=True, weights=None, data_task=(False, False), location=(None, None), times=None):
    G = nx.DiGraph()

    location, movement = location

    data_dict, target_dict = data_dict

    dep_dict = depend_dict[0]

    skip_data_end = True

    data_task, merge = data_task
    print("Show data tasks: ", data_task)
    print("Merge data tasks: ", merge)

    show_weights = True

    if weights is None:
        default_weight = 0
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

            if location is not None:
                G.nodes[source]['loc'] = location[str(source)]
                G.nodes[target]['loc'] = location[str(target)]
            

            if times is not None:
                G.nodes[source]['time'] = times[str(source)]
                G.nodes[target]['time'] = times[str(target)]

    if args.data:
        for target, deps in data_dict.items():
            for source in deps:

                move_flag = True
                edge_w = default_weight if move_flag else 0
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
                            try:
                                G.nodes[temp_id]['loc'] = location[str(source)]
                            except KeyError:
                                G.nodes[temp_id]['loc'] = -1

                    else:
                        d_idx = 0
                        for d in target_dict[edge_id]:
                            temp_id = edge_id+" - Data ["+str(d)+"]"

                            if weights is not None:

                                if (location is not None) and (movement is not None):
                                    #print("Data IDX: ", )
                                    move_flag, copy_from = check_movement(d, target, source, location, movement)
                                    #print(target, source, move_flag)
                                else:
                                    move_flag = True
                                    copy_from = source

                                edge_w = weights[edge_id][d_idx] if move_flag else 0

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
                                try:
                                    G.nodes[temp_id]['loc'] = copy_from
                                except KeyError:
                                    G.nodes[temp_id]['loc'] = -1


                        d_idx += 1

                else:
                    #print("No Data Task", source, target)
                    if show_weights:
                        G.add_edge(source, target, color='red', weight=edge_w, label=edge_w)
                    else:
                        G.add_edge(source, target, color='red', weight=edge_w)


    #nx.draw(G, with_labels=True, font_weight='bold')
    #plt.show()

    colors = ['black', '#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7']

    if location is not None:
        for node in G:
            #print(node)

            try:
                device_id = int(G.nodes[node]['loc'])
            except KeyError:
                device_id = -1


            if device_id >= 0:
                G.nodes[node]['style'] = 'filled'

            c = colors[device_id+1]
            G.nodes[node]['color'] = str(c)

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

    return G
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
        movement = load_movement(args.input, depend_dict)
        d = get_dimension(args.input)
    else:
        movement = None
        G_time = None
        G_loc = None
        d = 2

    #print(G_loc)

    if args.data:
        data_dict = find_data_edges(depend_dict, data_sizes)
    else:
        data_dict = (dict(), None, None)

    data_dict, weight_dict, target_dict = data_dict
    data_dict = data_dict, target_dict
    nxG = make_graph_nx(depend_dict, data_dict, weights=weight_dict, data_task=(args.data_nodes,args.merge), location=(G_loc, movement), times=G_time)


    def analyze_graph(G, submit_graph, input_flag=False):

        critical_path = nx.dag_longest_path(G, weight=1)

        #print(critical_path)
        generations = nx.topological_generations(G)

        generations = [g for g in generations]
        gen_size = np.array([len(g) for g in generations])
        #TODO: Why is this broken for args.maximum? (undirected is not equivalent)
        #uG = G.to_undirected()
        #if args.maximum:
        #    width = nx.algorithms.approximation.maximum_independent_set(G)
        #else:
        #   width = nx.algorithms.mis.maximal_independent_set(uG)

        #width = len(width)

        width = np.max(gen_size)

        print()
        print("Graph analysis:")
        print("--------------")
        print(f"The longest path in the DAG is: {len(critical_path)}")
        print(f"Generation Sizes. Min: {np.min(gen_size)}, Mean: {np.mean(gen_size)}, Max: {np.max(gen_size)}")

        if input_flag:
            data_count = nxG.size(weight='weight') * d * 8
            print("Total Data Movement: ", sizeof_fmt(data_count))


        task = submit_graph[0]
        task_info = task[1]
        compute_time = task_info[0]
        gil_count = task_info[3]
        gil_time = task_info[4]
        task_time = compute_time + gil_count * gil_time
        task_time = task_time / 10**6
        depth = len(critical_path)

        p = args.p 
        
        serial = task_time * len(G)
        est = max(serial/p, (depth*task_time))
        print("Assuming equal sized tasks and no data movement:")
        print("Degree of Parallelism in Generational Ordering =", width)
        print("Average Task Size: ", task_time, "seconds ")
        print("Lower bound estimate: ", est, " seconds")
        print("Serial Time: ", serial, " seconds")

        gen_time = 0
        for level in generations:
            gen_time += np.ceil(len(level)/p) * task_time
        print("Time under generation schedule: ", gen_time, " seconds")


        if args.input is not None:
            print("========")
            print('Performing bandwidth test...')
            bandwidth_table = generate_bandwidth()
            print("bandwidth test completed.")

            path_time = 0
            for i in range(len(critical_path)):
                node = critical_path[i]
                next_node = None
                if i+1 < len(critical_path) - 1:
                    next_node = critical_path[i+1]

                node_info = G.nodes[node]
                #print(node, next_node)
                if "Data" in str(node):
                    path_time += 0
                else:
                    try:
                        path_time += float(node_info['time'])
                    except KeyError:
                        path_time += 0

                if next_node is not None:
                    next_node_info = G.nodes[next_node]
                    edge_info = G.get_edge_data(node, next_node)
                    entries = edge_info['weight']*d
                    
                    try:
                        from_dev = int(node_info['loc'])+1
                        to_dev = int(next_node_info['loc'])+1
                    except KeyError:
                        continue

                    b = bandwidth_table[from_dev, to_dev] 
                    path_time += entries / b 
                    #print(node, next_node, entries, b)
                

            print("Critical path time with observed execution and expected data movement times:", path_time)


    analyze_graph(nxG, G, (args.input is not None))




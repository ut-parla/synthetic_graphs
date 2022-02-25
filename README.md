# Synthetic Test Graphs for Parla
Synthetic Task Graphs for Parla Testing and Benchmarks


This is a small directory for setting up toy synthetic graphs for the Parla Python tasking system. 

Task graphs execute with optional data movement and burn time with user specified busy waits (on CPU or GPU)


## Features

- scripts to generate test graphs
- execute test graphs with Parla 
   - Enable with no data movement, lazy movement, or eager movement
- visualize test graphs dependencies (with or without data movement tasks)
- analyze test graphs (average width and critical path length)
- verify parla task execution and data movement executed in a valid ordering
- IN PROGRESS: analyze Parla output and policy
   - Vizualize execution order and assigned mapping
   - Compute expected time (using observed task times and bandwidth)
   - Compute total data movement cost 
- IN PROGRESS: Dynamic task context names for inspection with vizviewer

## Install

You must compile the Cython `sleep` module which requires Cython & CUDA and must be set to an architecture newer than Pascal. 
```
[This allows one to potentially use the __nanosleep routine, which is currently unused in this implementation but might be more accurate for a future version] 
```

The architecture is currently hardcoded in `setup.py` for Frontera's RTX nodes (`sm_70`), but this can be changed on `L24`. 
After updating architeture the module can be compiled simply with `make` or 

```
python setup.py install <the usual options>
```

For simplicity we use the Kokkos `nvcc` wrapper to avoid having to precompile the CUDA into a shared object file.
Depending on your enviornment you may need to change the path in `nvcc_wrapper` to your `g++` executable.
Keep in mind that your CUDA env has a maximum supported version of GCC.  

The `synthetic` directory is currently maintained to be used as a module in-place.
It can likely be pip installed, but its not recommended. 

## Usage

Graphs are specified with "\*.gph" files with the following semantics:

The first line of the file specifies an initial data partitioning. 
This is a comma separated list of the number of elements in each partition.

Each subsequent line represents a task. 


```
<task_id> | <task time (μs)>, <1/vcus>, <location>, <# GIL access>, <GIL time (μs)> | <task dependencies> | <in_data> : <out_data> : <inout_data>
```

`<task_id>` can be an arbitrarily long list of comma seperated integers.

`<task_dependencies>` can be an arbitrarily long list of `<task_ids>` separated by colons ':'.

`<location>` can be 0=cpu, 1=gpu, 2=either.

Tasks are launched in file-order from top to bottom. 
Note this must be a valid launch order for Parla, otherwise the dependencies won't resolve. 

As an example the following specifies a serial chain graph such that each task depends (redundently) on its two immediate predecessors. 

- Each task is launched on the GPU and consumes a whole device (`vcus=1`). 
- Each task busy waits for 50000 microseconds without the GIL and 200 microsecoonds with the GIL. 
- Each task reads data_block[1] of size 100 and read/writes to data_block[0] of size 40. 


```
40, 100
0 | 50000, 1, 1, 1, 200 |   | 1 : : 0
1 | 50000, 1, 1, 1, 200 |  0 | 1 : : 0
2 | 50000, 1, 1, 1, 200 |  1 : 0 | 1 : : 0
3 | 50000, 1, 1, 1, 200 |  2 : 1 | 1 : : 0
4 | 50000, 1, 1, 1, 200 |  3 : 2 | 1 : : 0
5 | 50000, 1, 1, 1, 200 |  4 : 3 | 1 : : 0
6 | 50000, 1, 1, 1, 200 |  5 : 4 | 1 : : 0
7 | 50000, 1, 1, 1, 200 |  6 : 5 | 1 : : 0
8 | 50000, 1, 1, 1, 200 |  7 : 6 | 1 : : 0
9 | 50000, 1, 1, 1, 200 |  8 : 7 | 1 : : 0
```


Scripts to generate graph files are in the `graphs/` directory. 
`viz.py` is used to draw graphs to the screen (uses and REQUIRES networkx [https://networkx.org/] )
NOTE: `viz.py` also computes the average width and critical path length. (which can be used to estimate runtime)

`run.py` is used to launch the tasks
'verify.py' can take the verbose standard output of 'run.py' and verify that the observed ordering is correct

Note: graph analysis should only be interpreted for runtime estimates when run without data movement edges. 

The command line options for all scripts can be inspected by using '-h'. 
Theres a lot more than have been listed here and its worth taking a look. 
Important ones are: '-graph' to read a graph file, and '--data_move' to disable movement entirely, or enable lazy/eager copies. 

Example usage is:

```
//Generate the graph
python graph/generate_serial_graph.py

//Run the graph with Parla
python run.py -graph graphs/serial.gph -data_move 0 --verbose > output.txt

//Verify that output ran in a valid ordering
python verify.py -graph graphs/serial.gph -input output.txt

//Vizualize and analyze the graph with data movement edges
python viz.py -graph graphs/serial.gph -data 1 
```

This would generate a serial graph (with default configuration) and runs it without any data movement. 




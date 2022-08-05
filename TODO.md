
# SCHEDULER TODOs

- Eviction
    - Need to decide when it happens (only for compute tasks??, how to avoid
      deadlock)
    - If it happens for data movement tasks, how do we prevent trashing.



# OLD TODOs (Some of these are done. Need to go back and check)
- Add memory parameter to task launches based on used data
- Fix concurrent read/writes in 1D Stencil
- Use bandwidth estimate to configure and estimate data transfer costs in microseconds
- Build spawn_id to task_id dictionary
- Get location of data movement tasks based on runtime output
- Use runtime output to verify data movement correctness
- Compute total data movement cost
  - Use thresholded weights
- Refactor viz into anaylze.py
   - Pull apart plot function to build_graph and plot_graph
   - This was anaylsis can be run separately



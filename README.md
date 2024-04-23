### Cache Design

This document serves as a guide for the creation and utilization of our cache.

Run `python simulator_vanilla.py -h` to get the syntax for the simulator parameters.

### (Example: CLI commands)

Run `python simulator_vanilla.py 4 10 3 20 4 LFU INCLUDE 0`.

### (Example: Running experiment on trace files)

Run `python simulator_vanilla.py 4 10 3 20 4 LFU INCLUDE 2 < traces/gcc_trace.txt`.

# 1) Simulators
There are 3 simulators, `simulator_vanilla.py`, `simulator_adaptive.py` and `simulator_sequential.py`. For the purposes of creating graphs #1-4 for MP1, only `simulator_vanilla.py` is used, as it has an additional `--l1` parameter that allows the simulator to discard the L2 cache as well as nullify L2-related parameters. Run `python simulator_vanilla.py -h` for more information.

# 2) Results
Quantitative results computed using matplotlib can be found in the `assets/` folder.

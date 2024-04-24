# Cache Design

This document serves as a guide for the creation and utilization of our cache.

Run `python simulator_vanilla.py -h` to get the syntax for the simulator parameters.

All numerical parameters are powers of 2, except for the prefetch window size, e.g. Run `python simulator_vanilla.py 4 10 3 20 4 LFU INCLUDE 2' will lead to

- blocksize = 2^4
- l1size = 2^10
- l1assoc = 2^3
- l2size = 2^20
- l2assoc = 2^4
- prefetch window size = 2

Addendum: Setting the cache size of l2 to 0 will lead to 2^0=1. To remove the L2 cache, see instructions in section (1).

### (Example: CLI commands)

Run `python simulator_vanilla.py 4 10 3 20 4 LFU INCLUDE 0`.

### (Example: Running experiment on trace files)

Run `python simulator_vanilla.py 4 10 3 20 4 LFU INCLUDE 2 < traces/gcc_trace.txt`.

## 1) Simulators
There are 3 simulators, `simulator_vanilla.py`, `simulator_adaptive.py` and `simulator_sequential.py`.

For the purposes of creating graphs #1-4 for MP1, only `simulator_vanilla.py` is used, as it has an additional `--l1` parameter that allows the simulator to discard the L2 cache as well as nullify L2-related parameters. Run `python simulator_vanilla.py -h` for more information. For example:

`python simulator_vanilla.py 4 10 3 20 4 LFU INCLUDE 2 -- l1` will completey ignore the parameters CACHESIZE2 = 2^20, CACHEASSOC2 = 2^4, INCLUSION_POL and PREFETCH.

## 2) Commands
Once you run the simulator, you are able to type in 4 commands:

- read \<addr\>, reads decimal addresses
- write \<addr\> <\value\>, writes to decimal addresses
- r \<addr\>, reads hexadecimal addresses
- w \<addr\> <\value\>, writes to decimal addresses

`r` and `w` are introduced to read hexadecimal addresses from the trace files.

## 3) Results
Quantitative results computed using matplotlib can be found in the `assets/` folder.

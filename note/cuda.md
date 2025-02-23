# CUDA to implement parallel computing

## SHA256 speed test

Here, we try to implement the SHA256 algorithm using CUDA to accelerate the speed of hashing. Three way is used, one is the `batch processing`, this way the code is repeat to run the same code for many times.

The second is the `parallel processing`, which is use the _grid_ and _block_ term to parallel the code.

### Throughput Analysis

why the throughput is first increasing and then decreasing with message size?

1. Initial Increase Phase
   For small message sizes (4B to ~1024B), the throughput increases significantly because: **Overhead costs** (kernel launch, memory transfers) are amortized over larger data sizes The hardware utilization improves as more data is processed More parallelism can be exploited
2. Peak Performance
   The throughput reaches a peak around 2048B-4096B where: The GPU's memory bandwidth is being fully utilized The parallel processing units are working efficiently, The balance between computation and memory access is optimal
3. Decrease/Plateau Phase
   After the peak, throughput starts to plateau or slightly decrease because: Memory bandwidth becomes the bottleneck, Larger messages require more memory transactions Cache misses increase with larger data sizes, Memory latency has a greater impact on overall performance

```plaintext
sha256 speed test
-------------------CPU test--------------------
cpu: 4B               1.65 us         2.43MB/s
cpu: 8B               0.61 us        13.03MB/s
cpu: 16B              0.58 us        27.63MB/s
cpu: 32B              0.58 us        54.79MB/s
cpu: 64B              0.89 us        72.07MB/s
cpu: 128B             1.17 us       109.22MB/s
cpu: 256B             1.77 us       144.63MB/s
cpu: 512B             2.94 us       173.85MB/s
cpu: 1024B            5.28 us       194.01MB/s
cpu: 2048B            9.83 us       208.36MB/s
cpu: 4096B           18.99 us       215.68MB/s
cpu: 8192B           36.78 us       222.70MB/s
cpu: 16384B          72.09 us       227.26MB/s
cpu: 32768B         147.25 us       222.54MB/s
cpu: 65536B         284.82 us       230.09MB/s
cpu: 131072B        568.89 us       230.40MB/s
cpu: 262144B       1145.66 us       228.82MB/s
cpu: 524288B       2278.34 us       230.12MB/s
cpu: 1048576B      4611.85 us       227.37MB/s

---------------gpu one core test----------------
gpu: 4B              24.27 us         0.16MB/s
gpu: 8B              24.26 us         0.33MB/s
gpu: 16B             24.28 us         0.66MB/s
gpu: 32B             24.49 us         1.31MB/s
gpu: 64B             25.49 us         2.51MB/s
gpu: 128B            26.62 us         4.81MB/s
gpu: 256B            29.40 us         8.71MB/s
gpu: 512B            33.41 us        15.32MB/s
gpu: 1024B           42.47 us        24.11MB/s
gpu: 2048B           83.69 us        24.47MB/s
gpu: 4096B          170.44 us        24.03MB/s
gpu: 8192B          340.17 us        24.08MB/s
gpu: 16384B         645.23 us        25.39MB/s
gpu: 32768B        1307.19 us        25.07MB/s
gpu: 65536B        2757.74 us        23.76MB/s
gpu: 131072B       5854.69 us        22.39MB/s
gpu: 262144B      11771.52 us        22.27MB/s
gpu: 524288B      23451.40 us        22.36MB/s
gpu: 1048576B     46758.16 us        22.43MB/s
msg_N = 41984

---------------gpu dp test (82 * 512)----------------
dp 4 B,         147.65 us       1137.43MB/s     0.00 us/hash
dp 8 B,         41.19 us        8154.61MB/s     0.00 us/hash
dp 16 B,        38.96 us        17243.22MB/s    0.00 us/hash
dp 32 B,        42.14 us        31880.02MB/s    0.00 us/hash
dp 64 B,        41.07 us        65429.08MB/s    0.00 us/hash
dp 128 B,       46.54 us        115459.61MB/s   0.00 us/hash
dp 256 B,       56.67 us        189647.70MB/s   0.00 us/hash
dp 512 B,       71.88 us        299051.31MB/s   0.00 us/hash
dp 1024 B,      137.60 us       312439.07MB/s   0.00 us/hash
dp 2048 B,      267.89 us       320969.49MB/s   0.01 us/hash
dp 4096 B,      556.51 us       309008.20MB/s   0.01 us/hash
dp 8192 B,      1260.15 us      272929.07MB/s   0.03 us/hash
dp 16384 B,     2653.84 us      259196.04MB/s   0.06 us/hash
dp 32768 B,     5163.24 us      266447.16MB/s   0.12 us/hash
dp 65536 B,     10385.40 us     264935.72MB/s   0.25 us/hash
dp 131072 B,    20657.88 us     266383.85MB/s   0.49 us/hash
dp 262144 B,    40958.62 us     268706.67MB/s   0.98 us/hash

---------------gpu dp test (256 * 1024)----------------
dp 4 B,         195.22 us       5371.39MB/s     0.00 us/hash
dp 8 B,         196.94 us       10648.52MB/s    0.00 us/hash
dp 16 B,        191.65 us       21885.34MB/s    0.00 us/hash
dp 32 B,        198.35 us       42291.10MB/s    0.00 us/hash
dp 64 B,        195.29 us       85907.48MB/s    0.00 us/hash
dp 128 B,       212.68 us       157769.57MB/s   0.00 us/hash
dp 256 B,       267.81 us       250581.05MB/s   0.00 us/hash
dp 512 B,       383.97 us       349549.00MB/s   0.00 us/hash
dp 1024 B,      1200.65 us      223575.67MB/s   0.00 us/hash
dp 2048 B,      2356.45 us      227830.10MB/s   0.01 us/hash
dp 4096 B,      4787.37 us      224286.32MB/s   0.02 us/hash
dp 8192 B,      8869.97 us      242107.26MB/s   0.03 us/hash
dp 16384 B,     17752.07 us     241941.73MB/s   0.07 us/hash
dp 32768 B,     34830.77 us     246619.16MB/s   0.13 us/hash
dp 65536 B,     70134.67 us     244955.43MB/s   0.27 us/hash
msg_N = 41984

sha256 test
single core check right!
```

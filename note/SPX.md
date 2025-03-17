# SPHINCS-plus

Let us to improve the performance of SPHINCS+ by using the parallelism technique on the _Throughput_ and _Latency_.

## Throughput

Let us to improve the throughput by key point mind **dynamic parallelism**, we main idea is the every kernel function $g_i$ if we use the parallelism number $t_i$, it not means the $t_i$ to the max CUDA thread number, e.g the RTX-4090 have 128sm\*1024 threads, the function get the maximize performance. Here we use the precomputed thread number to maximize efficiency.

### theory analysis for the parallelism

First axiom: the parallelism number $t_i$ is the max CUDA thread number, the performance is the best for the function $g_i$. then we know the signature process including the public key generation, signing, and verifying. Those processes need serial run the function $g_i$. Not the optimal approach is use the parallelism number $t_i$ to the max CUDA thread number.
The performance is not the best for the function $g_i$.

Those have the Adaptive Thread function (AT) $AT:G\rightarrow T$, which maps each function $g_i \in G$ to its optimal thread count $t_i \in T$.

To accurately define this mapping, we can approach it through empirical performance modeling:

1. **Empirical Performance Model**: For each function $g_i$, we model execution time as:

   $T(g_i, t) = \alpha_i + \frac{\beta_i}{t} + \gamma_i \cdot t$

   Where:

   - $\alpha_i$ represents fixed overhead cost
   - $\frac{\beta_i}{t}$ captures the parallel speedup component
   - $\gamma_i \cdot t$ models thread management overhead
   - $t$ is the thread count

2. **Parameter Estimation**: We can estimate $\alpha_i$, $\beta_i$, and $\gamma_i$ by running benchmarks with varying thread counts and performing regression analysis.

3. **Optimal Thread Count**: The optimal thread count $t_i^*$ for function $g_i$ can be derived by finding the minimum of $T(g_i, t)$:

   $t_i^* = \sqrt{\frac{\beta_i}{\gamma_i}}$

4. **Implementation Strategy**: For practical implementation, we can:
   - Perform offline profiling for each key function
   - Build a lookup table mapping functions to their optimal thread counts
   - Apply dynamic thread adjustment based on runtime conditions

### max thread number parallelism

Here is the data parallelism of the **CUSPX**, this way is use the serial version implementation _SPX_ to parallelism signature the message. This way we not see the suit parallelism number.

```shell
n = 16, h = 66, d = 22, b = 6, k = 33, w = 16, len = 35
SLH-DSA-SHA-256-128f
num = 65536
Parameters: n = 16, h = 66, d = 22, a = 6, k = 33, w = 16, len = 35
warming up 1 iter
Running 5 iterations.
multi-keypair data parallelism
number, keypair, sign, verify, keypair per op, Sign per op, verify per op
0, 0.00, 0.00, 0.01, inf, inf, inf
1024, 18.81, 491.78, 52.79, 0.0184, 0.4803, 0.0516
2048, 18.78, 493.26, 53.62, 0.0092, 0.2408, 0.0262
3072, 18.85, 496.30, 54.67, 0.0061, 0.1616, 0.0178
4096, 18.87, 497.48, 55.45, 0.0046, 0.1215, 0.0135
5120, 19.63, 519.82, 58.21, 0.0038, 0.1015, 0.0114
6144, 19.71, 522.65, 59.17, 0.0032, 0.0851, 0.0096
7168, 20.05, 534.00, 60.71, 0.0028, 0.0745, 0.0085
8192, 20.98, 555.32, 62.66, 0.0026, 0.0678, 0.0076
9216, 24.61, 630.45, 74.55, 0.0027, 0.0684, 0.0081
10240, 26.02, 685.09, 79.44, 0.0025, 0.0669, 0.0078
11264, 28.23, 781.13, 86.67, 0.0025, 0.0693, 0.0077
12288, 30.24, 804.35, 93.65, 0.0025, 0.0655, 0.0076
13312, 32.41, 871.84, 100.38, 0.0024, 0.0655, 0.0075
14336, 33.39, 917.53, 106.06, 0.0023, 0.0640, 0.0074
15360, 34.95, 980.39, 112.32, 0.0023, 0.0638, 0.0073
16384, 35.74, 993.34, 116.48, 0.0022, 0.0606, 0.0071
17408, 54.57, 1484.83, 169.30, 0.0031, 0.0853, 0.0097
18432, 54.46, 1486.39, 169.87, 0.0030, 0.0806, 0.0092
19456, 54.53, 1490.36, 171.25, 0.0028, 0.0766, 0.0088
20480, 54.54, 1491.92, 172.24, 0.0027, 0.0728, 0.0084
21504, 55.40, 1514.53, 174.80, 0.0026, 0.0704, 0.0081
22528, 55.45, 1516.74, 176.03, 0.0025, 0.0673, 0.0078
23552, 55.84, 1529.38, 177.29, 0.0024, 0.0649, 0.0075
24576, 56.78, 1550.52, 179.13, 0.0023, 0.0631, 0.0073
25600, 60.39, 1625.98, 191.32, 0.0024, 0.0635, 0.0075
26624, 61.83, 1679.70, 195.97, 0.0023, 0.0631, 0.0074
27648, 64.10, 1776.63, 203.00, 0.0023, 0.0643, 0.0073
28672, 66.06, 1799.14, 209.78, 0.0023, 0.0627, 0.0073
29696, 68.29, 1865.93, 216.24, 0.0023, 0.0628, 0.0073
30720, 69.12, 1909.22, 221.31, 0.0023, 0.0621, 0.0072
31744, 70.69, 1972.32, 227.70, 0.0022, 0.0621, 0.0072
32768, 71.51, 1983.65, 231.13, 0.0022, 0.0605, 0.0071
33792, 90.27, 2476.94, 284.57, 0.0027, 0.0733, 0.0084
34816, 90.33, 2479.44, 285.09, 0.0026, 0.0712, 0.0082
35840, 90.36, 2482.46, 286.10, 0.0025, 0.0693, 0.0080
36864, 90.39, 2483.08, 286.75, 0.0025, 0.0674, 0.0078
37888, 91.16, 2506.08, 289.66, 0.0024, 0.0661, 0.0076
38912, 91.24, 2508.42, 290.55, 0.0023, 0.0645, 0.0075
39936, 91.54, 2520.98, 292.08, 0.0023, 0.0631, 0.0073
40960, 92.52, 2542.16, 293.86, 0.0023, 0.0621, 0.0072
41984, 96.14, 2618.07, 306.35, 0.0023, 0.0624, 0.0073
43008, 97.62, 2671.49, 311.03, 0.0023, 0.0621, 0.0072
44032, 99.75, 2768.66, 317.69, 0.0023, 0.0629, 0.0072
45056, 101.79, 2790.89, 324.63, 0.0023, 0.0619, 0.0072
46080, 104.08, 2858.59, 331.07, 0.0023, 0.0620, 0.0072
47104, 104.88, 2900.90, 336.23, 0.0022, 0.0616, 0.0071
48128, 106.44, 2963.86, 342.58, 0.0022, 0.0616, 0.0071
49152, 107.24, 2976.33, 346.37, 0.0022, 0.0606, 0.0070
50176, 126.02, 3469.04, 399.41, 0.0025, 0.0691, 0.0080
51200, 126.05, 3471.12, 399.83, 0.0025, 0.0678, 0.0078
52224, 126.12, 3473.98, 400.88, 0.0024, 0.0665, 0.0077
53248, 126.12, 3475.01, 401.62, 0.0024, 0.0653, 0.0075
54272, 126.95, 3497.49, 404.40, 0.0023, 0.0644, 0.0075
55296, 127.00, 3499.95, 405.81, 0.0023, 0.0633, 0.0073
56320, 127.27, 3513.86, 406.98, 0.0023, 0.0624, 0.0072
57344, 128.30, 3533.84, 408.66, 0.0022, 0.0616, 0.0071
58368, 131.92, 3609.56, 420.87, 0.0023, 0.0618, 0.0072
59392, 133.33, 3663.55, 425.61, 0.0022, 0.0617, 0.0072
60416, 135.52, 3760.51, 433.41, 0.0022, 0.0622, 0.0072
61440, 137.54, 3782.19, 439.65, 0.0022, 0.0616, 0.0072
62464, 139.76, 3849.74, 445.79, 0.0022, 0.0616, 0.0071
63488, 140.67, 3891.67, 451.00, 0.0022, 0.0613, 0.0071
64512, 142.26, 3955.36, 457.54, 0.0022, 0.0613, 0.0071
65536, 142.93, 3967.49, 460.74, 0.0022, 0.0605, 0.0070

1024, 18.76, 491.92, 52.81, 0.0183, 0.4804, 0.0516
2048, 18.78, 493.27, 53.64, 0.0092, 0.2409, 0.0262
4096, 18.87, 497.61, 55.53, 0.0046, 0.1215, 0.0136
8192, 21.06, 550.72, 62.94, 0.0026, 0.0672, 0.0077
16384, 35.67, 990.66, 115.19, 0.0022, 0.0605, 0.0070
32768, 71.26, 1980.49, 229.81, 0.0022, 0.0604, 0.0070
65536, 142.64, 3960.43, 459.02, 0.0022, 0.0604, 0.0070
```

here we change the block\*thread number for the `keypair`, we have the performance improvement. from the 0.0022 to 0.0017. `blocks, threads: 128 256` from the `blocks, threads: 512 32`.

```shell
n = 16, h = 66, d = 22, b = 6, k = 33, w = 16, len = 35
SLH-DSA-SHA-256-128f
num = 65536
Parameters: n = 16, h = 66, d = 22, a = 6, k = 33, w = 16, len = 35
warming up 1 iter
blocks, threads: 128 256
Running 5 iterations.
multi-keypair data parallelism
number, keypair, sign, verify, keypair per op, Sign per op, verify per op
1024, 26.95, 491.86, 52.81, 0.0263, 0.4803, 0.0516
2048, 27.13, 492.97, 53.59, 0.0132, 0.2407, 0.0262
4096, 27.15, 497.21, 55.47, 0.0066, 0.1214, 0.0135
8192, 27.34, 552.43, 67.35, 0.0033, 0.0674, 0.0082
16384, 37.19, 992.23, 116.28, 0.0023, 0.0606, 0.0071
32768, 56.95, 1985.24, 231.24, 0.0017, 0.0606, 0.0071
65536, 114.10, 3977.45, 460.71, 0.0017, 0.0607, 0.0070
```

use the `blocks, threads: 128 64`, is the 0.0025.

```shell
n = 16, h = 66, d = 22, b = 6, k = 33, w = 16, len = 35
SLH-DSA-SHA-256-128f
num = 65536
Parameters: n = 16, h = 66, d = 22, a = 6, k = 33, w = 16, len = 35
warming up 1 iter
Running 5 iterations.
multi-keypair data parallelism
number, keypair, sign, verify, keypair per op, Sign per op, verify per op
1024, 19.38, 491.95, 52.97, 0.0189, 0.4804, 0.0517
2048, 19.39, 493.33, 54.00, 0.0095, 0.2409, 0.0264
4096, 19.42, 497.56, 56.13, 0.0047, 0.1215, 0.0137
8192, 20.61, 560.05, 64.12, 0.0025, 0.0684, 0.0078
16384, 41.47, 992.06, 117.83, 0.0025, 0.0606, 0.0072
32768, 82.92, 1986.94, 235.27, 0.0025, 0.0606, 0.0072
65536, 166.08, 3977.61, 469.87, 0.0025, 0.0607, 0.0072
```

for max the thread number, we use the `blocks, threads: 128 512`, the performance is 0.0018.

```shell
n = 16, h = 66, d = 22, b = 6, k = 33, w = 16, len = 35
SLH-DSA-SHA-256-128f
num = 65536
Parameters: n = 16, h = 66, d = 22, a = 6, k = 33, w = 16, len = 35
warming up 1 iter
Running 5 iterations.
multi-keypair data parallelism
number, keypair, sign, verify, keypair per op, Sign per op, verify per op
1024, 40.39, 491.81, 52.80, 0.0394, 0.4803, 0.0516
2048, 40.36, 492.99, 53.60, 0.0197, 0.2407, 0.0262
4096, 40.62, 497.30, 55.45, 0.0099, 0.1214, 0.0135
8192, 40.69, 566.85, 63.33, 0.0050, 0.0692, 0.0077
16384, 42.08, 990.73, 115.17, 0.0026, 0.0605, 0.0070
32768, 68.37, 1981.43, 229.74, 0.0021, 0.0605, 0.0070
65536, 118.62, 3959.67, 459.46, 0.0018, 0.0604, 0.0070
```

## Latency

The maximin latency usually talked is the time to sign a message. As propose on the **CUSPX**, it used the three levels of parallelism to reduce the latency. The first level is the _tree-based parallelism_, the second level is the _node-based parallelism_, and the third level is the _WOTS-based parallelism_. Addition, we have the fourth level of parallelism, the _hash-based parallelism_. The benchmark of the **CUSPX** is shown in the following:

```shell
n = 24, h = 66, d = 22, b = 8, k = 33, w = 16, len = 51
SLH-DSA-SHA-256-192f
Warming up 40 iterations.
Running 200 iterations.

PKGEN 0 ..                31.382 ms (0.031 sec)
PKGEN 2 ..           blocks, threads: 13 * 32   all = 416       max = 16384           3.844 ms (0.004 sec)
PKGEN 2+dynamic ..           blocks, threads: 13 * 32   all = 416       max = 16384           3.822 ms (0.004 sec)
PKGEN 2+3 ..         blocks, threads: 13 * 32   all = 416       max = 16384           0.220 ms (0.000 sec)
PKGEN 2+3 one thead merger..         blocks, threads: 13 * 32   all = 416       max = 16384           0.245 ms (0.000 sec)
PKGEN 2+3 dynamic ..         blocks, threads: 13 * 32   all = 416       max = 16384           0.221 ms (0.000 sec)
PKGEN 2+3 dynamic + gpu optimize ..         blocks, threads: 13 * 32   all = 416       max = 16384           0.197 ms (0.000 sec)
Signing 0 ..             828.356 ms (0.828 sec)
Signing 1 ..         blocks, threads: 281 * 32  all = 8992      max = 16384          38.450 ms (0.038 sec)
Signing 1+2 ..       blocks, threads: 281 * 32  all = 8992      max = 16384           8.511 ms (0.009 sec)
Signing 1+2+3 ..     blocks, threads: 281 * 32  all = 8992      max = 16384           0.820 ms (0.001 sec)
Verifying 0 ..            43.517 ms (0.044 sec)
Verifying 2+3 ..     blocks, threads: 1 * 51    all = 51        max = 52224           3.474 ms (0.003 sec)
```

here we see the `dev_ap_treehash_wots_2` use the `branch_para` to limit the number of the thread on the nodes merger. so we use the thread to divide two to dynamic strategy to improve the performance, but the a litter improve from the `3.844 ms` to `3.822 ms`, so the main delay is on the other part of the code.

### The tree hash parallelism

Tree hash parallelism is a critical optimization technique in SPHINCS+. The recent optimizations to the `dev_ap_treehash_wots_23` function demonstrate significant performance improvements, reducing execution time from 0.221 ms to 0.197 ms. These optimizations include:

1. **Shared Memory Usage**: Replacing global memory access with shared memory for authentication path storage reduces memory latency and improves throughput.

2. **Memory Access Pattern Optimization**:

   - Implementing coalesced memory access patterns for WOTS chains
   - Direct access optimizations for thash input
   - Minimizing redundant memory operations during tree traversal

3. **Thread Synchronization Reduction**:

   - Consolidating synchronization points to minimize thread waiting time
   - Using a single sync point between tree levels instead of multiple syncs

4. **Efficient Workload Distribution**:

   - Dynamic thread allocation based on available resources
   - Optimized stride patterns for processing multiple WOTS chains per thread

5. **Computation Elimination**:
   - Pre-computing leaf and chain indices to avoid redundant calculations
   - Setting addressing components once per operation
   - Eliminating unnecessary temporary buffers

These optimizations collectively demonstrate how tree-based parallelism can be further enhanced through careful memory management and thread coordination, resulting in a 10.9% performance improvement for the treehash operation.

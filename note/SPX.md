# SPHINCS-plus

Let us to improve the performance of SPHINCS+ by using the parallelism technique on the _Throughput_ and _Latency_.

## Throughput

Let us to improve the throughput by key point mind **dynamic parallelism**, we main idea is the every kernel function 

here is the data parallelism of the **CUSPX**:

```shell
n = 16, h = 66, d = 22, b = 6, k = 33, w = 16, len = 35
SLH-DSA-SHA-256-128f
num = 7000
Parameters: n = 16, h = 66, d = 22, a = 6, k = 33, w = 16, len = 35
warming up 1 iter
Running 5 iterations.
multi-keypair data parallelism
number, keypair, sign, verify,Sign per op
0, 0.00, 0.00, 0.01, inf
1024, 18.76, 491.85, 52.80, 0.4803
2048, 18.77, 493.00, 53.61, 0.2407
3072, 18.83, 495.92, 54.67, 0.1614
4096, 18.86, 497.23, 55.48, 0.1214
5120, 19.61, 519.46, 58.17, 0.1015
6144, 19.68, 521.81, 59.13, 0.0849
7168, 20.04, 502.99, 30.05, 0.0702
8192, 21.24, 525.28, 30.52, 0.0641
9216, 24.96, 636.50, 35.30, 0.0691
10240, 26.93, 686.20, 40.04, 0.0670
11264, 29.69, 737.06, 42.66, 0.0654
12288, 29.37, 748.48, 43.41, 0.0609
13312, 32.04, 816.82, 46.42, 0.0614
14336, 33.19, 869.80, 50.38, 0.0607
15360, 34.94, 933.13, 51.63, 0.0608
16384, 35.60, 942.14, 53.95, 0.0575
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

# SPHINCS-plus

Let us to improve the performance of SPHINCS+ by using the parallelism technique on the _Throughput_ and _Latency_.

## Throughput

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
Signing 0 ..             828.356 ms (0.828 sec)
Signing 1 ..         blocks, threads: 281 * 32  all = 8992      max = 16384          38.450 ms (0.038 sec)
Signing 1+2 ..       blocks, threads: 281 * 32  all = 8992      max = 16384           8.511 ms (0.009 sec)
Signing 1+2+3 ..     blocks, threads: 281 * 32  all = 8992      max = 16384           0.820 ms (0.001 sec)
Verifying 0 ..            43.517 ms (0.044 sec)
Verifying 2+3 ..     blocks, threads: 1 * 51    all = 51        max = 52224           3.474 ms (0.003 sec)
```

here we see the `dev_ap_treehash_wots_2` use the `branch_para` to limit the number of the thread on the nodes merger. so we use the thread to divide two to dynamic strategy to improve the performance, but the a litter improve from the `3.844 ms` to `3.822 ms`, so the main delay is on the other part of the code.

### The tree-based parallelism

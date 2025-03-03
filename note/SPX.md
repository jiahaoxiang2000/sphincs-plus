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

PKGEN 0 ..                32.210 ms (0.032 sec)
PKGEN 2 ..           blocks, threads: 13 * 32   all = 416       max = 16384           3.823 ms (0.004 sec)
PKGEN 2+3 ..         blocks, threads: 13 * 32   all = 416       max = 16384           0.219 ms (0.000 sec)
Signing 0 ..             826.409 ms (0.826 sec)
Signing 1 ..         blocks, threads: 281 * 32  all = 8992      max = 16384          38.380 ms (0.038 sec)
Signing 1+2 ..       blocks, threads: 281 * 32  all = 8992      max = 16384           8.472 ms (0.008 sec)
Signing 1+2+3 ..     blocks, threads: 281 * 32  all = 8992      max = 16384           0.834 ms (0.001 sec)
Verifying 0 ..            43.526 ms (0.044 sec)
Verifying 2+3 ..     blocks, threads: 1 * 51    all = 51        max = 52224           3.475 ms (0.003 sec)
```

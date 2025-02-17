# CUDA to implement parallel computing

## SHA256 speed test

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

sha256 test
single core check right!
```

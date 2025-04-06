# Mind of the Paper Experiment

## Goal

Our paper's goal is to make SPX (SLH-DSA) more efficient and faster on GPU platforms. The main metric is the throughput of SLH-DSA.

## Approach

Our paper's main idea is Thread-Adaptation, where we adjust the number of threads for each kernel function on independent tasks. Having a specific number of threads optimized for each kernel function improves efficiency.

Following this approach, we analyze SLH-DSA from top to bottom:

1. At the top component level, we propose Adaptive Thread Allocation (**ATA**) to optimize SLH-DSA signature generation, verification, and keypair generation.

2. For lower-level optimization, we implement Function-Level Parallelism (**FLP**) to improve kernel functions that haven't been optimized yet.

### ATA

For our Adaptive Thread Allocation (ATA) approach, we modified the functions `face_mdp_crypto_sign_keypair`, `face_mdp_crypto_sign`, and `face_mdp_crypto_sign_open` in the `test/dp_benchmark.cu` file. Instead of using the maximum thread count or a constant thread count, we implemented a dynamic thread allocation system.

We modeled the relationship between thread count and performance using an **Empirical Performance Model**. For each function $g_i$, we express the execution time as:

$$T(g_i, t) = \alpha_i + \frac{\beta_i}{t} + \gamma_i \cdot t$$

Where:

- $\alpha_i$ represents the fixed overhead cost
- $\frac{\beta_i}{t}$ captures the parallel speedup component
- $\gamma_i \cdot t$ models the thread management overhead
- $t$ is the thread count

Using this approach, we achieved up to 20% improvement in maximum throughput for SLH-DSA.

### FLP

TODO: add the code diff for FLP

## Experiments

### Thread allocation efficiency

We tested 80 different combinations of block and thread numbers on three key functions. All data was collected for [keypair](../data/kaypair-32768.csv), [sign](../data/sign-32768.csv), and [verify](../data/verify-32768.csv) operations.

Based on the experimental data, we analyzed the theoretical model for our [Adaptive Thread Allocation](#ata) approach. This analysis resulted in the diagram titled _"Performance variation with thread allocation for key SLH-DSA operations"_. The diagram shows that our optimized thread allocation (indicated by markers) consistently approximates the empirical performance minimum, validating our theoretical model.

Additionally, we extracted the model parameters ($\alpha$, $\beta$, $\gamma$) for each operation by curve-fitting our experimental data. These parameters reveal important insights about each function's behavior:

| Operation | $\alpha$ (fixed overhead) | $\beta$ (parallelization factor) | $\gamma$ (thread overhead) |
| --------- | ------------------------: | -------------------------------: | -------------------------: |
| Keypair   |                     value |                            value |                      value |
| Sign      |                     value |                            value |                      value |
| Verify    |                     value |                            value |                      value |

The differences in these parameters explain why each operation benefits from different thread allocations. For instance, operations with higher $\gamma$ values show more performance degradation with excessive threads, while those with higher $\beta$ values benefit more from increased parallelization.

### Comparative performance analysis

We compared our Adaptive Thread Allocation (ATA) approach against three baseline thread allocation strategies:

- **Maximum Threads (origin)**: Using the maximum available threads for all operations
- **Fixed Optimal**: Using a single thread count optimized for average performance
- **Heuristic-based (ATA)**: Using a simple heuristic based on operation complexity

TODO: test

### Scalability analysis

We further validated our approach by testing scalability across different problem sizes. The SLH-DSA on SPX_128F SPX_128S, SPX_192S, SPX_192F, SPX_256S, and SPX_256F.

TODO: test

### energy efficiency analysis

TODO: not known how to test

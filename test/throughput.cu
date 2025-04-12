// #define _POSIX_C_SOURCE 199309L

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "api.h"
#include "common.h"
#include "fors.h"
#include "params.h"
#include "rng.h"
#include "wots.h"

#define SPX_MLEN 32
#define NTESTS 5

// multi-keypair is tested only in paper

#include "all_option.h"

// Function to run performance test and return metrics
double run_perf_test(int num_tasks, int blocks, int threads, int operation, u8* pk, u8* sk, u8* m,
                     u8* sm, u8* mout, unsigned long long* smlen, unsigned long long* mlen) {
    g_result = 0;
    for (int j = 0; j < NTESTS; j++) {
        switch (operation) {
        case 0: // Keypair
            face_mdp_crypto_sign_keypair(pk, sk, num_tasks, blocks, threads);
            break;
        case 1: // Sign
            face_mdp_crypto_sign(sm, smlen, m, SPX_MLEN, sk, num_tasks, blocks, threads);
            break;
        case 2: // Verify
            face_mdp_crypto_sign_open(mout, mlen, sm, *smlen, pk, num_tasks, blocks, threads);
            break;
        }
    }
    return g_result / NTESTS / 1e3; // convert to ms
}

int main(int argc, char** argv) {
    /* Make stdout buffer more responsive. */
    setbuf(stdout, NULL);

    int num = 32768;

    if (argv[1] != NULL) num = atoi(argv[1]);

    u8 *pk, *sk;
    u8 *m, *sm, *mout;

    CHECK(cudaMallocHost(&pk, SPX_PK_BYTES * num));
    CHECK(cudaMallocHost(&sk, SPX_SK_BYTES * num));
    CHECK(cudaMallocHost(&m, SPX_MLEN * num));
    CHECK(cudaMallocHost(&sm, (SPX_BYTES + SPX_MLEN) * num));
    CHECK(cudaMallocHost(&mout, SPX_MLEN * num));

    unsigned long long smlen;
    unsigned long long mlen;

    randombytes(m, SPX_MLEN * num);

    show_para();
    printf("num = %d\n", num);
    printf("Parameters: n = %d, h = %d, d = %d, a = %d, k = %d, w = %d, len = %d\n", SPX_N,
           SPX_FULL_HEIGHT, SPX_D, SPX_FORS_HEIGHT, SPX_FORS_TREES, SPX_WOTS_W, SPX_WOTS_LEN);

    printf("warming up 1 iter\n");
    for (int i = 0; i < 1; i++) {
        face_mdp_crypto_sign_keypair(pk, sk, num, 512, 32);
        face_mdp_crypto_sign(sm, &smlen, m, SPX_MLEN, sk, num, 512, 32);
        face_mdp_crypto_sign_open(mout, &mlen, sm, smlen, pk, num, 512, 32);
    }
    printf("Running %d iterations.\n", NTESTS);

    // Test with fixed number of keypairs (32768) and different block/thread configurations
    int test_num = num;

    // Define original and optimized configurations
    int original_blocks = 512;
    int original_threads = 32;

    // Optimal configurations from parameter.csv
    int optimal_blocks_kg = 128;
    int optimal_threads_kg = 256;
    int optimal_blocks_sign = 160;
    int optimal_threads_sign = 256;
    int optimal_blocks_verify = 128;
    int optimal_threads_verify = 256;

    // Print CSV header
    printf("\nPerformance Comparison (CSV format)\n");
    printf(
        "Configuration,KG Latency (ms),Sign Latency (ms),Verify Latency (ms),KG Throughput "
        "(tasks/sec),Sign Throughput (tasks/sec),Verify Throughput (tasks/sec)\n");

    // Test original configuration (512 blocks, 32 threads)
    double kg_latency_orig = run_perf_test(test_num, original_blocks, original_threads, 0, pk, sk,
                                           m, sm, mout, &smlen, &mlen);
    double sign_latency_orig = run_perf_test(test_num, original_blocks, original_threads, 1, pk, sk,
                                             m, sm, mout, &smlen, &mlen);
    double verify_latency_orig = run_perf_test(test_num, original_blocks, original_threads, 2, pk,
                                               sk, m, sm, mout, &smlen, &mlen);

    // much round run
    int original_round_number = test_num / (original_blocks * original_threads) + 1;
    kg_latency_orig = kg_latency_orig / original_round_number;
    sign_latency_orig = sign_latency_orig / original_round_number;
    verify_latency_orig = verify_latency_orig / original_round_number;
    double kg_throughput_orig = test_num / (kg_latency_orig / 1000.0);
    double sign_throughput_orig = test_num / (sign_latency_orig / 1000.0);
    double verify_throughput_orig = test_num / (verify_latency_orig / 1000.0);

    printf("Original (512x32),%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n", kg_latency_orig, sign_latency_orig,
           verify_latency_orig, kg_throughput_orig, sign_throughput_orig, verify_throughput_orig);

    // Test optimized configuration from parameter.csv
    double kg_latency_opt = run_perf_test(test_num, optimal_blocks_kg, optimal_threads_kg, 0, pk,
                                          sk, m, sm, mout, &smlen, &mlen);
    double sign_latency_opt = run_perf_test(test_num, optimal_blocks_sign, optimal_threads_sign, 1,
                                            pk, sk, m, sm, mout, &smlen, &mlen);
    double verify_latency_opt
        = run_perf_test(test_num, optimal_blocks_verify, optimal_threads_verify, 2, pk, sk, m, sm,
                        mout, &smlen, &mlen);

    // Calculate round numbers for optimized configurations
    int kg_round_number = test_num / (optimal_blocks_kg * optimal_threads_kg) + 1;
    int sign_round_number = test_num / (optimal_blocks_sign * optimal_threads_sign) + 1;
    int verify_round_number = test_num / (optimal_blocks_verify * optimal_threads_verify) + 1;

    // Adjust latency by round number
    kg_latency_opt = kg_latency_opt / original_round_number;
    sign_latency_opt = sign_latency_opt / original_round_number;
    verify_latency_opt = verify_latency_opt / original_round_number;

    double kg_throughput_opt = test_num / (kg_latency_opt / 1000.0);
    double sign_throughput_opt = test_num / (sign_latency_opt / 1000.0);
    double verify_throughput_opt = test_num / (verify_latency_opt / 1000.0);

    printf("Optimized,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n", kg_latency_opt, sign_latency_opt,
           verify_latency_opt, kg_throughput_opt, sign_throughput_opt, verify_throughput_opt);

    // Calculate improvement percentage
    double kg_improvement = (kg_latency_orig - kg_latency_opt) / kg_latency_orig * 100.0;
    double sign_improvement = (sign_latency_orig - sign_latency_opt) / sign_latency_orig * 100.0;
    double verify_improvement
        = (verify_latency_orig - verify_latency_opt) / verify_latency_orig * 100.0;

    printf("\nImprovement Percentage (%%)\n");
    printf("KG: %.2f%%, Sign: %.2f%%, Verify: %.2f%%\n", kg_improvement, sign_improvement,
           verify_improvement);

    CHECK(cudaFreeHost(pk));
    CHECK(cudaFreeHost(sk));
    CHECK(cudaFreeHost(m));
    CHECK(cudaFreeHost(sm));
    CHECK(cudaFreeHost(mout));

    return 0;
} // main

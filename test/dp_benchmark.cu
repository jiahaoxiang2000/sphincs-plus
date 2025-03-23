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

#define MEASURE_WHOLE(TEXT, MUL, FNCALL)                                                           \
    printf(TEXT);                                                                                  \
    g_result = 0;                                                                                  \
    g_count = 0;                                                                                   \
    for (int i = 0; i < MUL; i++)                                                                  \
        FNCALL;                                                                                    \
    printf("whole: %11.2lf ms (%2.2lf sec)\n", g_result / MUL / 1e3, g_result / MUL / 1e6);

#define MEASURE_INNER(TEXT, MUL, FNCALL)                                                           \
    printf(TEXT);                                                                                  \
    g_inner_result = 0;                                                                            \
    g_count = 0;                                                                                   \
    for (int i = 0; i < MUL; i++)                                                                  \
        FNCALL;                                                                                    \
    printf("inner: %11.2lf ms (%2.2lf sec)\n", g_inner_result / MUL / 1e3,                         \
           g_inner_result / MUL / 1e6);

int main(int argc, char** argv) {
    /* Make stdout buffer more responsive. */
    setbuf(stdout, NULL);

    int num = 65536;

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
        // face_mdp_crypto_sign(sm, &smlen, m, SPX_MLEN, sk, num);
        // face_mdp_crypto_sign_open(mout, &mlen, sm, smlen, pk, num);
    }
    printf("Running %d iterations.\n", NTESTS);

    printf("multi-keypair data parallelism\n");
    printf("number, keypair, sign, verify, keypair per op, Sign per op, verify per op\n");
    for (int i = 1024; i <= 65536; i = i * 2) {
        double t1, t2, t3;
        g_result = 0;
        for (int j = 0; j < NTESTS; j++)
            face_mdp_crypto_sign_keypair(pk, sk, i, 512, 32);
        t1 = g_result / NTESTS / 1e3;
        g_result = 0;
        printf("%d, %.2lf, %.2lf, %.2lf, %.4lf, %.4lf, %.4lf\n", i, t1, t2, t3, t1 / i, t2 / i,
               t3 / i);
    }

    CHECK(cudaFreeHost(pk));
    CHECK(cudaFreeHost(sk));
    CHECK(cudaFreeHost(m));
    CHECK(cudaFreeHost(sm));
    CHECK(cudaFreeHost(mout));

    return 0;
} // main

#include <iostream>
#include <stdint.h>
#include <string.h>
#include <time.h>
using namespace std;

#include "address.h"
#include "all_option.h"
#include "common.h"
#include "fors.h"
#include "hash.h"
#include "params.h"
#include "thash.h"
#include "utils.h"
#include "wots.h"

// Function declarations from fors.cu
extern void face_fors_sign(unsigned char* sig, unsigned char* pk, const unsigned char* msg,
                           const unsigned char* sk_seed, const unsigned char* pub_seed,
                           const uint32_t fors_addr[8], uint32_t loop_num);

// Function declarations from wots.cu
extern void face_wots_sign(unsigned char* sig, const unsigned char* msg,
                           const unsigned char* sk_seed, const unsigned char* pub_seed,
                           uint32_t addr[8], uint32_t loop_num);

// Reset global result variable before each measurement
extern double g_result;

#define NTESTS 10

double measure_fors_sign() {
    unsigned char sig[SPX_FORS_BYTES];
    unsigned char pk[SPX_FORS_PK_BYTES];
    unsigned char msg[SPX_FORS_MSG_BYTES];
    unsigned char sk_seed[SPX_N];
    unsigned char pub_seed[SPX_N];
    uint32_t fors_addr[8] = {0};

    // Initialize test data
    memset(sig, 0, sizeof(sig));
    memset(pk, 0, sizeof(pk));
    memset(msg, 0xAA, sizeof(msg));
    memset(sk_seed, 0xBB, sizeof(sk_seed));
    memset(pub_seed, 0xCC, sizeof(pub_seed));

    g_result = 0; // Reset global result

    // Run multiple iterations for more accurate measurement
    for (int i = 0; i < NTESTS; i++) {
        face_fors_sign(sig, pk, msg, sk_seed, pub_seed, fors_addr, 1);
    }

    // Return average time in milliseconds
    return g_result / NTESTS / 1000.0;
}

double measure_wots_sign() {
    unsigned char sig[SPX_WOTS_BYTES];
    unsigned char msg[SPX_N];
    unsigned char sk_seed[SPX_N];
    unsigned char pub_seed[SPX_N];
    uint32_t addr[8] = {0};

    // Initialize test data
    memset(sig, 0, sizeof(sig));
    memset(msg, 0xDD, sizeof(msg));
    memset(sk_seed, 0xEE, sizeof(sk_seed));
    memset(pub_seed, 0xFF, sizeof(pub_seed));

    g_result = 0; // Reset global result

    // Run multiple iterations for more accurate measurement
    for (int i = 0; i < NTESTS; i++) {
        face_wots_sign(sig, msg, sk_seed, pub_seed, addr, 1);
    }

    // Return average time in milliseconds
    return g_result / NTESTS / 1000.0;
}

int main() {
    /* Make stdout buffer more responsive. */
    setbuf(stdout, NULL);

    show_para();
    printf("Parameters: n = %d, h = %d, d = %d, a = %d, k = %d, w = %d, len = %d\n", SPX_N,
           SPX_FULL_HEIGHT, SPX_D, SPX_FORS_HEIGHT, SPX_FORS_TREES, SPX_WOTS_W, SPX_WOTS_LEN);

    printf("Running %d iterations for each function and reporting average.\n", NTESTS);
    printf("------------------------------------------------------------------\n");

    // Measure FORS signing latency
    double fors_time = measure_fors_sign();
    printf("face_fors_sign latency: %.3f ms\n", fors_time);

    // Measure WOTS signing latency
    double wots_time = measure_wots_sign();
    printf("face_wots_sign latency: %.3f ms\n", wots_time);

    printf("------------------------------------------------------------------\n");
    printf("FORS/WOTS signing time ratio: %.2f\n", fors_time / wots_time);

    return 0;
}

#include "common.h"
#include "sha256.h"

static unsigned long long cpucycles(void) {
    unsigned long long result;
    __asm volatile(".byte 15;.byte 49;shlq $32,%%rdx;orq %%rdx,%%rax" : "=a"(result)::"%rdx");

    return result;
} // cpucycles

void sha2_speed_test();
void sha2_validity_test();

int main(int argc, char** argv) {
    sha2_speed_test();
    // sha2_validity_test();

    return 0;
} // main

void sha2_speed_test() {
    struct timespec start, stop;
    double result;

    u64 hash_msg_bytes = 1024 * 1024 * 1024; // whole data

    hash_msg_bytes *= 16; // 16 GB
    u32 msg_num = 1024 * 1024;
    u8 *d, *md, *gpu_md, *gpu_para_md;

    CHECK(cudaMallocHost(&d, hash_msg_bytes));
    CHECK(cudaMallocHost(&md, 32));
    CHECK(cudaMallocHost(&gpu_md, 32));
    CHECK(cudaMallocHost(&gpu_para_md, 32 * msg_num));
    for (u64 i = 0; i < hash_msg_bytes; i++)
        d[i] = 2;

    printf("\nsha256 speed test\n");

    // printf("-------------------CPU test--------------------\n");
    // for (int i = 0; i < 10; i++) // warm up
    //     sha256(md, d, 1024);
    // for (int i = 1; i < 20; i++) {
    //     int msg_size = (2 << i);
    //     clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &start);
    //     sha256(md, d, msg_size);
    //     clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &stop);
    //     result = (stop.tv_sec - start.tv_sec) * 1e6 + (stop.tv_nsec - start.tv_nsec) / 1e3;
    //     printf("cpu: %dB \t%10.2lf us\t%10.2lfMB/s\n", msg_size, result, msg_size / result);
    // }

    // printf("\n");
    // printf("---------------gpu one core test----------------\n");
    // // First call to warm up the GPU
    // face_sha256(gpu_md, d, 1024, 1000); // 1000 iterations for warm-up

    // int iter = 100; // Number of measurements to average
    // for (int i = 1; i < 20; i++) {
    //     int msg_size = (2 << i);
    //     face_sha256(gpu_md, d, msg_size, iter);
    //     // Divide g_result by iter to get average time per operation
    //     printf("gpu: %dB \t%10.2lf us\t%10.2lfMB/s\n", msg_size, g_result / iter,
    //            msg_size / g_result * iter);
    // }

    printf("\n");
    printf("---------------gpu warp parallel test----------------\n");
    // First call to warm up the GPU
    face_warp_sha256(gpu_md, d, 1024, 1000); // 1000 iterations for warm-up

    int iter = 100; // Number of measurements to average
    for (int i = 1; i < 20; i++) {
        int msg_size = (2 << i);
        face_warp_sha256(gpu_md, d, msg_size, iter);
        // Divide g_result by iter to get average time per operation
        printf("warp: %dB \t%10.2lf us\t%10.2lfMB/s\n", msg_size, g_result / iter,
               msg_size / g_result * iter);
    }

    // printf("\n");
    // printf("---------------gpu dp test (128 * 256)----------------\n");
    // msg_num = 128 * 256;
    // for (int i = 1; i < 20; i++) {
    //     int msg_size = (2 << i);
    //     if ((u64) msg_size * msg_num > hash_msg_bytes) break;
    //     face_dp_sha256((const u8*) d, gpu_para_md, msg_size, msg_num, 128, 256);
    //     double per_hash_time = g_result / msg_num;
    //     printf("dp %d B, \t%.2lf us\t%.2lfMB/s\t%.2lf us/hash\n", msg_size, g_result,
    //            (double) msg_size * msg_num / g_result, per_hash_time);
    // }

    printf("\n");
    printf("---------------gpu dp warp test (128 * 256)----------------\n");
    msg_num = 128 * 256; // Use smaller batch due to 1 warp per block
    for (int i = 1; i < 20; i++) {
        int msg_size = (2 << i);
        if ((u64) msg_size * msg_num > hash_msg_bytes) break;
        face_dp_warp_sha256((const u8*) d, gpu_para_md, msg_size, msg_num);
        double per_hash_time = g_result / msg_num;
        printf("dp warp %d B, \t%.2lf us\t%.2lfMB/s\t%.2lf us/hash\n", msg_size, g_result,
               (double) msg_size * msg_num / g_result, per_hash_time);
    }

    printf("\n");
    printf("---------------gpu dp warp test (128 * 1024)----------------\n");
    msg_num = 128 * 1024; // Use smaller batch due to 1 warp per block
    for (int i = 1; i < 20; i++) {
        int msg_size = (2 << i);
        if ((u64) msg_size * msg_num > hash_msg_bytes) break;
        face_dp_warp_sha256((const u8*) d, gpu_para_md, msg_size, msg_num);
        double per_hash_time = g_result / msg_num;
        printf("dp warp %d B, \t%.2lf us\t%.2lfMB/s\t%.2lf us/hash\n", msg_size, g_result,
               (double) msg_size * msg_num / g_result, per_hash_time);
    }

    printf("\n");
    printf("---------------gpu dp test (128 * 128)----------------\n");
    msg_num = 128 * 128; // Try larger batch
    for (int i = 1; i < 20; i++) {
        int msg_size = (2 << i);
        if ((u64) msg_size * msg_num > hash_msg_bytes) break;
        face_dp_sha256((const u8*) d, gpu_para_md, msg_size, msg_num, 128, 128);
        double per_hash_time = g_result / msg_num;
        printf("dp %d B, \t%.2lf us\t%.2lfMB/s\t%.2lf us/hash\n", msg_size, g_result,
               (double) msg_size * msg_num / g_result, per_hash_time);
    }

    // printf("\n");
    // printf("---------------gpu msdp test (128 * 256 * 8)----------------\n");
    // msg_num = 128 * 256;
    // for (int i = 1; i < 20; i++) {
    //     int msg_size = (2 << i);
    //     if ((u64) msg_size * msg_num > hash_msg_bytes) break;
    //     face_msdp_sha256((const u8*) d, gpu_para_md, msg_size, msg_num, 128, 256);
    //     double per_hash_time = g_result / msg_num;
    //     printf("msdp %d B, \t%.2lf us\t%.2lfMB/s\t%.2lf us/hash\n", msg_size, g_result,
    //            (double) msg_size * msg_num / g_result, per_hash_time);
    // }

    // printf("\n");
    // printf("---------------gpu msdp test (128 * 1024 * 8)----------------\n");
    // msg_num = 128 * 1024; // Try larger batch
    // for (int i = 1; i < 20; i++) {
    //     int msg_size = (2 << i);
    //     if ((u64) msg_size * msg_num > hash_msg_bytes) break;
    //     face_msdp_sha256((const u8*) d, gpu_para_md, msg_size, msg_num, 128, 1024);
    //     double per_hash_time = g_result / msg_num;
    //     printf("msdp %d B, \t%.2lf us\t%.2lfMB/s\t%.2lf us/hash\n", msg_size, g_result,
    //            (double) msg_size * msg_num / g_result, per_hash_time);
    // }

} // sha2_speed_test

void sha2_validity_test() {
    struct timespec start, stop;
    double result;

    u32 se_msg_B = 1024 * 1024;
    u32 s_msg_B = 32;                 // single message size
    u32 p_msg_B = 82 * 512 * s_msg_B; // for parallel test
    u32 msg_N = p_msg_B / s_msg_B;

    printf("msg_N = %d\n", msg_N);
    u8 *d, *cpu_md, *gpu_md, *cpu_para_md, *gpu_para_md;

    int right;

    CHECK(cudaMallocHost(&d, p_msg_B));
    CHECK(cudaMallocHost(&cpu_md, 32));
    CHECK(cudaMallocHost(&gpu_md, 32));
    CHECK(cudaMallocHost(&cpu_para_md, 32 * msg_N));
    CHECK(cudaMallocHost(&gpu_para_md, 32 * msg_N));
    for (int i = 0; i < p_msg_B; i++)
        d[i] = i;
    for (int i = 0; i < p_msg_B; i += 7)
        d[i] += i;

    printf("\nsha256 test\n");
    cout << flush;

    sha256(cpu_md, d, se_msg_B);
    face_sha256(gpu_md, d, se_msg_B, 1);

    right = 1;
    for (int j = 0; j < 32; j++) {
        if (cpu_md[j] != gpu_md[j]) {
            right = 0;
            break;
        }
    }
    if (right == 1)
        printf("single core check right!\n");
    else
        printf("single core check wrong!\n");

    // Add warp parallel test
    face_warp_sha256(gpu_md, d, se_msg_B, 1);

    right = 1;
    for (int j = 0; j < 32; j++) {
        if (cpu_md[j] != gpu_md[j]) {
            right = 0;
            printf("Mismatch at byte %d: CPU=%02x, GPU Warp=%02x\n", j, cpu_md[j], gpu_md[j]);
            break;
        }
    }
    if (right == 1)
        printf("Warp parallel check right!\n");
    else
        printf("Warp parallel check wrong!\n");

    /* parallel test */
    for (int j = 0; j < msg_N; j++) {
        sha256(cpu_para_md + j * 32, d + j * s_msg_B, s_msg_B);
    }

    face_dp_sha256((const u8*) d, gpu_para_md, s_msg_B, msg_N, 82, 512);

    right = 1;
    for (int j = 0; j < msg_N; j++) {
        for (int k = 0; k < 32; k++) {
            if (cpu_para_md[j * 32 + k] != gpu_para_md[j * 32 + k]) {
                right = 0;
                printf("Mismatch at message %d, byte %d: CPU=%02x, GPU=%02x\n", j, k,
                       cpu_para_md[j * 32 + k], gpu_para_md[j * 32 + k]);
                break;
            }
        }
        if (!right) break;
    }
    if (right == 1)
        printf("Data parallel SHA256 check right!\n");
    else
        printf("Data parallel SHA256 check wrong!\n");

    /* data parallel warp test */
    for (int j = 0; j < msg_N; j++) {
        sha256(cpu_para_md + j * 32, d + j * s_msg_B, s_msg_B);
    }

    face_dp_warp_sha256((const u8*) d, gpu_para_md, s_msg_B, msg_N);

    right = 1;
    for (int j = 0; j < msg_N; j++) {
        for (int k = 0; k < 32; k++) {
            if (cpu_para_md[j * 32 + k] != gpu_para_md[j * 32 + k]) {
                right = 0;
                printf("Mismatch at message %d, byte %d: CPU=%02x, GPU Warp=%02x\n", j, k,
                       cpu_para_md[j * 32 + k], gpu_para_md[j * 32 + k]);
                break;
            }
        }
        if (!right) break;
    }
    if (right == 1)
        printf("Data parallel warp SHA256 check right!\n");
    else
        printf("Data parallel warp SHA256 check wrong!\n");

    /* multi-stream parallel test */
    for (int j = 0; j < msg_N; j++) {
        sha256(cpu_para_md + j * 32, d + j * s_msg_B, s_msg_B);
    }

    face_msdp_sha256((const u8*) d, gpu_para_md, s_msg_B, msg_N, 82, 512);

    right = 1;
    for (int j = 0; j < msg_N; j++) {
        for (int k = 0; k < 32; k++) {
            if (cpu_para_md[j * 32 + k] != gpu_para_md[j * 32 + k]) {
                right = 0;
                printf("Mismatch at message %d, byte %d: CPU=%02x, GPU=%02x\n", j, k,
                       cpu_para_md[j * 32 + k], gpu_para_md[j * 32 + k]);
                break;
            }
        }
        if (!right) break;
    }
    if (right == 1)
        printf("Multi-stream SHA256 check right!\n");
    else
        printf("Multi-stream SHA256 check wrong!\n");

} // sha2_validity_test

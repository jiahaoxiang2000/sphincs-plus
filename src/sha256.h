#ifndef SPX_SHA256_H
#define SPX_SHA256_H

#define SPX_SHA256_BLOCK_BYTES 64
#define SPX_SHA256_OUTPUT_BYTES 32 /* This does not necessarily equal SPX_N */

#if SPX_SHA256_OUTPUT_BYTES < SPX_N
#error Linking against SHA-256 with N larger than 32 bytes is not supported
#endif /* if SPX_SHA256_OUTPUT_BYTES < SPX_N */

#define SPX_SHA256_ADDR_BYTES 22

#include "all_option.h"
#include <stddef.h>
#include <stdint.h>

void sha256_inc_init(uint8_t* state);
__device__ void dev_sha256_inc_init(uint8_t* state);
void sha256_inc_blocks(uint8_t* state, const uint8_t* in, size_t inblocks);
__device__ void dev_sha256_inc_blocks(uint8_t* state, const void* in, size_t inblocks);
void sha256_inc_finalize(uint8_t* out, uint8_t* state, const uint8_t* in, size_t inlen);
__device__ void dev_sha256_inc_finalize(uint8_t* out, uint8_t* state, void* in, size_t inlen);
void sha256(uint8_t* out, const uint8_t* in, size_t inlen);
__device__ void dev_sha256(uint8_t* out, uint8_t* in, size_t inlen);

// Add warp-level parallel SHA256 function declarations
__device__ void dev_warp_sha256(uint8_t* out, uint8_t* in, size_t inlen);
__global__ void global_warp_sha256(uint8_t* out, uint8_t* in, size_t inlen, size_t loop_num);
void face_warp_sha256(uint8_t* out, uint8_t* in, size_t inlen, size_t loop_num);

// Add data parallel warp-level SHA256 declarations
__global__ void global_dp_warp_sha256(uint8_t* out, const uint8_t* in, size_t inlen,
                                      size_t total_msg_num);
void face_dp_warp_sha256(const uint8_t* in, uint8_t* out, size_t msg_size, size_t total_msg_num);

// Single thread GPU SHA256 function declarations
void face_sha256(uint8_t* out, uint8_t* in, size_t inlen, size_t loop_num);

// Add data parallel SHA256 function declarations
__global__ void global_dp_sha256(uint8_t* out, const uint8_t* in, size_t inlen,
                                 size_t total_msg_num);
void face_dp_sha256(const uint8_t* in, uint8_t* out, size_t msg_size, size_t total_msg_num,
                    size_t grid_size, size_t block_size);

// Multi-stream data parallel SHA256 declarations
void face_msdp_sha256(const uint8_t* in, uint8_t* out, size_t msg_size, size_t total_msg_num,
                      size_t grid_size, size_t block_size);

void mgf1(unsigned char* out, unsigned long outlen, const unsigned char* in, unsigned long inlen);
__device__ void dev_mgf1(unsigned char* out, unsigned long outlen, const unsigned char* in,
                         unsigned long inlen);
__device__ void dev_mgf1_hg(unsigned char* out, unsigned long outlen, const unsigned char* in,
                            unsigned long inlen);

extern uint8_t state_seeded[40];

void seed_state(const unsigned char* pub_seed);
__device__ void dev_seed_state(const unsigned char* pub_seed);

#endif /* ifndef SPX_SHA256_H */

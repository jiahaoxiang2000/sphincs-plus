#ifndef SPX_UTILS_H
#define SPX_UTILS_H

#include "params.h"
#include <stdint.h>

/**
 * Converts the value of 'in' to 'outlen' bytes in big-endian byte order.
 */
void ull_to_bytes(unsigned char* out, unsigned int outlen, unsigned long long in);
void u32_to_bytes(unsigned char* out, uint32_t in);

__device__ void dev_ull_to_bytes(unsigned char* out, unsigned int outlen, unsigned long long in);
__device__ void dev_u32_to_bytes(unsigned char* out, uint32_t in);

/**
 * Converts the inlen bytes in 'in' from big-endian byte order to an integer.
 */
unsigned long long bytes_to_ull(const unsigned char* in, unsigned int inlen);
__device__ unsigned long long dev_bytes_to_ull(const unsigned char* in, unsigned int inlen);

/**
 * Computes a root node given a leaf and an auth path.
 * Expects address to be complete other than the tree_height and tree_index.
 */
void compute_root(unsigned char* root, const unsigned char* leaf, uint32_t leaf_idx,
                  uint32_t idx_offset, const unsigned char* auth_path, uint32_t tree_height,
                  const unsigned char* pub_seed, uint32_t addr[8]);
__device__ void dev_compute_root(unsigned char* root, const unsigned char* leaf, uint32_t leaf_idx,
                                 uint32_t idx_offset, const unsigned char* auth_path,
                                 uint32_t tree_height, const unsigned char* pub_seed,
                                 uint32_t addr[8]);
// __device__ void dev_ap_compute_root(unsigned char* root, const unsigned char* leaf,
//                                     uint32_t leaf_idx, uint32_t idx_offset,
//                                     const unsigned char* auth_path, uint32_t tree_height,
//                                     const unsigned char* pub_seed, uint32_t addr[8]);
/**
 * For a given leaf index, computes the authentication path and the resulting
 * root node using Merkle's TreeHash algorithm.
 * Expects the layer and tree parts of the tree_addr to be set, as well as the
 * tree type (i.e. SPX_ADDR_TYPE_HASHTREE or SPX_ADDR_TYPE_FORSTREE).
 * Applies the offset idx_offset to indices before building addresses, so that
 * it is possible to continue counting indices across trees.
 */
void treehash(unsigned char* root, unsigned char* auth_path, const unsigned char* sk_seed,
              const unsigned char* pub_seed, uint32_t leaf_idx, uint32_t idx_offset,
              uint32_t tree_height,
              void (*gen_leaf)(unsigned char* /* leaf */, const unsigned char* /* sk_seed */,
                               const unsigned char* /* pub_seed */, uint32_t /* addr_idx */,
                               const uint32_t[8] /* tree_addr */),
              uint32_t tree_addr[8]);
__device__ void
dev_treehash(unsigned char* root, unsigned char* auth_path, const unsigned char* sk_seed,
             const unsigned char* pub_seed, uint32_t leaf_idx, uint32_t idx_offset,
             uint32_t tree_height,
             void (*gen_leaf)(unsigned char* /* leaf */, const unsigned char* /* sk_seed */,
                              const unsigned char* /* pub_seed */, uint32_t /* addr_idx */,
                              const uint32_t[8] /* tree_addr */),
             uint32_t tree_addr[8]);
__device__ void
dev_ap_treehash_fors(unsigned char* root, unsigned char* auth_path, const unsigned char* sk_seed,
                     const unsigned char* pub_seed, uint32_t leaf_idx, uint32_t idx_offset,
                     uint32_t tree_height,
                     void (*gen_leaf)(unsigned char* /* leaf */, const unsigned char* /* sk_seed */,
                                      const unsigned char* /* pub_seed */, uint32_t /* addr_idx */,
                                      const uint32_t[8] /* tree_addr */),
                     uint32_t tree_addr[8]);
__device__ void
dev_ap_treehash_wots(unsigned char* root, unsigned char* auth_path, const unsigned char* sk_seed,
                     const unsigned char* pub_seed, uint32_t leaf_idx, uint32_t idx_offset,
                     uint32_t tree_height,
                     void (*gen_leaf)(unsigned char* /* leaf */, const unsigned char* /* sk_seed */,
                                      const unsigned char* /* pub_seed */, uint32_t /* addr_idx */,
                                      const uint32_t[8] /* tree_addr */),
                     uint32_t tree_addr[8]);

__device__ void dev_ap_treehash_wots_2(
    unsigned char* root, unsigned char* auth_path, const unsigned char* sk_seed,
    const unsigned char* pub_seed, uint32_t leaf_idx, uint32_t idx_offset, uint32_t tree_height,
    void (*gen_leaf)(unsigned char* /* leaf */, const unsigned char* /* sk_seed */,
                     const unsigned char* /* pub_seed */, uint32_t /* addr_idx */,
                     const uint32_t[8] /* tree_addr */),
    uint32_t tree_addr[8]);

__device__ void dev_ap_treehash_wots_23(
    unsigned char* root, unsigned char* auth_path, const unsigned char* sk_seed,
    const unsigned char* pub_seed, uint32_t leaf_idx, uint32_t idx_offset, uint32_t tree_height,
    void (*gen_leaf)(unsigned char* /* leaf */, const unsigned char* /* sk_seed */,
                     const unsigned char* /* pub_seed */, uint32_t /* addr_idx */,
                     const uint32_t[8] /* tree_addr */),
    uint32_t tree_addr[8]);
__device__ void dev_ap_treehash_wots_dynamic(
    unsigned char* root, unsigned char* auth_path, const unsigned char* sk_seed,
    const unsigned char* pub_seed, uint32_t leaf_idx, uint32_t idx_offset, uint32_t tree_height,
    void (*dev_gen_leaf)(unsigned char* /* leaf */, const unsigned char* /* sk_seed */,
                         const unsigned char* /* pub_seed */, uint32_t /* addr_idx */,
                         const uint32_t[8] /* tree_addr */),
    uint32_t tree_addr[8]);

__device__ void dev_ap_treehash_wots_shared(
    unsigned char* root, unsigned char* auth_path, const unsigned char* sk_seed,
    const unsigned char* pub_seed, uint32_t leaf_idx, uint32_t idx_offset, uint32_t tree_height,
    void (*gen_leaf)(unsigned char* /* leaf */, const unsigned char* /* sk_seed */,
                     const unsigned char* /* pub_seed */, uint32_t /* addr_idx */,
                     const uint32_t[8] /* tree_addr */),
    uint32_t tree_addr[8]);

#endif /* ifndef SPX_UTILS_H */

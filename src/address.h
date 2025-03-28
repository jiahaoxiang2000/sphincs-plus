#ifndef SPX_ADDRESS_H
#define SPX_ADDRESS_H

#include <stdint.h>

/* The hash types that are passed to set_type */
#define SPX_ADDR_TYPE_WOTS 0
#define SPX_ADDR_TYPE_WOTSPK 1
#define SPX_ADDR_TYPE_HASHTREE 2
#define SPX_ADDR_TYPE_FORSTREE 3
#define SPX_ADDR_TYPE_FORSPK 4

void set_layer_addr(uint32_t addr[8], uint32_t layer);

void set_tree_addr(uint32_t addr[8], uint64_t tree);

void set_type(uint32_t addr[8], uint32_t type);

/* Copies the layer and tree part of one address into the other */
void copy_subtree_addr(uint32_t out[8], const uint32_t in[8]);

/* These functions are used for WOTS and FORS addresses. */

void set_keypair_addr(uint32_t addr[8], uint32_t keypair);

void set_chain_addr(uint32_t addr[8], uint32_t chain);

void set_hash_addr(uint32_t addr[8], uint32_t hash);

void copy_keypair_addr(uint32_t out[8], const uint32_t in[8]);

/* These functions are used for all hash tree addresses (including FORS). */

void set_tree_height(uint32_t addr[8], uint32_t tree_height);

void set_tree_index(uint32_t addr[8], uint32_t tree_index);

//------------------------------------------------------------//

__device__ void dev_set_layer_addr(uint32_t addr[8], uint32_t layer);

__device__ void dev_set_tree_addr(uint32_t addr[8], uint64_t tree);

__device__ void dev_set_type(uint32_t addr[8], uint32_t type);

/* Copies the layer and tree part of one address into the other */
__device__ void dev_copy_subtree_addr(uint32_t out[8], const uint32_t in[8]);

/* These functions are used for WOTS and FORS addresses. */

__device__ void dev_set_keypair_addr(uint32_t addr[8], uint32_t keypair);

__device__ void dev_set_chain_addr(uint32_t addr[8], uint32_t chain);

__device__ void dev_set_hash_addr(uint32_t addr[8], uint32_t hash);

__device__ void dev_copy_keypair_addr(uint32_t out[8], const uint32_t in[8]);

/* These functions are used for all hash tree addresses (including FORS). */

__device__ void dev_set_tree_height(uint32_t addr[8], uint32_t tree_height);

__device__ void dev_set_tree_index(uint32_t addr[8], uint32_t tree_index);

#endif

from spx.utils import *
from spx.constant import *
from spx.address import Address, AddrType

import hashlib


def prf_addr(out, key, addr: Address):
    buf = bytearray(SPX_N + SPX_SHA256_ADDR_BYTES)

    buf[:SPX_N] = key
    buf[SPX_N:] = addr.to_bytes()

    # Use hashlib.sha256() to compute the hash
    sha256_hash = hashlib.sha256(buf).digest()
    out[:] = sha256_hash[:SPX_N]


def fors_gen_sk(sk, sk_seed, fors_leaf_addr):
    prf_addr(sk, sk_seed, fors_leaf_addr)


def fors_sk_to_leaf(leaf, sk, pub_seed, fors_leaf_addr):
    thash(leaf, sk, 1, pub_seed, fors_leaf_addr)


def fors_gen_leaf(leaf, sk_seed, pub_seed, addr_idx, fors_tree_addr):
    fors_leaf_addr = Address()

    # Only copy the parts that must be kept in fors_leaf_addr.
    fors_leaf_addr.copy_keypair_addr(fors_tree_addr)
    fors_leaf_addr.set_type(3)
    fors_leaf_addr.set_tree_index(addr_idx)

    fors_gen_sk(leaf, sk_seed, fors_leaf_addr)
    fors_sk_to_leaf(leaf, leaf, pub_seed, fors_leaf_addr)
    return leaf


def message_to_indices(indices, m):
    offset = 0

    for i in range(SPX_FORS_TREES):
        indices[i] = 0
        for j in range(SPX_FORS_HEIGHT):
            indices[i] ^= ((m[offset >> 3] >> (offset & 0x7)) & 0x1) << j
            offset += 1


def fors_sign(sig, pk, m, sk_seed, pub_seed, fors_addr):
    indices = bytearray(SPX_FORS_TREES)
    roots = bytearray(SPX_FORS_TREES * SPX_N)
    fors_tree_addr = Address()
    fors_pk_addr = Address()

    fors_tree_addr.copy_keypair_addr(fors_addr)
    fors_pk_addr.copy_keypair_addr(fors_addr)

    fors_tree_addr.set_type(3)
    fors_pk_addr.set_type(4)
    message_to_indices(indices, m)

    for i in range(SPX_FORS_TREES):
        idx_offset = i * (1 << SPX_FORS_HEIGHT)
        fors_tree_addr.set_tree_height(0)
        fors_tree_addr.set_tree_index(indices[i] + idx_offset)

        temp = bytearray(SPX_N)

        # Include the secret key part that produces the selected leaf node.
        fors_gen_sk(temp, sk_seed, fors_tree_addr)
        sig[(i * SPX_FORS_HEIGHT) * SPX_N : (i * SPX_FORS_HEIGHT + 1) * SPX_N] = temp

        # Compute the authentication path for this leaf node.
        auth_path = bytearray(SPX_N * (SPX_FORS_HEIGHT - 1))
        treehash(
            temp,
            auth_path,
            sk_seed,
            pub_seed,
            indices[i],
            idx_offset,
            SPX_FORS_HEIGHT,
            fors_gen_leaf,
            fors_tree_addr,
        )
        roots[i * SPX_N : i * SPX_N + SPX_N] = temp
        sig[(i * SPX_FORS_HEIGHT + 1) * SPX_N : ((i + 1) * SPX_FORS_HEIGHT) * SPX_N] = (
            auth_path
        )

    # Hash horizontally across all tree roots to derive the public key.
    thash(pk, roots, SPX_FORS_TREES, pub_seed, fors_pk_addr)


def fors_pk_from_sig(pk, sig, m, pub_seed, fors_addr):
    indices = bytearray(SPX_FORS_TREES)
    roots = bytearray(SPX_FORS_TREES * SPX_N)
    leaf = bytearray(SPX_N)
    fors_tree_addr = Address()
    fors_pk_addr = Address()

    fors_tree_addr.copy_keypair_addr(fors_addr)
    fors_pk_addr.copy_keypair_addr(fors_addr)

    fors_tree_addr.set_type(3)
    fors_pk_addr.set_type(4)
    message_to_indices(indices, m)

    for i in range(SPX_FORS_TREES):
        idx_offset = i * (1 << SPX_FORS_HEIGHT)
        fors_tree_addr.set_tree_height(0)
        fors_tree_addr.set_tree_index(indices[i] + idx_offset)

        # Derive the leaf from the included secret key part.
        fors_sk_to_leaf(
            leaf,
            sig[(i * SPX_FORS_HEIGHT) * SPX_N : (i * SPX_FORS_HEIGHT + 1) * SPX_N],
            pub_seed,
            fors_tree_addr,
        )

        auth_path = bytearray(SPX_N * (SPX_FORS_HEIGHT - 1))
        auth_path = sig[(i + 1) * SPX_D : (i + SPX_FORS_HEIGHT) * SPX_D]
        index = indices[i] + idx_offset
        root = bytearray(SPX_N)

        for j in range(SPX_FORS_HEIGHT - 1):
            fors_tree_addr.set_tree_height(j + 1)
            index >>= 1
            fors_tree_addr.set_tree_index(index)
            buff = bytearray(SPX_N * 2)
            buff[:SPX_N] = auth_path[j * SPX_N : (j + 1) * SPX_N]
            buff[SPX_N:] = leaf
            thash(root, buff, 2, pub_seed, fors_tree_addr)

        roots[i * SPX_N : i * SPX_N + SPX_N] = root

    # Hash horizontally across all tree roots to derive the public key.
    thash(pk, roots, SPX_FORS_TREES, pub_seed, fors_pk_addr)

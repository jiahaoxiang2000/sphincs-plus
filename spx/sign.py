import hashlib
import os
from spx.utils import *
from spx.constant import *
from spx.address import Address, AddrType
from spx.wots import wots_gen_pk, wots_sign


def wots_gen_leaf(leaf, sk_seed, pub_seed, addr_idx, tree_addr: Address):
    pk = bytearray(SPX_WOTS_BYTES)
    wots_addr = Address()
    wots_pk_addr = Address()

    wots_addr.set_type(AddrType.WOTS_HASH)
    wots_pk_addr.set_type(AddrType.WOTS_PK)

    wots_addr.copy_subtree_addr(tree_addr)
    wots_addr.set_keypair_addr(addr_idx)

    wots_gen_pk(pk, sk_seed, pub_seed, wots_addr)

    wots_pk_addr.copy_keypair_addr(wots_addr)

    thash(leaf, pk, SPX_WOTS_LEN, pub_seed, wots_pk_addr)


def crypto_sign_seed_keypair(pk, sk, seed):
    auth_path = bytearray(SPX_TREE_HEIGHT * SPX_N)
    top_tree_addr = Address()

    top_tree_addr.set_layer_addr(SPX_D - 1)
    top_tree_addr.set_type(AddrType.TREE)

    sk[:] = seed[:CRYPTO_SEEDBYTES]

    pk[:] = sk[2 * SPX_N : 2 * SPX_N + SPX_N]

    initialize_hash_function(pk, sk)
    out = sk[3 * SPX_N : 3 * SPX_N + SPX_N]
    treehash(
        out,
        auth_path,
        sk,
        sk[2 * SPX_N : 2 * SPX_N + SPX_N],
        0,
        0,
        SPX_TREE_HEIGHT,
        wots_gen_leaf,
        top_tree_addr,
    )
    sk[3 * SPX_N : 3 * SPX_N + SPX_N] = out

    pk[SPX_N : SPX_N + SPX_N] = sk[3 * SPX_N : 3 * SPX_N + SPX_N]


def crypto_sign_keypair(pk, sk):
    seed = os.urandom(CRYPTO_SEEDBYTES)
    return crypto_sign_seed_keypair(pk, sk, seed)


def gen_message_random(R, sk_prf, optrand, m, mlen):
    import hmac
    import hashlib

    # This implements HMAC-SHA256 using hmac and hashlib
    key = bytes(sk_prf)
    msg = bytes(optrand + m)
    hmac_sha256 = hmac.new(key, msg, hashlib.sha256).digest()
    R[:] = hmac_sha256[:SPX_N]


# Assuming sha256_inc_init, sha256_inc_blocks, and sha256_inc_finalize are custom functions
def sha256_inc_init(state):
    state[:] = hashlib.sha256().digest()


def sha256_inc_blocks(state, data, num_blocks):
    sha256 = hashlib.sha256()
    sha256.update(data[: num_blocks * 64])
    state[:] = sha256.digest()


def sha256_inc_finalize(output, state, data, data_len):
    sha256 = hashlib.sha256(state)
    sha256.update(data[:data_len])
    output[:] = sha256.digest()


def mgf1(out, outlen, in_data, inlen):
    inbuf = bytearray(inlen + 4)
    outbuf = bytearray(SPX_SHA256_OUTPUT_BYTES)
    inbuf[:inlen] = in_data

    i = 0
    while (i + 1) * SPX_SHA256_OUTPUT_BYTES <= outlen:
        inbuf[inlen:] = i.to_bytes(4, byteorder="big")
        hashlib.sha256(out, inbuf)
        out[outlen:] = out[:SPX_SHA256_OUTPUT_BYTES]
        out = out[SPX_SHA256_OUTPUT_BYTES:]
        i += 1

    if outlen > i * SPX_SHA256_OUTPUT_BYTES:
        inbuf[inlen:] = i.to_bytes(4, byteorder="big")
        hashlib.sha256(outbuf, inbuf)
        out[outlen:] = outbuf[: outlen - i * SPX_SHA256_OUTPUT_BYTES]


def hash_message(digest, tree, leaf_idx, R, pk, m, mlen):
    SPX_TREE_BITS = SPX_TREE_HEIGHT * (SPX_D - 1)
    SPX_TREE_BYTES = (SPX_TREE_BITS + 7) // 8
    SPX_LEAF_BITS = SPX_TREE_HEIGHT
    SPX_LEAF_BYTES = (SPX_LEAF_BITS + 7) // 8
    SPX_DGST_BYTES = SPX_FORS_MSG_BYTES + SPX_TREE_BYTES + SPX_LEAF_BYTES
    SPX_SHA256_BLOCK_BYTES = 64
    SPX_SHA256_OUTPUT_BYTES = 32

    seed = bytearray(SPX_SHA256_OUTPUT_BYTES)

    # Round to nearest multiple of SPX_SHA256_BLOCK_BYTES
    if (SPX_SHA256_BLOCK_BYTES & (SPX_SHA256_BLOCK_BYTES - 1)) != 0:
        raise ValueError("Assumes that SPX_SHA256_BLOCK_BYTES is a power of 2")
    SPX_INBLOCKS = (
        (SPX_N + SPX_PK_BYTES + SPX_SHA256_BLOCK_BYTES - 1) & -SPX_SHA256_BLOCK_BYTES
    ) // SPX_SHA256_BLOCK_BYTES
    inbuf = bytearray(SPX_INBLOCKS * SPX_SHA256_BLOCK_BYTES)

    buf = bytearray(SPX_DGST_BYTES)
    bufp = buf
    state = bytearray(40)

    sha256_inc_init(state)

    inbuf[:SPX_N] = R
    inbuf[SPX_N : SPX_N + SPX_PK_BYTES] = pk

    # If R + pk + message cannot fill up an entire block
    if SPX_N + SPX_PK_BYTES + mlen < SPX_INBLOCKS * SPX_SHA256_BLOCK_BYTES:
        inbuf[SPX_N + SPX_PK_BYTES : SPX_N + SPX_PK_BYTES + mlen] = m
        sha256_inc_finalize(seed, state, inbuf, SPX_N + SPX_PK_BYTES + mlen)
    # Otherwise first fill a block, so that finalize only uses the message
    else:
        inbuf[
            SPX_N
            + SPX_PK_BYTES : SPX_N
            + SPX_PK_BYTES
            + SPX_INBLOCKS * SPX_SHA256_BLOCK_BYTES
            - SPX_N
            - SPX_PK_BYTES
        ] = m[: SPX_INBLOCKS * SPX_SHA256_BLOCK_BYTES - SPX_N - SPX_PK_BYTES]
        sha256_inc_blocks(state, inbuf, SPX_INBLOCKS)

        m = m[SPX_INBLOCKS * SPX_SHA256_BLOCK_BYTES - SPX_N - SPX_PK_BYTES :]
        mlen -= SPX_INBLOCKS * SPX_SHA256_BLOCK_BYTES - SPX_N - SPX_PK_BYTES
        sha256_inc_finalize(seed, state, m, mlen)

    # By doing this in two steps, we prevent hashing the message twice;
    # otherwise each iteration in MGF1 would hash the message again.
    mgf1(bufp, SPX_DGST_BYTES, seed, SPX_SHA256_OUTPUT_BYTES)

    digest[:] = bufp[:SPX_FORS_MSG_BYTES]
    bufp = bufp[SPX_FORS_MSG_BYTES:]

    if SPX_TREE_BITS > 64:
        raise ValueError(
            "For given height and depth, 64 bits cannot represent all subtrees"
        )

    # Replace bytes_to_ull with int.from_bytes
    tree[0] = int.from_bytes(bufp[:SPX_TREE_BYTES], byteorder="little", signed=False)
    tree[0] &= (~(0)) >> (64 - SPX_TREE_BITS)
    bufp = bufp[SPX_TREE_BYTES:]

    leaf_idx[0] = int.from_bytes(
        bufp[:SPX_LEAF_BYTES], byteorder="little", signed=False
    )
    leaf_idx[0] &= (~(0)) >> (32 - SPX_LEAF_BITS)


def initialize_hash_function(pub_seed, sk):
    seed_state(pub_seed)


def crypto_sign_signature(sig, siglen, m, mlen, sk):
    sk_seed = sk
    sk_prf = sk[SPX_N : SPX_N + SPX_N]
    pk = sk[2 * SPX_N : 2 * SPX_N + SPX_N]
    pub_seed = pk

    optrand = bytearray(SPX_N)
    mhash = bytearray(SPX_FORS_MSG_BYTES)
    root = bytearray(SPX_N)
    wots_addr = Address()
    tree_addr = Address()

    initialize_hash_function(pub_seed, sk_seed)

    wots_addr.set_type(AddrType.WOTS_HASH)
    tree_addr.set_type(AddrType.TREE)

    optrand[:] = os.urandom(SPX_N)
    gen_message_random(sig, sk_prf, optrand, m, mlen)

    tree = [0]
    idx_leaf = [0]
    hash_message(mhash, tree, idx_leaf, sig, pk, m, mlen)
    sig = sig[SPX_N:]

    wots_addr.set_tree_addr(tree[0])
    wots_addr.set_keypair_addr(idx_leaf[0])

    # fors_sign(sig, root, mhash, sk_seed, pub_seed, wots_addr)
    sig = sig[SPX_FORS_BYTES:]

    for i in range(SPX_D):
        tree_addr.set_layer_addr(i)
        tree_addr.set_tree_addr(tree[0])
        wots_addr.copy_subtree_addr(tree_addr)
        wots_addr.set_keypair_addr(idx_leaf[0])

        wots_sign(sig, root, sk_seed, pub_seed, wots_addr)
        sig = sig[SPX_WOTS_BYTES:]

        treehash(
            root,
            sig,
            sk_seed,
            pub_seed,
            idx_leaf[0],
            0,
            SPX_TREE_HEIGHT,
            wots_gen_leaf,
            tree_addr,
        )
        sig = sig[SPX_TREE_HEIGHT * SPX_N :]

        idx_leaf[0] = tree[0] & ((1 << SPX_TREE_HEIGHT) - 1)
        tree[0] >>= SPX_TREE_HEIGHT

    siglen[0] = SPX_BYTES

    return 0

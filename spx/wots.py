import hashlib
from typing import List, Tuple

from spx.address import Address
from spx.utils import thash
from spx.constant import *


def prf_addr(key: bytes, addr: Address) -> bytes:
    """PRF function using SHA256"""
    addr_bytes = addr.to_bytes()[:SPX_SHA256_ADDR_BYTES]
    return hashlib.sha256(key + addr_bytes).digest()[:SPX_N]


def gen_chain(
    input_data: bytearray, start: int, steps: int, pub_seed: bytearray, addr: Address
) -> bytearray:
    """Compute the chaining function"""
    out = input_data[:SPX_N]

    for i in range(start, min(start + steps, SPX_WOTS_W)):
        addr.set_hash_addr(i)
        thash(out, out, 1, pub_seed, addr)

    return out


def wots_gen_sk(sk_seed: bytes, addr: Address) -> bytes:
    """Generate WOTS secret key element"""
    # no problem with this
    addr.set_hash_addr(0)
    return bytearray(prf_addr(sk_seed, addr))


def base_w(msg: bytes, out_len: int) -> bytearray:
    """Convert byte string to base w"""
    consumed = 0
    bits = 0
    total = 0
    output = bytearray()

    for _ in range(out_len):
        if bits == 0:
            total = msg[consumed]
            bits = 8
            consumed += 1
        bits -= SPX_WOTS_LOGW
        output.append((total >> bits) & (SPX_WOTS_W - 1))

    return output


def wots_checksum(msg_base_w: bytearray) -> bytearray:
    """Compute the checksum of the message in base-w format and convert it to base-w."""
    csum = 0
    csum_bytes = bytearray((SPX_WOTS_LEN2 * SPX_WOTS_LOGW + 7) // 8)

    # Compute checksum.
    for i in range(SPX_WOTS_LEN1):
        csum += SPX_WOTS_W - 1 - msg_base_w[i]

    # Convert checksum to base_w.
    # Make sure expected empty zero bits are the least significant bits.
    csum = csum << ((8 - ((SPX_WOTS_LEN2 * SPX_WOTS_LOGW) % 8)) % 8)
    csum_bytes = csum.to_bytes(len(csum_bytes), byteorder="big")
    return base_w(csum_bytes, SPX_WOTS_LEN2)


def chain_lengths(lengths: bytearray, msg: bytearray):
    """Compute the lengths by the msg, where spilt to base w and computer the checksum"""
    lengths[:SPX_WOTS_LEN1] = base_w(msg, SPX_WOTS_LEN1)
    lengths[SPX_WOTS_LEN1 : SPX_WOTS_LEN1 + SPX_WOTS_LEN2] = wots_checksum(lengths)


def wots_sign(
    sig: bytearray,
    msg: bytearray,
    sk_seed: bytearray,
    pub_seed: bytearray,
    addr: Address,
) -> None:
    """Generate WOTS signature"""
    lengths = bytearray(SPX_WOTS_LEN)

    chain_lengths(lengths, msg)

    for i in range(SPX_WOTS_LEN):
        addr.set_chain_addr(i)
        sig[i * SPX_N : (i + 1) * SPX_N] = wots_gen_sk(sk_seed, addr)
        sig[i * SPX_N : (i + 1) * SPX_N] = gen_chain(
            sig[i * SPX_N : (i + 1) * SPX_N], 0, lengths[i], pub_seed, addr
        )


def wots_gen_pk(sk_seed: bytes, pub_seed: bytes, addr: Address) -> bytes:
    """Generate WOTS public key"""
    pk = bytearray()

    for i in range(SPX_WOTS_LEN):
        addr.set_chain_addr(i)
        sk = wots_gen_sk(sk_seed, addr)
        pk_element = gen_chain(sk, 0, SPX_WOTS_W - 1, pub_seed, addr)
        pk.extend(pk_element)

    return bytes(pk)

import hashlib
from typing import List, Tuple

from spx.utils import seed_state

from .address import WOTSAddress

# Parameters
SPX_N = 16  # Hash output length in bytes
SPX_WOTS_W = 16  # Winternitz parameter
SPX_WOTS_LOGW = 4  # log2(SPX_WOTS_W)
SPX_WOTS_LEN1 = 64  # Length of message part
SPX_WOTS_LEN2 = 3   # Length of checksum part
SPX_WOTS_LEN = SPX_WOTS_LEN1 + SPX_WOTS_LEN2  # Total length
SPX_WOTS_BYTES = SPX_WOTS_LEN * SPX_N
SPX_WOTS_PK_BYTES = SPX_WOTS_BYTES
SPX_SHA256_OUTPUT_BYTES = 32

def prf_addr(key: bytes, addr: WOTSAddress) -> bytes:
    """PRF function using SHA256"""
    addr_bytes = addr.to_bytes()
    return hashlib.sha256(key + addr_bytes).digest()[:SPX_N]





def thash(input: bytes, pub_seed: bytes, addr: WOTSAddress) -> None:
    """
    T-hash function using SHA256
    Args:
        out: output buffer (SPX_N bytes)
        in_blocks: concatenated input blocks
        inblocks: number of input blocks
        pub_seed: public seed (not used in simple variant)
        addr: address structure
    """
    buf = addr + input
    # TODO: need to global init state_seeded
    global state_seeded
    seed_state(pub_seed)
    out = hashlib.sha256(buf).digest()[:SPX_N] 
    
    # Generate hash
    
    return out

def gen_chain(input_data: bytes, start: int, steps: int, pub_seed: bytes, addr: WOTSAddress) -> bytes:
    """Compute the chaining function"""
    out = input_data[:SPX_N]
    
    for i in range(start, min(start + steps, SPX_WOTS_W)):
        addr.hash = i.to_bytes(4, 'big')
        out = thash(out, pub_seed, addr)
    
    return out

def wots_gen_sk(sk_seed: bytes, addr: WOTSAddress) -> bytes:
    """Generate WOTS secret key element"""
    addr.hash = bytes(4)  # Zero the hash address
    return prf_addr(sk_seed, addr)

def base_w(msg: bytes, out_len: int) -> List[int]:
    """Convert byte string to base w"""
    consumed = 0
    bits = 0
    total = 0
    output = []
    
    for i in range(out_len):
        if bits == 0:
            total = msg[consumed // (8 // SPX_WOTS_LOGW)]
            bits = 8
            consumed += SPX_WOTS_LOGW
        bits -= SPX_WOTS_LOGW
        output.append((total >> bits) & (SPX_WOTS_W - 1))
    
    return output

def chain_lengths(msg: bytes) -> List[int]:
    """Calculate chain lengths from message"""
    lengths = base_w(msg, SPX_WOTS_LEN1)
    
    # Compute checksum
    csum = 0
    for length in lengths:
        csum += SPX_WOTS_W - 1 - length
    
    # Make sure expected empty zero bits are the least significant bits
    csum = csum << ((8 - ((SPX_WOTS_LEN2 * SPX_WOTS_LOGW) % 8)) % 8)
    csum_bytes = ull_to_bytes(csum, (SPX_WOTS_LEN2 * SPX_WOTS_LOGW + 7) // 8)
    
    # Convert checksum to base_w
    lengths.extend(base_w(csum_bytes, SPX_WOTS_LEN2))
    return lengths

def wots_gen_pk(sk_seed: bytes, pub_seed: bytes, addr: WOTSAddress) -> bytes:
    """Generate WOTS public key"""
    pk = bytearray()
    
    for i in range(SPX_WOTS_LEN):
        addr.chain = i.to_bytes(4, 'big')
        sk = wots_gen_sk(sk_seed, addr)
        pk_element = gen_chain(sk, 0, SPX_WOTS_W - 1, pub_seed, addr)
        pk.extend(pk_element)
    
    return bytes(pk)

def wots_sign(msg: bytes, sk_seed: bytes, pub_seed: bytes, addr: WOTSAddress) -> bytes:
    """Generate WOTS signature"""
    lengths = chain_lengths(msg)
    sig = bytearray()
    
    for i in range(SPX_WOTS_LEN):
        addr.chain = i.to_bytes(4, 'big')
        sk = wots_gen_sk(sk_seed, addr)
        sig_element = gen_chain(sk, 0, lengths[i], pub_seed, addr)
        sig.extend(sig_element)
    
    return bytes(sig)

def wots_pk_from_sig(sig: bytes, msg: bytes, pub_seed: bytes, addr: WOTSAddress) -> bytes:
    """Compute public key from signature"""
    lengths = chain_lengths(msg)
    pk = bytearray()
    
    for i in range(SPX_WOTS_LEN):
        addr.chain = i.to_bytes(4, 'big')
        sig_element = sig[i*SPX_N:(i+1)*SPX_N]
        pk_element = gen_chain(sig_element, lengths[i], 
                             SPX_WOTS_W - 1 - lengths[i], 
                             pub_seed, addr)
        pk.extend(pk_element)
    
    return bytes(pk)

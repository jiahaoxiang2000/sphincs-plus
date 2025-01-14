# from spx.wots import SPX_N
# from Crypto.Hash import SHA256
SPX_N = 16  # Hash output length in bytes

state_seeded = bytearray(40)  # 32 bytes hash state + 8 bytes counter

# Initialize SHA256 IV constants
IV_256 = bytes([
    0x6a, 0x09, 0xe6, 0x67, 0xbb, 0x67, 0xae, 0x85,
    0x3c, 0x6e, 0xf3, 0x72, 0xa5, 0x4f, 0xf5, 0x3a,
    0x51, 0x0e, 0x52, 0x7f, 0x9b, 0x05, 0x68, 0x8c,
    0x1f, 0x83, 0xd9, 0xab, 0x5b, 0xe0, 0xcd, 0x19
])


def rotr(x: int, n: int) -> int:
    return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF

def ch(x: int, y: int, z: int) -> int:
    return (x & y) ^ (~x & z)

def maj(x: int, y: int, z: int) -> int:
    return (x & y) ^ (x & z) ^ (y & z)

def sigma0(x: int) -> int:
    return rotr(x, 2) ^ rotr(x, 13) ^ rotr(x, 22)

def sigma1(x: int) -> int:
    return rotr(x, 6) ^ rotr(x, 11) ^ rotr(x, 25)

def gamma0(x: int) -> int:
    return rotr(x, 7) ^ rotr(x, 18) ^ (x >> 3)

def gamma1(x: int) -> int:
    return rotr(x, 17) ^ rotr(x, 19) ^ (x >> 10)

def load_bigendian_32(x: bytes) -> int:
    return int.from_bytes(x[:4], byteorder='big')

def store_bigendian_32(val: int) -> bytes:
    return val.to_bytes(4, byteorder='big')

def crypto_hashblocks_sha256(statebytes: bytearray, input_data: bytes, inlen: int) -> int:
    K = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
        0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
        0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
        0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
        0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
        0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
        0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
        0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
        0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ]
    
    # Load state
    state = [load_bigendian_32(statebytes[i:i+4]) for i in range(0, 32, 4)]
    
    while inlen >= 64:
        # Load block into W
        W = [load_bigendian_32(input_data[i:i+4]) for i in range(0, 64, 4)]
        
        # Extend the sixteen 32-bit words into sixty-four 32-bit words
        for i in range(16, 64):
            W.append((gamma1(W[i-2]) + W[i-7] + gamma0(W[i-15]) + W[i-16]) & 0xFFFFFFFF)
        
        # Initialize working variables
        a, b, c, d, e, f, g, h = state
        
        # Main loop
        for i in range(64):
            T1 = (h + sigma1(e) + ch(e, f, g) + K[i] + W[i]) & 0xFFFFFFFF
            T2 = (sigma0(a) + maj(a, b, c)) & 0xFFFFFFFF
            h = g
            g = f
            f = e
            e = (d + T1) & 0xFFFFFFFF
            d = c
            c = b
            b = a
            a = (T1 + T2) & 0xFFFFFFFF
        
        # Update state
        state = [(x + y) & 0xFFFFFFFF for x, y in zip(state, [a, b, c, d, e, f, g, h])]
        
        input_data = input_data[64:]
        inlen -= 64
    
    # Store state back
    for i, s in enumerate(state):
        statebytes[i*4:(i+1)*4] = store_bigendian_32(s)
    
    return inlen

def seed_state(pub_seed: bytes) -> None:
    # Initialize state with IV
    state_seeded[0:32] = IV_256
    count = state_seeded[32:40]
    # transform the counter to integer
    count = int.from_bytes(count, byteorder='big')
    
    # Prepare input block
    block = bytearray(64)  # SPX_SHA256_BLOCK_BYTES
    block[0:SPX_N] = pub_seed[0:SPX_N]
    # Rest of block remains zero
    
    # Update state with block
    crypto_hashblocks_sha256(state_seeded, block, 64) 
    count += 64
    state_seeded[32:40] = count.to_bytes(8, byteorder='big')
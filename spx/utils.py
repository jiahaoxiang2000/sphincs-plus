import hashlib
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

from hashlib import sha256

def crypto_hashblocks_sha256(statebytes: bytearray, input_data: bytes, inlen: int) -> int:
    """
    Python implementation of crypto_hashblocks_sha256 using hashlib
    TODO: this function is not implemented correctly, the tweak is not implemented, ths hash is impacted by the tweak
    """
    # Create SHA256 object with existing state
    sha256_state = hashlib.sha256()
    
    # Process blocks of 64 bytes
    while inlen >= 64:
        block = input_data[:64]
        sha256_state.update(block)
        
        # Get intermediate hash value
        digest = sha256_state.digest()
        statebytes[:32] = digest
        
        input_data = input_data[64:]
        inlen -= 64
    
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
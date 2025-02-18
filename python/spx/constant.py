# constants.py

# Offsets of various fields in the address structure when we use SHA256 as the Sphincs+ hash function
SPX_OFFSET_LAYER = 0  # The byte used to specify the Merkle tree layer
SPX_OFFSET_TREE = 1  # The start of the 8 byte field used to specify the tree
SPX_OFFSET_TYPE = 9  # The byte used to specify the hash type (reason)
SPX_OFFSET_KP_ADDR2 = (
    12  # The high byte used to specify the key pair (which one-time signature)
)
SPX_OFFSET_KP_ADDR1 = 13  # The low byte used to specify the key pair
SPX_OFFSET_CHAIN_ADDR = (
    17  # The byte used to specify the chain address (which Winternitz chain)
)
SPX_OFFSET_HASH_ADDR = (
    21  # The byte used to specify the hash address (where in the Winternitz chain)
)
SPX_OFFSET_TREE_HGT = (
    17  # The byte used to specify the height of this node in the FORS or Merkle tree
)
SPX_OFFSET_TREE_INDEX = 18  # The start of the 4 byte field used to specify the node in the FORS or Merkle tree

# Hash output length in bytes.
SPX_N = 16
# Height of the hypertree.
SPX_FULL_HEIGHT = 66
# Number of subtree layer.
SPX_D = 22
# FORS tree dimensions.
SPX_FORS_HEIGHT = 6
SPX_FORS_TREES = 33
# Winternitz parameter.
SPX_WOTS_W = 16

# For clarity
SPX_ADDR_BYTES = 32

# WOTS parameters.
if SPX_WOTS_W == 256:
    SPX_WOTS_LOGW = 8
elif SPX_WOTS_W == 16:
    SPX_WOTS_LOGW = 4
else:
    raise ValueError("SPX_WOTS_W assumed 16 or 256")

SPX_WOTS_LEN1 = 8 * SPX_N // SPX_WOTS_LOGW

# SPX_WOTS_LEN2 is floor(log(len_1 * (w - 1)) / log(w)) + 1; we precompute
if SPX_WOTS_W == 256:
    if SPX_N <= 1:
        SPX_WOTS_LEN2 = 1
    elif SPX_N <= 256:
        SPX_WOTS_LEN2 = 2
    else:
        raise ValueError("Did not precompute SPX_WOTS_LEN2 for n outside {2, .., 256}")
elif SPX_WOTS_W == 16:
    if SPX_N <= 8:
        SPX_WOTS_LEN2 = 2
    elif SPX_N <= 136:
        SPX_WOTS_LEN2 = 3
    elif SPX_N <= 256:
        SPX_WOTS_LEN2 = 4
    else:
        raise ValueError("Did not precompute SPX_WOTS_LEN2 for n outside {2, .., 256}")

SPX_WOTS_LEN = SPX_WOTS_LEN1 + SPX_WOTS_LEN2
SPX_WOTS_BYTES = SPX_WOTS_LEN * SPX_N
SPX_WOTS_PK_BYTES = SPX_WOTS_BYTES

# Subtree size.
SPX_TREE_HEIGHT = SPX_FULL_HEIGHT // SPX_D

if SPX_TREE_HEIGHT * SPX_D != SPX_FULL_HEIGHT:
    raise ValueError("SPX_D should always divide SPX_FULL_HEIGHT")

# FORS parameters.
SPX_FORS_MSG_BYTES = (SPX_FORS_HEIGHT * SPX_FORS_TREES + 7) // 8
SPX_FORS_BYTES = (SPX_FORS_HEIGHT + 1) * SPX_FORS_TREES * SPX_N
SPX_FORS_PK_BYTES = SPX_N

# Resulting SPX sizes.
SPX_BYTES = SPX_N + SPX_FORS_BYTES + SPX_D * SPX_WOTS_BYTES + SPX_FULL_HEIGHT * SPX_N
SPX_PK_BYTES = 2 * SPX_N
SPX_SK_BYTES = 2 * SPX_N + SPX_PK_BYTES

# Optionally, signing can be made non-deterministic using optrand.
# This can help counter side-channel attacks that would benefit from
# getting a large number of traces when the signer uses the same nodes.
SPX_OPTRAND_BYTES = 32

# SHA256 specific constants
SPX_SHA256_OUTPUT_BYTES = 32
SPX_SHA256_ADDR_BYTES = 22


CRYPTO_SECRETKEYBYTES = SPX_SK_BYTES
CRYPTO_PUBLICKEYBYTES = SPX_PK_BYTES
CRYPTO_BYTES = SPX_BYTES
CRYPTO_SEEDBYTES = 3 * SPX_N

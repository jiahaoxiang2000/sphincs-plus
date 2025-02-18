set(SPHINCS_SOURCES
    common.cu
    address.cu
    rng.cu
    wots.cu
    utils.cu
    fors.cu
    sign.cu
    fips202.cu
    gpu_fips202.cu
    hash_shake256.cu
    thash_shake256.cu
    sha256.cu
    gpu_sha256.cu
    hash_sha256.cu
    thash_sha256.cu
)

# Convert to absolute paths
list(TRANSFORM SPHINCS_SOURCES PREPEND "${CMAKE_CURRENT_SOURCE_DIR}/")

# Make sources available to parent scope
set(SPHINCS_SOURCES ${SPHINCS_SOURCES} PARENT_SCOPE)
set(SPHINCS_INCLUDE_DIR ${CMAKE_CURRENT_SOURCE_DIR} PARENT_SCOPE)


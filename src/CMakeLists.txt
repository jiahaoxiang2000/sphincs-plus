set(SOURCES
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

# Create library target
add_library(sphincs_plus_lib STATIC ${SOURCES})

target_include_directories(sphincs_plus_lib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(sphincs_plus_lib PUBLIC 
    OpenSSL::Crypto
    CUDA::cudart
)

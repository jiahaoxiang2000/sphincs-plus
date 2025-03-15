set(COMMON_COMPILE_OPTIONS
    -O3 
    -m64 
    -dc 
    --expt-relaxed-constexpr
)


set(CMAKE_CUDA_ARCHITECTURES 89)
# Separate CUDA-specific options - changed LTO specification
set(CUDA_SPECIFIC_OPTIONS
    -gencode=arch=compute_89,code=lto_89  # Changed from -dlto -arch=sm_89
)

function(add_benchmark_target NAME HASH_TYPE SPX_TYPE)
    add_executable(bm-${NAME} 
        ${SPHINCS_SOURCES}
    )
    
    # Make sure source files can be found relative to current directory
    set_source_files_properties(PROPERTIES
        COMPILE_FLAGS "-I${CMAKE_CURRENT_SOURCE_DIR}"
    )
    
    target_compile_definitions(bm-${NAME} PRIVATE 
        VARIANT
        ${HASH_TYPE}
        ${SPX_TYPE}
        SIMPLE
    )
    
    target_include_directories(bm-${NAME} PRIVATE
        ${SPHINCS_INCLUDE_DIR}
    )
    
    # Separate CUDA and general compile options
    target_compile_options(bm-${NAME} PRIVATE 
        ${COMMON_COMPILE_OPTIONS}
        $<$<COMPILE_LANGUAGE:CUDA>:${CUDA_SPECIFIC_OPTIONS}>
    )
    
    set_target_properties(bm-${NAME} PROPERTIES 
        CUDA_SEPARABLE_COMPILATION ON
        CUDA_ARCHITECTURES 89
        CUDA_RESOLVE_DEVICE_SYMBOLS ON  # Changed back to ON
    )
    
    # Let CMake handle CUDA-specific link options automatically
    target_link_libraries(bm-${NAME} PRIVATE
        OpenSSL::Crypto
        CUDA::cudart
    )
endfunction()

# Function for test targets (without bm_ap.cu and specific definitions)
function(add_test_target NAME TYPE)
    add_executable(${TYPE}-${NAME}
        ${TYPE}.cu  # e.g. sha256.cu, wots.cu, etc.
        ${SPHINCS_SOURCES}
    )
    
    target_include_directories(${TYPE}-${NAME} PRIVATE
        ${SPHINCS_INCLUDE_DIR}
    )
    
    target_compile_options(${TYPE}-${NAME} PRIVATE 
        ${COMMON_COMPILE_OPTIONS}
        $<$<COMPILE_LANGUAGE:CUDA>:${CUDA_SPECIFIC_OPTIONS}>
    )
    
    set_target_properties(${TYPE}-${NAME} PROPERTIES 
        CUDA_SEPARABLE_COMPILATION ON
        CUDA_ARCHITECTURES 89
        CUDA_RESOLVE_DEVICE_SYMBOLS ON
    )
    
    target_link_libraries(${TYPE}-${NAME} PRIVATE
        OpenSSL::Crypto
        CUDA::cudart
    )

endfunction()

# SHA256 variants
add_benchmark_target("sha256_128s" SHA256 SPX_128S)
add_benchmark_target("sha256_128f" SHA256 SPX_128F)
add_benchmark_target("sha256_192s" SHA256 SPX_192S)
add_benchmark_target("sha256_192f" SHA256 SPX_192F)
add_benchmark_target("sha256_256s" SHA256 SPX_256S)
add_benchmark_target("sha256_256f" SHA256 SPX_256F)

# SHAKE256 variants
add_benchmark_target("shake256_128s" SHAKE256 SPX_128S)
add_benchmark_target("shake256_128f" SHAKE256 SPX_128F)
add_benchmark_target("shake256_192s" SHAKE256 SPX_192S)
add_benchmark_target("shake256_192f" SHAKE256 SPX_192F)
add_benchmark_target("shake256_256s" SHAKE256 SPX_256S)
add_benchmark_target("shake256_256f" SHAKE256 SPX_256F)

# Group targets matching Makefile structure
add_custom_target(sha256 DEPENDS
    bm-sha256_128s bm-sha256_128f
    bm-sha256_192s bm-sha256_192f
    bm-sha256_256s bm-sha256_256f
)

add_custom_target(shake256 DEPENDS
    bm-shake256_128s bm-shake256_128f
    bm-shake256_192s bm-shake256_192f
    bm-shake256_256s bm-shake256_256f
)

# Target to run all benchmarks
add_custom_target(benchmark_all DEPENDS sha256 shake256)

# Add record target similar to Makefile
add_custom_target(record
    COMMAND ${CMAKE_COMMAND} -E echo "Recording benchmarks to 1.txt"
    COMMAND ${CMAKE_COMMAND} -E rm -f 1.txt
    COMMAND ${CMAKE_COMMAND} -E touch 1.txt
    COMMAND ${CMAKE_COMMAND} -E echo "bm-sha256_128s" >> 1.txt
    COMMAND $<TARGET_FILE:bm-sha256_128s> >> 1.txt
    # ... similar commands for other variants ...
    DEPENDS benchmark_all
)

# Add test targets
add_test_target("test" "sha256")
add_test_target("test" "wots")
add_test_target("test" "fors")
add_test_target("test" "spx")
add_test_target("test" "ap_spx")
add_test_target("test" "ap_benchmark")
add_test_target("test" "dp_benchmark")
add_test_target("test" "dp_spx")
add_test_target("test" "hp_spx")

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



add_test_target("test" "dp_benchmark")
add_test_target("test" "ata")


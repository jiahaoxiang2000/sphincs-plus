# # Helper function to create benchmark targets
# function(add_benchmark_target NAME HASH_TYPE SPX_TYPE)
#     add_executable(bm-${NAME} bm_ap.cu)
#     target_compile_definitions(bm-${NAME} PRIVATE 
#         VARIANT
#         ${HASH_TYPE}
#         ${SPX_TYPE}
#         SIMPLE
#     )
#     target_link_libraries(bm-${NAME} PRIVATE sphincs_plus_lib)
# endfunction()

# # SHA256 variants
# add_benchmark_target(sha256-128s SHA256 SPX_128S)
# add_benchmark_target(sha256-128f SHA256 SPX_128F)
# add_benchmark_target(sha256-192s SHA256 SPX_192S)
# add_benchmark_target(sha256-192f SHA256 SPX_192F)
# add_benchmark_target(sha256-256s SHA256 SPX_256S)
# add_benchmark_target(sha256-256f SHA256 SPX_256F)

# # SHAKE256 variants
# add_benchmark_target(shake256-128s SHAKE256 SPX_128S)
# add_benchmark_target(shake256-128f SHAKE256 SPX_128F)
# add_benchmark_target(shake256-192s SHAKE256 SPX_192S)
# add_benchmark_target(shake256-192f SHAKE256 SPX_192F)
# add_benchmark_target(shake256-256s SHAKE256 SPX_256S)
# add_benchmark_target(shake256-256f SHAKE256 SPX_256F)

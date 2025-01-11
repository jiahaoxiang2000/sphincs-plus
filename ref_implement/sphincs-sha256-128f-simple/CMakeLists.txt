cmake_minimum_required(VERSION 3.10)
project(sphincs_plus C)

# Set C standard
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Set compiler flags
add_compile_options(-Wall -Wextra -Wpedantic -O3)

# Find OpenSSL
find_package(OpenSSL REQUIRED)

# Source files
set(SOURCES
    address.c
    fors.c
    hash_sha256.c
    rng.c
    sha256.c
    sign.c
    thash_sha256_simple.c
    utils.c
    wots.c
)

# Create the main library
add_library(sphincs_plus ${SOURCES})
target_link_libraries(sphincs_plus OpenSSL::Crypto)
target_include_directories(sphincs_plus PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

# Create the PQCgenKAT_sign executable
add_executable(PQCgenKAT_sign PQCgenKAT_sign.c)
target_link_libraries(PQCgenKAT_sign sphincs_plus)

# Create test targets if test directory exists
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/test")
    # WOTS test
    add_executable(test_wots test/wots.c)
    target_link_libraries(test_wots sphincs_plus)

    # FORS test
    add_executable(test_fors test/fors.c)
    target_link_libraries(test_fors sphincs_plus)

    # SPX test
    add_executable(test_spx test/spx.c)
    target_link_libraries(test_spx sphincs_plus)

    # Benchmark
    add_executable(benchmark test/benchmark.c)
    target_link_libraries(benchmark sphincs_plus)
endif()

# Install rules
install(TARGETS sphincs_plus
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib)

install(FILES 
    address.h
    api.h
    fors.h
    hash.h
    params.h
    rng.h
    thash.h
    utils.h
    wots.h
    DESTINATION include/sphincs_plus)

# Install the executable
install(TARGETS PQCgenKAT_sign DESTINATION bin)

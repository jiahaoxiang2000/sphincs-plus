cmake_minimum_required(VERSION 3.18)

# dependence on our machine, number of cpu cores
set(CMAKE_BUILD_PARALLEL_LEVEL 30)


# set(CMAKE_CUDA_ARCHITECTURES 89)
set(CMAKE_CUDA_COMPILER /usr/local/cuda-12.5/bin/nvcc)


project(sphincs_plus LANGUAGES CUDA CXX)

# Find required packages
find_package(OpenSSL REQUIRED)
find_package(CUDAToolkit REQUIRED)

# Add subdirectories
add_subdirectory(src)
add_subdirectory(test)

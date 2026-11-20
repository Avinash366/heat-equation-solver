cmake_minimum_required(VERSION 3.16)
project(heat_equation_solver LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(OpenMP REQUIRED)
find_package(Threads REQUIRED)

add_executable(heat_sequential src/heat_sequential.cpp)

add_executable(heat_openmp src/heat_openmp.cpp)
target_link_libraries(heat_openmp PRIVATE OpenMP::OpenMP_CXX)

add_executable(heat_threads src/heat_threads.cpp)
target_link_libraries(heat_threads PRIVATE Threads::Threads)

add_executable(heat_optimized src/heat_optimized.cpp)
target_link_libraries(heat_optimized PRIVATE OpenMP::OpenMP_CXX)
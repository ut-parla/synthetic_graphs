cmake_minimum_required(VERSION 3.14)
set(CMAKE_CXX_STANDARD 17)

project(sleep LANGUAGES C CXX)

set(CMAKE_VERBOSE_MAKEFILE ON)

find_package(PythonExtensions REQUIRED)
find_package(Cython REQUIRED)

find_package(Python3 REQUIRED COMPONENTS Interpreter NumPy)
include_directories(${Python3_NumPy_INCLUDE_DIRS})
include_directories(${NUMPY_INCLUDE})

message(STATUS "Python3_EXECUTABLE: ${Python3_EXECUTABLE}")
message(STATUS "Python3_INCLUDE_DIRS: ${Python3_INCLUDE_DIRS}")
message(STATUS "Python3_LIBRARIES: ${Python3_LIBRARIES}")
message(STATUS "Python3_VERSION: ${Python3_VERSION}")
message(STATUS "Numpy Include: ${NUMPY_INCLUDE}")
message(STATUS "Numpy Include Directories : ${Python3_NumPy_INCLUDE_DIRS}")

#Compile C++ Implementation Source
add_subdirectory(sleep/impl)

#Compute Cython Wrapper
add_subdirectory(sleep)

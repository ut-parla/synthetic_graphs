file(GLOB IMPL_HDR ${CMAKE_CURRENT_SOURCE_DIR}/include/*.hpp)

if(SLEEP_ENABLE_CUDA)
    message(STATUS "Enabling CUDA support.")
    enable_language(CUDA)
    find_package(CUDAToolkit REQUIRED)
    message(STATUS "CUDAToolkit_LIBRARY_DIR: " ${CUDAToolkit_LIBRARY_DIR})
    file(GLOB IMPL_SRC "${CMAKE_CURRENT_SOURCE_DIR}/*.cu")
else()
    file(GLOB IMPL_SRC "${CMAKE_CURRENT_SOURCE_DIR}/*.cpp")
endif(SLEEP_ENABLE_CUDA)

add_library(busysleep SHARED ${IMPL_SRC})
set_target_properties(busysleep PROPERTIES PUBLIC_HEADER "${IMPL_HDR}")
set_target_properties(busysleep PROPERTIES POSITION_INDEPENDENT_CODE ON)

if(SLEEP_ENABLE_CUDA)
    target_compile_definitions(busysleep PUBLIC SLEEP_ENABLE_CUDA)

    set(GPU_ARCH $ENV{CUDA_ARCH})
    if(GPU_ARCH)
        set_target_properties(busysleep PROPERTIES CUDA_ARCHITECTURES ${GPU_ARCH})
    else()
        set_target_properties(busysleep PROPERTIES CUDA_ARCHITECTURES OFF)
    endif(GPU_ARCH)

    target_link_directories(busysleep PUBLIC ${CUDAToolkit_LIBRARY_ROOT})
    set_target_properties(busysleep PROPERTIES CUDA_SEPARABLE_COMPILATION ON)
    set_target_properties(busysleep PROPERTIES CUDA_RESOLVE_DEVICE_SYMBOLS ON)
    target_compile_options(busysleep PRIVATE $<$<COMPILE_LANGUAGE:CUDA>:--expt-extended-lambda -DPROD>)
    target_compile_options(busysleep PRIVATE $<$<COMPILE_LANGUAGE:CUDA>:--expt-relaxed-constexpr>)
    target_link_libraries(busysleep PUBLIC CUDA::cudart)
endif(SLEEP_ENABLE_CUDA)

if(SLEEP_ENABLE_NVTX)
    message(STATUS "Enabling NVTX support.")
    target_include_directories(busysleep PUBLIC ${NVTX_INCLUDE})
    target_compile_definitions(busysleep PUBLIC PARLA_ENABLE_NVTX)
endif(SLEEP_ENABLE_NVTX)

target_include_directories(busysleep PUBLIC ${CUDAToolkit_LIBRARY_DIR})
target_include_directories(busysleep PUBLIC ${CUDAToolkit_LIBRARY_ROOT})
target_include_directories(busysleep PUBLIC ${CUDAToolkit_INCLUDE_DIRS})
target_include_directories(busysleep PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_include_directories(busysleep PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)

#Move the libraries to the conda lib folder. This puts them on the library path.
install(
        TARGETS busysleep
        LIBRARY
            DESTINATION lib
        PUBLIC_HEADER
            DESTINATION include
    )

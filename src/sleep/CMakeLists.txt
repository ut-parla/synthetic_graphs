set(CYTHON_FLAGS "${CYTHON_FLAGS} -I${CMAKE_CURRENT_SOURCE_DIR}")
set(CMAKE_SHARED_MODULE_PREFIX "")

if(SLEEP_ENABLE_CUDA)
    message(STATUS "Enabling CUDA support.")
    find_package(CUDAToolkit REQUIRED)
endif(SLEEP_ENABLE_CUDA)

add_cython_target(core core.pyx CXX PY3)

add_library(core MODULE ${core})

message(STATUS "PYTHON_RELATIVE_SITE_PACKAGES_DIR: ${PYTHON_RELATIVE_SITE_PACKAGES_DIR}")
message(STATUS "CMAKE_INSTALL_PREFIX: ${CMAKE_INSTALL_PREFIX}")

if(SLEEP_ENABLE_NVTX)
    message(STATUS "Enabling NVTX support.")
    target_include_directories(core PUBLIC ${NVTX_INCLUDE})
    target_compile_definitions(core PUBLIC PARLA_ENABLE_NVTX)
endif(SLEEP_ENABLE_NVTX)



install(TARGETS core LIBRARY DESTINATION ${PYTHON_RELATIVE_SITE_PACKAGES_DIR}/sleep/)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/__init__.py DESTINATION ${PYTHON_RELATIVE_SITE_PACKAGES_DIR}/sleep/)

target_link_libraries(core ${PYTHON_LIBRARIES})
target_link_libraries(core busysleep)

if(SLEEP_ENABLE_CUDA)
    target_link_libraries(core CUDA::cudart)
    target_compile_definitions(core PUBLIC SLEEP_ENABLE_CUDA)
endif(SLEEP_ENABLE_CUDA)

target_include_directories(core PUBLIC ${PROJECT_SOURCE_DIR}/src/sleep/impl/)
target_include_directories(core PUBLIC ${NumPy_INCLUDE_DIRS})
target_include_directories(core PUBLIC ${PYTHON_INCLUDE_DIRS})
target_include_directories(core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

python_extension_module(core)

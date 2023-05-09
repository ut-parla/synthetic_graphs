set(CYTHON_FLAGS "${CYTHON_FLAGS} -I${CMAKE_CURRENT_SOURCE_DIR}")
set(CMAKE_SHARED_MODULE_PREFIX "")

find_package(CUDAToolkit REQUIRED)

add_cython_target(core core.pyx CXX PY3)

add_library(core MODULE ${core})

message(STATUS "PYTHON_RELATIVE_SITE_PACKAGES_DIR: ${PYTHON_RELATIVE_SITE_PACKAGES_DIR}")
message(STATUS "CMAKE_INSTALL_PREFIX: ${CMAKE_INSTALL_PREFIX}")

install(TARGETS core LIBRARY DESTINATION ${PYTHON_RELATIVE_SITE_PACKAGES_DIR}/sleep/)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/__init__.py DESTINATION ${PYTHON_RELATIVE_SITE_PACKAGES_DIR}/sleep/)

target_link_libraries(core ${PYTHON_LIBRARIES})
target_link_libraries(core busysleep)

target_link_libraries(core CUDA::cudart)

target_include_directories(core PUBLIC ${PROJECT_SOURCE_DIR}/sleep_src/impl/)
target_include_directories(core PUBLIC ${NumPy_INCLUDE_DIRS})
target_include_directories(core PUBLIC ${PYTHON_INCLUDE_DIRS})
target_include_directories(core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

python_extension_module(core)

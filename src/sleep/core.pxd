#distutils: language = c++

from libc.stdint cimport intptr_t

cdef extern from "include/sleep.h" nogil:
    cdef void sleeper(int t) except +
    cdef int busy_sleep(int milli) except +
    cdef void gpu_sleeper(int dev, unsigned long t, intptr_t stream) except +

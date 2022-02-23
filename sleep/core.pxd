#distutils: language = c++

from libc.stdint cimport intptr_t

cdef extern from "sleep.h" nogil:
    cdef void sleeper(int t);
    cdef void busy_sleep(int milli);

cdef extern from "sleep.cu" nogil:
    cdef void gpu_sleeper(int dev, unsigned long t, intptr_t stream)

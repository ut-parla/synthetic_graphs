from sleep_src.core cimport sleeper, busy_sleep
from libc.stdint cimport intptr_t
import time 

def sleep(t):
    cdef unsigned int c_t = t
    with nogil:
        sleeper(c_t)

def bsleep(t):
    cdef unsigned int c_t = t
    with nogil:
        busy_sleep(c_t)

def sleep_with_gil(t):
    cdef unsigned int c_t = t
    busy_sleep(c_t)

def spin_gil(interval):
    start = time.perf_counter()
    count = 0
    while True:
        count += 1
        end = time.perf_counter()
        if (end-start)>interval:
            break
    #print(count)

def gpu_sleep(dev, t, stream):
    cdef int c_dev = dev
    cdef unsigned long c_t = t
    cdef intptr_t c_stream = stream.ptr
    with nogil:
        gpu_sleeper(c_dev, c_t, c_stream)

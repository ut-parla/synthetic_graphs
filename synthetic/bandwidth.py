import cupy as cp
import numpy as np

import time

def generate_bandwidth(N=2**23, d=10, samples=10):

    n_devices = cp.cuda.runtime.getDeviceCount()
    n_devices += 1

    def copy(arr, fr=0, to=0):

        if fr > 0 and to == 0:
            return cp.asnumpy(arr)
        if fr == 0 and to > 0:
            return cp.asarray(arr)
        if fr == 0 and to == 0:
            return np.copy(arr)


    timing = np.zeros([n_devices, n_devices])
    for i in range(n_devices):
        for j in range(n_devices):

            if i == 0:
                A = np.zeros([N, d], dtype=np.float32)+i
            if i > 0:
                with cp.cuda.Device(i-1):
                    A = cp.zeros([N, d], dtype=np.float32)+i


            for k in range(samples):
                if j == 0:
                    start = time.perf_counter()
                    B = copy(A, fr=i, to=j)
                    stop = time.perf_counter()
                if j > 0:
                    with cp.cuda.Device(j-1):
                        stream = cp.cuda.get_current_stream()

                        start = time.perf_counter()
                        B = copy(A, fr=i, to=j)
                        stream.synchronize()
                        stop = time.perf_counter()

                timing[i, j] += (N*d)/(stop - start)

            timing[i, j] = timing[i,j]/samples

    return timing

if __name__ == '__main__':
    print("Bandwidth: ")
    print(generate_bandwidth())

#include "include/sleep.h"
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cuda.h>
#include <cuda_runtime_api.h>
#include <stdio.h>
#include <sys/time.h>
#include <unistd.h>

using namespace std;
using namespace chrono;

void gpu_sleeper(const int device, const unsigned long t, intptr_t stream_ptr) {
  printf("Warning: Attempting to use GPU sleep on a non-GPU build.\n");
}

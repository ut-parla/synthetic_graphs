#pragma once
#ifndef CYTHON_SLEEP_H
#define CYTHON_SLEEP_H

#include <chrono>
#include <time.h>
#include <unistd.h>

#ifdef SLEEP_ENABLE_NVTX
#include <nvtx3/nvtx3.hpp>
#endif

using namespace std;
using namespace chrono;

void busy_sleep(const unsigned micro) {

#ifdef SLEEP_ENABLE_NVTX
  nvtx3::scoped_range r{"Internal Sleep"};
#endif

  auto block = chrono::microseconds(micro);
  auto time_start = chrono::high_resolution_clock::now();

  auto now = chrono::high_resolution_clock::now();
  auto elapsed = chrono::duration_cast<chrono::microseconds>(now - time_start);

  do {

    now = chrono::high_resolution_clock::now();
    elapsed = chrono::duration_cast<chrono::microseconds>(now - time_start);
  } while (elapsed.count() < micro);
}

void sleeper(const unsigned int t) { sleep(t); }

void gpu_sleeper(const int device, const unsigned long t, intptr_t stream_ptr);

#endif
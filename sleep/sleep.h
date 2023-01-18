#ifndef CYTHON_SLEEP_H
#define CYTHON_SLEEP_H

#include<unistd.h>
#include<time.h>
#include<chrono>

#ifdef NVTX_ENABLE
#include<nvtx3/nvtx3.hpp>
#endif

using namespace std;
using namespace chrono;

/*
void busy_sleep(const unsigned milli){
    clock_t time_end;
    time_end = clock() + milli * CLOCKS_PER_SEC/1000;
    while(clock() < time_end)
    {
    }
}
*/

void busy_sleep(const unsigned micro){

    #ifdef NVTX_ENABLE
    nvtx3::scoped_range r{"Internal Sleep"};
    #endif

    auto block = chrono::microseconds(micro);
    auto time_start = chrono::high_resolution_clock::now();

    auto now = chrono::high_resolution_clock::now();
    auto elapsed = chrono::duration_cast<chrono::microseconds>(now - time_start);

    do{

        now = chrono::high_resolution_clock::now();
        elapsed = chrono::duration_cast<chrono::microseconds>(now - time_start);
    }
    while(elapsed.count() < micro);
}


void sleeper(const unsigned int t){
    sleep(t);
}

#endif

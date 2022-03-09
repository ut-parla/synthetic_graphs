#include<unistd.h>
#include<stdio.h>
#include<cuda.h>
#include<sys/time.h>
#include<chrono>
#include<cuda_runtime_api.h>
#include<cstdio>
#include<cstdint>

using namespace std;
using namespace chrono;

__device__ void gpu_sleep_0_bak(volatile clock_t* d_o, clock_t clock_count){
    clock_t start = clock();
    clock_t now;
    clock_t cycles;

    for(;;){
        now = clock();
        cycles = now > start ? now - start : now + (0xffffffff - start);
        if (cycles >= clock_count){
            break;
        }
    }

    *d_o = cycles;
}

__global__ void gpu_sleep_0(clock_t clock_count){
    static volatile clock_t buffer;
    gpu_sleep_0_bak(&buffer, clock_count);
}

__device__ void gpu_sleep_1_bak(unsigned long sleep_cycles)
{
    unsigned long start = clock64();
    unsigned long cycles_elapsed;
    do { cycles_elapsed = clock64() - start; } 
    while (cycles_elapsed < sleep_cycles);
}

__global__ void gpu_sleep_1(clock_t clock_count){
    gpu_sleep_1_bak(clock_count);
}


/*
__device__ void gpu_sleep_2_bak(unsigned int sleep_cycles)
{
    __nanosleep(sleep_cycles);
}

__global__ void gpu_sleep_2(unsigned int clock_count){

    //clock_count += 1;
    __nanosleep(clock_count);
    //gpu_sleep_2_bak(clock_count);
}
*/

void gpu_sleeper(const int device, const unsigned long t, intptr_t stream_ptr){
    cudaStream_t stream = reinterpret_cast<cudaStream_t>(stream_ptr);
    gpu_sleep_1<<<1, 1, device, stream>>>(t);
}

/*
int main(int argc, char* argv[]){

    int t = atoi(argv[1]);

    cudaStream_t stream;
    cudaStreamCreate(&stream);

    auto time_start = chrono::high_resolution_clock::now();
    gpu_sleeper(t, stream);
    cudaStreamSynchronize(stream);
    auto time_stop = chrono::high_resolution_clock::now();
    printf("Time elapsed: %f \n", chrono::duration<double>(time_stop - time_start)); 


    time_start = chrono::high_resolution_clock::now();
    gpu_sleeper(t, stream);
    cudaStreamSynchronize(stream);
    time_stop = chrono::high_resolution_clock::now();
    printf("Time elapsed: %f \n", chrono::duration<double>(time_stop - time_start)); 

}
*/

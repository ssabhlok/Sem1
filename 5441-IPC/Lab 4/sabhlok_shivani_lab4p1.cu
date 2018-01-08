/*
This is a cuda parallel vesion program to multiply a matrix with its transpose on the GPU
This will also multiply on the CPU to verify the reults
The matrix will be generated internally with numbers between [1.0,2.0]
*/
#include<time.h>
#include<stdio.h>
#include<stdlib.h>
#include<math.h>
#include<sys/time.h>
#define THRESHOLD .00001

//thread hierarchy
int blocks[] = {2,4,8,16,16};
int threadsPerBlock[] = {1024,512,1024,512,1024};

//matrix multiplied with its transpose on GPU device.
__global__ void MatrixTransposeMultiply_Device(double *A, double *C, int dim)
{
	for (int i = blockIdx.x; i < dim; i += gridDim.x) {
		for (int j = threadIdx.x; j < dim; j += blockDim.x) {
        double sum = 0.0;

        for (int k = 0; k < dim; k++) {
            double a = A[k * dim + i];
            double b = A[k * dim + j];
            sum += a * b;
        }
        C[i * dim + j] = sum;
    }
	}
}

//matrix multiplied with its transpose on CPU.
void MatrixTransposeMultiply_Host(double A[][1024], double C[][1024], int dim) {
    for (int i = 0; i < dim; i++)
        for (int j = 0; j < dim; j++)
        {
            double sum=0;
            for(int k = 0; k < dim; k++)
                sum += A[k][i] * A[k][j];
            C[i][j] = sum;
        }
}

//verification on CPU
int MatrixTransposeMultiply_HostValidate(double A[][1024], double C[][1024], int dim)
{
    int goodResult = 1;
    for (int i = 0; i < dim; i++)
        for (int j = 0; j < dim; j++) {
            if( abs(C[i][j] - A[i][j]) > THRESHOLD)
            {
                goodResult = 0;
                break;
            }
        }
    return goodResult;
}

int main(void) {
    double A[1024][1024], C[1024][1024],result[1024][1024];
    int dim = 1024;
    double *d_A, *d_C;
    size_t memSize = dim * dim * sizeof(double);

    //initializing matrix with random values between 1.0 to 2.0
    for (int i= 0; i< dim; i++)
        for (int j = 0; j < dim; j++)
            A[i][j] = ((double)rand() / RAND_MAX) + 1.0;

    //Allocate and initialize device memory
    cudaMalloc( (void**) &d_A, memSize);
    cudaMalloc( (void**) &d_C, memSize);
    cudaMemcpy(d_A, A, memSize, cudaMemcpyHostToDevice);
    cudaMemcpy(d_C, C, memSize, cudaMemcpyHostToDevice);

    //timing constructs 
    struct timeval TIMEVAL;
	struct timezone TIMEZONE;
    gettimeofday (&TIMEVAL, &TIMEZONE);
	double startTime = (TIMEVAL.tv_sec + TIMEVAL.tv_usec*1.0e-6);
    //multiplication on the host
    MatrixTransposeMultiply_Host(A, C, dim);
    gettimeofday (&TIMEVAL, &TIMEZONE);
    double endTime = (TIMEVAL.tv_sec + TIMEVAL.tv_usec*1.0e-6);
    //performance on CPU
	printf("\n\n***********************************************************************\n");
    printf("Time taken on CPU (sec) = %lf \n",endTime- startTime);
    printf("GFLOPS = %lf\n\n", (2L * dim * dim * (dim-1))/ (1e9*(endTime- startTime)));

    //Launch kernel
	for(int i = 0; i< 5;i++)
    {
		dim3 dimGrid(blocks[i]);
		dim3 dimBlock(threadsPerBlock[i]);
		startTime = (TIMEVAL.tv_sec + TIMEVAL.tv_usec*1.0e-6);
		//multiplication on device
		MatrixTransposeMultiply_Device<<<dimGrid, dimBlock>>>(d_A, d_C, dim);
		//cuda synchronize
		cudaThreadSynchronize();
		gettimeofday (&TIMEVAL, &TIMEZONE);
		endTime = (TIMEVAL.tv_sec + TIMEVAL.tv_usec*1.0e-6);
		//performance on GPU
		printf("With %d blocks and %d threads per block, Time taken on GPU (sec) = %lf \n",blocks[i],threadsPerBlock[i], endTime- startTime);
		printf("GFLOPS per sec = %lf\n", (2.0 * dim * dim * (dim-1))/ (1e9*(endTime- startTime)));
	}
    //copy results back to host
    cudaMemcpy(result, d_C, memSize, cudaMemcpyDeviceToHost);

    //verification
    if(!MatrixTransposeMultiply_HostValidate(C, result, dim))
        fprintf(stderr, "oops\n");
	else
		printf("Results matched \n");
	printf("\n\n***********************************************************************\n");
    //Free memory
    cudaFree(d_A);
    cudaFree(d_C);
}

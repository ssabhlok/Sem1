/*
This is a serial program to multiply a matrix with its transpose on the CPU
The matrix will be generated internally with numbers between [1.0,2.0]
*/
#include<time.h>
#include<stdio.h>
#include<stdlib.h>
#include<math.h>
#include<sys/time.h>

// matrix multiplied with its transpose on CPU.
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

int main(void) {
    double A[1024][1024], C[1024][1024];
    int dim = 1024;

    //initializing matrix with random values between 1.0 to 2.0
    for (int i= 0; i< dim; i++)
        for (int j = 0; j < dim; j++)
            A[i][j] = ((double)rand() / RAND_MAX) + 1.0;
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
    printf("GFLOPS = %.5f\n", (2L * dim * dim * (dim-1))/ (1e9*(endTime- startTime)));
	printf("\n\n***********************************************************************\n");
}

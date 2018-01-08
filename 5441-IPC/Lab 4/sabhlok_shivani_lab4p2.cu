/*
This is a cuda parallel vesion program of sobel operator on GPU
Kernel is launched with the read input image and grid to write to for output along with threshold in each iteration.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "time.h"
#include <math.h>
extern "C" {
#include "read_bmp.h"
}
void GPURelatedStuff(uint8_t *bmp_data,uint8_t *new_bmp_img, int size, uint32_t height, uint32_t width);
#define MAX_ALLOWED_CMD_ARGS  3
#define MIN_RGB_VALUE 0
#define MAX_RGB_VALUE 255
//kernel thread and block configuration combinations
int blocks[] = {64,128,64};
int threadsPerBlock[] = {64,128,32};

//kernel code
__global__ void kernel_sobel_filter(const uint8_t * device_input_data, uint8_t * device_output_data, uint32_t threshold, const uint32_t height, const uint32_t width) {
    //width is number of columns
    //height is number of rows
    int tid = threadIdx.x;
    for (int row = tid; row < height - 1; row += blockDim.x) {
        for (int block = blockIdx.x; block < width - 1; block += gridDim.x) {
            int idx = row * width + block;
            //skip 0th and 0th column
            if (idx >= 0 && idx < width)
				continue;
            if (idx % width == 0)
                continue;
			int neighborIndex[][3] = {{idx - width - 1, idx - width, idx - width + 1},
                                      {idx - 1,         idx,         idx + 1},
                                      {idx + width - 1, idx + width, idx + width + 1}};
            //To detect horizontal lines. This is effectively the gx.
            const int sobel_x[3][3] = {{-1, 0, 1},
                                       {-2, 0, 2},
                                       {-1, 0, 1}};
            // To detect vertical lines. This is effectively the gy.
            const int sobel_y[3][3] = {{1,  2,  1},
                                       {0,  0,  0},
                                       {-1, -2, -1}};
            float magnitude_x = 0.0;
            float magnitude_y = 0.0;
			//applying sobel stencil
            for (int i = 0; i < 3; ++i) {
                for (int j = 0; j < 3; ++j) {
                    magnitude_x += device_input_data[neighborIndex[i][j]] * sobel_x[i][j];
                    magnitude_y += device_input_data[neighborIndex[i][j]] * sobel_y[i][j];
                }
            }

            uint32_t mag = __double2int_ru(sqrt((double)(magnitude_x * magnitude_x + magnitude_y * magnitude_y)));
			if(mag > threshold)
            {
                 device_output_data[idx] = MAX_RGB_VALUE;
            }
            else
            {
				device_output_data[idx]= MIN_RGB_VALUE;
            }
            //device_output_data[idx] = mag;
        }
    }
}

int main(int argc, char* argv[])
{
    int cmd_arg;
    uint8_t *bmp_data;
    uint8_t *new_bmp_img;
    uint32_t wd, ht;
    FILE *out_file, *inFile;
    uint32_t total_cells;

    /*Check if no of arguments is permissible to execute*/
    if (argc != MAX_ALLOWED_CMD_ARGS)
    {
        fprintf(stderr, "Missing input file name and/or output file name in command line parameters\n");
        exit(EXIT_FAILURE);
    }
    /*Reading command line arguments and obtain the values*/
    for (cmd_arg = 1; cmd_arg < argc; cmd_arg++)
    {
        switch (cmd_arg)
        {
            case 1:
                inFile = fopen(argv[cmd_arg], "rb");
                break;

            case 2:
                out_file = fopen(argv[cmd_arg], "wb");
                break;
        }
    }
    //Read the binary bmp file into
    bmp_data = (uint8_t *)read_bmp_file(inFile);
    //Allocate space for new sobel image
    new_bmp_img = (uint8_t *)malloc(get_num_pixel());
    wd = get_image_width();
    ht = get_image_height();
	total_cells = wd * ht;
	//do GPU related memory allocation and other initializations
    GPURelatedStuff(bmp_data,new_bmp_img,total_cells,ht,wd);
    //Write the buffer into the bmp file
    write_bmp_file(out_file, new_bmp_img);

    return 0;
}

void GPURelatedStuff(uint8_t *bmp_data,uint8_t *new_bmp_img, int size, uint32_t height, uint32_t width)
{
	//initialize timing constructs
	cudaEvent_t start, stop;
	float time;
	cudaEventCreate(&start);
	cudaEventCreate(&stop);
    uint8_t * device_input_data;
    uint8_t * device_output_data;
    cudaMalloc((void **) & device_input_data, size);
    cudaMalloc((void **) & device_output_data, size);
    /* Copy the input data to the device. */
    cudaMemcpy(device_input_data, bmp_data, size, cudaMemcpyHostToDevice);
	printf("\n\n***********************************************************************\n");
    /* Launch the kernel! */
	for(int i = 0; i< 3;i++)
    {
		dim3 dimGrid(blocks[i]);
		dim3 dimBlock(threadsPerBlock[i]);
		double percent_black_cells = 0;
		uint32_t total_cells;
		int threshold   = 0;
		total_cells = width * height;
		cudaEventRecord(start, 0);
		while(percent_black_cells < 75) {
			percent_black_cells = 0;
			threshold += 1;
			kernel_sobel_filter<<<dimGrid, dimBlock>>>(device_input_data,device_output_data,threshold, height, width);
			cudaThreadSynchronize();
			cudaMemcpy(new_bmp_img, device_output_data, size, cudaMemcpyDeviceToHost);
			cudaThreadSynchronize();
			for(uint32_t i=1; i < (height-1); i++) {
				for (uint32_t j = 1; j < (width-1); j++) {
					if (new_bmp_img[i * width + j] == 0) {
						percent_black_cells++;
					}
				}
			}
			percent_black_cells = (percent_black_cells * 100.0) / (double)total_cells;
		}
		cudaEventRecord(stop, 0);
		cudaEventSynchronize(stop);
		cudaEventElapsedTime(&time, start, stop);
		printf ("With %d blocks and %d threads per block, Time for converging with %d threshold on kernel: %f s\n", blocks[i],threadsPerBlock[i],threshold,time/1e3);
	}
	printf("\n\n***********************************************************************\n");
    cudaFree(device_input_data);
    cudaFree(device_output_data);
}


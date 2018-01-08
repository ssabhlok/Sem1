/*
This is a serial vesion program of sobel operator on CPU
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "time.h"
#include <math.h>
#include<sys/time.h>
extern "C" {
#include "read_bmp.h"
}

#define MAX_ALLOWED_CMD_ARGS  3

#define MIN_RGB_VALUE 0
#define MAX_RGB_VALUE 255

int main(int argc, char* argv[])
{
    int cmd_arg;
    uint8_t *bmp_data;
    uint8_t *new_bmp_img;
    uint32_t wd, ht;
    uint32_t i, j;
    double sum1, sum2;
	double mag;
    uint32_t threshold;
    FILE *out_file, *inFile;
    uint32_t percent_black_cells = 0;
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
    threshold   = 0;
    total_cells = wd * ht;
	//timing constructs 
    struct timeval TIMEVAL;
	struct timezone TIMEZONE;
    gettimeofday (&TIMEVAL, &TIMEZONE);
	double startTime = (TIMEVAL.tv_sec + TIMEVAL.tv_usec*1.0e-6);
    //serial code
    while(percent_black_cells < 75)
    {
        percent_black_cells = 0;
        threshold += 1;
        for(i=1; i < (ht-1); i++)
        {
            for(j=1; j < (wd-1); j++)
            {
				//applying sobel stencil
                sum1 = bmp_data[ (i-1)*wd + (j+1) ] - bmp_data[ (i-1)*wd + (j-1) ] \
						+ 2*bmp_data[ (i)*wd + (j+1) ] - 2*bmp_data[ (i)*wd + (j-1) ] \
						+ bmp_data[ (i+1)*wd + (j+1) ] - bmp_data[ (i+1)*wd + (j-1) ];

                sum2 = bmp_data[ (i-1)*wd + (j-1) ] + 2*bmp_data[ (i-1)*wd + (j) ] \
						+ bmp_data[ (i-1)*wd + (j+1) ] - bmp_data[ (i+1)*wd + (j-1) ] \
						- 2*bmp_data[ (i+1)*wd + (j) ] - bmp_data[ (i+1)*wd + (j+1) ];

                mag = sqrt(sum1 * sum1 + sum2 * sum2);
                if(mag > threshold)
                {
                    new_bmp_img[ i*wd + j] = MAX_RGB_VALUE;
                }
                else
                {
                    new_bmp_img[ i*wd + j] = MIN_RGB_VALUE;
                    percent_black_cells++;
                }
            }
        }
        percent_black_cells = (percent_black_cells * 100) / total_cells;
    }

    //end bechmark measurement prior to writing out file
    gettimeofday (&TIMEVAL, &TIMEZONE);
    double endTime = (TIMEVAL.tv_sec + TIMEVAL.tv_usec*1.0e-6);
    //performance on CPU
	printf("\n\n***********************************************************************\n");
    printf("Elapsed time for Sobel Operation on CPU (sec): %f\n\n",endTime- startTime);
    printf("Theshold: %d\n",threshold);
	printf("\n\n***********************************************************************\n");
    //Write the buffer into the bmp file
    write_bmp_file(out_file, new_bmp_img);

    return 0;
}
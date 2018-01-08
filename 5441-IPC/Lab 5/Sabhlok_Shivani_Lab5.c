/*
This is an extension to serial vesion program of sobel operator on CPU
This program is parallelized by MPI as well as OpenMP
*/
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include<stdint.h>
#include<omp.h>
#include <mpi.h>
#define MAX_ALLOWED_CMD_ARGS  3

#define MIN_RGB_VALUE 0
#define MAX_RGB_VALUE 255


int main(int argc, char* argv[])
{
    int cmd_arg;//to iterate command args
    uint8_t *bmp_data;//for reading input image file
    uint8_t *new_bmp_img;//for writing final output file
    uint8_t *new_bmp_img_temp;//temp array for each MPI process to write the output file
    uint32_t wd, ht;//ht and wd of the input image
    double sum1, sum2;//used for sobel calculation
    double mag;//final sobel stencil calculation
    uint32_t threshold=0;//threshold to check for convergence
    FILE *out_file, *inFile;//file pointers for input and output image respectively
    int percent_black_cells = 0;//to keep track of percentage of black cells
    uint32_t total_cells;//to keep track of total number of cells in the image
    int rowsPerTask;//number of rows in a block assigned to each MPI process
    int	numtasks,//number of MPI processes
            taskid,//MPI process id
            i, j,rc;  //misc variables for loop iteration
    double t1, t2;//to keep track of start and end of time
    MPI_Status status;

    MPI_Init(&argc,&argv);
    MPI_Comm_rank(MPI_COMM_WORLD,&taskid);
    MPI_Comm_size(MPI_COMM_WORLD,&numtasks);
    if (numtasks < 2 ) {
        printf("Need at least two MPI tasks. Quitting...\n");
        MPI_Abort(MPI_COMM_WORLD, rc);
        exit(1);
    }
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
        }
    }

    //All MPI processes do this.
    //Read the binary bmp file into.
    bmp_data = (uint8_t *)read_bmp_file(inFile);
    wd = get_image_width();
    ht = get_image_height();
    total_cells = ht*wd;
    rowsPerTask = ceil(((double)ht)/numtasks);

    //allocating temporary write space to MPI slave processes
    if(taskid != (numtasks-1)&& taskid != 0)
    {
        new_bmp_img_temp = (uint8_t *)malloc(rowsPerTask*wd);
    }
    else if(taskid == (numtasks-1))
    {

        new_bmp_img_temp = (uint8_t *)malloc((ht - ((numtasks-1)*rowsPerTask))*wd);
    }

    omp_set_num_threads(16);
    //waiting for all MPI processes to reach before master/rank 0 MPI process starts the timing construct
    MPI_Barrier(MPI_COMM_WORLD);
    //only one process needs to write the output and clock the timing
    if(taskid == 0)
    {
        t1 = MPI_Wtime();
        out_file = fopen(argv[2], "wb");
        new_bmp_img = (uint8_t *)malloc(get_num_pixel());
        new_bmp_img_temp = (uint8_t *)malloc(rowsPerTask*wd);
    }
    ///loop to check convergence
    while(percent_black_cells < 0.75*total_cells)
    {
        MPI_Barrier(MPI_COMM_WORLD);
        percent_black_cells = 0;
        threshold += 1;
        int start = taskid*rowsPerTask;
        int end = (taskid+1)*rowsPerTask < ht ? (taskid+1)*rowsPerTask : ht;
            for(i=start; i < end; i++)
            {
                //skip the 0th row and last row
                if(i==0 || i == (ht-1)) {
                    continue;
                }
                //OMP parallelization
#pragma omp parallel for private(mag, sum1, sum2) reduction(+:percent_black_cells)
                for(j=1; j < (wd-1); j+=1)
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
                        new_bmp_img_temp[(i-taskid*rowsPerTask)*wd+j] = MAX_RGB_VALUE;
                    }
                    else
                    {
                        new_bmp_img_temp[ (i-taskid*rowsPerTask)*wd+j] = MIN_RGB_VALUE;
                        percent_black_cells++;
                    }
                }
            }
        //calling reduce to update percent black cells over the entire image.
        MPI_Allreduce(MPI_IN_PLACE, &percent_black_cells, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD);
    }
//after convergence, gathering to produce the output image
    //only the last MPI process might get lesser number of rows in chunk this a special if .. else check
    if(taskid != (numtasks-1))
    {
        MPI_Gather( new_bmp_img_temp, rowsPerTask*wd, MPI_UNSIGNED_CHAR, new_bmp_img, rowsPerTask*wd, MPI_UNSIGNED_CHAR, 0, MPI_COMM_WORLD);
    }
    else
    {
        int size = (ht - ((numtasks-1)*rowsPerTask))*wd;
        MPI_Gather( new_bmp_img_temp, size, MPI_UNSIGNED_CHAR, new_bmp_img, size, MPI_UNSIGNED_CHAR, 0, MPI_COMM_WORLD);
    }
//only one of the MPI process, rank 0 in this case will stop the timing and write the output
    if(taskid == 0) {
        t2 = MPI_Wtime();
        printf("\n\n***********************************************************************\n");
        //Write the buffer into the bmp file
        write_bmp_file(out_file, new_bmp_img);
        printf("Time taken for MPI operation: %f secs\n",t2-t1);
        printf("Threshold during convergence:: %d\n",threshold);
        printf("\n\n***********************************************************************\n");

    }

    MPI_Finalize();
    return 0;
}
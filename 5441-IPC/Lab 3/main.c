#include<stdlib.h>
#include<stdio.h>
#include "Simulation.h"

float affectRate;
float epsilon;
int numThreads;
int main(int argc, char *argv[]) {
    if(argc < 4) {
        fprintf(stderr, "Missing AFFECT RATE and/or EPSILON and/or Number of threads in command line parameters\n");
        exit(EXIT_FAILURE);
    } else if (argc > 4) {
        fprintf(stderr, "Extra parameters\n");
        exit(EXIT_FAILURE);
    }
    char c;
    int *p = &c;
     sscanf(argv[1], "%f", &affectRate);
     sscanf(argv[2], "%f", &epsilon);
     sscanf(argv[3], "%d", &numThreads);

    InitSimulation();
    ExecuteDissipation();
    TerminateSimulation();
    return EXIT_SUCCESS;
}

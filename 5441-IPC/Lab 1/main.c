#include<stdlib.h>
#include<stdio.h>
#include<string.h>
#include<float.h>
#include<time.h>

#ifndef MAX
#define MAX(a,b)            (((a) > (b)) ? (a) : (b))
#endif

#ifndef MIN
#define MIN(a,b)            (((a) < (b)) ? (a) : (b))
#endif


float affectRate;
float epsilon;
struct BOX* arrBox = NULL;
int numGridBoxes;
float maxDSV = FLT_MIN, minDSV = FLT_MAX;
float *arrDsv;
float *arrTempDsv;

struct BOX {
    int        id;
    int        upperLeftX;
    int        upperLeftY;
    int        height;
    int        width;
    int        perimeter;
    struct BOX** topNeighbors;
    int        topNeighborsCount;
    struct BOX** bottomNeighbors;
    int        bottomNeighborsCount;
    struct BOX** leftNeighbors;
    int        leftNeighborsCount;
    struct BOX** rightNeighbors;
    int        rightNeighborsCount;
    //float     dsv;
    //float     dsv_temp;
};

void InitBoxes();
void ExecuteDissipation();
void DisplayResult(int iterationCount,clock_t clockTick,time_t clockTime, double chronoTime);

int main(int argc, char *argv[]) {

    if(argc < 3) {
        fprintf(stderr, "Missing AFFECT RATE and/or EPSILON in command line parameters\n");
        exit(EXIT_FAILURE);
    } else if (argc > 3) {
        fprintf(stderr, "Extra parameters\n");
        exit(EXIT_FAILURE);
    }

    sscanf(argv[1], "%f", &affectRate);
    sscanf(argv[2], "%f", &epsilon);

    InitBoxes();
    ExecuteDissipation();


    // Free the memory used during the simulation.
    return EXIT_SUCCESS;
}

float GetMaxDsv(){
    return maxDSV;
}

float GetMinDsv(){
    return minDSV;
}

void UpdateDsv()
{
    int index = 0;
    struct BOX *currBox = arrBox;
    float avgAdjacentTemp = 0;

    maxDSV = FLT_MIN;
    minDSV = FLT_MAX;
    int idx = 0;
    int overlap = 0;
    while(idx < numGridBoxes) {
        avgAdjacentTemp = 0;
        for(index = 0; index < currBox->topNeighborsCount; index++) {
            struct BOX *neighbor =  currBox->topNeighbors[index];
            overlap = MIN(neighbor->upperLeftX + neighbor->width,currBox->upperLeftX + currBox->width) -MAX(neighbor->upperLeftX,currBox->upperLeftX);
            if(overlap > 0)
                avgAdjacentTemp +=  overlap * neighbor->dsv;
        }

        for(index = 0; index < currBox->bottomNeighborsCount; index++) {
            struct BOX* neighbor =  currBox->bottomNeighbors[index];
            overlap = MIN(neighbor->upperLeftX + neighbor->width,currBox->upperLeftX + currBox->width) -MAX(neighbor->upperLeftX,currBox->upperLeftX);
            if(overlap > 0)
                avgAdjacentTemp +=  overlap * neighbor->dsv;
        }

        for(index = 0; index < currBox->leftNeighborsCount; index++) {
            struct BOX* neighbor =  currBox->leftNeighbors[index];
            overlap = MIN(neighbor->upperLeftY + neighbor->height,currBox->upperLeftY + currBox->height) -MAX(neighbor->upperLeftY,currBox->upperLeftY);
            if(overlap > 0)
                avgAdjacentTemp +=  overlap * neighbor->dsv;
        }

        for(index = 0; index < currBox->rightNeighborsCount; index++) {
            struct BOX *neighbor =  currBox->rightNeighbors[index];
            overlap = MIN(neighbor->upperLeftY + neighbor->height,currBox->upperLeftY + currBox->height) -MAX(neighbor->upperLeftY,currBox->upperLeftY);
            if(overlap > 0)
                avgAdjacentTemp +=  overlap * neighbor->dsv;
        }
        // Box on the edge
        if(currBox->topNeighborsCount == 0)
        {
            avgAdjacentTemp +=  (currBox->width) * currBox->dsv;
        }
        if(currBox->bottomNeighborsCount == 0)
        {
            avgAdjacentTemp +=  (currBox->width) * currBox->dsv;
        }
        if(currBox->leftNeighborsCount == 0)
        {
            avgAdjacentTemp +=  (currBox->height) * currBox->dsv;
        }
        if(currBox->rightNeighborsCount == 0)
        {
            avgAdjacentTemp +=  (currBox->height) * currBox->dsv;
        }
        //Avg weighted sum
        avgAdjacentTemp/= currBox->perimeter;

        // Store the updated box DSV in a separate indexed memory location.
        currBox->dsv_temp = currBox->dsv - affectRate * (currBox->dsv - avgAdjacentTemp);

        // Calculate the maximum DSV within the grid.
        if( currBox->dsv_temp  > maxDSV) {
            maxDSV =  currBox->dsv_temp;
        }

        // Calculate the minimum DSV within the grid.
        if( currBox->dsv_temp  < minDSV) {
            minDSV =  currBox->dsv_temp ;
        }
        idx++;
        currBox++;
    }
    currBox = arrBox;
    idx = 0;
    while (idx < numGridBoxes)
    {
        currBox->dsv = currBox->dsv_temp;
        idx++;
        currBox++;
    }
}
void ExecuteDissipation() {
    struct timespec start_c, end_c;
    double diff;
    long NS_PER_US = 1000;
    clock_gettime(CLOCK_REALTIME,& start_c);

    clock_t begin, end;
    time_t start, finish;
    clock_t clockTick = 0;
    time_t clockTime=0;
    int iterationCount = 0;
    time(&start);
    begin = clock();
    while((GetMaxDsv() - GetMinDsv()) > epsilon*GetMaxDsv()) {
        UpdateDsv();
        iterationCount++;
    }
    end = clock();
    time(&finish);
    clock_gettime(CLOCK_REALTIME,& end_c);
    diff = (double)( ((end_c.tv_sec - start_c.tv_sec)*CLOCKS_PER_SEC) + ((end_c.tv_nsec -start_c.tv_nsec)/NS_PER_US) );
    clockTick = end - begin;
    clockTime = finish - start;
    DisplayResult(iterationCount,clockTick,clockTime,diff);
}
void InitBoxes()
{
    int numRows, numCols;
    scanf("%d%d%d", &numGridBoxes, &numRows, &numCols);
    arrBox = calloc(numGridBoxes,sizeof(struct BOX));
    arrDsv = calloc(numGridBoxes,sizeof(float));
    arrTempDsv = calloc(numGridBoxes, sizeof(float));
    float *arrCurrDsv = arrDsv;
    struct BOX* currBox = arrBox;
    int iterator;
    int id;
    int count = 0;
    while(count < numGridBoxes) {
        scanf("%d",&currBox->id);
        scanf("%d%d%d%d", &(currBox->upperLeftY), &(currBox->upperLeftX), &(currBox->height), &(currBox->width));
        scanf("%d", &(currBox->topNeighborsCount));
        currBox->topNeighbors = malloc(sizeof(struct BOX*) * currBox->topNeighborsCount);
        for(iterator = 0; iterator < currBox->topNeighborsCount; iterator++) {
            scanf("%d", &id);
            currBox->topNeighbors[iterator] =  arrBox + id;
        }

        scanf("%d", &(currBox->bottomNeighborsCount));
        currBox->bottomNeighbors = malloc(sizeof(struct BOX*) * currBox->bottomNeighborsCount);
        for(iterator = 0; iterator < currBox->bottomNeighborsCount; iterator++) {
            scanf("%d", &id);
            currBox->bottomNeighbors[iterator] =  arrBox + id;
        }

        scanf("%d", &(currBox->leftNeighborsCount ));
        currBox->leftNeighbors = malloc(sizeof(struct BOX*) * currBox->leftNeighborsCount);
        for(iterator = 0; iterator < currBox->leftNeighborsCount; iterator++) {
            scanf("%d", &id);
            currBox->leftNeighbors[iterator] =  arrBox + id;
        }

        scanf("%d", &(currBox->rightNeighborsCount));
        currBox->rightNeighbors = malloc(sizeof(struct BOX*) * currBox->rightNeighborsCount);
        for(iterator = 0; iterator < currBox->rightNeighborsCount; iterator++) {
            scanf("%d", &id);
            currBox->rightNeighbors[iterator] =  arrBox + id;
        }
        //**************************
        scanf("%f", arrDsv[id]);
       // scanf("%f", &(currBox->dsv));
        //****************************************

        // Calculate the maximum DSV value within the intial grid configuration.
        if(currBox->dsv > maxDSV) {
            //maxDSV = currBox->dsv;
            maxDSV = arrDsv[id];
        }

        // Calculate the minimum DSV value within the intial grid configuration.
        if(currBox->dsv < minDSV) {
            //minDSV = currBox->dsv;
           minDSV = arrDsv[id];
        }


        currBox->perimeter = 2 * (currBox->width + currBox->height);
        currBox++;
        count++;
    }

    // Skip the last -1 from the stdin indicating the end of input.
    scanf("%*d");

}

void DisplayResult(int iterationCount,clock_t clockTick,time_t clockTime, double chronoTime) {
    printf("\n\n***********************************************************************\n");
    printf("dissipation converged in %d iterations,\n", iterationCount);
    printf("\twith max DSV = %g and min DSV = %g\n", GetMaxDsv(), GetMinDsv());
    printf("\taffect rate  = %g and epsilon = %g\n\n", affectRate, epsilon);
    printf("elapsed convergence loop time (clock): %ld \n", clockTick);
    printf("elapsed convergence loop time  (time): %ld \n", clockTime);
    printf("elapsed convergence loop time  (chrono): %lf \n", chronoTime);
    printf("***********************************************************************\n\n\n");
}
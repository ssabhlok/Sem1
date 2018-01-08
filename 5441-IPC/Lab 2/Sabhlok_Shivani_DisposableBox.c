#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<stdint.h>
#include<float.h>
#include "Box.h"
#include "Simulation.h" //for affect rate
#include<pthread.h>

#ifndef MAX
#define MAX(a,b)            (((a) > (b)) ? (a) : (b))
#endif

#ifndef MIN
#define MIN(a,b)            (((a) < (b)) ? (a) : (b))
#endif

struct BOX* arrBox = NULL;
int numGridBoxes;
float maxDSV = FLT_MIN, minDSV = FLT_MAX;
float *arrDsv;
float *arrTempDsv;
pthread_t *arrPthread;
int *arrPthreadStartIndex;

//this can only be calculated after all the threads have returned
float GetMaxDsv(){
    maxDSV = arrTempDsv[0];
    int i;
    for(i =0;i<numGridBoxes;i++)
    {
        if(maxDSV < arrTempDsv[i])
            maxDSV = arrTempDsv[i];
    }
    return maxDSV;
}
//this can only be calculated after all the threads have returned
float GetMinDsv(){
    minDSV = arrTempDsv[0];
    int i;
    for(i =0;i<numGridBoxes;i++)
    {
        if(minDSV > arrTempDsv[i])
            minDSV = arrTempDsv[i];
    }
    return minDSV;
}

void InitBoxes()
{
    int numRows, numCols;
    scanf("%d%d%d", &numGridBoxes, &numRows, &numCols);
    arrBox = calloc(numGridBoxes,sizeof(struct BOX));
    arrDsv = calloc(numGridBoxes,sizeof(float));
    arrTempDsv = calloc(numGridBoxes, sizeof(float));
    //we point it to temp because thats what saves the updated value during simulation
    float *arrCurrDsv = arrTempDsv;
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
        scanf("%f", arrCurrDsv);
        // scanf("%f", &(currBox->dsv));
        //****************************************

        // Calculate the maximum DSV value within the intial grid configuration.
        if(*arrCurrDsv > maxDSV) {
            //maxDSV = currBox->dsv;
            maxDSV = *arrCurrDsv;
        }

        // Calculate the minimum DSV value within the intial grid configuration.
        if(*arrCurrDsv < minDSV) {
            //minDSV = currBox->dsv;
            minDSV = *arrCurrDsv;
        }


        currBox->perimeter = 2 * (currBox->width + currBox->height);
        currBox++;
        arrCurrDsv++;
        count++;
    }

    // Skip the last -1 from the stdin indicating the end of input.
    scanf("%*d");
    //New disposable thread related work.. we do cyclic thread distribution
    arrPthread = malloc(sizeof(pthread_t) * numThreads);
    arrPthreadStartIndex = malloc(sizeof(int) * numThreads);
    for(iterator = 0; iterator < numThreads; iterator++) {
        arrPthreadStartIndex[iterator] = iterator;
    }

}

void *ThreadSafe_UpdateDsv(void *startingIndex)
{
    int index=0;
    struct BOX *currBox = arrBox + *((int *) startingIndex);
    float avgAdjacentTemp = 0;
    float *arrCurrDsv = arrTempDsv + *((int *) startingIndex);
    int idx = *((int *) startingIndex);
    int overlap = 0;
    while(idx < numGridBoxes) {
        avgAdjacentTemp = 0;
        for(index = 0; index < currBox->topNeighborsCount; index++) {
            struct BOX *neighbor =  currBox->topNeighbors[index];
            overlap = MIN(neighbor->upperLeftX + neighbor->width,currBox->upperLeftX + currBox->width) -MAX(neighbor->upperLeftX,currBox->upperLeftX);
            if(overlap > 0)
                avgAdjacentTemp +=  overlap * arrDsv[neighbor->id];
        }

        for(index = 0; index < currBox->bottomNeighborsCount; index++) {
            struct BOX* neighbor =  currBox->bottomNeighbors[index];
            overlap = MIN(neighbor->upperLeftX + neighbor->width,currBox->upperLeftX + currBox->width) -MAX(neighbor->upperLeftX,currBox->upperLeftX);
            if(overlap > 0)
                avgAdjacentTemp +=  overlap * arrDsv[neighbor->id];
        }

        for(index = 0; index < currBox->leftNeighborsCount; index++) {
            struct BOX* neighbor =  currBox->leftNeighbors[index];
            overlap = MIN(neighbor->upperLeftY + neighbor->height,currBox->upperLeftY + currBox->height) -MAX(neighbor->upperLeftY,currBox->upperLeftY);
            if(overlap > 0)
                avgAdjacentTemp +=  overlap * arrDsv[neighbor->id];
        }

        for(index = 0; index < currBox->rightNeighborsCount; index++) {
            struct BOX *neighbor =  currBox->rightNeighbors[index];
            overlap = MIN(neighbor->upperLeftY + neighbor->height,currBox->upperLeftY + currBox->height) -MAX(neighbor->upperLeftY,currBox->upperLeftY);
            if(overlap > 0)
                avgAdjacentTemp +=  overlap * arrDsv[neighbor->id];
        }
        // Box on the edge
        if(currBox->topNeighborsCount == 0)
        {
            avgAdjacentTemp +=  (currBox->width) * arrDsv[currBox->id];
        }
        if(currBox->bottomNeighborsCount == 0)
        {
            avgAdjacentTemp +=  (currBox->width) * arrDsv[currBox->id];
        }
        if(currBox->leftNeighborsCount == 0)
        {
            avgAdjacentTemp +=  (currBox->height) * arrDsv[currBox->id];
        }
        if(currBox->rightNeighborsCount == 0)
        {
            avgAdjacentTemp +=  (currBox->height) * arrDsv[currBox->id];
        }
        //Avg weighted sum
        avgAdjacentTemp/= currBox->perimeter;

        // Store the updated box DSV in a separate indexed memory location.
        *arrCurrDsv = arrDsv[currBox->id] - affectRate * (arrDsv[currBox->id] - avgAdjacentTemp);

        idx+= numThreads;
        arrCurrDsv+=numThreads;
        currBox+=numThreads;
    }
    pthread_exit(NULL);
}
void UpdateDsv()
{
    memcpy(arrDsv,arrTempDsv, sizeof(float)*numGridBoxes);
    int index = 0;
    //doing cyclic distribution
    for(index = 0; index<numThreads;index++)
    {
        pthread_create(arrPthread+index,NULL,ThreadSafe_UpdateDsv,arrPthreadStartIndex+index);
    }
    //wait for all threads to come back
    for(index=0;index<numThreads;index++)
    {
        pthread_join(arrPthread[index],NULL);
    }
}
void FreeMemory()
{
    int i;
    for(i =0; i<numGridBoxes;i++)
    {
        free(arrBox[i].leftNeighbors);
        free(arrBox[i].rightNeighbors);
        free(arrBox[i].topNeighbors);
        free(arrBox[i].bottomNeighbors);
    }
    free(arrBox);
    free(arrDsv);
    free(arrTempDsv);
    free(arrPthread);
    free(arrPthreadStartIndex);
}
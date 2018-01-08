

#ifndef LAB_2_FINAL_BOX_H
#define LAB_2_FINAL_BOX_H
#include<pthread.h>

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
};
void InitBoxes();
float GetMaxDsv();
float GetMinDsv();
void UpdateDsv();
void FreeMemory();
void *ThreadSafe_UpdateDsv(void *startingIndex);
extern pthread_t *arrPthread;
extern float *arrDsv;
extern float *arrTempDsv;
extern int *arrPthreadStartIndex;
extern int numGridBoxes;
#endif //LAB_2_FINAL_BOX_H

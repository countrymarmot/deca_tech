//
// cpu_buffers.h
// libarcherite
//
// Created by Craig Bishop on 23 February 2012
// Copyright 2012 All rights reserved
//

#ifndef H_CPU_BUFFERS
#define H_CPU_BUFFERS

#include <string>
#include <stdlib.h>
#include <stdio.h>

#define ROUTE_POINT_LIST_SIZE 3000

namespace o4
{
  namespace cpuroutestage
  {
    struct CPUBuffers
    {
      int* endPointX;
      int* endPointY;
      int* routeComplete;
      float* minDistance;
      
      int openListSize;
      int* openListFreeIndex;
      int* openListScanRange;
      int* openListValid;
      int* openListPositionX;
      int* openListPositionY;
      int* openListGScore;
      int* openListFScore;
      int* openListParentIndex;

      int closedListSize;
      int* closedListNextIndex;
      int* closedListPositionX;
      int* closedListPositionY;
      int* closedListParentIndex;

      int* bestListPositionX;
      int* bestListPositionY;
      int* bestListGScore;
      int* bestListFScore;
      int* bestListParentIndex;

      int* scoreListValid;
      int* scoreListPositionX;
      int* scoreListPositionY;
      int* scoreListGScore;
      int* scoreListFScore;
      int* scoreListParentIndex;
      
      int routePointGridChunkSize;
      int routePointListSize;
      int routePointGridWidth;
      int routePointGridHeight;
      int *routePointListNum;
      int *routePointListNetID;
      int *routePointListPositionX;
      int *routePointListPositionY;
      float *routePointListTraceWidth;

      int numItems;
      size_t totalMem;

      CPUBuffers(const int numWorkItems, const int pOpenListSize,
          const int pClosedListSize, const int gridWidth, const int gridHeight,
          const int gridChunk)
      {
        numItems = numWorkItems;
        totalMem = 0;
        openListSize = pOpenListSize;
        closedListSize = pClosedListSize;

        endPointX = new int[numWorkItems];
        totalMem += numWorkItems * sizeof(int);
        endPointY = new int[numWorkItems];
        totalMem += numWorkItems * sizeof(int);
        routeComplete = new int[numWorkItems];
        totalMem += numWorkItems * sizeof(int);
        minDistance = new float[numWorkItems];
        totalMem += numWorkItems * sizeof(float);

        openListFreeIndex = new int[numWorkItems];
        totalMem += numWorkItems * sizeof(int);
        openListScanRange = new int[numWorkItems];
        totalMem += numWorkItems * sizeof(int);
        openListValid = new int[numWorkItems * openListSize];
        totalMem += numWorkItems * openListSize * sizeof(int);
        openListPositionX = new int[numWorkItems * openListSize];
        totalMem += numWorkItems * openListSize * sizeof(int);
        openListPositionY = new int[numWorkItems * openListSize];
        totalMem += numWorkItems * openListSize * sizeof(int);
        openListGScore = new int[numWorkItems * openListSize];
        totalMem += numWorkItems * openListSize * sizeof(int);
        openListFScore = new int[numWorkItems * openListSize];
        totalMem += numWorkItems * openListSize * sizeof(int);
        openListParentIndex = new int[numWorkItems * openListSize];
        totalMem += numWorkItems * openListSize * sizeof(int);

        closedListNextIndex = new int[numWorkItems];
        totalMem += numWorkItems * sizeof(int);
        closedListPositionX = new int[numWorkItems * closedListSize];
        totalMem += numWorkItems * closedListSize *  sizeof(int);
        closedListPositionY = new int[numWorkItems * closedListSize];
        totalMem += numWorkItems * closedListSize *  sizeof(int);
        closedListParentIndex = new int[numWorkItems * closedListSize];
        totalMem += numWorkItems * closedListSize *  sizeof(int);

        bestListPositionX = new int[numWorkItems];
        totalMem += numWorkItems * sizeof(int);
        bestListPositionY = new int[numWorkItems];
        totalMem += numWorkItems * sizeof(int);
        bestListGScore = new int[numWorkItems];
        totalMem += numWorkItems * sizeof(int);
        bestListFScore = new int[numWorkItems];
        totalMem += numWorkItems * sizeof(int);
        bestListParentIndex = new int[numWorkItems];
        totalMem += numWorkItems * sizeof(int);

        scoreListValid = new int[numWorkItems * 8];
        totalMem += numWorkItems * 8 * sizeof(int);
        scoreListPositionX = new int[numWorkItems * 8];
        totalMem += numWorkItems * 8 * sizeof(int);
        scoreListPositionY = new int[numWorkItems * 8];
        totalMem += numWorkItems * 8 * sizeof(int);
        scoreListGScore = new int[numWorkItems * 8];
        totalMem += numWorkItems * 8 * sizeof(int);
        scoreListFScore = new int[numWorkItems * 8];
        totalMem += numWorkItems * 8 * sizeof(int);
        scoreListParentIndex = new int[numWorkItems * 8];
        totalMem += numWorkItems * 8 * sizeof(int);

        routePointListSize = ROUTE_POINT_LIST_SIZE;
        routePointGridChunkSize = gridChunk;
        routePointGridWidth = gridWidth;
        routePointGridHeight = gridHeight;
        int gridSize = gridWidth * gridHeight;
        routePointListNum = new int[numItems * gridSize];
        memset(routePointListNum, 0, numItems * gridSize * sizeof(int));
        totalMem += numWorkItems * sizeof(int) * gridSize;
        routePointListNetID = new int[numItems * routePointListSize * gridSize];
        totalMem += numWorkItems * routePointListSize * sizeof(int) * gridSize;
        routePointListPositionX = new int[numItems * routePointListSize * gridSize];
        totalMem += numWorkItems * routePointListSize * sizeof(int) * gridSize;
        routePointListPositionY = new int[numItems * routePointListSize * gridSize];
        totalMem += numWorkItems * routePointListSize * sizeof(int) * gridSize;
        routePointListTraceWidth = new float[numItems * routePointListSize * gridSize];
        totalMem += numWorkItems * routePointListSize * sizeof(float) * gridSize;
      }

      ~CPUBuffers()
      {
        delete[] endPointX;
        delete[] endPointY;
        delete[] routeComplete;
        delete[] minDistance;

        delete[] openListFreeIndex;
        delete[] openListScanRange;
        delete[] openListValid;
        delete[] openListPositionX;
        delete[] openListPositionY;
        delete[] openListGScore;
        delete[] openListFScore;
        delete[] openListParentIndex;

        delete[] closedListNextIndex;
        delete[] closedListPositionX;
        delete[] closedListPositionY;
        delete[] closedListParentIndex;

        delete[] bestListPositionX;
        delete[] bestListPositionY;
        delete[] bestListGScore;
        delete[] bestListFScore;
        delete[] bestListParentIndex;

        delete[] scoreListValid;
        delete[] scoreListPositionX;
        delete[] scoreListPositionY;
        delete[] scoreListGScore;
        delete[] scoreListFScore;
        delete[] scoreListParentIndex;

        delete[] routePointListNum;
        delete[] routePointListNetID;
        delete[] routePointListPositionX;
        delete[] routePointListPositionY;
        delete[] routePointListTraceWidth;
      }
    };
  }
}

#endif


//
// cpu_router.cpp
// libarcherite
//
// Created by Craig Bishop on 23 February 2012
// Copyright 2012 All rights reserved
//

#include "cpu_router.h"
#include <vector>
#include <climits>
#include <algorithm>
#include <math.h>
#include <assert.h>

using namespace o4;
using namespace cpuroutestage;

void transform_xy(float* x, float* y, float sX, float sY, float t,
    float dieX, float dieY)
{
  // translate
  float tx = *x - dieX;
  float ty = *y - dieY;

  // rotate
  float rx = (tx * cos(t)) - (ty * sin(t));
  float ry = (tx * sin(t)) + (ty * cos(t));
  
  // store
  *x = rx + sX + dieX;
  *y = ry + sY + dieY;
}


void o4::cpuroutestage::cpurouter_startRoutes(int a, int b, const zinc::Design& design,
    zinc::RoutingWorkResults& workResults, CPUBuffers* buffers,
    const zinc::Shifts& shifts, int routeIndex, int batchStart,
    int designLayerIndex, int shiftStart)
{
  int openListSize = buffers->openListSize;
  float startX;
  float startY;
  float endX;
  float endY;
  int numRoutes = design.layers(designLayerIndex).routedefinitions_size();
  const zinc::RouteDefinition& routeDef =
    design.layers(designLayerIndex).routedefinitions(routeIndex);
  float gMinSpace = design.rules().minglobalspacing();
  float traceWidth =
    design.layers(designLayerIndex).routedefinitions(routeIndex).tracewidth();
  
  for (int tid = a; tid < b; tid++)
  {
    startX = routeDef.xy0().x();
    startY = routeDef.xy0().y();
    if (routeDef.isshifted0())
    {
      int dieIndex = routeDef.dieindex0();
      const zinc::Point& xyShift =
          shifts.units(shiftStart + batchStart + tid).die(dieIndex).shift();
      float theta = shifts.units(shiftStart + batchStart + tid).die(dieIndex).theta();
      const zinc::Point& dieCenter = design.unitdie(dieIndex).outline().center();
      transform_xy(&startX, &startY, xyShift.x(), xyShift.y(), theta,
          dieCenter.x(), dieCenter.y());
    }

    endX = routeDef.xy1().x();
    endY = routeDef.xy1().y();
    if (routeDef.isshifted1())
    {
      int dieIndex = routeDef.dieindex1();
      const zinc::Point& xyShift =
          shifts.units(shiftStart + batchStart + tid).die(dieIndex).shift();
      float theta = shifts.units(shiftStart + batchStart + tid).die(dieIndex).theta();
      const zinc::Point& dieCenter = design.unitdie(dieIndex).outline().center();
      transform_xy(&endX, &endY, xyShift.x(), xyShift.y(), theta,
          dieCenter.x(), dieCenter.y());
    }

    buffers->endPointX[tid] = endX;
    buffers->endPointY[tid] = endY;

    // check that the unit is within spec before routing

    // reset completion flags and array indices
    if (!workResults.routedunits(batchStart + tid).routinggood())
      buffers->routeComplete[tid] = 1;
    else
      buffers->routeComplete[tid] = 0;
    buffers->openListFreeIndex[tid] = 0;
    buffers->closedListNextIndex[tid] = 0;
    buffers->minDistance[tid] = (traceWidth / 2.0f) + gMinSpace;

    // init the openlist freelist structure
    for (int i = 0; i < openListSize; i++)
    {
      buffers->openListValid[(tid * openListSize) + i] = i + 1;
    }
    buffers->openListValid[(tid * openListSize) +
        openListSize - 1] = INT_MAX;

    // add the first node to the openlist
    int sindex = buffers->openListFreeIndex[tid];
    buffers->openListFreeIndex[tid] =
        buffers->openListValid[(tid * openListSize) + sindex];
    buffers->openListValid[(tid * openListSize) + sindex] = -1;
    buffers->openListPositionX[(tid * openListSize) + sindex] = startX;
    buffers->openListPositionY[(tid * openListSize) + sindex] = startY;
    buffers->openListGScore[(tid * openListSize) + sindex] = 0;
    buffers->openListFScore[(tid * openListSize) + sindex] = 0;
    buffers->openListParentIndex[(tid * openListSize) + sindex] = -1;

    // init the scan range
    buffers->openListScanRange[tid] = sindex + 1;
  }
}

/// SELECT BEST ///
void o4::cpuroutestage::cpurouter_selectBest(int a, int b,
    CPUBuffers* buffers, int routeIndex)
{
  int openListSize = buffers->openListSize;
  for (int tid = a; tid < b; tid++)
  {
    if (buffers->routeComplete[tid] <= 0)
    {
      // find the index of the lowest fScore node in the open list
      int lowest = INT_MAX;
      int index = -1;
      int scanRange = buffers->openListScanRange[tid];
      for (int i = 0; i < scanRange; i++)
      {
        if (buffers->openListFScore[(tid * openListSize) + i] < lowest &&
          buffers->openListValid[(tid * openListSize) + i] < 0)
        {
          lowest = buffers->openListFScore[(tid * openListSize) + i];
          index = i;
        }
      }

      int bestX = buffers->openListPositionX[(tid * openListSize) + index];
      int bestY = buffers->openListPositionY[(tid * openListSize) + index];

      // copy this node to the best node
      buffers->bestListPositionX[tid] =
          buffers->openListPositionX[(tid * openListSize) + index];
      buffers->bestListPositionY[tid] = 
          buffers->openListPositionY[(tid * openListSize) + index];
      buffers->bestListGScore[tid] =
          buffers->openListGScore[(tid * openListSize) + index];
      buffers->bestListFScore[tid] =
          buffers->openListFScore[(tid * openListSize) + index];
      buffers->bestListParentIndex[tid] =
          buffers->openListParentIndex[(tid * openListSize) + index];

      // remove the selected node from the open list
      buffers->openListValid[(tid * openListSize) + index] =
          buffers->openListFreeIndex[tid];
      buffers->openListFreeIndex[tid] = index;
    }
  }
}
/// SELECT BEST ///

/// GET NEW OPEN NODES ///
void o4::cpuroutestage::cpurouter_getNewOpenNodes(int a, int b,
    CPUBuffers* buffers, int routeIndex)
{
  int openListSize = buffers->openListSize;
  int closedListSize = buffers->closedListSize;
  for (int tid = a; tid < b; tid++)
  {
    if (buffers->routeComplete[tid] <= 0)
    {
      // get position and gScore of best node
      int posX = buffers->bestListPositionX[tid];
      int posY = buffers->bestListPositionY[tid];
      int gScore = buffers->bestListGScore[tid];

      // add best node to the closed list
      int cindex = buffers->closedListNextIndex[tid];
      buffers->closedListNextIndex[tid] = cindex + 1;
      buffers->closedListPositionX[(tid * closedListSize) + cindex] =
          posX;
      buffers->closedListPositionY[(tid * closedListSize) + cindex] =
          posY;
      buffers->closedListParentIndex[(tid * closedListSize) + cindex] =
          buffers->bestListParentIndex[tid];

      // fill in all the nodes around the best node into the score list
      buffers->scoreListValid[(tid * 8) + 0] = -1;
      buffers->scoreListPositionX[(tid * 8) + 0] = posX - 1;
      buffers->scoreListPositionY[(tid * 8) + 0] = posY;
      buffers->scoreListGScore[(tid * 8) + 0] = gScore;
      buffers->scoreListParentIndex[(tid * 8) + 0] = cindex;

      buffers->scoreListValid[(tid * 8) + 1] = -1;
      buffers->scoreListPositionX[(tid * 8) + 1] = posX + 1;
      buffers->scoreListPositionY[(tid * 8) + 1] = posY;
      buffers->scoreListGScore[(tid * 8) + 1] = gScore;
      buffers->scoreListParentIndex[(tid * 8) + 1] = cindex;

      buffers->scoreListValid[(tid * 8) + 2] = -1;
      buffers->scoreListPositionX[(tid * 8) + 2] = posX;
      buffers->scoreListPositionY[(tid * 8) + 2] = posY - 1;
      buffers->scoreListGScore[(tid * 8) + 2] = gScore;
      buffers->scoreListParentIndex[(tid * 8) + 2] = cindex;

      buffers->scoreListValid[(tid * 8) + 3] = -1;
      buffers->scoreListPositionX[(tid * 8) + 3] = posX;
      buffers->scoreListPositionY[(tid * 8) + 3] = posY + 1;
      buffers->scoreListGScore[(tid * 8) + 3] = gScore;
      buffers->scoreListParentIndex[(tid * 8) + 3] = cindex;

      buffers->scoreListValid[(tid * 8) + 4] = -1;
      buffers->scoreListPositionX[(tid * 8) + 4] = posX - 1;
      buffers->scoreListPositionY[(tid * 8) + 4] = posY - 1;
      buffers->scoreListGScore[(tid * 8) + 4] = gScore;
      buffers->scoreListParentIndex[(tid * 8) + 4] = cindex;

      buffers->scoreListValid[(tid * 8) + 5] = -1;
      buffers->scoreListPositionX[(tid * 8) + 5] = posX - 1;
      buffers->scoreListPositionY[(tid * 8) + 5] = posY + 1;
      buffers->scoreListGScore[(tid * 8) + 5] = gScore;
      buffers->scoreListParentIndex[(tid * 8) + 5] = cindex;

      buffers->scoreListValid[(tid * 8) + 6] = -1;
      buffers->scoreListPositionX[(tid * 8) + 6] = posX + 1;
      buffers->scoreListPositionY[(tid * 8) + 6] = posY - 1;
      buffers->scoreListGScore[(tid * 8) + 6] = gScore;
      buffers->scoreListParentIndex[(tid * 8) + 6] = cindex;

      buffers->scoreListValid[(tid * 8) + 7] = -1;
      buffers->scoreListPositionX[(tid * 8) + 7] = posX + 1;
      buffers->scoreListPositionY[(tid * 8) + 7] = posY + 1;
      buffers->scoreListGScore[(tid * 8) + 7] = gScore;
      buffers->scoreListParentIndex[(tid * 8) + 7] = cindex;
    }
  }
}
/// GET NEW OPEN NODES ///

/// SCORE NODES ///
void scoreNode(const zinc::Design& design, const zinc::Shifts& shifts,
    const zinc::Layer& layer, DieLayerList* dieLayers, CPUBuffers* buffers,
    int tid, int i, int endX, int endY, int preCost, float packageWidth,
    float packageHeight, int closedBound, int openBound, float netID,
    float traceWidth, float pMinX, float pMaxX, float pMinY, float pMaxY,
    int batchStart, int shiftStart)
{
  int closedListSize = buffers->closedListSize;
  int openListSize = buffers->openListSize;

  int posX = buffers->scoreListPositionX[(tid * 8) + i];
  int posY = buffers->scoreListPositionY[(tid * 8) + i];

  int pwo2 = packageWidth / 2;
  int pho2 = packageHeight / 2;

  float cx, cy;
  float radius;
  float dist;

  // check for out of routing area
  if (posX < pMinX || posX >= pMaxX || posY < pMinY || posY >= pMaxY)
  {
    buffers->scoreListValid[(tid * 8) + i] = INT_MAX;
    return;
  }

  // apply scoring algorithm -- optimized for 45 deg turns
  int h_diag = std::min(abs(posX - endX), abs(posY - endY));
  int h_straight = abs(posX - endX) + abs(posY - endY);
  int hScore = (14 * h_diag) + (10 * (h_straight - (2 * h_diag)));
  int gScore = buffers->scoreListGScore[(tid * 8) + i] + 10 + preCost;
  int fScore = gScore + (10 * hScore);

  buffers->scoreListGScore[(tid * 8) + i] = gScore;
  buffers->scoreListFScore[(tid * 8) + i] = fScore;

  // now check for uniqueness
  for (int j = 0; j < closedBound; j++)
  {
    if (posX == buffers->closedListPositionX[(tid * closedListSize) + j] &&
      posY == buffers->closedListPositionY[(tid * closedListSize) + j])
    {
      buffers->scoreListValid[(tid * 8) + i] = INT_MAX;
      return;
    }
  }
  for (int j = 0; j < openBound; j++)
  {
    if (posX == buffers->openListPositionX[(tid * openListSize) + j] &&
      posY == buffers->openListPositionY[(tid * openListSize) + j])
    {
      buffers->scoreListValid[(tid * 8) + i] = INT_MAX;
      return;
    }
  }

  int addtlCost = 0;
  float minDistf = buffers->minDistance[tid];

  // check for minimum distance from fixed pads
  int pnetID;
  size_t numPads = layer.fixedpads_size();
  for (size_t pi = 0; pi < numPads; pi++)
  {
    const zinc::Pad& pad = layer.fixedpads(pi);
    pnetID = pad.netid();
    if (pnetID == netID)
      continue;
    cx = pad.xy().x();
    cy = pad.xy().y();
    radius = pad.radius();
    dist = (posX - cx)*(posX - cx) + (posY - cy)*(posY - cy);
    dist = sqrt(dist) - radius;
    if (dist < minDistf)
    {
      buffers->scoreListValid[(tid * 8) + i] = INT_MAX;
      return;
    }
    else if (dist < minDistf + 10.0)
      addtlCost = 400;
    else if (dist < minDistf + 20.0)
      addtlCost = std::max(addtlCost, 200);
    else if (dist < minDistf + 30.0)
      addtlCost = std::max(addtlCost, 100);
  }

  // check for minimum distance from dynamic pads
  for (int dieLayerIndex = 0; dieLayerIndex < (*dieLayers).size(); dieLayerIndex++)
  {
    int dieIndex = 0;//(*dieLayers)[dieLayerIndex].first;
    zinc::DieLayer* dieLayer = (*dieLayers)[dieLayerIndex].second;
    numPads = dieLayer->dynamicpads_size();
    float shiftX = shifts.units(shiftStart + batchStart + tid).die(dieIndex).shift().x();
    float shiftY = shifts.units(shiftStart + batchStart + tid).die(dieIndex).shift().y();
    float theta = shifts.units(shiftStart + batchStart + tid).die(dieIndex).theta();
    float dieX = design.unitdie(dieIndex).outline().center().x();
    float dieY = design.unitdie(dieIndex).outline().center().y();
    for (size_t pi = 0; pi < numPads; pi++)
    {
      const zinc::Pad& pad = dieLayer->dynamicpads(pi);
      pnetID = pad.netid();
      if (pnetID == netID)
        continue;
      cx = pad.xy().x();
      cy = pad.xy().y();
      transform_xy(&cx, &cy, shiftX, shiftY, theta, dieX, dieY);
      radius = pad.radius();
      dist = (posX - cx)*(posX - cx) + (posY - cy)*(posY - cy);
      dist = sqrt(dist) - radius;
      if (dist < minDistf)
      {
        buffers->scoreListValid[(tid * 8) + i] = INT_MAX;
        return;
      }
      else if (dist < minDistf + 10.0)
        addtlCost = 400;
      else if (dist < minDistf + 20.0)
        addtlCost = std::max(addtlCost, 200);
      else if (dist < minDistf + 30.0)
        addtlCost = std::max(addtlCost, 100);
    }
  }
  
  // check minimum distance from path line segs
  size_t numSegs = layer.fixedpaths_size();
  float segmindist;
  for (size_t pi = 0; pi < numSegs; pi++)
  {
    const zinc::Path& path = layer.fixedpaths(pi);
    pnetID = path.netid();
    if (pnetID == netID)
      continue;
    segmindist = minDistf  + (path.tracewidth() / 2.0f);
    float dist;
    float x0 = path.xy0().x();
    float y0 = path.xy0().y();
    float x1 = path.xy1().x();
    float y1 = path.xy1().y();

    if (abs(x0 - x1) < 0.001 && abs(y0 - y1) < 0.001)
      continue;

    float l2 = (x0 - x1)*(x0 - x1) + (y0 - y1)*(y0 - y1);

    if (l2 < 0.1)
    {
      dist = sqrt(l2);
      if (dist < segmindist)
      {
        buffers->scoreListValid[(tid * 8) + i] = INT_MAX;
        return;
      }
      else if (dist < segmindist + 10.0)
        addtlCost = 400;
      else if (dist < segmindist + 20.0)
        addtlCost = std::max(addtlCost, 200);
      else if (dist < segmindist + 30.0)
        addtlCost = std::max(addtlCost, 100);
    }
    else
    {
      float sx1, sy1;
      sx1 = posX - x0;
      sy1 = posY - y0;
      float sx2, sy2;
      sx2 = x1 - x0;
      sy2 = y1 - y0;
      float t = (sx1 * sx2) + (sy1 * sy2);
      t /= l2;

      if (t < 0.0)
        dist = sqrt((posX - x0)*(posX - x0) + (posY - y0)*(posY - y0));
      else if (t > 1.0)
        dist = sqrt((posX - x1)*(posX - x1) + (posY - y1)*(posY - y1));
      else
      {
        float projX = x0 + ((x1 - x0) * t);
        float projY = y0 + ((y1 - y0) * t);
        dist = sqrt((posX - projX)*(posX - projX) + (posY - projY)*(posY - projY));
      }

      if (dist < segmindist)
      {
        buffers->scoreListValid[(tid * 8) + i] = INT_MAX;
        return;
      }
      else if (dist < segmindist + 10.0)
        addtlCost = 400;
      else if (dist < segmindist + 20.0)
        addtlCost = std::max(addtlCost, 200);
      else if (dist < segmindist + 30.0)
        addtlCost = std::max(addtlCost, 100);
    }
  }

  int rplSize = buffers->routePointListSize;
  int gridSize = buffers->routePointGridWidth * buffers->routePointGridHeight;
  int gridWidth = buffers->routePointGridWidth;
  int gridHeight = buffers->routePointGridHeight;
  int chunkSize = buffers->routePointGridChunkSize;

  int gridX = (posX + pwo2) / chunkSize;
  int gridY = (posY + pho2) / chunkSize;
  int minGX = std::max(gridX - 1, 0);
  int maxGX = std::min(gridX + 1, gridWidth - 1);
  int minGY = std::max(gridY - 1, 0);
  int maxGY = std::min(gridY + 1, gridHeight - 1);
  int numPoints, ioff;
  int px, py;
  int dsq;

  float targetWidth;
  int minDistSq;
  int minDistSq10;
  int minDistSq20;
  int minDistSq30;

  for (int gx = minGX; gx <= maxGX; gx++)
  {
    for (int gy = minGY; gy <= maxGY; gy++)
    {
      ioff = tid * gridSize;
      numPoints = buffers->routePointListNum[ioff + (gy * gridWidth) + gx];
      for (int pi = 0; pi < numPoints; pi++)
      {
        px = buffers->routePointListPositionX[((ioff + (gy * gridWidth) + gx) *
            rplSize) + pi];
        py = buffers->routePointListPositionY[((ioff + (gy * gridWidth) + gx) *
            rplSize) + pi];
        pnetID = buffers->routePointListNetID[((ioff + (gy * gridWidth) + gx) *
            rplSize) + pi];
        targetWidth = buffers->routePointListTraceWidth[((ioff + (gy * gridWidth) + gx) *
            rplSize) + pi] / 2.0;
        if (pnetID == netID)
          continue;
        dsq = ((px - posX)*(px - posX) + (py - posY)*(py - posY));

        minDistSq = pow(targetWidth + minDistf, 2);
        minDistSq10 = pow(targetWidth + minDistf + 10.0, 2);
        minDistSq20 = pow(targetWidth + minDistf + 20.0, 2);
        minDistSq30 = pow(targetWidth + minDistf + 30.0, 2);

        if (dsq <= minDistSq)
        {
          buffers->scoreListValid[(tid * 8) + i] = INT_MAX;
          return;
        }
        else if (dsq <= minDistSq10)
          addtlCost = 400;
        else if (dsq <= minDistSq20)
          addtlCost = std::max(addtlCost, 200);
        else if (dsq <= minDistSq30)
          addtlCost = std::max(addtlCost, 100);
      }
    }
  }

  buffers->scoreListFScore[(tid * 8) + i] += addtlCost;
}

void o4::cpuroutestage::cpurouter_scoreNodes(int a, int b,
    const zinc::Design& design, const zinc::Shifts& shifts,
    CPUBuffers* buffers, DieLayerList* dieLayers, int routeIndex,
    int designLayerIndex, int batchStart, int shiftStart)
{
  float packageWidth = design.package().outline().width();
  float packageHeight = design.package().outline().height();
  float keepInWidth = design.rules().routekeepin().width();
  float keepInHeight = design.rules().routekeepin().height();
  float pMinX = design.rules().routekeepin().center().x() - (keepInWidth / 2.0);
  float pMaxX = design.rules().routekeepin().center().x() + (keepInWidth / 2.0);
  float pMinY = design.rules().routekeepin().center().y() - (keepInHeight / 2.0);
  float pMaxY = design.rules().routekeepin().center().y() + (keepInHeight / 2.0);

  float traceWidth =
    design.layers(designLayerIndex).routedefinitions(routeIndex).tracewidth();
  int netID = design.layers(designLayerIndex).routedefinitions(routeIndex).netid();
  const zinc::Layer& layer = design.layers(designLayerIndex);

  for (int tid = a; tid < b; tid++)
  {
    if (buffers->routeComplete[tid] <= 0)
    {
      // get the endpoint
      int endX = buffers->endPointX[tid];
      int endY = buffers->endPointY[tid];

      // get the openlist and closedlist boundaries
      int closedListBound = buffers->closedListNextIndex[tid];
      int openListBound = buffers->openListScanRange[tid];

      // score the node distance
      scoreNode(design, shifts, layer, dieLayers, buffers, tid, 0, endX,
          endY, 0, packageWidth, packageHeight, closedListBound, openListBound,
          netID, traceWidth, pMinX, pMaxX, pMinY, pMaxY, batchStart, shiftStart);
      scoreNode(design, shifts, layer, dieLayers, buffers, tid, 1, endX,
          endY, 0, packageWidth, packageHeight, closedListBound, openListBound,
          netID, traceWidth, pMinX, pMaxX, pMinY, pMaxY, batchStart, shiftStart);
      scoreNode(design, shifts, layer, dieLayers, buffers, tid, 2, endX,
          endY, 0, packageWidth, packageHeight, closedListBound, openListBound,
          netID, traceWidth, pMinX, pMaxX, pMinY, pMaxY, batchStart, shiftStart);
      scoreNode(design, shifts, layer, dieLayers, buffers, tid, 3, endX,
          endY, 0, packageWidth, packageHeight, closedListBound, openListBound,
          netID, traceWidth, pMinX, pMaxX, pMinY, pMaxY, batchStart, shiftStart);
      scoreNode(design, shifts, layer, dieLayers, buffers, tid, 4, endX,
          endY, 4, packageWidth, packageHeight, closedListBound, openListBound,
          netID, traceWidth, pMinX, pMaxX, pMinY, pMaxY, batchStart, shiftStart);
      scoreNode(design, shifts, layer, dieLayers, buffers, tid, 5, endX,
          endY, 4, packageWidth, packageHeight, closedListBound, openListBound,
          netID, traceWidth, pMinX, pMaxX, pMinY, pMaxY, batchStart, shiftStart);
      scoreNode(design, shifts, layer, dieLayers, buffers, tid, 6, endX,
          endY, 4, packageWidth, packageHeight, closedListBound, openListBound,
          netID, traceWidth, pMinX, pMaxX, pMinY, pMaxY, batchStart, shiftStart);
      scoreNode(design, shifts, layer, dieLayers, buffers, tid, 7, endX,
          endY, 4, packageWidth, packageHeight, closedListBound, openListBound,
          netID, traceWidth, pMinX, pMaxX, pMinY, pMaxY, batchStart, shiftStart);
    }
  }
}
/// SCORE NODES ///

/// ADD OPEN NODES ///
void addOpenNode(CPUBuffers* buffers, int tid, int i, int openListSize)
{
  // if node is score list is valid, copy it
  if (buffers->scoreListValid[(tid * 8) + i] < 0)
  {
    // get a new openlist node index
    int ni = buffers->openListFreeIndex[tid];
    buffers->openListFreeIndex[tid] =
        buffers->openListValid[(tid * openListSize) + ni];
    buffers->openListScanRange[tid] =
        std::max(buffers->openListScanRange[tid], ni + 1);

    // copy over to open list
    buffers->openListValid[(tid * openListSize) + ni] = -1;
    buffers->openListPositionX[(tid * openListSize) + ni] =
        buffers->scoreListPositionX[(tid * 8) + i];
    buffers->openListPositionY[(tid * openListSize) + ni] =
        buffers->scoreListPositionY[(tid * 8) + i];
    buffers->openListGScore[(tid * openListSize) + ni] =
        buffers->scoreListGScore[(tid * 8) + i];
    buffers->openListFScore[(tid * openListSize) + ni] =
        buffers->scoreListFScore[(tid * 8) + i];
    buffers->openListParentIndex[(tid * openListSize) + ni] =
        buffers->scoreListParentIndex[(tid * 8) + i];
  }
}

void o4::cpuroutestage::cpurouter_addOpenNodes(int a, int b,
    CPUBuffers* buffers, int routeIndex)
{
  int openListSize = buffers->openListSize;
  for (int tid = a; tid < b; tid++)
  {
    if (buffers->routeComplete[tid] <= 0)
    {
      addOpenNode(buffers, tid, 0, openListSize);
      addOpenNode(buffers, tid, 1, openListSize);
      addOpenNode(buffers, tid, 2, openListSize);
      addOpenNode(buffers, tid, 3, openListSize);
      addOpenNode(buffers, tid, 4, openListSize);
      addOpenNode(buffers, tid, 5, openListSize);
      addOpenNode(buffers, tid, 6, openListSize);
      addOpenNode(buffers, tid, 7, openListSize);
    }
  }
}
/// ADD OPEN NODES ///

/// EVALUATE ///
int o4::cpuroutestage::cpurouter_evaluate(int a, int b, 
    zinc::RoutingWorkResults& workResults,
    CPUBuffers* buffers, int routeIndex, int batchStart)
{
  int done = 1;
  for (int tid = a; tid < b; tid++)
  {
    if (abs(buffers->bestListPositionX[tid] - buffers->endPointX[tid]) < 0.5f &&
      abs(buffers->bestListPositionY[tid] - buffers->endPointY[tid]) < 0.5f)
    {
      buffers->routeComplete[tid] = 1;
    }
    if (buffers->closedListNextIndex[tid] >= buffers->closedListSize)
    {
      buffers->routeComplete[tid] = 1;
      workResults.mutable_routedunits(batchStart + tid)->set_routinggood(false);
    }
    
    if (buffers->routeComplete[tid] <= 0)
      done = 0;
  }

  return done;
}
/// EVALUATE ///

/// COLLECT ///
void o4::cpuroutestage::cpurouter_collect(int a, int b,
    const zinc::Design& design, zinc::RoutingWorkResults& workResults,
    CPUBuffers* buffers, int designLayerIndex, int routedLayerIndex,
    int routeIndex, int batchStart)
{
  const zinc::Layer& layer = design.layers(designLayerIndex);
  const zinc::RouteDefinition& routeDef =
    design.layers(designLayerIndex).routedefinitions(routeIndex);
  int numRoutes = layer.routedefinitions_size();
  int closedListSize = buffers->closedListSize;
  int rplSize = buffers->routePointListSize;
  int netID = routeDef.netid();
  int gridSize = buffers->routePointGridWidth * buffers->routePointGridHeight;
  int gridWidth = buffers->routePointGridWidth;
  int gridHeight = buffers->routePointGridHeight;
  int chunkSize = buffers->routePointGridChunkSize;
  float traceWidth = layer.routedefinitions(routeIndex).tracewidth();
  int packageWidth = design.package().outline().width();
  int packageHeight = design.package().outline().height();
  int pwo2 = packageWidth / 2;
  int pho2 = packageHeight / 2;

  int x, y;
  int lx, ly;
  int ix, iy, ioff;
  int ldx, ldy;
  int dx, dy;
  int pi, ci, ei, numPoints;
  int rpli;
  for (int i = a; i < b; i++)
  {
    if (buffers->closedListNextIndex[i] > buffers->closedListSize ||
        workResults.routedunits(batchStart + i).routinggood() == false)
    {
      workResults.mutable_routedunits(batchStart + i)->set_routinggood(false);
      continue;
    }
    zinc::RoutedLayer* routedLayer =
        workResults.mutable_routedunits(batchStart + i)->
        mutable_routedlayers(routedLayerIndex);
    zinc::Route* route = routedLayer->add_routes();
    route->set_routeindex(routeIndex);

    lx = buffers->bestListPositionX[i];
    ly = buffers->bestListPositionY[i];
    zinc::Point* firstPoint = route->add_points();
    firstPoint->set_x(lx);
    firstPoint->set_y(ly);
    ix = (lx + pwo2) / chunkSize;
    iy = (ly + pho2) / chunkSize;
    ioff = i * gridSize;
    ci = buffers->routePointListNum[ioff + (iy * gridWidth) + ix]++;
    buffers->routePointListPositionX[((ioff + (iy * gridWidth) + ix) * rplSize) + ci] = lx;
    buffers->routePointListPositionY[((ioff + (iy * gridWidth) + ix) * rplSize) + ci] = ly;
    buffers->routePointListNetID[((ioff + (iy * gridWidth) + ix) * rplSize) + ci] = netID;
    buffers->routePointListTraceWidth[((ioff + (iy * gridWidth) + ix) * rplSize) + ci] = traceWidth;
    pi = buffers->bestListParentIndex[i];

    x = buffers->closedListPositionX[(i * closedListSize) + pi];
    y = buffers->closedListPositionY[(i * closedListSize) + pi];
    ix = (x + pwo2) / chunkSize;
    iy = (y + pho2) / chunkSize;
    ioff = i * gridSize;
    ci = buffers->routePointListNum[ioff + (iy * gridWidth) + ix]++;
    buffers->routePointListPositionX[((ioff + (iy * gridWidth) + ix) * rplSize) + ci] = x;
    buffers->routePointListPositionY[((ioff + (iy * gridWidth) + ix) * rplSize) + ci] = y;
    buffers->routePointListNetID[((ioff + (iy * gridWidth) + ix) * rplSize) + ci] = netID;
    ldx = x - lx;
    ldy = y - ly;
    lx = x;
    ly = y;
    pi = buffers->closedListParentIndex[(i * closedListSize) + pi];

    while (pi >= 0)
    {
      x = buffers->closedListPositionX[(i * closedListSize) + pi];
      y = buffers->closedListPositionY[(i * closedListSize) + pi];
      ix = (x + pwo2) / chunkSize;
      iy = (y + pho2) / chunkSize;
      ioff = i * gridSize;
      ci = buffers->routePointListNum[ioff + (iy * gridWidth) + ix]++;
      if (ci >= rplSize)
        break;
      buffers->routePointListPositionX[((ioff + (iy * gridWidth) + ix) * rplSize) + ci] = x;
      buffers->routePointListPositionY[((ioff + (iy * gridWidth) + ix) * rplSize) + ci] = y;
      buffers->routePointListNetID[((ioff + (iy * gridWidth) + ix) * rplSize) + ci] = netID;
      dx = x - lx;
      dy = y - ly;
      pi = buffers->closedListParentIndex[(i * closedListSize) + pi];
      if (dx != ldx || dy != ldy || pi < 0)
      {
        zinc::Point* point = route->add_points();
        point->set_x(x);
        point->set_y(y);
      }
      ldx = dx;
      ldy = dy;
      lx = x;
      ly = y;
    }
  }
}
/// COLLECT ///

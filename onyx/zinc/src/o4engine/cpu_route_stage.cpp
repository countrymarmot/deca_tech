//
// cpu_route_stage.cpp
// libarcherite
//
// Created by Craig Bishop on 23 February 2012
// Copyright 2012 All rights reserved
//

#include "cpu_route_stage.h"
#include "cpu_buffers.h"
#include "cpu_router.h"
#include "tbb/tbb.h"
#include <stdio.h>
#include <math.h>
#include <algorithm>

using namespace o4;
using namespace cpuroutestage;
using namespace tbb;

static const int kOpenListSize = 15000;
static const int kClosedListSize = 8000;
static const int kChunkSize = 500;
static const int kBatchSize = 500;

/*
 * Used by Intel TBB for map of operator() on the
 * supplied bounded range
 */
class ApplyRouter
{
private:
  const zinc::Design& m_Design;
  const zinc::Shifts& m_Shifts;
  zinc::RoutingWorkResults& m_WorkResults;
  CPUBuffers* m_Buffers;
  int m_RouteIndex;
  int m_RoutedLayerIndex;
  int m_DesignLayerIndex;
  int m_BatchStart;
  int m_ShiftStart;
  DieLayerList m_DieLayers;

public:
  void operator() (const blocked_range<int>& r) const
  {
    cpurouter_startRoutes(r.begin(), r.end(), m_Design, m_WorkResults,
        m_Buffers, m_Shifts, m_RouteIndex, m_BatchStart, m_DesignLayerIndex,
        m_ShiftStart);
    int done = 0;
    int iterations = 0;
    while (!done)
    {
      cpurouter_selectBest(r.begin(), r.end(), m_Buffers, m_RouteIndex);
      cpurouter_getNewOpenNodes(r.begin(), r.end(), m_Buffers, m_RouteIndex);
      cpurouter_scoreNodes(r.begin(), r.end(), m_Design, m_Shifts, m_Buffers,
          const_cast<DieLayerList*>(&m_DieLayers), m_RouteIndex, m_DesignLayerIndex,
          m_BatchStart, m_ShiftStart);
      cpurouter_addOpenNodes(r.begin(), r.end(), m_Buffers, m_RouteIndex);
      done = cpurouter_evaluate(r.begin(), r.end(), m_WorkResults, m_Buffers,
          m_RouteIndex, m_BatchStart);
      iterations++;
    }
    cpurouter_collect(r.begin(), r.end(), m_Design, m_WorkResults, m_Buffers,
        m_DesignLayerIndex, m_RoutedLayerIndex, m_RouteIndex, m_BatchStart);
    //printf("Block done. Route #%i. Size %lu. Iterations %i\n", m_RouteIndex,
       //r.size(), iterations);
  }

  ApplyRouter(const zinc::Design& design, zinc::RoutingWorkResults& workResults,
      const zinc::Shifts& shifts, CPUBuffers* buffers, int routeIndex,
      int routedLayerIndex, int designLayerIndex, int batchStart,
      int shiftStart) :
          m_Design(design), m_Shifts(shifts), m_WorkResults(workResults)
  {
    m_Buffers = buffers;
    m_RouteIndex = routeIndex;
    m_RoutedLayerIndex = routedLayerIndex;
    m_DesignLayerIndex = designLayerIndex;
    m_BatchStart = batchStart;
    m_ShiftStart = shiftStart;

    // find all relevant layers
    int designLayerNum = design.layers(m_DesignLayerIndex).number();
    for (int dieIndex = 0; dieIndex < design.unitdie_size(); dieIndex++)
    {
      for (int i = 0; i < design.unitdie(dieIndex).dielayers_size(); i++)
      {
        const zinc::DieLayer& dieLayer = design.unitdie(dieIndex).dielayers(i);
        if (dieLayer.number() == designLayerNum && (dieLayer.dynamicpads_size() > 0 ||
            dieLayer.dynamicpaths_size() > 0 || dieLayer.dynamicshapes_size() > 0))
          m_DieLayers.push_back(DieLayerPair(dieIndex, const_cast<zinc::DieLayer*>
              (&design.unitdie(dieIndex).dielayers(i))));
      }
    }
  }
};

/*
 * Prints out correctly formatted amount of memory
 * used by CPUBuffers structure
 *
 * @param buffers Allocated CPUBuffers structure
 */
void printRoutingMemory(CPUBuffers* buffers)
{
  if (buffers->totalMem > 1024 * 1024)
    printf("Total routing memory: %lu MB\n", buffers->totalMem / (1024 * 1024));
  else
    printf("Total routing memory: %lu kB\n", buffers->totalMem / 1024);
}


/*
 * Rounds input float to neared integer
 *
 * @param n Floating-point number
 * @return n rounded to nearest integer; 0.5 rounds up
 */
float round(float n)
{
  return floor(n + 0.5);
}

/*
 * Adds enough RoutedUnits to the RoutingWorkResults to
 * fit all of the routing results
 *
 * @param workResults zinc::RoutingWorkResults to fill
 * @param count How many units to create
 */
void precreateRoutedUnits(zinc::RoutingWorkResults& workResults,
    const zinc::RoutingWorkItem& workItem)
{
  for (int i = workItem.workrange().start();
      i <= workItem.workrange().end(); i++)
  {
    zinc::RoutedUnit* routedUnit = workResults.add_routedunits();
    routedUnit->mutable_unit()->CopyFrom(workItem.shifts().units(i));
    // see if out of spec, let auto-router mark if bad otherwise
    routedUnit->set_routinggood(workItem.shifts().units(i).inspec());
  }
}

/*
 * Creates a RoutedLayer in the repeated routedLayers field of
 * each RoutedUnit
 *
 * @param workResults zinc::RoutingWorkResults to fill
 * @param count How many units to process
 * @param layer Layer number to create for
 * @return Index of RoutedLayer in the RoutedUnit list
 */
int precreateRoutedLayer(zinc::RoutingWorkResults& workResults,
    int count, int layer)
{
  for (int i = 0; i < count; i++)
  {
    zinc::RoutedLayer* routedLayer =
        workResults.mutable_routedunits(i)->add_routedlayers();
    routedLayer->set_layernumber(layer);
  }
  return workResults.routedunits(0).routedlayers_size() - 1;
}

bool o4::cpu_route_stage(const zinc::RoutingWorkItem& workItem,
      zinc::RoutingWorkResults* workResults, bool verbose)
{
  workResults->mutable_workrange()->CopyFrom(workItem.workrange());
  workResults->set_panelid(workItem.panelid());

  int numUnits = workItem.workrange().end() -
      workItem.workrange().start() + 1;
  int numLayers = workItem.design().layers_size();
  const zinc::Design& design = workItem.design();
  int shiftStart = workItem.workrange().start();

  // calculate the parameters for the routed point storage grid
  int gridWidth = design.package().outline().width() / kChunkSize;
  int gridHeight = design.package().outline().height() / kChunkSize;
  if (int(round(design.package().outline().width())) % kChunkSize > 0)
    gridWidth++;
  if (int(round(design.package().outline().height())) % kChunkSize > 0)
    gridHeight++;

  // only run maximum of kBatchSize units at a time
  int numBatches = numUnits / kBatchSize;
  if (numUnits % kBatchSize > 0)
    numBatches++;
  if (verbose)
  {
    printf("Number of batches: %i\n", numBatches);
    printf("Pre-creating routed unit containers\n");
  }
  precreateRoutedUnits(*workResults, workItem);

  // run all the routes for each layer
  for (int layerIndex = 0; layerIndex < numLayers; layerIndex++)
  {
    const zinc::Layer& layer = workItem.design().layers(layerIndex);
    // first check if there are any routes to do
    int numRoutes = layer.routedefinitions_size();
    if (numRoutes == 0)
      continue;
    if (verbose)
      printf("Precreating routed layer containers\n");
    int routedLayerIndex = precreateRoutedLayer(*workResults, numUnits,
        layer.number());
    if (verbose)
      printf("Routing layer: %s\nNumber of routes: %i\n", layer.name().c_str(),
          numRoutes);

    // run each batch
    for (int batchIndex = 0; batchIndex < numBatches; batchIndex++)
    {
      int batchStart = batchIndex * kBatchSize;
      int batchEnd = std::min(batchStart + kBatchSize, numUnits - 1);
      int batchSize = batchEnd - batchStart;

      CPUBuffers buffers(batchSize, kOpenListSize, kClosedListSize,
          gridWidth, gridHeight, kChunkSize);
      if (verbose)
        printRoutingMemory(&buffers);
      for (int routeIndex = 0; routeIndex < numRoutes; routeIndex++)
      {
        parallel_for(blocked_range<int>(0, batchSize),
            ApplyRouter(workItem.design(), *workResults, workItem.shifts(),
              &buffers, routeIndex, routedLayerIndex, layerIndex, batchStart,
              shiftStart));
        //ApplyRouter(workItem.design(), *workResults, workItem.shifts(),
              //&buffers, routeIndex, routedLayerIndex, layerIndex, batchStart)
          //(blocked_range<int>(0, batchSize));
        if (verbose)
          printf("Finished route %i of %i; batch %i of %i\n", routeIndex + 1,
              numRoutes, batchIndex + 1, numBatches);
      }
    }
  }
  return true;
}


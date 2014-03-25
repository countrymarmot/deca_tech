//
// cpu_router.h
// libarcherite
//
// Created by Craig Bishop on 23 February 2012
// Copyright 2012 All rights reserved
//

#ifndef H_CPU_ROUTER
#define H_CPU_ROUTER

#include "zinc.pb.h"
#include "cpu_buffers.h"
#include <utility>

namespace o4
{
  namespace cpuroutestage
  {
    typedef std::pair<int, zinc::DieLayer*> DieLayerPair;
    typedef std::vector<DieLayerPair> DieLayerList;

    void cpurouter_startRoutes(int a, int b, const zinc::Design& design,
        zinc::RoutingWorkResults& workResults, CPUBuffers* buffers,
        const zinc::Shifts& shifts, int routeIndex, int batchStart,
        int designLayerIndex, int shiftStart);
    void cpurouter_selectBest(int a, int b,
        CPUBuffers* buffers, int routeIndex);
    void cpurouter_getNewOpenNodes(int a, int b,
         CPUBuffers* buffers, int routeIndex);
    void cpurouter_scoreNodes(int a, int b,
        const zinc::Design& design, const zinc::Shifts& shifts,
        CPUBuffers* buffers, DieLayerList* dieLayers, int routeIndex,
        int designLayerIndex, int batchStart, int shiftStart);
    void cpurouter_addOpenNodes(int a, int b, CPUBuffers* buffers,
        int routeIndex);
    int cpurouter_evaluate(int a, int b, 
        zinc::RoutingWorkResults& workResults,
        CPUBuffers* buffers, int routeIndex, int batchStart);
    void cpurouter_collect(int a, int b,
        const zinc::Design& design, zinc::RoutingWorkResults& workResults,
        CPUBuffers* buffers, int designLayerIndex, int routedLayerIndex,
        int routeIndex, int batchStart);
 
  }
}

#endif


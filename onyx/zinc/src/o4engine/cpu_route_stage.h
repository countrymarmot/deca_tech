//
// cpu_route_stage.h
// libarcherite
//
// Created by Craig Bishop on 23 February 2012
// Copyright 2012 All rights reserved
//

#ifndef H_CPU_ROUTE_STAGE
#define H_CPU_ROUTE_STAGE

#include "zinc.pb.h"

namespace o4
{
  /*
   * Runs the CPU-based auto-router on with the design, shifts,
   * and work range specified in workItem
   *
   * @param workItem zinc::RoutingWorkItem containing all
   *                 info to complete routing
   * @param workResults Pointer to zinc::RoutingWorkResults that
   *                    will contain all completed routes
   * @param verbose Whether to print progress information
   * @return true on success, false on error
   */
  bool cpu_route_stage(const zinc::RoutingWorkItem& workItem,
      zinc::RoutingWorkResults* workResults, bool verbose=false);
}

#endif


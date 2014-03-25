//
// smooth_stage.h
// zinc
//
// Created by Craig Bishop on 24 January 2013
// Copyright 2013 All rights reserved
//

#ifndef H_SMOOTH_STAGE
#define H_SMOOTH_STAGE

#include "zinc.pb.h"

namespace smoother
{
  bool smooth_stage(const zinc::RoutingWorkItem& workItem,
      zinc::RoutingWorkResults* workResults, bool verbose=false);
}

#endif


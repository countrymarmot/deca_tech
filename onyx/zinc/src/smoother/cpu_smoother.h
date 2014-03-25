//
// cpu_smoother.h
// zinc
//
// Created by Craig Bishop on 24 January 2013
// Copyright 2013 All rights reserved
//

#ifndef H_CPU_SMOOTHER
#define H_CPU_SMOOTHER

#include "zinc.pb.h"

void SmoothRoutes(int a, int b, const zinc::RoutingWorkItem& workItem,
    zinc::RoutingWorkResults* workResults);

#endif


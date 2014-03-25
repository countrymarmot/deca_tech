//
// smooth_stage.cpp
// zinc
//
// Created by Craig Bishop on 24 January 2013
// Copyright 2013 All rights reserved
//

#include "smooth_stage.h"
#include "cpu_smoother.h"
#include "tbb/tbb.h"
#include <stdio.h>
#include <algorithm>

using namespace tbb;

static const int kSmoothBatchSize = 500;

class ApplySmoother
{
private:
  zinc::RoutingWorkResults* m_WorkResults;
  const zinc::RoutingWorkItem& m_WorkItem;
  bool m_Verbose;

public:
  void operator() (const blocked_range<int>& r) const
  {
    SmoothRoutes(r.begin(), r.end(), m_WorkItem,  m_WorkResults);
    if (m_Verbose)
      printf("Block smoothed. Size %lu.\n", r.size());
  }

  ApplySmoother(const zinc::RoutingWorkItem& workItem,
      zinc::RoutingWorkResults* workResults, bool verbose) :
    m_WorkItem(workItem)
  {
    m_WorkResults = workResults;
    m_Verbose = verbose; 
  }
};

bool smoother::smooth_stage(const zinc::RoutingWorkItem& workItem,
    zinc::RoutingWorkResults* workResults, bool verbose)
{
  int numUnits = workResults->routedunits_size();
  // only run maximum of kSmoothBatchSize units at a time
  int numBatches = numUnits / kSmoothBatchSize;
  if (numUnits % kSmoothBatchSize > 0)
    numBatches++;

  for (int batchIndex = 0; batchIndex < numBatches; batchIndex++)
  {
    int batchStart = batchIndex * kSmoothBatchSize;
    int batchEnd = std::min(batchStart + kSmoothBatchSize, numUnits - 1);
    int batchSize = batchEnd - batchStart;
    parallel_for(blocked_range<int>(batchStart, batchEnd),
        ApplySmoother(workItem, workResults, verbose));
  }
  return true;
}


//
// cpu_smoother.cpp
// zinc
//
// Created by Craig Bishop on 24 January 2013
// Copyright 2013 All rights reserved
//

#include "cpu_smoother.h"
#include <math.h>
#include <algorithm>

void transform_xy_smoothing(float* x, float* y, float sX, float sY, float t,
    float dieX, float dieY)
{
  // rotate
  float rx = (*x * cos(t)) - (*y * sin(t));
  float ry = (*x * sin(t)) + (*y * cos(t));
  
  // store
  *x = rx + sX;
  *y = ry + sY;
}

float distancePointToLineSeg(float px, float py, float lx0, float ly0,
    float lx1, float ly1)
{
  float l2 = pow(lx0 - lx1, 2) + pow(ly0 - ly1, 2);
  if (l2 < 0.1)
  {
    return sqrt(pow(lx0 - px, 2) + pow(ly0 - py, 2));
  }
  float sx1 = px - lx0;
  float sy1 = py - ly0;
  float sx2 = lx1 - lx0;
  float sy2 = ly1 - ly0;
  float t = (sx1 * sx2) + (sy1 * sy2);
  t /= l2;
  if (t < 0.0)
    return sqrt(pow(px - lx0, 2) + pow(py - ly0, 2));
  else if (t > 1.0)
    return sqrt(pow(px - lx1, 2) + pow(py - ly1, 2));
  else
  {
    float projX = lx0 + ((lx1 - lx0) * t);
    float projY = ly0 + ((ly1 - ly0) * t);
    return sqrt(pow(px - projX, 2) + pow(py - projY, 2));
  }
}

bool ccw(float ax, float ay, float bx, float by, float cx, float cy)
{
  return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax);
}

bool lineSegsIntersect(float ax0, float ay0, float ax1, float ay1,
    float bx0, float by0, float bx1, float by1)
{
  if (distancePointToLineSeg(bx0, by0, ax0, ay0, ax1, ay1) < 0.1 ||
        distancePointToLineSeg(bx1, by1, ax0, ay0, ax1, ay1) < 0.1)
    return true;

  return (ccw(ax0, ay0, bx0, by0, bx1, by1) != ccw(ax1, ay1, bx0, by0, bx1, by1)) &&
      (ccw(ax0, ay0, ax1, ay1, bx0, by0) != ccw(ax0, ay0, ax1, ay1, bx1, by1));
}

float distanceLineSegToLineSeg(float ax0, float ay0, float ax1, float ay1,
    float bx0, float by0, float bx1, float by1)
{
  if (lineSegsIntersect(ax0, ay0, ax1, ay1, bx0, by0, bx1, by1))
    return 0;

  float d1 = distancePointToLineSeg(bx0, by0, ax0, ay0, ax1, ay1);
  float d2 = distancePointToLineSeg(bx1, by1, ax0, ay0, ax1, ay1);
  float d3 = distancePointToLineSeg(ax0, ay0, bx0, by0, bx1, by1);
  float d4 = distancePointToLineSeg(ax1, ay1, bx0, by0, bx1, by1);
  return std::min(std::min(std::min(d1, d2), d3), d4);
}

bool checkLineSeg(float x0, float y0, float x1, float y1, const zinc::Shifts& shifts,
    float minDist, int tid, const zinc::RouteDefinition& routeDef, int shiftStart,
    const zinc::Layer& layer, const zinc::Design& design, int routeIndex,
    const zinc::RoutedLayer& routedLayer)
{
  const zinc::Unit& unit = shifts.units(shiftStart + tid);

  // first check against prestratum
  // fixed pads first
  size_t numPads = layer.fixedpads_size();
  for (size_t pi = 0; pi < numPads; pi++)
  {
    const zinc::Pad pad = layer.fixedpads(pi);
    int pnetID = pad.netid();
    if (pnetID == routeDef.netid())
      continue;
    float cx = pad.xy().x();
    float cy = pad.xy().y();
    float radius = pad.radius();

    if (distancePointToLineSeg(cx, cy, x0, y0, x1, y1) - radius < minDist)
      return false;
  }

  // dynamic pads
  for (int dieIndex = 0; dieIndex < 1/*design.unitdie_size()*/; dieIndex++)
  {
    const zinc::Die& die = design.unitdie(dieIndex);
    for (int dieLayerIndex = 0; dieLayerIndex < die.dielayers_size(); dieLayerIndex++)
    {
      const zinc::DieLayer& dieLayer = die.dielayers(dieLayerIndex);
      numPads = dieLayer.dynamicpads_size();
      for (size_t pi = 0; pi < numPads; pi++)
      {
        const zinc::Pad& pad = dieLayer.dynamicpads(pi);
        int pnetID = pad.netid();
        if (pnetID == routeDef.netid())
          continue;
        float shiftX = unit.die(dieIndex).shift().x();
        float shiftY = unit.die(dieIndex).shift().y();
        float theta = unit.die(dieIndex).theta();
        float dieX = unit.die(dieIndex).nominalxy().x();
        float dieY = unit.die(dieIndex).nominalxy().y();
        float cx = pad.xy().x();
        float cy = pad.xy().y();
        transform_xy_smoothing(&cx, &cy, shiftX, shiftY, theta, dieX, dieY);
        float radius = pad.radius();

        if (distancePointToLineSeg(cx, cy, x0, y0, x1, y1) - radius < minDist)
          return false;
      }
    }
  }

  // prestratum line segs
  size_t numSegs = layer.fixedpaths_size();
  for (size_t pi = 0; pi < numSegs; pi++)
  {
    const zinc::Path& path = layer.fixedpaths(pi);
    int pnetID = path.netid();
    if (pnetID == routeDef.netid())
      continue;
    float segmindist = (path.tracewidth() / 2.0f) + minDist;
    float sx0 = path.xy0().x();
    float sy0 = path.xy0().y();
    float sx1 = path.xy1().x();
    float sy1 = path.xy1().y();

    if (distanceLineSegToLineSeg(x0, y0, x1, y1, sx0, sy0, sx1, sy1) -
        segmindist < 0)
      return false;
  }

  // other route line segs
  int numRoutes = layer.routedefinitions_size();
  for (int i = 0; i < numRoutes; i++)
  {
    if (i == routeIndex)
      continue;
    const zinc::Route& route = routedLayer.routes(i);
    float rtw = layer.routedefinitions(i).tracewidth();
    float segmindist = (rtw / 2.0f) + minDist;
    for (size_t si = 1; si < route.points_size(); si++)
    {
      float sx0 = route.points(si - 1).x();
      float sy0 = route.points(si - 1).y();
      float sx1 = route.points(si).x();
      float sy1 = route.points(si).y();
      if (distanceLineSegToLineSeg(x0, y0, x1, y1, sx0, sy0, sx1, sy1) -
          segmindist < 0)
        return false;
    }
  }

  return true;
}

const zinc::Layer& LayerForLayerNumber(int number, const zinc::Design& design)
{
  for (int i = 0; i < design.layers_size(); i++)
  {
    if (design.layers(i).number() == number)
      return design.layers(i);
  }
}

void SmoothRoutes(int a, int b, const zinc::RoutingWorkItem& workItem,
    zinc::RoutingWorkResults* workResults)
{
  float gMinSpace = workItem.design().rules().minglobalspacing();
  int shiftStart = workItem.workrange().start();

  for (int tid = a; tid < b; tid++)
  {
    zinc::RoutedUnit* routedUnit = workResults->mutable_routedunits(tid);
    if (!routedUnit->routinggood())
      continue;
    for (int routedLayerIndex = 0; routedLayerIndex < routedUnit->routedlayers_size();
        routedLayerIndex++)
    {
      zinc::RoutedLayer* routedLayer = routedUnit->mutable_routedlayers(routedLayerIndex);
      const zinc::Layer& layer = LayerForLayerNumber(routedLayer->layernumber(),
          workItem.design());
      for (int routeIndex = 0; routeIndex < routedLayer->routes_size(); routeIndex++)
      {
        zinc::Route* route = routedLayer->mutable_routes(routeIndex);
        zinc::Route newRoute;
        int netID = layer.routedefinitions(routeIndex).netid();
        float traceWidth = layer.routedefinitions(routeIndex).tracewidth();
        float minDist = (traceWidth / 2.0) + gMinSpace;
        int i = 0;
        while (i + 1 < route->points_size())
        {
          float sx0 = route->points(i).x();
          float sy0 = route->points(i).y();
          int removeTo = i;
          for (int j = i + 1; j < route->points_size(); j++)
          {
            float sx1 = route->points(j).x();
            float sy1 = route->points(j).y();
            if (checkLineSeg(sx0, sy0, sx1, sy1, workItem.shifts(), minDist, tid,
                  layer.routedefinitions(routeIndex), shiftStart, layer, workItem.design(),
                  routeIndex, *routedLayer))
            {
              removeTo = j;
            }
          }
          if (removeTo == i)
            removeTo++;
          zinc::Point* newPoint = newRoute.mutable_points()->Add();
          newPoint->CopyFrom(route->points(i));
          i = removeTo;
        }
        zinc::Point* newPoint = newRoute.mutable_points()->Add();
        newPoint->CopyFrom(route->points(route->points_size() - 1));
        route->mutable_points()->CopyFrom(newRoute.points());
      }
    }
  }
}
  

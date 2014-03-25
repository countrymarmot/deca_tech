# Geom.py
# Created by Craig Bishop on 11 June 2012
#
# malachite
# Copyright Deca Technologies 2012 All Rights Reserved
#

import math
import sys
import util


class Vector:
  def __init__(self):
    self.x = 0.0
    self.y = 0.0

  @classmethod
  def fromXY(cls, x, y):
    v = Vector()
    v.x = x
    v.y = y
    return v

  def scalarMul(self, rhs):
    return Vector.fromXY(self.x * rhs, self.y * rhs)

  def dot(self, rhs):
    return (self.x * rhs.x) + (self.y * rhs.y)

  def cross(self, rhs):
    return (self.x * rhs.y) - (self.y * rhs.x)

  def add(self, rhs):
    return Vector.fromXY(self.x + rhs.x, self.y + rhs.y)

  def sub(self, rhs):
    return Vector.fromXY(self.x - rhs.x, self.y - rhs.y)

  def __add__(self, other):
    if isinstance(other, self.__class__):
      return self.add(other)

  def __sub__(self, other):
    if isinstance(other, self.__class__):
      return self.sub(other)

  def __mul__(self, other):
    if type(other) is float or type(other) is int:
      return self.scalarMul(other)

  def __str__(self):
    return "({0}, {1})".format(self.x, self.y)

  def __repr__(self):
    return "<Geom.Vector ({0}, {1})>".format(self.x, self.y)

  def __cmp__(self, other):
    if util.approx_equal(self.x, other.x) and\
            util.approx_equal(self.y, other.y):
      return 0
    else:
      return -1


class Point(Vector):
  def __init__(self):
    Vector.__init__(self)
    self.x = 0.0
    self.y = 0.0

  @classmethod
  def fromXY(cls, x, y):
    p = Point()
    p.x = x
    p.y = y
    return p

  def rotate(self, angleRad):
    return Point.fromXY((float(self.x) * math.cos(angleRad)) -
        (float(self.y) * math.sin(angleRad)),
        (float(self.y) * math.cos(angleRad)) +
        (float(self.x) * math.sin(angleRad)))

  def distanceToPoint(self, rhs):
    return math.sqrt(math.pow(self.x - rhs.x, 2) + math.pow(self.y - rhs.y, 2))

  def __str__(self):
    return "({0}, {1})".format(self.x, self.y)

  def __repr__(self):
    return "<Geom.Point ({0}, {1})>".format(self.x, self.y)

  def __cmp__(self, other):
    if util.approx_equal(self.x, other.x) and\
            util.approx_equal(self.y, other.y):
      return 0
    else:
      return -1


class Rect:
  def __init__(self):
    self.p1 = Point()
    self.p2 = Point()

  @classmethod
  def fromPoints(cls, p1, p2):
    r = Rect()
    r.p1 = p1
    r.p2 = p2
    return r

  @classmethod
  def fromXYAndDim(cls, x, y, width, height):
    r = Rect()
    r.p1 = Point.fromXY(x, y)
    r.p2 = Point.fromXY(x + width, y + height)
    return r

  def __repr__(self):
    return "<Geom.Rect ({0}, {1}) {2}x{3}>".format(self.p1.x, self.p1.y,
        self.p2.x - self.p1.x, self.p2.y - self.p1.y)

  def width(self):
    return abs(self.p1.x - self.p2.x)

  def height(self):
    return abs(self.p1.y - self.p2.y)

  def center(self):
    return midPoint(self.p1, self.p2)

  def __cmp__(self, other):
    if self.p1 == other.p1 and self.p2 == other.p2:
      return 0
    else:
      return -1


class LineSeg:
  def __init__(self):
    self.p1 = Point()
    self.p2 = Point()

  @classmethod
  def fromPoints(cls, p1, p2):
    seg = LineSeg()
    seg.p1 = p1
    seg.p2 = p2
    return seg

  @classmethod
  def fromXYs(cls, x1, y1, x2, y2):
    seg = LineSeg()
    seg.p1 = Point.fromXY(x1, y1)
    seg.p2 = Point.fromXY(x2, y2)
    return seg

  def rotate(self, angleRad):
    return LineSeg.fromPoints(self.p1.rotate(angleRad),
        self.p2.rotate(angleRad))

  def length(self):
    return self.p1.distanceToPoint(self.p2)

  def __str__(self):
    return "Segment: ({0}, {1}) to ({2}, {3})".format(self.p1.x, self.p1.y,
        self.p2.x, self.p2.y)

  def __repr__(self):
    return "<Geom.LineSeg ({0}, {1}) to ({2}, {3})>"\
        .format(self.p1.x, self.p1.y,
            self.p2.x, self.p2.y)

  def __cmp__(self, rhs):
    if self.p1 == rhs.p1 and self.p2 == rhs.p2:
        return 0
    else:
      return -1


class Arc:
  def __init__(self):
    self.p1 = Point()
    self.p2 = Point()
    self.center = Point()
    self.cw = False

  @classmethod
  def fromPointsAndCenter(cls, p1, p2, c, cw):
    arc = Arc()
    arc.p1 = p1
    arc.p2 = p2
    arc.center = c
    arc.cw = cw
    return arc

  @classmethod
  def fromXYs(cls, x1, y1, x2, y2, cx, cy, cw):
    arc = Arc()
    arc.p1 = Point.fromXY(x1, y1)
    arc.p2 = Point.fromXY(x2, y2)
    arc.center = Point.fromXY(cx, cy)
    arc.cw = cw
    return arc

  def rotate(self, angleRad):
    newarc = Arc.fromPointsAndCenter(self.p1.rotate(angleRad),
        self.p2.rotate(angleRad), self.center.rotate(angleRad),
        self.cw)
    newarc.cw = self.cw
    return newarc

  def radius(self):
    return distancePointToPoint(self.center, self.p1)

  def startAngle(self):
    return math.degrees(math.atan2(self.p1.y - self.center.y,
        self.p1.x - self.center.x))

  def endAngle(self):
    return math.degrees(math.atan2(self.p2.y - self.center.y,
        self.p2.x - self.center.x))

  def linearSegments(self):
    segs = []
    theta = self.startAngle()
    endTheta = self.endAngle()
    if self.cw:
      while endTheta >= theta:
          endTheta -= 360
    else:
      while endTheta <= theta:
          endTheta += 360

    r = self.radius()
    sweep = abs(endTheta - theta)
    L = math.radians(sweep) * r
    steps = max(5, int(L / 5.0))
    step = sweep / float(steps)
    if self.cw:
      step *= -1.0
    for i in range(steps):
      p1 = self.center.add(Point.fromXY(math.cos(math.radians(theta)) * r,
          math.sin(math.radians(theta)) * r))
      p2 = self.center.add(Point.fromXY(
          math.cos(math.radians(theta + step)) * r,
          math.sin(math.radians(theta + step)) * r))
      seg = LineSeg.fromPoints(p1, p2)
      segs.append(seg)
      theta += step
    return segs


class LineSegPath:
  def __init__(self):
    self.segments = []

  @classmethod
  def fromSegments(cls, segs):
    l = LineSegPath()
    l.segments = segs
    return l

  def addSegment(self, seg):
    self.segments.append(seg)


class Polygon:
  def __init__(self):
    self.segments = []

  @classmethod
  def fromSegments(cls, segs):
    if len(segs) < 3:
      raise RuntimeError("A polygon must have at least 3 segments")
    poly = Polygon()
    poly.segments = segs
    return poly

  def __str__(self):
    return "Polygon: {0} segments".format(len(self.segments))

  def __repr__(self):
    return "<Geom.Polygon {0} segments>".format(len(self.segments))


class Circle:
  def __init__(self):
    self.center = Point()
    self.diameter = 1.0

  @classmethod
  def fromXYAndRadius(cls, x, y, radius):
    c = Circle()
    c.center = Point.fromXY(x, y)
    c.diameter = radius * 2
    return c

  @classmethod
  def fromXYAndDiameter(cls, x, y, diameter):
    c = Circle()
    c.center = Point.fromXY(x, y)
    c.diameter = diameter
    return c

  def radius(self):
    return self.diameter / 2

  def __str__(self):
    return "Circle: ({0}, {1}) d: {2}".format(self.center.x, self.center.y,
        self.diameter)

  def __repr__(self):
    return "<Geom.Circle ({0}, {1}) d: {2}>"\
        .format(self.center.x, self.center.y, self.diameter)


def distancePointToPoint(lhs, rhs):
  return math.sqrt(math.pow(lhs.x - rhs.x, 2) + math.pow(lhs.y - rhs.y, 2))


def midPoint(p1, p2):
  return Point.fromXY((float(p1.x) + float(p2.x)) / 2,
      (float(p1.y) + float(p2.y)) / 2)


def distanceLineSegToPoint(seg, p):
  # get length^2 of line segment
  l2 = math.pow(distancePointToPoint(seg.p1, seg.p2), 2)

  # if seg is length zero
  if (l2 == 0):
    return distancePointToPoint(seg.p1, p)

  # project p onto the line
  t = p.sub(seg.p1).dot(seg.p2.sub(seg.p1)) / l2

  # beyond p1 end of segment
  if (t < 0.0):
    return distancePointToPoint(seg.p1, p)
  # beyond p2 end of segment
  elif (t > 1.0):
    return distancePointToPoint(seg.p2, p)
  # in middle somewhere
  else:
    proj = seg.p1.add(seg.p2.sub(seg.p1).scalarMul(t))
    return distancePointToPoint(p, proj)


def distanceCircleToPoint(c, p):
  dist = distancePointToPoint(p, c.center) - c.radius()
  if dist < 0:
    return 0
  else:
    return dist


def distanceCircleToCircle(c1, c2):
  dist = distancePointToPoint(c1.center, c2.center)
  dist -= float(c1.radius())
  dist -= float(c2.radius())
  return max(0.0, float(dist))


def distanceCircleToLineSeg(c, seg):
  dist = distanceLineSegToPoint(seg, c.center) - c.radius()
  if dist < 0:
    return 0
  else:
    return dist


def distanceLineSegPathToPoint(segPath, p):
  dist = float("inf")
  for seg in segPath.segments:
    dist = min(dist, distanceLineSegToPoint(seg, p))
  return dist


def distanceLineSegToPolygon(seg, poly):
  if distancePolygonToPoint(poly, seg.p1) == 0 or\
          distancePolygonToPoint(poly, seg.p2) == 0:
    return 0

  dist = sys.maxint
  for pseg in poly.segments:
    if lineSegmentsIntersect(seg, pseg):
      return 0
    dist = min(dist, distanceLineSegToLineSeg(seg, pseg))
  return dist


def distancePolygonToPoint(poly, p):
  # first test if the point is inside the polygon
  inside = False
  for seg in poly.segments:
    if p.y > min(seg.p1.y, seg.p2.y) and \
            p.y <= max(seg.p1.y, seg.p2.y) and \
            p.x <= max(seg.p1.x, seg.p2.x):
      if seg.p1.y != seg.p2.y:
        xinters = (p.y-seg.p1.y)*(seg.p2.x-seg.p1.x) / \
            (seg.p2.y-seg.p1.y) + seg.p1.x
      if seg.p1.x == seg.p2.x or p.x <= xinters:
        inside = not inside
  if inside:
    return 0

  dist = float("inf")
  for seg in poly.segments:
    dist = min(dist, distanceLineSegToPoint(seg, p))
  return dist


def distancePolygonToPolygon(poly1, poly2):
  dist = sys.maxint
  for seg in poly1.segments:
    d = distanceLineSegToPolygon(seg, poly2)
    dist = min(d, dist)
  for seg in poly2.segments:
    d = distanceLineSegToPolygon(seg, poly1)
    dist = min(d, dist)
  return dist


def distanceLineSegToLineSeg(seg1, seg2):
  if lineSegmentsIntersect(seg1, seg2):
    return 0

  d1 = distanceLineSegToPoint(seg1, seg2.p1)
  d2 = distanceLineSegToPoint(seg1, seg2.p2)
  d3 = distanceLineSegToPoint(seg2, seg1.p1)
  d4 = distanceLineSegToPoint(seg2, seg1.p2)
  return min(d1, min(d2, min(d3, d4)))


def lineSegmentsIntersect(seg1, seg2):
  def ccw(a, b, c):
    return (c.y - a.y) * (b.x - a.x) > (b.y - a.y) * (c.x - a.x)

  if distanceLineSegToPoint(seg1, seg2.p1) == 0 or \
          distanceLineSegToPoint(seg1, seg2.p2) == 0:
    return True

  return ccw(seg1.p1, seg2.p1, seg2.p2) != ccw(seg1.p2, seg2.p1, seg2.p2) and \
      ccw(seg1.p1, seg1.p2, seg2.p1) != ccw(seg1.p1, seg1.p2, seg2.p2)


def lineSegmentsIntersectionPoint(seg1, seg2):
  if not lineSegmentsIntersect(seg1, seg2):
    return None

  # need to find value of parameter t on the parameterization of the lines at
  # which the line segments intersect
  # taken from answer 2 on:
  # http://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line
  #-segments-intersect
  p = seg1.p1
  r = seg1.p2.sub(p)
  q = seg2.p1
  s = seg2.p2.sub(q)
  rcross = r.cross(s)
  # if rcross is 0, then some part of the lines is shared or parallel,
  # so there isn't
  # really a point of intersection
  if rcross == 0:
    return None

  # the Vector class doesn't know about the type of number it's using,
  # so we need to explicity cast to floats
  t = float((q.sub(p)).cross(s)) / float(rcross)
  return p.add(r.scalarMul(t))


def boundingBoxForSegments(segments):
  minX = sys.maxint
  maxX = -sys.maxint
  minY = sys.maxint
  maxY = -sys.maxint

  for seg in segments:
    for p in [seg.p1, seg.p2]:
      minX = min(minX, p.x)
      minY = min(minY, p.y)
      maxX = max(maxX, p.x)
      maxY = max(maxY, p.y)

  return Rect.fromPoints(Point.fromXY(minX, minY),
      Point.fromXY(maxX, maxY))


def closestPointOnLineSegToPoint(seg, p):
  # get length^2 of line segment
  l2 = math.pow(distancePointToPoint(seg.p1, seg.p2), 2)

  # if seg is length zero
  if (l2 == 0):
    return seg.p1

  # project p onto the line
  t = p.sub(seg.p1).dot(seg.p2.sub(seg.p1)) / l2

  # beyond p1 end of segment
  if (t < 0.0):
    return seg.p1
  # beyond p2 end of segment
  elif (t > 1.0):
    return seg.p2
  # in middle somewhere
  else:
    proj = seg.p1.add(seg.p2.sub(seg.p1).scalarMul(t))
    return proj


def closestPointOnLineSegPathToPoint(path, p):
  closestSeg = None
  minDist = float("inf")
  for seg in path.segments:
    d = distanceLineSegToPoint(seg, p)
    if d < minDist:
      minDist = d
      closestSeg = seg
  return closestPointOnLineSegToPoint(closestSeg, p)


def closestPointsLineSegPathToPolygon(path, poly):
  # first determine closest point to the polygon in the path
  closestLineSeg = None
  minDist = float("inf")
  for seg in path.segments:
    d = distanceLineSegToPolygon(seg, poly)
    if d < minDist:
      minDist = d
      closestLineSeg = seg

  # on the line seg, find the closest point
  segPoint = closestLineSeg.p1
  if distancePolygonToPoint(poly, closestLineSeg.p2) < \
          distancePolygonToPoint(poly, closestLineSeg.p1):
    segPoint = closestLineSeg.p2

  # now get the closest segment in the polygon
  minDist = float("inf")
  polySeg = None
  for seg in poly.segments:
    d = distanceLineSegToPoint(seg, segPoint)
    if d < minDist:
      minDist = d
      polySeg = seg

  return [segPoint, closestPointOnLineSegToPoint(polySeg, segPoint)]


def closestPointsLineSegToLineSeg(seg1, seg2):
  # if they intersect, then the intersection point is the both of the points
  p = lineSegmentsIntersectionPoint(seg1, seg2)
  if p:
    return [p, p]

  # otherwise, one of the points in a segment is the closest point
  # we need to find which point and which segment
  otherSeg = seg2
  closestPoint = seg1.p1
  minDist = distanceLineSegToPoint(seg2, closestPoint)

  d = distanceLineSegToPoint(seg2, seg1.p2)
  if d < minDist:
    minDist = d
    otherSeg = seg2
    closestPoint = seg1.p2

  d = distanceLineSegToPoint(seg1, seg2.p1)
  if d < minDist:
    minDist = d
    otherSeg = seg1
    closestPoint = seg2.p1

  d = distanceLineSegToPoint(seg1, seg2.p2)
  if d < minDist:
    minDist = d
    otherSeg = seg1
    closestPoint = seg2.p2

  # one of the points is the closest point on the segment we found
  # now we need to calculate the point on the other
  # segment using the projection
  p2 = closestPointOnLineSegToPoint(otherSeg, closestPoint)
  return [closestPoint, p2]


def closestPointsLineSegPathToLineSegPath(path1, path2):
  closestSegs = None
  minDist = float("inf")
  for seg1 in path1.segments:
    for seg2 in path2.segments:
      d = distanceLineSegToLineSeg(seg1, seg2)
      if d < minDist:
        minDist = d
        closestSegs = [seg1, seg2]
  return closestPointsLineSegToLineSeg(closestSegs[0], closestSegs[1])


def closestPointOnPolygonToPoint(poly, p):
  closestSeg = None
  minDist = float("inf")
  for seg in poly.segments:
    d = distanceLineSegToPoint(seg, p)
    if d < minDist:
      minDist = d
      closestSeg = seg
  return closestPointOnLineSegToPoint(closestSeg, p)


def closestPointsPolygonToPolygon(poly1, poly2):
  closestSegs = None
  minDist = float("inf")
  for seg1 in poly1.segments:
    for seg2 in poly2.segments:
      d = distanceLineSegToLineSeg(seg1, seg2)
      if d < minDist:
        minDist = d
        closestSegs = [seg1, seg2]
  return closestPointsLineSegToLineSeg(closestSegs[0], closestSegs[1])


def closestLineSegOnLineSegPathToPoint(path, p):
  closestSeg = None
  minDist = float("inf")
  for seg in path.segments:
    d = distanceLineSegToPoint(seg, p)
    if d < minDist:
      minDist = d
      closestSeg = seg
  return closestSeg

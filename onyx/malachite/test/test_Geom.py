# test_Geom.py
# Created by Craig Bishop on 11 June 2012
#
# malachite
# Copyright 2012 All Rights Reserved
#

import unittest
import math
from malachite.Geom import Vector, Point, Rect, LineSeg, distancePointToPoint,\
    midPoint, distanceLineSegToPoint, Circle, distanceCircleToPoint,\
    distanceCircleToCircle, distanceCircleToLineSeg, Polygon,\
    distancePolygonToPoint, LineSegPath, distanceLineSegPathToPoint,\
    boundingBoxForSegments, lineSegmentsIntersect,\
    lineSegmentsIntersectionPoint, distanceLineSegToLineSeg,\
    distanceLineSegToPolygon, distancePolygonToPolygon, Arc,\
    closestPointOnLineSegToPoint, closestPointsLineSegPathToPolygon,\
    closestPointsLineSegToLineSeg, closestLineSegOnLineSegPathToPoint


class VectorSanityCheck(unittest.TestCase):
  def testAddition(self):
    v1 = Vector.fromXY(5, 6)
    v2 = Vector.fromXY(3, 7)
    v3 = v1 + v2
    self.assertAlmostEqual(v3.x, 8)
    self.assertAlmostEqual(v3.y, 13)

    v1 = Vector.fromXY(-1, 6)
    v2 = Vector.fromXY(3, -7)
    v3 = v1 + v2
    self.assertAlmostEqual(v3.x, 2)
    self.assertAlmostEqual(v3.y, -1)

  def testSubtraction(self):
    v1 = Vector.fromXY(5, 6)
    v2 = Vector.fromXY(3, 7)
    v3 = v1 - v2
    self.assertAlmostEqual(v3.x, 2)
    self.assertAlmostEqual(v3.y, -1)

    v1 = Vector.fromXY(-1, 6)
    v2 = Vector.fromXY(3, -7)
    v3 = v1 - v2
    self.assertAlmostEqual(v3.x, -4)
    self.assertAlmostEqual(v3.y, 13)

  def testScalarMul(self):
    v1 = Vector.fromXY(-1, 6)
    v2 = Vector.fromXY(3, -7)

    v3 = v1 * 2
    v4 = v2 * 3

    self.assertAlmostEqual(v3.x, -2)
    self.assertAlmostEqual(v3.y, 12)

    self.assertAlmostEqual(v4.x, 9)
    self.assertAlmostEqual(v4.y, -21)

  def testDotProduct(self):
    v1 = Vector.fromXY(-1, 6)
    v2 = Vector.fromXY(3, -7)

    dp = v1.dot(v2)
    self.assertAlmostEqual(dp, -45)

  def testCrossProduct(self):
    v1 = Vector.fromXY(-1, 6)
    v2 = Vector.fromXY(3, -7)

    cp = v1.cross(v2)
    self.assertAlmostEqual(cp, -11)

  def testCmp(self):
    v1 = Vector.fromXY(1, 2)
    v2 = Vector.fromXY(1, 2)
    self.assertTrue(v1 == v2)

    v1 = Vector.fromXY(1, 2)
    v2 = Vector.fromXY(2, 3)
    self.assertFalse(v1 == v2)

  def testStr(self):
    v1 = Vector.fromXY(1.23, 4.56)
    txt = str(v1)
    self.assertEqual("(1.23, 4.56)", txt)

  def testRepr(self):
    v1 = Vector.fromXY(1.23, 4.56)
    txt = str(v1)
    txt = v1.__repr__()
    self.assertEqual("<Geom.Vector (1.23, 4.56)>", txt)


class PointSanityCheck(unittest.TestCase):
  def testDistanceToPoint(self):
    p1 = Point.fromXY(4, 3)
    p2 = Point.fromXY(0, -1)
    d = p1.distanceToPoint(p2)
    self.assertAlmostEqual(d, 5.65685424949238)

    p1 = Point.fromXY(0, 0)
    p2 = Point.fromXY(0, 0)
    d = p2.distanceToPoint(p1)
    self.assertAlmostEqual(d, 0)

  def testStr(self):
    p = Point.fromXY(1.23, 4.56)
    self.assertEqual(str(p), "(1.23, 4.56)")

  def testRepr(self):
    p = Point.fromXY(1.23, 4.56)
    self.assertEqual(p.__repr__(), "<Geom.Point (1.23, 4.56)>")

  def testCmp(self):
    p = Point.fromXY(1, 2)
    p2 = Point.fromXY(1, 2)
    self.assertTrue(p == p2)
    p3 = Point.fromXY(-1, 2)
    self.assertFalse(p3 == p)


class PointComparisonCheck(unittest.TestCase):
  def testEquality(self):
    p1 = Point.fromXY(1, 2)
    p2 = Point.fromXY(1, 2)
    self.assertTrue(p1 == p2)

  def testInequalityX(self):
    p1 = Point.fromXY(2, 2)
    p2 = Point.fromXY(1, 2)
    self.assertFalse(p1 == p2)

  def testInequalityY(self):
    p1 = Point.fromXY(1, 2)
    p2 = Point.fromXY(1, 4)
    self.assertFalse(p1 == p2)


class PointRotationTest(unittest.TestCase):
  def testAboutZero(self):
    p = Point.fromXY(0, 0)
    p = p.rotate(math.radians(5))
    self.assertEqual(p, Point.fromXY(0, 0))

  def test90(self):
    p = Point.fromXY(0, 1)
    p = p.rotate(math.radians(90))
    self.assertAlmostEqual(p.x, -1)
    self.assertAlmostEqual(p.y, 0)

  def test180(self):
    p = Point.fromXY(0, 1)
    p = p.rotate(math.radians(180))
    self.assertAlmostEqual(p.x, 0)
    self.assertAlmostEqual(p.y, -1)

  def testOddAngle(self):
    p = Point.fromXY(1, 0)
    p = p.rotate(math.radians(5))
    self.assertAlmostEqual(p.x, 0.996195, places=5)
    self.assertAlmostEqual(p.y, 0.0871557, places=5)

  def testNegativeAngle(self):
    p = Point.fromXY(1, 0)
    p = p.rotate(math.radians(-5))
    self.assertAlmostEqual(p.x, 0.996195, places=5)
    self.assertAlmostEqual(p.y, -0.0871557, places=5)


class RectSanityCheck(unittest.TestCase):
  def testFromPoints(self):
    r = Rect.fromPoints(Point.fromXY(-1, -2), Point.fromXY(5, 5))
    self.assertAlmostEqual(r.width(), 6)
    self.assertAlmostEqual(r.height(), 7)

  def testFromXYAndDim(self):
    r = Rect.fromXYAndDim(-1, -2, 6, 7)
    self.assertAlmostEqual(r.p1.x, -1)
    self.assertAlmostEqual(r.p1.y, -2)
    self.assertAlmostEqual(r.p2.x, 5)
    self.assertAlmostEqual(r.p2.y, 5)
    self.assertAlmostEqual(r.width(), 6)
    self.assertAlmostEqual(r.height(), 7)

  def testWidth(self):
    r = Rect.fromXYAndDim(0, 0, 20, 20)
    self.assertAlmostEqual(r.width(), 20)

  def testHeight(self):
    r = Rect.fromXYAndDim(0, 0, 20, 20)
    self.assertAlmostEqual(r.height(), 20)

  def testCenter(self):
    r = Rect.fromXYAndDim(1, 1, 5, 5)
    self.assertEqual(r.center(), Point.fromXY(3.5, 3.5))

  def testRepr(self):
    r = Rect.fromXYAndDim(1, 2, 5, 6)
    self.assertEqual(r.__repr__(), "<Geom.Rect (1, 2) 5x6>")


class RectComparisonCheck(unittest.TestCase):
  def testEquality(self):
    r1 = Rect.fromXYAndDim(0, 0, 20, 20)
    r2 = Rect.fromXYAndDim(0, 0, 20, 20)
    self.assertTrue(r1 == r2)

  def testInequalityX(self):
    r1 = Rect.fromXYAndDim(1, 0, 20, 20)
    r2 = Rect.fromXYAndDim(0, 0, 20, 20)
    self.assertFalse(r1 == r2)

  def testInequalityY(self):
    r1 = Rect.fromXYAndDim(0, 0, 20, 20)
    r2 = Rect.fromXYAndDim(0, 1, 20, 20)
    self.assertFalse(r1 == r2)

  def testInequalityWidth(self):
    r1 = Rect.fromXYAndDim(0, 0, 19, 20)
    r2 = Rect.fromXYAndDim(0, 0, 20, 20)
    self.assertFalse(r1 == r2)

  def testInequalityHeight(self):
    r1 = Rect.fromXYAndDim(0, 0, 20, 20)
    r2 = Rect.fromXYAndDim(0, 0, 20, 21)
    self.assertFalse(r1 == r2)


class LineSegSanityCheck(unittest.TestCase):
  def testFromXYs(self):
    ls = LineSeg.fromXYs(-1, -1, 3, 3)
    self.assertAlmostEqual(ls.p1.x, -1)
    self.assertAlmostEqual(ls.p1.y, -1)
    self.assertAlmostEqual(ls.p2.x, 3)
    self.assertAlmostEqual(ls.p2.y, 3)

  def testLength(self):
    ls = LineSeg.fromXYs(-1, -1, 3, 3)
    self.assertAlmostEqual(ls.length(), 5.65685424949238)

  def testFromPoints(self):
    seg = LineSeg.fromPoints(Point.fromXY(0, 1), Point.fromXY(1, 2))
    self.assertEqual(seg.p1, Point.fromXY(0, 1))
    self.assertEqual(seg.p2, Point.fromXY(1, 2))

  def testStr(self):
    ls = LineSeg.fromXYs(1, 2, 3, 4)
    self.assertEqual(str(ls), "Segment: (1, 2) to (3, 4)")

  def testRepr(self):
    ls = LineSeg.fromXYs(1, 2, 3, 4)
    self.assertEqual(ls.__repr__(), "<Geom.LineSeg (1, 2) to (3, 4)>")

  def testCmp(self):
    ls = LineSeg.fromXYs(1, 2, 3, 4)
    ls2 = LineSeg.fromXYs(1, 2, 3, 4)
    print(ls)
    print(ls2)
    self.assertTrue(ls == ls2)
    ls3 = LineSeg.fromXYs(-1, 2, 3, 4)
    self.assertFalse(ls == ls3)


class LineSegRotationCheck(unittest.TestCase):
  def test90(self):
    p1 = Point.fromXY(1, 1)
    p2 = Point.fromXY(2, 2)
    seg = LineSeg.fromPoints(p1, p2)
    seg = seg.rotate(math.radians(90))

    self.assertAlmostEqual(seg.p1.x, -1)
    self.assertAlmostEqual(seg.p1.y, 1)
    self.assertAlmostEqual(seg.p2.x, -2)
    self.assertAlmostEqual(seg.p2.y, 2)

  def testNegative(self):
    p1 = Point.fromXY(1, 1)
    p2 = Point.fromXY(2, 2)
    seg = LineSeg.fromPoints(p1, p2)
    seg = seg.rotate(math.radians(-90))

    self.assertAlmostEqual(seg.p1.x, 1)
    self.assertAlmostEqual(seg.p1.y, -1)
    self.assertAlmostEqual(seg.p2.x, 2)
    self.assertAlmostEqual(seg.p2.y, -2)


class LineSegPathSanityCheck(unittest.TestCase):
  def testFromSegments(self):
    l1 = LineSeg.fromXYs(0, 0, 1, 0)
    l2 = LineSeg.fromXYs(1, 0, 1, 1)
    l3 = LineSeg.fromXYs(1, 1, 0, 1)
    l4 = LineSeg.fromXYs(0, 1, 0, 0)
    path = LineSegPath.fromSegments([l1, l2, l3, l4])
    self.assertEqual(path.segments[0], l1)
    self.assertEqual(path.segments[1], l2)
    self.assertEqual(path.segments[2], l3)
    self.assertEqual(path.segments[3], l4)

  def testAddSegment(self):
    l1 = LineSeg.fromXYs(0, 0, 1, 0)
    l2 = LineSeg.fromXYs(1, 0, 1, 1)
    l3 = LineSeg.fromXYs(1, 1, 0, 1)
    l4 = LineSeg.fromXYs(0, 1, 0, 0)
    path = LineSegPath.fromSegments([l1, l2, l3])
    self.assertEqual(path.segments[0], l1)
    self.assertEqual(path.segments[1], l2)
    self.assertEqual(path.segments[2], l3)
    path.addSegment(l4)
    self.assertEqual(path.segments[0], l1)
    self.assertEqual(path.segments[1], l2)
    self.assertEqual(path.segments[2], l3)
    self.assertEqual(path.segments[3], l4)


class PolygonSanityCheck(unittest.TestCase):
  def testfromSegments(self):
    l1 = LineSeg.fromXYs(0, 0, 1, 0)
    l2 = LineSeg.fromXYs(1, 0, 1, 1)
    l3 = LineSeg.fromXYs(1, 1, 0, 1)
    l4 = LineSeg.fromXYs(0, 1, 0, 0)
    poly = Polygon.fromSegments([l1, l2, l3, l4])
    self.assertEqual(poly.segments[0], l1)
    self.assertEqual(poly.segments[1], l2)
    self.assertEqual(poly.segments[2], l3)
    self.assertEqual(poly.segments[3], l4)

  def testTwoSegments(self):
    l1 = LineSeg.fromXYs(0, 0, 1, 0)
    l2 = LineSeg.fromXYs(1, 0, 1, 1)
    with self.assertRaises(RuntimeError):
      Polygon.fromSegments([l1, l2])

  def testStr(self):
    l1 = LineSeg.fromXYs(0, 0, 1, 0)
    l2 = LineSeg.fromXYs(1, 0, 1, 1)
    l3 = LineSeg.fromXYs(1, 1, 0, 1)
    l4 = LineSeg.fromXYs(0, 1, 0, 0)
    poly = Polygon.fromSegments([l1, l2, l3, l4])
    self.assertEqual("Polygon: 4 segments", str(poly))

  def testRepr(self):
    l1 = LineSeg.fromXYs(0, 0, 1, 0)
    l2 = LineSeg.fromXYs(1, 0, 1, 1)
    l3 = LineSeg.fromXYs(1, 1, 0, 1)
    l4 = LineSeg.fromXYs(0, 1, 0, 0)
    poly = Polygon.fromSegments([l1, l2, l3, l4])
    self.assertEqual("<Geom.Polygon 4 segments>", poly.__repr__())


class CircleSanityCheck(unittest.TestCase):
  def testfromXYAndRadius(self):
    c = Circle.fromXYAndRadius(1, 1, 10)
    self.assertEqual(c.center, Point.fromXY(1, 1))
    self.assertEqual(c.diameter, 20)

  def testFromXYAndDiameter(self):
    c = Circle.fromXYAndDiameter(1, 1, 20)
    self.assertEqual(c.center, Point.fromXY(1, 1))
    self.assertEqual(c.diameter, 20)
    self.assertEqual(c.radius(), 10)

  def testRadius(self):
    c = Circle.fromXYAndRadius(1, 1, 10)
    self.assertEqual(c.radius(), 10)

  def testStr(self):
    c = Circle.fromXYAndRadius(1, 1, 10)
    self.assertEqual("Circle: (1, 1) d: 20", str(c))

  def testRepr(self):
    c = Circle.fromXYAndRadius(1, 1, 10)
    self.assertEqual("<Geom.Circle (1, 1) d: 20>", c.__repr__())


class DistancePointToPointSanityCheck(unittest.TestCase):
  def testBasicDistance(self):
    p1 = Point.fromXY(-1, 2)
    p2 = Point.fromXY(10, 3)
    self.assertAlmostEqual(distancePointToPoint(p1, p2), 11.0453610171873)

    p1 = Point.fromXY(0, 0)
    p2 = Point.fromXY(0, 0)
    self.assertAlmostEqual(distancePointToPoint(p1, p2), 0)


class MidPointSanityCheck(unittest.TestCase):
  def testBasicMidPoint(self):
    p1 = Point.fromXY(-1, -1)
    p2 = Point.fromXY(1, 1)
    self.assertEqual(midPoint(p1, p2), Point.fromXY(0, 0))

    p1 = Point.fromXY(-25, 42)
    p2 = Point.fromXY(27, 45)
    self.assertEqual(midPoint(p1, p2), Point.fromXY(1, 43.5))


class DistanceLineSegToPointSanityCheck(unittest.TestCase):
  def testAlongLineNegative(self):
    ls = LineSeg.fromXYs(1, 1, 2, 2)
    p = Point.fromXY(0, 0)
    d = distanceLineSegToPoint(ls, p)
    self.assertAlmostEqual(d, 1.4142135623731)

  def testAlongLinePositive(self):
    ls = LineSeg.fromXYs(1, 1, 2, 2)
    p = Point.fromXY(3, 3)
    d = distanceLineSegToPoint(ls, p)
    self.assertAlmostEqual(d, 1.4142135623731)

  def testAbove(self):
    ls = LineSeg.fromXYs(1, 1, 3, 3)
    p = Point.fromXY(2, 3)
    d = distanceLineSegToPoint(ls, p)
    self.assertAlmostEqual(d, 0.7071067811865476)

  def testBelow(self):
    ls = LineSeg.fromXYs(1, 1, 3, 3)
    p = Point.fromXY(0, 3)
    d = distanceLineSegToPoint(ls, p)
    self.assertAlmostEqual(d, 2.1213203435596424)

  def testOn(self):
    ls = LineSeg.fromXYs(1, 1, 3, 3)
    p = Point.fromXY(2, 2)
    d = distanceLineSegToPoint(ls, p)
    self.assertAlmostEqual(d, 0)

  def testColinear(self):
    ls = LineSeg.fromXYs(0, 0, 10, 0)
    p = Point.fromXY(-10, 0)
    d = distanceLineSegToPoint(ls, p)
    self.assertAlmostEqual(d, 10)

  def testLengthZero(self):
    ls = LineSeg.fromXYs(0, 0, 0, 0)
    p = Point.fromXY(1, 0)
    d = distanceLineSegToPoint(ls, p)
    self.assertAlmostEqual(d, 1)


class DistanceCircleToPointSanityCheck(unittest.TestCase):
  def testOutside(self):
    c = Circle.fromXYAndRadius(5, 5, 3)
    p = Point.fromXY(0, 0)
    d = distanceCircleToPoint(c, p)
    self.assertAlmostEqual(d, 4.0710678118654755)

    c = Circle.fromXYAndRadius(5, 5, 3)
    p = Point.fromXY(0, 5)
    d = distanceCircleToPoint(c, p)
    self.assertAlmostEqual(d, 2.0)

  def testInside(self):
    c = Circle.fromXYAndRadius(5, 5, 3)
    p = Point.fromXY(3, 5)
    d = distanceCircleToPoint(c, p)
    self.assertAlmostEqual(d, 0.0)

  def testCenter(self):
    c = Circle.fromXYAndRadius(5, 5, 3)
    p = Point.fromXY(5, 5)
    d = distanceCircleToPoint(c, p)
    self.assertAlmostEqual(d, 0.0)


class DistanceCircleToCircleSanityCheck(unittest.TestCase):
  def testOutside(self):
    c1 = Circle.fromXYAndDiameter(0, 0, 80)
    c2 = Circle.fromXYAndDiameter(200, 0, 80)
    d = distanceCircleToCircle(c1, c2)
    self.assertAlmostEqual(d, 120)

  def testOn(self):
    c1 = Circle.fromXYAndDiameter(0, 0, 80)
    c2 = Circle.fromXYAndDiameter(80, 0, 80)
    d = distanceCircleToCircle(c1, c2)
    self.assertAlmostEqual(d, 0)

  def testInside(self):
    c1 = Circle.fromXYAndDiameter(0, 0, 80)
    c2 = Circle.fromXYAndDiameter(40, 0, 80)
    d = distanceCircleToCircle(c1, c2)
    self.assertAlmostEqual(d, 0)


class DistanceCircleToLineSegSanityCheck(unittest.TestCase):
  def testOutside(self):
    c = Circle.fromXYAndRadius(5, 5, 3)
    ls = LineSeg.fromXYs(0, 0, 5, 0)
    d = distanceCircleToLineSeg(c, ls)
    self.assertAlmostEqual(d, 2)

  def testInside(self):
    c = Circle.fromXYAndRadius(5, 5, 3)
    ls = LineSeg.fromXYs(0, 3, 5, 3)
    d = distanceCircleToLineSeg(c, ls)
    self.assertAlmostEqual(d, 0)

  def testThroughCenter(self):
    c = Circle.fromXYAndRadius(5, 5, 3)
    ls = LineSeg.fromXYs(0, 5, 5, 5)
    d = distanceCircleToLineSeg(c, ls)
    self.assertAlmostEqual(d, 0)


class DistancePolygonToPointSanityCheck(unittest.TestCase):
  def setUp(self):
    seg1 = LineSeg.fromXYs(0, 0, 0, 1)
    seg2 = LineSeg.fromXYs(0, 1, 1, 1)
    seg3 = LineSeg.fromXYs(1, 1, 1, 0)
    seg4 = LineSeg.fromXYs(1, 0, 0, 0)
    self.poly = Polygon.fromSegments([seg1, seg2, seg3, seg4])

  def testOutside(self):
    p = Point.fromXY(2, 1)
    d = distancePolygonToPoint(self.poly, p)
    self.assertAlmostEqual(d, 1)

  def testInside(self):
    p = Point.fromXY(0.5, 0.5)
    d = distancePolygonToPoint(self.poly, p)
    self.assertAlmostEqual(d, 0)

  def testOnASeg(self):
    p = Point.fromXY(1, 0.5)
    d = distancePolygonToPoint(self.poly, p)
    self.assertAlmostEqual(d, 0)

  def testOnACorner(self):
    p = Point.fromXY(1, 1)
    d = distancePolygonToPoint(self.poly, p)
    self.assertAlmostEqual(d, 0)


class DistanceLineSegPathToPointSanityCheck(unittest.TestCase):
  def setUp(self):
    seg1 = LineSeg.fromXYs(0, 0, 0, 1)
    seg2 = LineSeg.fromXYs(0, 1, 1, 1)
    self.segPath = LineSegPath.fromSegments([seg1, seg2])

  def testInside(self):
    p = Point.fromXY(1, 0)
    d = distanceLineSegPathToPoint(self.segPath, p)
    self.assertAlmostEqual(d, 1)

  def testOutside(self):
    p = Point.fromXY(1, 2)
    d = distanceLineSegPathToPoint(self.segPath, p)
    self.assertAlmostEqual(d, 1)

  def testCorner(self):
    p = Point.fromXY(0, 1)
    d = distanceLineSegPathToPoint(self.segPath, p)
    self.assertAlmostEqual(d, 0)

  def testOnLineSeg(self):
    p = Point.fromXY(0, 1)
    d = distanceLineSegPathToPoint(self.segPath, p)
    self.assertAlmostEqual(d, 0)


class TestBoundingBoxForSegments(unittest.TestCase):
  def setUp(self):
    self.segments = [LineSeg.fromXYs(0, 0, 5, 5),
        LineSeg.fromXYs(5, 5, 5, 0)]

  def testBoundingBox(self):
    bBox = boundingBoxForSegments(self.segments)
    self.assertEqual(bBox.width(), 5)
    self.assertEqual(bBox.height(), 5)
    self.assertEqual(bBox.center().x, 2.5)
    self.assertEqual(bBox.center().y, 2.5)


class TestLineSegmentsIntersect(unittest.TestCase):
  def testNotIntersecting(self):
    seg1 = LineSeg.fromXYs(0, 0, 10, 0)
    seg2 = LineSeg.fromXYs(1, 1, 10, 10)
    self.assertFalse(lineSegmentsIntersect(seg1, seg2))

  def testParallel(self):
    seg1 = LineSeg.fromXYs(0, 0, 0, 10)
    seg2 = LineSeg.fromXYs(10, 0, 10, 10)
    self.assertFalse(lineSegmentsIntersect(seg1, seg2))

  def testCrossPerp(self):
    seg1 = LineSeg.fromXYs(0, 10, 10, 0)
    seg2 = LineSeg.fromXYs(10, 10, 0, 0)
    self.assertTrue(lineSegmentsIntersect(seg1, seg2))

  def testSameLine(self):
    seg1 = LineSeg.fromXYs(0, 0, 10, 10)
    seg2 = LineSeg.fromXYs(0, 0, 10, 10)
    self.assertTrue(lineSegmentsIntersect(seg1, seg2))

  def testSameSubLine(self):
    seg1 = LineSeg.fromXYs(0, 0, 10, 10)
    seg2 = LineSeg.fromXYs(0, 0, 5, 5)
    self.assertTrue(lineSegmentsIntersect(seg1, seg2))

  def testTouchAtOnePoint(self):
    seg1 = LineSeg.fromXYs(0, 0, 10, 0)
    seg2 = LineSeg.fromXYs(10, 0, 10, 10)
    self.assertTrue(lineSegmentsIntersect(seg1, seg2))

  def testColinear(self):
    seg1 = LineSeg.fromXYs(0, 0, 10, 0)
    seg2 = LineSeg.fromXYs(-10, 0, -20, 0)
    self.assertFalse(lineSegmentsIntersect(seg1, seg2))


class TestLineSegmentsIntersection(unittest.TestCase):
  def testNotIntersecting(self):
    seg1 = LineSeg.fromXYs(0, 0, 10, 0)
    seg2 = LineSeg.fromXYs(1, 1, 10, 10)
    self.assertIsNone(lineSegmentsIntersectionPoint(seg1, seg2))

  def testParallel(self):
    seg1 = LineSeg.fromXYs(0, 0, 0, 10)
    seg2 = LineSeg.fromXYs(10, 0, 10, 10)
    self.assertIsNone(lineSegmentsIntersectionPoint(seg1, seg2))

  def testCrossPerp(self):
    seg1 = LineSeg.fromXYs(0, 10, 10, 0)
    seg2 = LineSeg.fromXYs(10, 10, 0, 0)
    self.assertEqual(lineSegmentsIntersectionPoint(seg1, seg2),
        Point.fromXY(5, 5))

  def testSameLine(self):
    seg1 = LineSeg.fromXYs(0, 0, 10, 10)
    seg2 = LineSeg.fromXYs(0, 0, 10, 10)
    p = lineSegmentsIntersectionPoint(seg1, seg2)
    self.assertIsNone(p)

  def testSameSubLine(self):
    seg1 = LineSeg.fromXYs(0, 0, 10, 10)
    seg2 = LineSeg.fromXYs(0, 0, 5, 5)
    p = lineSegmentsIntersectionPoint(seg1, seg2)
    self.assertIsNone(p)

  def testTouchAtOnePoint(self):
    seg1 = LineSeg.fromXYs(0, 0, 10, 0)
    seg2 = LineSeg.fromXYs(10, 0, 10, 10)
    self.assertEqual(lineSegmentsIntersectionPoint(seg1, seg2),
        Point.fromXY(10, 0))

  def testPerpTouchAtOnePoint(self):
    seg1 = LineSeg.fromXYs(0, 0, 10, 0)
    seg2 = LineSeg.fromXYs(5, 0, 5, 10)
    self.assertEqual(lineSegmentsIntersectionPoint(seg1, seg2),
        Point.fromXY(5, 0))

  def testColinear(self):
    seg1 = LineSeg.fromXYs(0, 0, 10, 0)
    seg2 = LineSeg.fromXYs(-10, 0, -20, 0)
    self.assertIsNone(lineSegmentsIntersectionPoint(seg1, seg2))


class TestDistanceLineSegToLineSeg(unittest.TestCase):
  def testSanity(self):
    seg1 = LineSeg.fromXYs(0, 0, 10, 0)
    seg2 = LineSeg.fromXYs(5, 2, 5, 10)
    self.assertAlmostEqual(distanceLineSegToLineSeg(seg1, seg2), 2)

  def testParallel(self):
    seg1 = LineSeg.fromXYs(0, 0, 0, 10)
    seg2 = LineSeg.fromXYs(10, 0, 10, 10)
    self.assertAlmostEqual(distanceLineSegToLineSeg(seg1, seg2), 10)

  def testIntersecting(self):
    seg1 = LineSeg.fromXYs(0, 0, 10, 10)
    seg2 = LineSeg.fromXYs(10, 0, 0, 10)
    self.assertAlmostEqual(distanceLineSegToLineSeg(seg1, seg2), 0)

  def testColinear(self):
    seg1 = LineSeg.fromXYs(0, 0, 10, 0)
    seg2 = LineSeg.fromXYs(-10, 0, -20, 0)
    d = distanceLineSegToLineSeg(seg1, seg2)
    self.assertAlmostEqual(d, 10)

  def testNonTouchingT(self):
    seg1 = LineSeg.fromXYs(0, 0, 10, 0)
    seg2 = LineSeg.fromXYs(11, 5, 11, -5)
    d = distanceLineSegToLineSeg(seg1, seg2)
    self.assertAlmostEqual(d, 1)


class TestDistanceLineSegToPolygon(unittest.TestCase):
  def testSanity(self):
    poly = Polygon()
    poly.segments.append(LineSeg.fromXYs(0, 0, 10, 0))
    poly.segments.append(LineSeg.fromXYs(10, 0, 10, 10))
    poly.segments.append(LineSeg.fromXYs(10, 10, 0, 10))
    poly.segments.append(LineSeg.fromXYs(0, 10, 0, 0))
    seg = LineSeg.fromXYs(0, 20, 20, 20)
    self.assertEqual(distanceLineSegToPolygon(seg, poly), 10)

  def testCrossPolygon(self):
    poly = Polygon()
    poly.segments.append(LineSeg.fromXYs(0, 0, 10, 0))
    poly.segments.append(LineSeg.fromXYs(10, 0, 10, 10))
    poly.segments.append(LineSeg.fromXYs(10, 10, 0, 10))
    poly.segments.append(LineSeg.fromXYs(0, 10, 0, 0))
    seg = LineSeg.fromXYs(-5, -5, 25, 25)
    self.assertEqual(distanceLineSegToPolygon(seg, poly), 0)

  def testTouchAtOnePoint(self):
    poly = Polygon()
    poly.segments.append(LineSeg.fromXYs(0, 0, 10, 0))
    poly.segments.append(LineSeg.fromXYs(10, 0, 10, 10))
    poly.segments.append(LineSeg.fromXYs(10, 10, 0, 10))
    poly.segments.append(LineSeg.fromXYs(0, 10, 0, 0))
    seg = LineSeg.fromXYs(10, 10, 20, 20)
    self.assertEqual(distanceLineSegToPolygon(seg, poly), 0)

  def testCompletelyInside(self):
    poly = Polygon()
    poly.segments.append(LineSeg.fromXYs(0, 0, 10, 0))
    poly.segments.append(LineSeg.fromXYs(10, 0, 10, 10))
    poly.segments.append(LineSeg.fromXYs(10, 10, 0, 10))
    poly.segments.append(LineSeg.fromXYs(0, 10, 0, 0))
    seg = LineSeg.fromXYs(1, 5, 9, 5)
    self.assertEqual(distanceLineSegToPolygon(seg, poly), 0)


class TestDistancePolygonToPolygon(unittest.TestCase):
  def testSanity(self):
    poly1 = Polygon()
    poly1.segments.append(LineSeg.fromXYs(0, 0, 10, 0))
    poly1.segments.append(LineSeg.fromXYs(10, 0, 10, 10))
    poly1.segments.append(LineSeg.fromXYs(10, 10, 0, 10))
    poly1.segments.append(LineSeg.fromXYs(0, 10, 0, 0))

    poly2 = Polygon()
    poly2.segments.append(LineSeg.fromXYs(20, 0, 30, 0))
    poly2.segments.append(LineSeg.fromXYs(30, 0, 30, 10))
    poly2.segments.append(LineSeg.fromXYs(30, 10, 20, 10))
    poly2.segments.append(LineSeg.fromXYs(20, 10, 20, 0))

    self.assertEqual(distancePolygonToPolygon(poly1, poly2), 10)

  def testContainedPolygon(self):
    poly1 = Polygon()
    poly1.segments.append(LineSeg.fromXYs(0, 0, 10, 0))
    poly1.segments.append(LineSeg.fromXYs(10, 0, 10, 10))
    poly1.segments.append(LineSeg.fromXYs(10, 10, 0, 10))
    poly1.segments.append(LineSeg.fromXYs(0, 10, 0, 0))

    poly2 = Polygon()
    poly2.segments.append(LineSeg.fromXYs(1, 1, 9, 1))
    poly2.segments.append(LineSeg.fromXYs(9, 1, 9, 9))
    poly2.segments.append(LineSeg.fromXYs(9, 9, 1, 9))
    poly2.segments.append(LineSeg.fromXYs(1, 9, 1, 1))

    self.assertEqual(distancePolygonToPolygon(poly1, poly2), 0)

  def testIntersectingPolygons(self):
    poly1 = Polygon()
    poly1.segments.append(LineSeg.fromXYs(0, 0, 10, 0))
    poly1.segments.append(LineSeg.fromXYs(10, 0, 10, 10))
    poly1.segments.append(LineSeg.fromXYs(10, 10, 0, 10))
    poly1.segments.append(LineSeg.fromXYs(0, 10, 0, 0))

    poly2 = Polygon()
    poly2.segments.append(LineSeg.fromXYs(5, 0, 15, 0))
    poly2.segments.append(LineSeg.fromXYs(15, 0, 15, 10))
    poly2.segments.append(LineSeg.fromXYs(15, 10, 5, 10))
    poly2.segments.append(LineSeg.fromXYs(5, 10, 5, 0))

    self.assertEqual(distancePolygonToPolygon(poly1, poly2), 0)


class ArcSanityCheck(unittest.TestCase):
  def testFromPointsAndCenter(self):
    arc = Arc.fromPointsAndCenter(Point.fromXY(2, 4), Point.fromXY(4, 2),
        Point.fromXY(2, 2), False)
    self.assertAlmostEqual(arc.radius(), 2)
    self.assertAlmostEqual(arc.startAngle(), 90)
    self.assertAlmostEqual(arc.endAngle(), 0)

  def testFromXYs(self):
    arc = Arc.fromXYs(2, 4, 4, 2, 2, 2, False)
    self.assertAlmostEqual(arc.radius(), 2)
    self.assertAlmostEqual(arc.startAngle(), 90)
    self.assertAlmostEqual(arc.endAngle(), 0)


class ArcRotationCheck(unittest.TestCase):
  def test90(self):
    arc = Arc.fromPointsAndCenter(Point.fromXY(0, 1), Point.fromXY(1, 0),
        Point.fromXY(1, 1), False)
    arc = arc.rotate(math.radians(90))
    self.assertAlmostEqual(arc.p1.x, -1)
    self.assertAlmostEqual(arc.p1.y, 0)
    self.assertAlmostEqual(arc.p2.x, 0)
    self.assertAlmostEqual(arc.p2.y, 1)
    self.assertAlmostEqual(arc.center.x, -1)
    self.assertAlmostEqual(arc.center.y, 1)
    self.assertEqual(arc.cw, False)

  def test90CW(self):
    arc = Arc.fromPointsAndCenter(Point.fromXY(0, 1), Point.fromXY(1, 0),
        Point.fromXY(1, 1), True)
    arc = arc.rotate(math.radians(90))
    self.assertAlmostEqual(arc.p1.x, -1)
    self.assertAlmostEqual(arc.p1.y, 0)
    self.assertAlmostEqual(arc.p2.x, 0)
    self.assertAlmostEqual(arc.p2.y, 1)
    self.assertAlmostEqual(arc.center.x, -1)
    self.assertAlmostEqual(arc.center.y, 1)
    self.assertEqual(arc.cw, True)


class ArcLinearSegmentsCheck(unittest.TestCase):
  def testLinearSegmentCW(self):
    arc = Arc.fromPointsAndCenter(Point.fromXY(0, 1), Point.fromXY(1, 0),
        Point.fromXY(0, 0), True)
    segs = arc.linearSegments()
    radius = distancePointToPoint(arc.p1, arc.center)
    self.assertEqual(len(segs), 5)
    self.assertAlmostEqual(segs[0].p1.x, 0)
    self.assertAlmostEqual(segs[0].p1.y, 1)
    self.assertAlmostEqual(segs[1].p1.x, math.cos(math.radians(72)) * radius)
    self.assertAlmostEqual(segs[1].p1.y, math.sin(math.radians(72)) * radius)
    self.assertAlmostEqual(segs[2].p1.x, math.cos(math.radians(54)) * radius)
    self.assertAlmostEqual(segs[2].p1.y, math.sin(math.radians(54)) * radius)
    self.assertAlmostEqual(segs[3].p1.x, math.cos(math.radians(36)) * radius)
    self.assertAlmostEqual(segs[3].p1.y, math.sin(math.radians(36)) * radius)
    self.assertAlmostEqual(segs[4].p1.x, math.cos(math.radians(18)) * radius)
    self.assertAlmostEqual(segs[4].p1.y, math.sin(math.radians(18)) * radius)
    self.assertAlmostEqual(segs[4].p2.x, 1)
    self.assertAlmostEqual(segs[4].p2.y, 0)

  def testLinearSegmentCCW(self):
    arc = Arc.fromPointsAndCenter(Point.fromXY(0, 1), Point.fromXY(1, 0),
        Point.fromXY(0, 0), False)
    segs = arc.linearSegments()
    radius = distancePointToPoint(arc.p1, arc.center)
    self.assertEqual(len(segs), 5)
    self.assertAlmostEqual(segs[0].p1.x, 0)
    self.assertAlmostEqual(segs[0].p1.y, 1)
    self.assertAlmostEqual(segs[1].p1.x, math.cos(math.radians(144)) * radius)
    self.assertAlmostEqual(segs[1].p1.y, math.sin(math.radians(144)) * radius)
    self.assertAlmostEqual(segs[2].p1.x, math.cos(math.radians(198)) * radius)
    self.assertAlmostEqual(segs[2].p1.y, math.sin(math.radians(198)) * radius)
    self.assertAlmostEqual(segs[3].p1.x, math.cos(math.radians(252)) * radius)
    self.assertAlmostEqual(segs[3].p1.y, math.sin(math.radians(252)) * radius)
    self.assertAlmostEqual(segs[4].p1.x, math.cos(math.radians(306)) * radius)
    self.assertAlmostEqual(segs[4].p1.y, math.sin(math.radians(306)) * radius)
    self.assertAlmostEqual(segs[4].p2.x, 1)
    self.assertAlmostEqual(segs[4].p2.y, 0)

  def testLinearSegementsLargeRadius(self):
    arc = Arc.fromPointsAndCenter(Point.fromXY(0, 100), Point.fromXY(100, 0),
        Point.fromXY(0, 0), True)
    segs = arc.linearSegments()
    radius = distancePointToPoint(arc.p1, arc.center)
    step = -90.0 / 31.0
    self.assertEqual(len(segs), 31)
    for i in range(31):
      self.assertAlmostEqual(segs[i].p1.x,
          math.cos(math.radians(90 + (i * step))) * radius)
      self.assertAlmostEqual(segs[i].p1.y,
          math.sin(math.radians(90 + (i * step))) * radius)
    self.assertAlmostEqual(segs[30].p2.x, 100)
    self.assertAlmostEqual(segs[30].p2.y, 0)

  def testLinearSegmentsCWWrap(self):
    arc = Arc.fromPointsAndCenter(Point.fromXY(0, 1), Point.fromXY(-1, 0),
        Point.fromXY(0, 0), True)
    segs = arc.linearSegments()
    radius = distancePointToPoint(arc.p1, arc.center)
    step = -54.0
    self.assertEqual(len(segs), 5)
    for i in range(5):
      self.assertAlmostEqual(segs[i].p1.x,
          math.cos(math.radians(90 + (i * step))) * radius)
      self.assertAlmostEqual(segs[i].p1.y,
          math.sin(math.radians(90 + (i * step))) * radius)
    self.assertAlmostEqual(segs[4].p2.x, -1)
    self.assertAlmostEqual(segs[4].p2.y, 0)


class TestClosestPointOnLineSegToPoint(unittest.TestCase):
  def testClosestPointAxisAligned(self):
    seg = LineSeg.fromXYs(0, 0, 10, 0)
    point = Point.fromXY(5, 5)
    p = closestPointOnLineSegToPoint(seg, point)
    self.assertEqual(p, Point.fromXY(5, 0))

  def testClosestPointSlopedPointOnLine(self):
    seg = LineSeg.fromXYs(0, 0, 10, 10)
    point = Point.fromXY(5, 5)
    p = closestPointOnLineSegToPoint(seg, point)
    self.assertEqual(p, Point.fromXY(5, 5))

  def testClosestPointSloped(self):
    seg = LineSeg.fromXYs(0, 0, 10, 10)
    point = Point.fromXY(0, 10)
    p = closestPointOnLineSegToPoint(seg, point)
    self.assertEqual(p, Point.fromXY(5, 5))

  def testLengthZero(self):
    seg = LineSeg.fromXYs(0, 0, 0, 0)
    p = Point.fromXY(0, 1)
    p = closestPointOnLineSegToPoint(seg, p)
    self.assertEqual(p, Point.fromXY(0, 0))


class TestClosestPointsLineSegPathToPolygon(unittest.TestCase):
  def setUp(self):
    seg1 = LineSeg.fromXYs(0, 0, 20, 0)
    self.seg2 = LineSeg.fromXYs(20, 0, 20, 20)
    self.path = LineSegPath.fromSegments([seg1, self.seg2])

    seg3 = LineSeg.fromXYs(10, 30, 30, 30)
    seg4 = LineSeg.fromXYs(30, 30, 30, 50)
    seg5 = LineSeg.fromXYs(30, 50, 10, 50)
    seg6 = LineSeg.fromXYs(10, 50, 10, 30)
    self.poly = Polygon.fromSegments([seg3, seg4, seg5, seg6])

  def testClosestPoints(self):
    points = closestPointsLineSegPathToPolygon(self.path, self.poly)
    self.assertIn(self.seg2.p2, points)
    self.assertIn(Point.fromXY(20, 30), points)


class TestClosestPointsLineSegToLineSeg(unittest.TestCase):
  def testClosestPointsCoLinear(self):
    seg1 = LineSeg.fromXYs(0, 0, 10, 0)
    seg2 = LineSeg.fromXYs(20, 0, 30, 0)
    points = closestPointsLineSegToLineSeg(seg1, seg2)
    self.assertIn(Point.fromXY(20, 0), points)
    self.assertIn(Point.fromXY(10, 0), points)

  def testClosestPointsPerpSpaced(self):
    seg1 = LineSeg.fromXYs(0, 0, 10, 0)
    seg2 = LineSeg.fromXYs(5, 5, 5, 30)
    points = closestPointsLineSegToLineSeg(seg1, seg2)
    self.assertIn(Point.fromXY(5, 0), points)
    self.assertIn(Point.fromXY(5, 5), points)

  def testClosestPointsParallel(self):
    seg1 = LineSeg.fromXYs(0, 0, 10, 0)
    seg2 = LineSeg.fromXYs(0, 10, 10, 10)
    points = closestPointsLineSegToLineSeg(seg1, seg2)
    p1 = [p for p in points if p.y == 0][0]
    self.assertAlmostEqual(distanceLineSegToPoint(seg1, p1), 0)
    p2 = [p for p in points if p.y == 10][0]
    self.assertAlmostEqual(distanceLineSegToPoint(seg2, p2), 0)

  def testClosestPointsIntersection(self):
    seg1 = LineSeg.fromXYs(0, 0, 10, 10)
    seg2 = LineSeg.fromXYs(0, 10, 10, 0)
    points = closestPointsLineSegToLineSeg(seg1, seg2)
    for p in points:
      self.assertEqual(p, Point.fromXY(5, 5))

  def testClosestPointsPerp(self):
    seg1 = LineSeg.fromXYs(0, 0, 0, 2)
    seg2 = LineSeg.fromXYs(3, 1, 1, 1)
    points = closestPointsLineSegToLineSeg(seg1, seg2)
    self.assertTrue(Point.fromXY(0, 1) in points)
    self.assertTrue(Point.fromXY(1, 1) in points)


class TestClosestLineSegOnLineSegPathToPoint(unittest.TestCase):
  def testSpaced(self):
    seg1 = LineSeg.fromXYs(10, 30, 30, 30)
    seg2 = LineSeg.fromXYs(30, 30, 30, 50)
    seg3 = LineSeg.fromXYs(30, 50, 10, 50)
    seg4 = LineSeg.fromXYs(10, 50, 10, 30)
    path = LineSegPath.fromSegments([seg1, seg2, seg3, seg4])
    p = Point.fromXY(20, 20)
    closestSeg = closestLineSegOnLineSegPathToPoint(path, p)
    self.assertEqual(closestSeg, seg1)

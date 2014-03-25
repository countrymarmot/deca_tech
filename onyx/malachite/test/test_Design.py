# test_Design.py
# Created by Craig Bishop on 18 June 2012
#
# malachite
# Copyright 2012 All Rights Reserved
#

import unittest
from malachite.Design import *
from malachite import Geom

class TestDesignObjectProperties(unittest.TestCase):
  def setUp(self):
    self.do = DesignObject("TEST")
    self.do.test = ""

  def testDefaultProperties(self):
    self.assertIn("objType", self.do.propertyNames())

  def testDefineProperty(self):
    self.do._defineProperty("test", "A Test")
    self.assertTrue(self.do.propertyNames())


class TestDesignObjectPropertyAccess(unittest.TestCase):
  def setUp(self):
    self.do = DesignObject("TEST")
    self.do.test = "some text"
    self.do._defineProperty("test", "A Test")

  def testPropertyNames(self):
    self.assertIn("test", self.do.propertyNames())

  def testPropertyText(self):
    self.assertEqual(self.do.propertyText("test"), "A Test")

  def testPropertyReadOnly(self):
    self.assertFalse(self.do.propertyReadOnly("test"))

  def testPropertyType(self):
    self.assertEqual(self.do.propertyType("test"), "TEXT")

  def testPropertyValue(self):
    self.assertEqual(self.do.propertyValue("test"), "some text")

  def testSetPropertyValue(self):
    self.do.setPropertyValue("test", "diff text")
    self.assertEqual(self.do.propertyValue("test"), "diff text")

  def testReadOnlyValue(self):
    self.assertRaises(RuntimeError, self.do.setPropertyValue, "objType", "BLAH")


class TestDesignObjectPropertySubObject(unittest.TestCase):
  def setUp(self):
    self.do = DesignObject("TEST")
    self.do.p = Geom.Point.fromXY(10, 20)
    self.do._defineProperty("x", "X Coord", evalStr="self.p")
    self.do._defineProperty("y", "Y Coord", evalStr="self.p")

  def testPropertyValues(self):
    self.assertEqual(self.do.propertyValue("x"), 10)
    self.assertEqual(self.do.propertyValue("y"), 20)

  def testSetPropertyValues(self):
    self.do.setPropertyValue("x", 33)
    self.do.setPropertyValue("y", 43)
    self.assertEqual(self.do.propertyValue("x"), 33)
    self.assertEqual(self.do.propertyValue("y"), 43)
    self.assertEqual(self.do.p.x, 33)
    self.assertEqual(self.do.p.y, 43)


class TestDesignObjectPropertyOrder(unittest.TestCase):
  def setUp(self):
    self.do = DesignObject("TEST")
    self.do.prop1 = 0
    self.do.prop2 = 0
    self.do.prop3 = 0

    self.do._defineProperty("prop2", "Prop2")
    self.do._defineProperty("prop3", "Prop3")
    self.do._defineProperty("prop1", "Prop1")

  def testPropertyNameOrder(self):
    propNames = self.do.propertyNames()
    self.assertEqual(propNames[0], "objType")
    self.assertEqual(propNames[1], "prop2")
    self.assertEqual(propNames[2], "prop3")
    self.assertEqual(propNames[3], "prop1")


class TestDesignProperties(unittest.TestCase):
  def setUp(self):
    self.design = Design()

  def testObjType(self):
    self.assertEqual(self.design.objType, "DESIGN")

  def testPackageExists(self):
    self.assertIsNotNone(self.design.package)


class TestPackageProperties(unittest.TestCase):
  def setUp(self):
    self.package = Package()

  def testObjType(self):
    self.assertEqual(self.package.objType, "PACKAGE")

  def testNetListExists(self):
    self.assertIsNotNone(self.package.nets)
    self.assertIsInstance(self.package.nets, list)

  def testDieListExits(self):
    self.assertIsNotNone(self.package.dies)
    self.assertIsInstance(self.package.dies, list)


class TestDieProperties(unittest.TestCase):
  def setUp(self):
    self.die = Die()

  def testObjType(self):
    self.assertEqual(self.die.objType, "DIE")


class TestLayerProperties(unittest.TestCase):
  def setUp(self):
    self.layer = Layer()

  def testObjType(self):
    self.assertEqual(self.layer.objType, "LAYER")

  def testHasPackage(self):
    self.assertIsNone(self.layer.package)

  def hasChildren(self):
    self.assertIsNotNone(self.layer.children)
    self.assertIsInstance(self.layer.children, list)


class TestNetProperties(unittest.TestCase):
  def setUp(self):
    self.net = Net()

  def testObjType(self):
    self.assertEqual(self.net.objType, "NET")

  def testHasPackage(self):
    self.assertIsNone(self.net.package)

  def testHasBranches(self):
    self.assertIsNotNone(self.net.branches)
    self.assertIsInstance(self.net.branches, list)


class TestBranchProperties(unittest.TestCase):
  def setUp(self):
    self.branch = Branch()

  def testObjType(self):
    self.assertEqual(self.branch.objType, "BRANCH")

  def testHasNet(self):
    self.assertIsNone(self.branch.net)

  def testHasChildren(self):
    self.assertIsNotNone(self.branch.children)
    self.assertIsInstance(self.branch.children, list)


class TestPadProperties(unittest.TestCase):
  def setUp(self):
    self.pad = Pad()

  def testObjType(self):
    self.assertEqual(self.pad.objType, "PAD")

  def testHasBranch(self):
    self.assertIsNone(self.pad.branch)

  def testHasLayer(self):
    self.assertIsNone(self.pad.layer)


class TestPathProperties(unittest.TestCase):
  def setUp(self):
    self.path = Path()

  def testObjType(self):
    self.assertEqual(self.path.objType, "PATH")

  def testHasBranch(self):
    self.assertIsNone(self.path.branch)

  def testHasLayer(self):
    self.assertIsNone(self.path.layer)

  def testHasSegments(self):
    self.assertIsNotNone(self.path.segments)
    self.assertIsInstance(self.path.segments, list)


class TestPathSegmentProperties(unittest.TestCase):
  def setUp(self):
    self.pathSeg = PathSegment()

  def testObjType(self):
    self.assertEqual(self.pathSeg.objType, "PATHSEGMENT")

  def testHasPath(self):
    self.assertIsNone(self.pathSeg.path)


class TestShapeProperties(unittest.TestCase):
  def setUp(self):
    self.shape = Shape()

  def testObjType(self):
    self.assertEqual(self.shape.objType, "SHAPE")

  def testHasBranch(self):
    self.assertIsNone(self.shape.branch)

  def testHasLayer(self):
    self.assertIsNone(self.shape.layer)


class TestRouteProperties(unittest.TestCase):
  def setUp(self):
    self.routeDef = RouteDefinition()

  def testBranches(self):
    self.assertIsNone(self.routeDef.designObject1)
    self.assertIsNone(self.routeDef.designObject2)


class TestDistancePadToPad(unittest.TestCase):
  def setUp(self):
    self.pad1 = Pad()
    self.pad1.center = Point.fromXY(0, 0)
    self.pad1.diameter = 80

    self.pad2 = Pad()
    self.pad2.center = Point.fromXY(200, 0)
    self.pad2.diameter = 80

  def testDistance(self):
    self.assertAlmostEqual(distancePadToPad(self.pad1, self.pad2),
        120)


class TestDistancePadToPath(unittest.TestCase):
  def setUp(self):
    self.pad = Pad()
    self.pad.center = Point.fromXY(0, 0)
    self.pad.diameter = 20.0

    self.path = Path()
    seg = PathSegment()
    seg.p1 = Point.fromXY(100, 0)
    seg.p2 = Point.fromXY(200, 100)
    seg.traceWidth = 20.0
    self.path.segments.append(seg)

  def testDistance(self):
    self.assertAlmostEqual(distancePadToPath(self.pad, self.path),
        80)


class TestDistancePadToShape(unittest.TestCase):
  def setUp(self):
    self.pad = Pad()
    self.pad.center = Point.fromXY(20, 0)
    self.pad.diameter = 10.0

    self.shape = Shape()
    self.shape.segments.append(Geom.LineSeg.fromXYs(0, 0, 10, 0))
    self.shape.segments.append(Geom.LineSeg.fromXYs(10, 0, 10, 10))
    self.shape.segments.append(Geom.LineSeg.fromXYs(10, 10, 0, 10))
    self.shape.segments.append(Geom.LineSeg.fromXYs(0, 10, 0, 0))

  def testDistance(self):
    self.assertAlmostEqual(distancePadToShape(self.pad, self.shape), 5)


class TestDistancePathToPath(unittest.TestCase):
  def setUp(self):
    self.path1 = Path()
    seg = PathSegment()
    seg.p1 = Geom.Point.fromXY(0, 0)
    seg.p2 = Geom.Point.fromXY(-10, 0)
    seg.traceWidth = 10.0
    self.path1.segments.append(seg)

    self.path2 = Path()
    seg = PathSegment()
    seg.p1 = Geom.Point.fromXY(20, 0)
    seg.p2 = Geom.Point.fromXY(30, 0)
    seg.traceWidth = 10.0
    self.path2.segments.append(seg)

  def testDistance(self):
    self.assertAlmostEqual(distancePathToPath(self.path1, self.path2), 10)


class TestDistancePathToShape(unittest.TestCase):
  def setUp(self):
    self.shape = Shape()
    self.shape.segments.append(Geom.LineSeg.fromXYs(0, 0, 10, 0))
    self.shape.segments.append(Geom.LineSeg.fromXYs(10, 0, 10, 10))
    self.shape.segments.append(Geom.LineSeg.fromXYs(10, 10, 0, 10))
    self.shape.segments.append(Geom.LineSeg.fromXYs(0, 10, 0, 0))

    self.path = Path()
    seg = PathSegment()
    seg.p1 = Geom.Point.fromXY(30, 0)
    seg.p2 = Geom.Point.fromXY(40, 0)
    seg.traceWidth = 20.0
    self.path.segments.append(seg)

  def testDistance(self):
    self.assertAlmostEqual(distancePathToShape(self.path, self.shape), 10)


class TestDistanceShapeToShape(unittest.TestCase):
  def setUp(self):
    self.shape1 = Shape()
    self.shape1.segments.append(Geom.LineSeg.fromXYs(0, 0, 10, 0))
    self.shape1.segments.append(Geom.LineSeg.fromXYs(10, 0, 10, 10))
    self.shape1.segments.append(Geom.LineSeg.fromXYs(10, 10, 0, 10))
    self.shape1.segments.append(Geom.LineSeg.fromXYs(0, 10, 0, 0))

    self.shape2 = Shape()
    self.shape2.segments.append(Geom.LineSeg.fromXYs(20, 0, 30, 0))
    self.shape2.segments.append(Geom.LineSeg.fromXYs(30, 0, 30, 10))
    self.shape2.segments.append(Geom.LineSeg.fromXYs(30, 10, 20, 10))
    self.shape2.segments.append(Geom.LineSeg.fromXYs(20, 10, 20, 0))

  def testDistance(self):
    self.assertAlmostEqual(distanceShapeToShape(self.shape1, self.shape2), 10)


class TestCreateShortestRouteDefintion(unittest.TestCase):
  def setUp(self):
    self.branch1 = Branch()
    self.branch2 = Branch()

    self.pad1 = Pad()
    self.pad1.center = Geom.Point.fromXY(0, 0)
    self.pad1.diameter = 30
    self.pad1.branch = self.branch1
    self.branch1.children.append(self.pad1)

    self.pad2 = Pad()
    self.pad2.center = Geom.Point.fromXY(100, 0)
    self.pad2.diameter = 30
    self.pad2.branch = self.branch2
    self.branch2.children.append(self.pad2)

    self.path1 = Path()
    self.path1.branch = self.branch1
    seg1 = PathSegment()
    seg1.traceWidth = 20.0
    seg1.path = self.path1
    seg1.p1 = Geom.Point.fromXY(0, 0)
    seg1.p2 = Geom.Point.fromXY(50, 0)
    self.path1.segments.append(seg1)
    self.branch1.children.append(self.path1)

  def testRouteDefinitionDOs(self):
    routeDef = createShortestRouteDefinition(self.branch1, self.branch2)
    DOs = [routeDef.designObject1, routeDef.designObject2]
    self.assertIn(self.path1, DOs)
    self.assertIn(self.pad2, DOs)


class TestClosestPointsBetweenDesignObjets(unittest.TestCase):
  def testPadToPad(self):
    pad1 = Pad()
    pad1.center = Geom.Point.fromXY(0, 0)
    pad1.diameter = 30

    pad2 = Pad()
    pad2.center = Geom.Point.fromXY(100, 0)
    pad2.diameter = 30

    endPoints = closestPointsBetweenDesignObjects(pad1, pad2)
    self.assertIn(pad1.center, endPoints)
    self.assertIn(pad2.center, endPoints)
    endPoints = closestPointsBetweenDesignObjects(pad2, pad1)
    self.assertIn(pad1.center, endPoints)
    self.assertIn(pad2.center, endPoints)

  def testPadToPathEndPoints(self):
    pad = Pad()
    pad.center = Geom.Point.fromXY(0, 0)
    pad.diameter = 20

    path = Path()
    seg1 = PathSegment()
    seg1.p1 = Geom.Point.fromXY(20, -10)
    seg1.p2 = Geom.Point.fromXY(20, 10)
    path.segments.append(seg1)

    endPoints = closestPointsBetweenDesignObjects(pad, path)
    self.assertIn(pad.center, endPoints)
    self.assertIn(Geom.Point.fromXY(20, 0), endPoints)
    endPoints = closestPointsBetweenDesignObjects(path, pad)
    self.assertIn(pad.center, endPoints)
    self.assertIn(Geom.Point.fromXY(20, 0), endPoints)

  def testPathToPathEndPoints(self):
    path1 = Path()
    seg1 = PathSegment()
    seg1.p1 = Geom.Point.fromXY(0, 0)
    seg1.p2 = Geom.Point.fromXY(10, 0)
    seg2 = PathSegment()
    seg2.p1 = Geom.Point.fromXY(0, 10)
    seg2.p2 = Geom.Point.fromXY(0, 0)
    path1.segments = [seg1, seg2]

    path2 = Path()
    seg3 = PathSegment()
    seg3.p1 = Geom.Point.fromXY(20, 0)
    seg3.p2 = Geom.Point.fromXY(30, 0)
    seg4 = PathSegment()
    seg4.p1 = Geom.Point.fromXY(30, 10)
    seg4.p2 = Geom.Point.fromXY(30, 0)
    path2.segments = [seg3, seg4]

    endPoints = closestPointsBetweenDesignObjects(path1, path2)
    self.assertIn(Geom.Point.fromXY(10, 0), endPoints)
    self.assertIn(Geom.Point.fromXY(20, 0), endPoints)
    endPoints = closestPointsBetweenDesignObjects(path2, path1)
    self.assertIn(Geom.Point.fromXY(10, 0), endPoints)
    self.assertIn(Geom.Point.fromXY(20, 0), endPoints)

  def testPathToPolyEndPoints(self):
    seg1 = LineSeg.fromXYs(10, 10, 10, 20)
    seg2 = LineSeg.fromXYs(10, 20, 20, 20)
    seg3 = LineSeg.fromXYs(20, 20, 20, 10)
    seg4 = LineSeg.fromXYs(20, 10, 10, 10)
    shape = Shape()
    shape.segments = [seg1, seg2, seg3, seg4]

    path = Path()
    seg5 = PathSegment()
    seg5.p1 = Geom.Point.fromXY(0, 15)
    seg5.p2 = Geom.Point.fromXY(5, 15)
    path.segments.append(seg5)

    endPoints = closestPointsBetweenDesignObjects(path, shape)
    self.assertIn(Geom.Point.fromXY(5, 15), endPoints)
    self.assertIn(Geom.Point.fromXY(10, 15), endPoints)
    endPoints = closestPointsBetweenDesignObjects(shape, path)
    self.assertIn(Geom.Point.fromXY(5, 15), endPoints)
    self.assertIn(Geom.Point.fromXY(10, 15), endPoints)

  def testPadToPolygon(self):
    seg1 = LineSeg.fromXYs(10, 10, 10, 20)
    seg2 = LineSeg.fromXYs(10, 20, 20, 20)
    seg3 = LineSeg.fromXYs(20, 20, 20, 10)
    seg4 = LineSeg.fromXYs(20, 10, 10, 10)
    shape = Shape()
    shape.segments = [seg1, seg2, seg3, seg4]

    pad = Pad()
    pad.center = Geom.Point.fromXY(0, 15)
    pad.diameter = 10

    endPoints = closestPointsBetweenDesignObjects(shape, pad)
    self.assertIn(Geom.Point.fromXY(0, 15), endPoints)
    self.assertIn(Geom.Point.fromXY(10, 15), endPoints)
    endPoints = closestPointsBetweenDesignObjects(pad, shape)
    self.assertIn(Geom.Point.fromXY(0, 15), endPoints)
    self.assertIn(Geom.Point.fromXY(10, 15), endPoints)

  def testPolygonToPolygon(self):
    seg1 = LineSeg.fromXYs(10, 10, 10, 20)
    seg2 = LineSeg.fromXYs(10, 20, 20, 20)
    seg3 = LineSeg.fromXYs(20, 20, 20, 10)
    seg4 = LineSeg.fromXYs(20, 10, 10, 10)
    shape1 = Shape()
    shape1.segments = [seg1, seg2, seg3, seg4]

    seg5 = LineSeg.fromXYs(0, 0, -10, 0)
    seg6 = LineSeg.fromXYs(-10, 0, -10, -10)
    seg7 = LineSeg.fromXYs(-10, -10, 0, 0)
    shape2 = Shape()
    shape2.segments = [seg5, seg6, seg7]

    endPoints = closestPointsBetweenDesignObjects(shape1, shape2)
    self.assertIn(Geom.Point.fromXY(0, 0), endPoints)
    self.assertIn(Geom.Point.fromXY(10, 10), endPoints)

    endPoints = closestPointsBetweenDesignObjects(shape2, shape1)
    self.assertIn(Geom.Point.fromXY(0, 0), endPoints)
    self.assertIn(Geom.Point.fromXY(10, 10), endPoints)


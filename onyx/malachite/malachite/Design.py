# Design.py
# Created by Craig Bishop on 11 June 2012
#
# malachite
# Copyright 2012 Deca Technologies All Rights Reserved
#

from Geom import Point, LineSeg, LineSegPath, Circle, Polygon, Arc,\
    distanceCircleToCircle, distanceCircleToLineSeg, distancePolygonToPoint,\
    distanceLineSegToLineSeg, distanceLineSegToPolygon,\
    distancePolygonToPolygon,\
    closestPointOnLineSegPathToPoint,\
    closestPointsLineSegPathToLineSegPath, closestPointsLineSegPathToPolygon,\
    closestPointOnPolygonToPoint, closestPointsPolygonToPolygon,\
    distanceLineSegToPoint,\
    distanceCircleToPoint
import sys
import random
import math
import copy


class DesignObject:
  _propertyTypes = {str: "TEXT",
                    float: "NUMBER",
                    int: "NUMBER",
                    bool: "BOOL"
                    }

  def __init__(self, objType):
    self._properties = {}
    self._propertyNames = []
    self.objType = objType
    self._defineProperty("objType", "Object Type", readOnly=True)

  def propertyNames(self):
    return self._propertyNames

  def propertyText(self, propertyName):
    return self._properties[propertyName]['text']

  def propertyReadOnly(self, propertyName):
    return self._properties[propertyName]['readonly']

  def propertyType(self, propertyName):
    return self._properties[propertyName]['type']

  def propertyValue(self, propertyName):
    prop = self._properties[propertyName]
    return getattr(eval(prop['evalStr']), prop['attr'])

  def setPropertyValue(self, propertyName, value):
    prop = self._properties[propertyName]
    if prop['readonly']:
      raise RuntimeError
    setattr(eval(prop['evalStr']), prop['attr'], value)

  def _defineProperty(self, name, text, ptype=None, evalStr=None, attr=None,
          readOnly=None):
    if evalStr is None:
      evalStr = "self"
    if attr is None:
      attr = name
    if ptype is None:
      ptype = self._propertyTypes.get(type(getattr(eval(evalStr), attr)),
          "UNKNOWN")
    if readOnly is None:
      readOnly = False
    prop = {'text': text,
            'readonly': readOnly,
            'type': ptype,
            'evalStr': evalStr,
            'attr': attr}
    self._properties[name] = prop
    self._propertyNames.append(name)


class Rules(DesignObject):
  def __init__(self):
    DesignObject.__init__(self, "RULES")
    self.minGlobalSpacing = 10

    self._defineProperty("minGlobalSpacing", u"Min Global Spacing (\u03bcm)")


class Design(DesignObject):
  def __init__(self):
    DesignObject.__init__(self, "DESIGN")
    self.package = Package()
    self.routeDefinitions = []
    self.rules = Rules()


class Package(DesignObject):
  def __init__(self):
    DesignObject.__init__(self, "PACKAGE")
    self.name = "Unnamed Package"
    self.center = Point()
    self.width = 0
    self.height = 0
    self.nets = []
    self.dies = []
    self.layers = []
    self.designNumber = ""
    self.designRevision = ""
    self.routeKeepInCenter = Point()
    self.routeKeepInWidth = 0
    self.routeKeepInHeight = 0

    self._defineProperty("name", "Name")
    self._defineProperty("designNumber", "Drawing #")
    self._defineProperty("designRevision", "Drawing Rev")
    #self._defineProperty("x", "Center X", evalStr="self.center")
    #self._defineProperty("y", "Center Y", evalStr="self.center")
    self._defineProperty("width", u"Width (\u03bcm)")
    self._defineProperty("height", u"Height (\u03bcm)")
    self._defineProperty("x", "Route Keep-In Center X",
        evalStr="self.routeKeepInCenter")
    self._defineProperty("y", "Route Keep-In Center Y",
        evalStr="self.routeKeepInCenter")
    self._defineProperty("routeKeepInWidth", "Route Keep-In Width")
    self._defineProperty("routeKeepInHeight", "Route Keep-In Height")

  def layerForName(self, name):
    try:
      return [layer for layer in self.layers if layer.name == name][0]
    except IndexError:
      return None


class ShiftConstraint:
  def __init__(self):
    self.maxRadialShift = 45.0
    self.constraintX = 0.0
    self.constraintY = 0.0


class Die(DesignObject):
  def __init__(self):
    DesignObject.__init__(self, "DIE")
    self.name = "Unnamed Die"
    self.center = Point()
    self.width = 0
    self.height = 0
    self.shiftConstraint = ShiftConstraint()
    self.placement = []
    self.showInDesign = True
    self.fiducial = False
    self.critical = False

    self._defineProperty("name", "Name")
    self._defineProperty("x", "Center X", evalStr="self.center")
    self._defineProperty("y", "Center Y", evalStr="self.center")
    self._defineProperty("width", u"Width (\u03bcm)")
    self._defineProperty("height", u"Height (\u03bcm)")
    self._defineProperty("maxRadialShift", u"Max Radial Shift (\u03bcm)",
        evalStr="self.shiftConstraint")
    self._defineProperty("constraintX", u"Shift Constraint X (\u03bcm)",
        evalStr="self.shiftConstraint")
    self._defineProperty("constraintY", u"Shift Constraint Y (\u03bcm)",
        evalStr="self.shiftConstraint")


class Prestratum:
  def __init__(self):
    self.isShifted = False
    self.gdsData = None


class GDSTemplate:
  def __init__(self, offset):
    self.hasGlobalOffset = offset
    self.gdsData = None


class Layer(DesignObject):
  def __init__(self):
    DesignObject.__init__(self, "LAYER")
    self.name = "Unnamed Layer"
    self.number = 1
    self.package = None
    self.children = []
    self.prestratum = None

    self._defineProperty("name", "Name")
    self._defineProperty("number", "Number")


class Net(DesignObject):
  def __init__(self):
    DesignObject.__init__(self, "NET")
    self.name = "Unnamed Net"
    self.package = None
    self.branches = []
    self.color = (random.randint(90, 255), random.randint(90, 200),
        random.randint(90, 255))

    self._defineProperty("name", "Name")

  def netColor(self):
    if not self.color:
      self.color = (random.randint(90, 255), random.randint(90, 200),
          random.randint(90, 255))
    return self.color


class Branch(DesignObject):
  def __init__(self):
    DesignObject.__init__(self, "BRANCH")
    self.net = None
    self.children = []


class Pad(DesignObject, Circle):
  def __init__(self):
    DesignObject.__init__(self, "PAD")
    Circle.__init__(self)
    self.name = "Unnamed Pad"
    self.branch = None
    self.layer = None
    self.shifts = False

    self._defineProperty("layer", "Layer", "TEXT", "self.layer", "name", True)
    self._defineProperty("net", "Net", "TEXT", "self.branch.net", "name", True)
    self._defineProperty("name", "Name")
    self._defineProperty("x", "Center X", evalStr="self.center")
    self._defineProperty("y", "Center Y", evalStr="self.center")
    self._defineProperty("diameter", u"Diameter (\u03bcm)")
    self._defineProperty("shifts", u"Shifts)", "BOOL")


class Path(DesignObject, LineSegPath):
  def __init__(self):
    DesignObject.__init__(self, "PATH")
    LineSegPath.__init__(self)
    self.branch = None
    self.layer = None

    self._defineProperty("layer", "Layer", "TEXT", "self.layer", "name", True)
    self._defineProperty("net", "Net", "TEXT", "self.branch.net", "name", True)

  def linearSegments(self):
    segs = []
    for seg in self.segments:
      if isinstance(seg, PathArc):
        segs += seg.linearSegments()
      else:
        segs.append(seg)
    return segs


class PathSegment(DesignObject, LineSeg):
  def __init__(self):
    DesignObject.__init__(self, "PATHSEGMENT")
    LineSeg.__init__(self)
    self.traceWidth = 0.0
    self.path = None

    self._defineProperty("traceWidth", u"Trace Width (\u03bcm)")
    self._defineProperty("startX", "Start X", evalStr="self.p1", attr="x")
    self._defineProperty("startY", "Start Y", evalStr="self.p1", attr="y")
    self._defineProperty("endX", "End X", evalStr="self.p2", attr="x")
    self._defineProperty("endY", "End Y", evalStr="self.p2", attr="y")


class PathArc(DesignObject, Arc):
  def __init__(self):
    DesignObject.__init__(self, "PATHARC")
    Arc.__init__(self)
    self.traceWidth = 0.0
    self.path = None

    self._defineProperty("traceWidth", u"Trace Width (\u03bcm)")
    self._defineProperty("startX", "Start X", evalStr="self.p1", attr="x")
    self._defineProperty("startY", "Start Y", evalStr="self.p1", attr="y")
    self._defineProperty("endX", "End X", evalStr="self.p2", attr="x")
    self._defineProperty("endY", "End Y", evalStr="self.p2", attr="y")
    self._defineProperty("centerX", "Center X", evalStr="self.center",
        attr="x")
    self._defineProperty("centerY", "Center Y", evalStr="self.center",
        attr="y")

  def linearizedSegments(self):
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
    steps = max(5, int(L) / 5)
    step = sweep / float(steps)
    if self.cw:
      step *= -1.0
    lastPos = self.p1
    for i in range(steps):
      p = self.center.add(Point.fromXY(math.cos(math.radians(theta)) * r,
          math.sin(math.radians(theta)) * r))
      pseg = PathSegment()
      pseg.path = self.path
      pseg.traceWidth = self.traceWidth
      pseg.p1 = lastPos
      pseg.p2 = p
      segs.append(pseg)
      lastPos = p
      theta += step
    return segs


class Shape(DesignObject, Polygon):
  def __init__(self):
    DesignObject.__init__(self, "SHAPE")
    Polygon.__init__(self)
    self.branch = None
    self.layer = None

    self._defineProperty("layer", "Layer", "TEXT", "self.layer", "name", True)
    self._defineProperty("net", "Net", "TEXT", "self.branch.net", "name", True)

  def linearSegments(self):
    segs = []
    for seg in self.segments:
      if isinstance(seg, Arc):
        segs += seg.linearSegments()
      else:
        segs.append(seg)
    return segs


class RouteDefinition(DesignObject):
  def __init__(self):
    DesignObject.__init__(self, "ROUTEDEFINITION")
    self.designObject1 = None
    self.designObject2 = None
    self.traceWidth = 20.0

    self._defineProperty("traceWidth", u"Trace Width (\u03bcm)")

  def endPoints(self):
    return closestPointsBetweenDesignObjects(self.designObject1,
        self.designObject2)


def maxTraceWidthForPath(path):
  ret = -sys.maxint
  for seg in path.segments:
    ret = max(ret, seg.traceWidth)
  return ret


def distancePadToPad(pad1, pad2):
  return distanceCircleToCircle(pad1, pad2)


def distancePadToPath(pad, path):
  dist = float("inf")
  for seg in path.segments:
    d = distanceCircleToLineSeg(pad, seg)
    d -= seg.traceWidth / 2
    d = max(0, d)
    dist = min(dist, d)
  return dist


def findAllPads(design):
  pads = []
  for net in design.package.nets:
    for branch in net.branches:
      for do in branch.children:
        if do.objType == "PAD":
          pads.append(do)
  return pads


def findAllPaths(design):
  paths = []
  for net in design.package.nets:
    for branch in net.branches:
      for do in branch.children:
        if do.objType == "PATH":
          paths.append(do)
  return paths


def findAllShapes(design):
  shapes = []
  for net in design.package.nets:
    for branch in net.branches:
      for do in branch.children:
        if do.objType == "SHAPE":
          shapes.append(do)
  return shapes


def findAllDesignObjectsOnLayer(design, layer):
  dobjs = findAllPads(design) + findAllPaths(design) + findAllShapes(design)
  dobjs = [do for do in dobjs if do.layer == layer]
  return dobjs


def distancePadToShape(pad, shape):
  return max(0, distancePolygonToPoint(shape, pad.center) - pad.radius())


def distancePathToPad(path, pad):
  return distancePadToPath(pad, path)


def distancePathToPath(path1, path2):
  dist = sys.maxint
  for lseg in path1.segments:
    for rseg in path2.segments:
      d = distanceLineSegToLineSeg(lseg, rseg)
      d = max(0, d - (lseg.traceWidth / 2) - (rseg.traceWidth / 2))
      dist = min(d, dist)
  return dist


def distancePathToShape(path, shape):
  dist = sys.maxint
  for seg in path.segments:
    d = distanceLineSegToPolygon(seg, shape) - (seg.traceWidth / 2)
    d = max(0, d)
    dist = min(dist, d)
  return dist


def distanceShapeToPad(shape, pad):
  return distancePadToShape(pad, shape)


def distanceShapeToPath(shape, path):
  return distancePathToShape(path, shape)


def distanceShapeToShape(shape1, shape2):
  return distancePolygonToPolygon(shape1, shape2)


def distanceDesignObjectToDesignObject(do1, do2):
  funcmap = {("PAD", "PAD"): distancePadToPad,
             ("PAD", "PATH"): distancePadToPath,
             ("PAD", "SHAPE"): distancePadToShape,
             ("PATH", "PAD"): distancePathToPad,
             ("PATH", "PATH"): distancePathToPath,
             ("PATH", "SHAPE"): distancePathToShape,
             ("SHAPE", "PAD"): distanceShapeToPad,
             ("SHAPE", "PATH"): distanceShapeToPath,
             ("SHAPE", "SHAPE"): distanceShapeToShape}

  return funcmap[(do1.objType, do2.objType)](do1, do2)


def distancePointToPath(p, path):
  dist = float("inf")
  for seg in path.segments:
    d = distanceLineSegToPoint(seg, p) - (seg.traceWidth / 2)
    d = max(0, d)
    dist = min(dist, d)
  return dist


def distancePointToDie(p, die):
  ul = Point.fromXY(die.center.x - (die.width / 2), die.center.y +
      (die.height / 2))
  ur = Point.fromXY(die.center.x + (die.width / 2), die.center.y +
      (die.height / 2))
  ll = Point.fromXY(die.center.x - (die.width / 2), die.center.y -
      (die.height / 2))
  lr = Point.fromXY(die.center.x + (die.width / 2), die.center.y -
      (die.height / 2))
  poly = Polygon.fromSegments([LineSeg.fromPoints(ul, ll),
      LineSeg.fromPoints(ll, lr), LineSeg.fromPoints(lr, ur),
      LineSeg.fromPoints(ur, ul)])
  return distancePolygonToPoint(poly, p)


def distancePointToDesignObject(p, do):
  if do.objType == "PAD":
    return distanceCircleToPoint(do, p)
  elif do.objType == "PATH":
    return distancePointToPath(p, do)
  elif do.objType == "SHAPE":
    return distancePolygonToPoint(do, p)
  elif do.objType == "DIE":
    return distancePointToDie(p, do)
  elif do.objType == "ROUTEDEFINITION":
    points = closestPointsBetweenDesignObjects(do.designObject1,
        do.designObject2)
    seg = LineSeg.fromPoints(points[0], points[1])
    d = distanceLineSegToPoint(seg, p)
    d = max(0, d - (do.traceWidth / 2))
    return d
  return float("inf")


def distanceBranchToBranch(branch1, branch2):
  minDist = float("inf")
  for do1 in branch1.children:
    for do2 in branch2.children:
      d = distanceDesignObjectToDesignObject(do1, do2)
      minDist = min(minDist, d)
  return minDist


def createShortestRouteDefinition(branch1, branch2):
  if len(branch1.children) == 0 or len(branch2.children) == 0:
    return None

  rdef = RouteDefinition()
  minDist = float("inf")
  do1 = None
  do2 = None
  for c1 in branch1.children:
    for c2 in branch2.children:
      d = distanceDesignObjectToDesignObject(c1, c2)
      if d < minDist:
        minDist = d
        do1 = c1
        do2 = c2
  rdef.designObject1 = do1
  rdef.designObject2 = do2

  tws = [maxTraceWidthForPath(p) for p in [do1, do2] if p.objType == "PATH"]
  if not tws:
    tws += [p.diameter for p in [do1, do2] if p.objType == "PAD"]
  if tws:
    rdef.traceWidth = min(tws)
  else:
    tws = 20
  return rdef


def createShortestRouteDefinitionsForNet(net, existingRouteDefs=[]):
  routeDefs = []
  connectivity = []

  # fill connectivity list with existing route defs
  for rd in existingRouteDefs:
    connectivity.append(set([rd.designObject1, rd.designObject2]))

  if len(net.branches) < 2:
    return routeDefs
  for branch in net.branches:
    minDist = float("inf")
    closestBranch = None
    # find closest other branch
    for branch2 in net.branches:
      if branch2 == branch:
        continue
      d = distanceBranchToBranch(branch, branch2)
      if d < minDist:
        minDist = d
        closestBranch = branch2
    if minDist == float("inf"):
      continue
    if set([branch, closestBranch]) not in connectivity:
      rd = createShortestRouteDefinition(branch, closestBranch)
      routeDefs.append(rd)
      connectivity.append(set([branch, closestBranch]))
  return routeDefs


def createShortestRouteDefinitionsForDesign(design):
  routeDefs = []
  for net in design.package.nets:
    routeDefs += createShortestRouteDefinitionsForNet(net,
        design.routeDefinitions)
  return routeDefs


def closestPointsBetweenDesignObjects(do1, do2):
  if (do1.objType == "PAD" and do2.objType == "PAD"):
    return [do1.center, do2.center]
  if (do1.objType == "PAD" and do2.objType == "PATH"):
    return [do1.center, closestPointOnLineSegPathToPoint(do2, do1.center)]
  if (do2.objType == "PAD" and do1.objType == "PATH"):
    return [do2.center, closestPointOnLineSegPathToPoint(do1, do2.center)]
  if (do1.objType == "PATH" and do2.objType == "PATH"):
    return closestPointsLineSegPathToLineSegPath(do1, do2)
  if (do1.objType == "PATH" and do2.objType == "SHAPE"):
    return closestPointsLineSegPathToPolygon(do1, do2)
  if (do2.objType == "PATH" and do1.objType == "SHAPE"):
    return closestPointsLineSegPathToPolygon(do2, do1)
  if (do1.objType == "SHAPE" and do2.objType == "PAD"):
    return [do2.center, closestPointOnPolygonToPoint(do1, do2.center)]
  if (do2.objType == "SHAPE" and do1.objType == "PAD"):
    return [do1.center, closestPointOnPolygonToPoint(do2, do1.center)]
  if (do1.objType == "SHAPE" and do2.objType == "SHAPE"):
    return closestPointsPolygonToPolygon(do1, do2)


CLOCKWISE = 1
COUNTERCLOCKWISE = 2


def rotated(dobj, dir):
  return {
      "DESIGN": rotated_design,
      "PACKAGE": rotated_package,
      "DIE": rotated_die,
      "NET": rotated_net,
      "BRANCH": rotated_branch,
      "PAD": rotated_pad,
      "PATH": rotated_path,
      "PATHSEGMENT": rotated_path_segment,
      "PATHARC": rotated_path_arc,
      "SHAPE": rotated_shape
  }[dobj.objType](dobj, dir)


def rotated_design(design, dir):
  rotdesign = copy.deepcopy(design)
  rotdesign.package = rotated(rotdesign.package, dir)
  return rotdesign


def rotated_package(package, dir):
  newpkg = copy.deepcopy(package)
  newpkg.width = package.height
  newpkg.height = package.width
  for die in newpkg.dies:
    index = newpkg.dies.index(die)
    newpkg.dies.pop(index)
    newdie = rotated(die, dir)
    newpkg.dies.insert(index, newdie)
  for net in newpkg.nets:
    index = newpkg.nets.index(net)
    newpkg.nets.pop(index)
    newnet = rotated(net, dir)
    newnet.package = newpkg
    newpkg.nets.insert(index, newnet)
  return newpkg


def rotated_die(die, dir):
  newdie = copy.copy(die)
  newdie.width = die.height
  newdie.height = die.width
  if dir == CLOCKWISE:
    newdie.center = newdie.center.rotate(-math.pi / 2.0)
  else:
    newdie.center = newdie.center.rotate(math.pi / 2.0)
  return newdie


def rotated_net(net, dir):
  newnet = copy.copy(net)
  for b in newnet.branches:
    index = newnet.branches.index(b)
    newnet.branches.pop(index)
    newbranch = rotated(b, dir)
    newbranch.net = newnet
    newnet.branches.insert(index, newbranch)
  return newnet


def rotated_branch(branch, dir):
  newbranch = copy.copy(branch)
  for dobj in newbranch.children:
    index = newbranch.children.index(dobj)
    newbranch.children.pop(index)
    newdobj = rotated(dobj, dir)
    newdobj.branch = newbranch
    newbranch.children.insert(index, newdobj)
  return newbranch


def rotated_pad(pad, dir):
  newpad = copy.copy(pad)
  if dir == CLOCKWISE:
    newpad.center = newpad.center.rotate(-math.pi / 2.0)
  else:
    newpad.center = newpad.center.rotate(math.pi / 2.0)
  return newpad


def rotated_path(path, dir):
  newpath = copy.copy(path)
  for seg in newpath.segments:
    index = newpath.segments.index(seg)
    newpath.segments.pop(index)
    newseg = rotated(seg, dir)
    newseg.path = newpath
    newpath.segments.insert(index, newseg)
  return newpath


def rotated_path_segment(pathseg, dir):
  newpathseg = copy.copy(pathseg)
  if dir == CLOCKWISE:
    newpathseg.p1 = newpathseg.p1.rotate(-math.pi / 2.0)
    newpathseg.p2 = newpathseg.p2.rotate(-math.pi / 2.0)
  else:
    newpathseg.p1 = newpathseg.p1.rotate(math.pi / 2.0)
    newpathseg.p2 = newpathseg.p2.rotate(math.pi / 2.0)
  return newpathseg


def rotated_path_arc(patharc, dir):
  newpatharc = copy.copy(patharc)
  if dir == CLOCKWISE:
    newpatharc.center = newpatharc.center.rotate(-math.pi / 2.0)
    newpatharc.p1 = newpatharc.p1.rotate(-math.pi / 2.0)
    newpatharc.p2 = newpatharc.p2.rotate(-math.pi / 2.0)
  else:
    newpatharc.center = newpatharc.center.rotate(math.pi / 2.0)
    newpatharc.p1 = newpatharc.p1.rotate(math.pi / 2.0)
    newpatharc.p2 = newpatharc.p2.rotate(math.pi / 2.0)
  return newpatharc


def rotated_shape(shape, dir):
  newshape = copy.copy(shape)
  for seg in newshape.segments:
    index = newshape.segments.index(seg)
    newshape.segments.pop(index)
    if dir == CLOCKWISE:
      newseg = seg.rotate(-math.pi / 2.0)
    else:
      newseg = seg.rotate(math.pi / 2.0)
    newshape.segments.insert(index, newseg)
  return newshape

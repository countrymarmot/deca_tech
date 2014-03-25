# SIPImport.py
# Created by Craig Bishop on 12 July 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

import xml.etree.ElementTree as ET
from malachite.Geom import Point, Rect, LineSeg, Arc
from malachite import Design, Package, Die, Layer, Net, Branch, Pad,\
    Shape, Path, PathSegment, PathArc
from Command import Command
import copy

class SIPImporter:
  def _parsePackage(self, root, design):
    packageNode = root.find("package_geometry")
    llary = packageNode.find("ll").text.split(",")
    urary = packageNode.find("ur").text.split(",")
    ll = Point.fromXY(float(llary[0]), float(llary[1]))
    ur = Point.fromXY(float(urary[0]), float(urary[1]))
    rect = Rect.fromPoints(ll, ur)

    package = Package()
    package.center = rect.center()
    package.width = rect.width()
    package.height = rect.height()
    design.package = package

  def _parseDies(self, root, package):
    diesNode = root.find("die_geometries")
    for dieNode in diesNode.findall("die_outline"):
      llary = dieNode.find("ll").text.split(",")
      urary = dieNode.find("ur").text.split(",")
      ll = Point.fromXY(float(llary[0]), float(llary[1]))
      ur = Point.fromXY(float(urary[0]), float(urary[1]))
      rect = Rect.fromPoints(ll, ur)
      
      die = Die()
      die.center = rect.center()
      die.width = rect.width()
      die.height = rect.height()
      package.dies.append(die)

  def _parseLayers(self, root, package):
    layersNode = root.find("layers")
    for layerNode in layersNode.findall("layer"):
      layer = Layer()
      layer.name = layerNode.get("name")
      layer.package = package
      layer.number = int(layerNode.get("number"))
      package.layers.append(layer)

  def _parsePads(self, branchNode, branch):
    for padNode in branchNode.findall("pad"):
      pad = Pad()
      pad.name = padNode.get("name")
      pad.branch = branch
      layerName = padNode.get("layer")
      pad.layer = branch.net.package.layerForName(layerName)
      position = padNode.get("position").split(",")
      pad.center = Point.fromXY(float(position[0]), float(position[1]))
      pad.diameter = float(padNode.get("diameter"))
      branch.children.append(pad)

  def _parseShapes(self, branchNode, branch):
    for shapeNode in branchNode.findall("shape"):
      shape = Shape()
      shape.branch = branch
      layerName = shapeNode.get("layer")
      shape.layer = branch.net.package.layerForName(layerName)
      for segNode in shapeNode:
        start = segNode.get("start").split(",")
        end = segNode.get("end").split(",")
        if segNode.tag == "segment":
          seg = LineSeg.fromXYs(float(start[0]), float(start[1]), float(end[0]), float(end[1]))
        elif segNode.tag == "arc":
          center = segNode.get("center").split(",")
          seg = Arc.fromXYs(float(start[0]), float(start[1]), float(end[0]), float(end[1]),
              float(center[0]), float(center[1]), False)
          if segNode.get("dir") == "CW":
            seg.cw = True
        shape.segments.append(seg)
      branch.children.append(shape)

  def _parsePaths(self, branchNode, branch):
    for pathNode in branchNode.findall("path"):
      path = Path()
      path.branch = branch
      layerName = pathNode.get("layer")
      path.layer = branch.net.package.layerForName(layerName)
      for segNode in pathNode:
        start = segNode.get("start").split(",")
        end = segNode.get("end").split(",")
        if segNode.tag == "segment":
          seg = PathSegment()
          seg.p1 = Point.fromXY(float(start[0]), float(start[1]))
          seg.p2 = Point.fromXY(float(end[0]), float(end[1]))
        elif segNode.tag == "arc":
          seg = PathArc()
          center = segNode.get("center").split(",")
          seg.p1 = Point.fromXY(float(start[0]), float(start[1]))
          seg.p2 = Point.fromXY(float(end[0]), float(end[1]))
          seg.center = Point.fromXY(float(center[0]), float(center[1]))
          if segNode.get("dir") == "CW":
            seg.cw = True
        seg.traceWidth = float(segNode.get("width"))
        path.segments.append(seg)
      branch.children.append(path)

  def _parseBranches(self, netNode, net):
    for branchNode in netNode.findall("branch"):
      branch = Branch()
      branch.net = net
      net.branches.append(branch)
      self._parsePads(branchNode, branch)
      self._parseShapes(branchNode, branch)
      self._parsePaths(branchNode, branch)

  def _parseNets(self, root, package):
    netsNode = root.find("nets")
    for netNode in netsNode.findall("net"):
      net = Net()
      net.name = netNode.get("name")
      net.package = package
      package.nets.append(net)

      self._parseBranches(netNode, net)

  def designFromXML(self, xml):
    design = Design()
    root = ET.fromstring(xml)
    self._parsePackage(root, design)
    self._parseDies(root, design.package)
    self._parseLayers(root, design.package)
    self._parseNets(root, design.package)
    return design


class SIPImportCommand(Command):
  def __init__(self, project, importFilename):
    self.project = project
    self.filename = importFilename
    self.oldDesign = copy.deepcopy(project.design)

    importer = SIPImporter()
    self.importedDesign = importer.designFromXML(open(self.filename, 'r').read())

  def do(self):
    self.project.design = self.importedDesign
    self.project.setDirty()
    self.project.notifications.designHierarchyChanged.emit()

  def undo(self):
    self.project.design = self.oldDesign
    self.project.setDirty()
    self.project.notifications.designHierarchyChanged.emit()

  def __str__(self):
    return u"Import {0}".format(self.filename)


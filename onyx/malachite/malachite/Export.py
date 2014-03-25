# Export.py
# Created by Craig Bishop on 27 November 2012
#
# malachite
# Copyright 2012 All Rights Reserved
#

import Design
import Geom
from Design import findAllPads, findAllPaths, findAllShapes
import zinc_pb2
import zlib


def CreateFiducialDieForExport(design):
  fiducialDie = Design.Die()
  fiducialDie.name = "FIDUCIAL"
  fiducialDie.center = Geom.Point()
  fiducialDie.width = 2000
  fiducialDie.height = 2000
  fiducialDie.shiftConstraint.maxRadialShift = 1000.0
  fiducialDie.shiftConstraint.constraintX = 0.0
  fiducialDie.shiftConstraint.constraintY = 0.0
  fiducialDie.showInDesign = False
  fiducialDie.critical = True
  fiducialDie.fiducial = True
  return fiducialDie


def ExportRulesToZinc(design, zdesign):
  # just some constants until an interface for defining these is built
  zdesign.rules.minGlobalSpacing = design.rules.minGlobalSpacing
  zdesign.rules.routeKeepIn.center.x = design.package.routeKeepInCenter.x
  zdesign.rules.routeKeepIn.center.y = design.package.routeKeepInCenter.y
  zdesign.rules.routeKeepIn.width = design.package.routeKeepInWidth
  zdesign.rules.routeKeepIn.height = design.package.routeKeepInHeight


def ExportDiesToZinc(design, dies, zdesign_field):
  for die in dies:
    zdie = zdesign_field.add()
    zdie.name = die.name
    zdie.index = dies.index(die)
    zdie.outline.center.x = die.center.x
    zdie.outline.center.y = die.center.y
    zdie.outline.width = die.width
    zdie.outline.height = die.height

    zdie.critical = die.critical
    zshiftConstraint = zdie.shiftConstraints.add()

    zshiftConstraint.maxRadialShift = die.shiftConstraint.maxRadialShift
    zshiftConstraint.constraintX = die.shiftConstraint.constraintX
    zshiftConstraint.constraintY = die.shiftConstraint.constraintY

    if not die.fiducial:
      ExportDieLayersToZinc(design, zdie)
    else:
      ExportFiducialDieLayersToZinc(design, zdie)


def ExportDieLayersToZinc(design, zdie):
  layers = design.package.layers
  for layer in layers:
    zdielayer = zdie.dieLayers.add()
    zdielayer.number = layer.number
    ExportPadsToZinc(design, layer, zdielayer, True)
    ExportPrestratumToZinc(design, layer, zdielayer)
    ExportShiftedPrestratumToZinc(design, layer, zdielayer)


def ExportFiducialDieLayersToZinc(design, zdie):
  layers = design.package.layers
  for layer in layers:
    zdielayer = zdie.dieLayers.add()
    zdielayer.number = layer.number
    if hasattr(layer, "fiducial"):
      prestratum = zdielayer.shiftedPrestratums.add()
      prestratum.isShifted = True
      prestratum.uncompressedSize = len(layer.fiducial.gdsData)
      prestratum.gdsData = zlib.compress(layer.fiducial.gdsData, 9)


def ExportPrestratumToZinc(design, layer, zdielayer):
  if not layer.prestratum:
    return
  prestratum = zdielayer.fixedPrestratums.add()
  prestratum.isShifted = layer.prestratum.isShifted
  prestratum.uncompressedSize = len(layer.prestratum.gdsData)
  prestratum.gdsData = zlib.compress(layer.prestratum.gdsData, 9)


def ExportShiftedPrestratumToZinc(design, layer, zdielayer):
  if not getattr(layer, "shiftedPrestratum", None):
    return
  shiftedPrestratum = zdielayer.shiftedPrestratums.add()
  shiftedPrestratum.isShifted = layer.shiftedPrestratum.isShifted
  shiftedPrestratum.uncompressedSize = len(layer.shiftedPrestratum.gdsData)
  shiftedPrestratum.gdsData = zlib.compress(layer.shiftedPrestratum.gdsData, 9)


def ExportPackageToZinc(design, zdesign):
  zdesign.package.outline.center.x = design.package.center.x
  zdesign.package.outline.center.y = design.package.center.y
  zdesign.package.outline.width = design.package.width
  zdesign.package.outline.height = design.package.height


def ExportLayersToZinc(design, zdesign):
  layers = design.package.layers
  for layer in layers:
    zlayer = zdesign.layers.add()
    zlayer.number = layer.number
    zlayer.name = layer.name
    ExportPadsToZinc(design, layer, zlayer, False)
    ExportPathsToZinc(design, layer, zlayer)
    ExportShapesToZinc(design, layer, zlayer)
    ExportRouteDefsToZinc(design, layer, zlayer)
    ExportOOSUnitDrawingToZinc(design, layer, zlayer)
    ExportDummyMetalTemplateToZinc(design, layer, zlayer)
    ExportWaferTemplateToZinc(design, layer, zlayer)


def ExportOOSUnitDrawingToZinc(design, layer, zlayer):
  if not getattr(layer, "outOfSpecUnitDrawing", None):
    return
  zlayer.outOfSpecPrestratum.isShifted = False
  zlayer.outOfSpecPrestratum.uncompressedSize =\
      len(layer.outOfSpecUnitDrawing.gdsData)
  zlayer.outOfSpecPrestratum.gdsData =\
      zlib.compress(layer.outOfSpecUnitDrawing.gdsData, 9)


def ExportDummyMetalTemplateToZinc(design, layer, zlayer):
  if not getattr(layer, "dummyMetalTemplate", None):
    return
  template = zlayer.gdsTemplates.add()
  template.hasGlobalOffset = layer.dummyMetalTemplate.hasGlobalOffset
  template.uncompressedSize = len(layer.dummyMetalTemplate.gdsData)
  template.gdsData = zlib.compress(layer.dummyMetalTemplate.gdsData, 9)


def ExportWaferTemplateToZinc(design, layer, zlayer):
  if not getattr(layer, "waferTemplate", None):
    return
  template = zlayer.gdsTemplates.add()
  template.hasGlobalOffset = layer.waferTemplate.hasGlobalOffset
  template.uncompressedSize = len(layer.waferTemplate.gdsData)
  template.gdsData = zlib.compress(layer.waferTemplate.gdsData, 9)


def ExportPadsToZinc(design, layer, zlayer, dynamic):
  pads = findAllPads(design)
  pads = [pad for pad in pads if (pad.layer.number == layer.number and
      pad.layer.name == layer.name)]
  for pad in pads:
    if pad.shifts != dynamic:
      continue
    if pad.shifts:
      zpad = zlayer.dynamicPads.add()
      zpad.dieIndex = 0
    else:
      zpad = zlayer.fixedPads.add()
    zpad.netID = design.package.nets.index(pad.branch.net) + 1
    zpad.xy.x = pad.center.x
    zpad.xy.y = pad.center.y
    zpad.radius = pad.radius()


def ExportPathsToZinc(design, layer, zlayer):
  paths = findAllPaths(design)
  paths = [path for path in paths if (path.layer.number == layer.number and
      path.layer.name == layer.name)]
  for path in paths:
    for seg in path.linearSegments():
      zpath = zlayer.fixedPaths.add()
      zpath.netID = design.package.nets.index(path.branch.net) + 1
      zpath.xy0.x = seg.p1.x
      zpath.xy0.y = seg.p1.y
      zpath.xy1.x = seg.p2.x
      zpath.xy1.y = seg.p2.y
      zpath.traceWidth = seg.traceWidth


def ExportShapesToZinc(design, layer, zlayer):
  shapes = findAllShapes(design)
  shapes = [shape for shape in shapes if (shape.layer.number == layer.number
      and shape.layer.name == layer.name)]
  for shape in shapes:
    zshape = zlayer.fixedShapes.add()
    zshape.netID = design.package.nets.index(shape.branch.net) + 1
    for seg in shape.linearSegments():
      zseg = zshape.segments.add()
      zseg.xy0.x = seg.p1.x
      zseg.xy0.y = seg.p1.y
      zseg.xy1.x = seg.p2.x
      zseg.xy1.y = seg.p2.y


def ExportRouteDefsToZinc(design, layer, zlayer):
  routedefs = design.routeDefinitions
  routedefs = [rd for rd in routedefs if (rd.designObject1.layer.name ==
      layer.name and rd.designObject1.layer.number == layer.number)]

  for rd in routedefs:
    zroutedef = zlayer.routeDefinitions.add()
    zroutedef.netID = design.package.nets.index(rd.designObject1.branch.net)\
        + 1
    zroutedef.netName = rd.designObject1.branch.net.name
    endPoints = rd.endPoints()
    zroutedef.xy0.x = endPoints[0].x
    zroutedef.xy0.y = endPoints[0].y
    zroutedef.xy1.x = endPoints[1].x
    zroutedef.xy1.y = endPoints[1].y
    zroutedef.traceWidth = rd.traceWidth

    got0, got1 = False, False
    for do in [rd.designObject1, rd.designObject2]:
      if do.objType == "PAD":
        if endPoints.index(do.center) == 0:
          zroutedef.isShifted0 = do.shifts
          got0 = True
        else:
          zroutedef.isShifted1 = do.shifts
          got1 = True
    if not got0:
      zroutedef.isShifted0 = False
    if not got1:
      zroutedef.isShifted1 = False
    zroutedef.dieIndex0 = 0
    zroutedef.dieIndex1 = 0


def ExportDesignToZinc(design):
  zdesign = zinc_pb2.Design()
  zdesign.designNumber = design.package.designNumber
  zdesign.designRevision = design.package.designRevision

  ExportRulesToZinc(design, zdesign)

  ExportDiesToZinc(design, design.package.dies, zdesign.unitDie)
  ExportDiesToZinc(design, [CreateFiducialDieForExport(design)],
      zdesign.referenceDie)
  ExportLayersToZinc(design, zdesign)
  ExportPackageToZinc(design, zdesign)

  return zdesign.SerializeToString()

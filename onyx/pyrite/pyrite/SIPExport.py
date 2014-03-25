# SIPExport.py
# Created by Craig Bishop on 19 June 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

class ExportScriptOptionsException(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)

class ExportScriptOptions:
  def __init__(self):
    self._layers = []
    self._dieWScribeLayer = ""

  def dieWithScribeLayer(self):
    return self._dieWScribeLayer

  def setDieWithScribeLayer(self, layerName):
    self._dieWScribeLayer = layerName.upper()

  def layers(self):
    return self._layers

  def layerExists(self, name):
    for layer in self._layers:
      if layer["name"] == name:
        return True
    return False

  def layerForName(self, name):
    for layer in self._layers:
      if layer["name"] == name:
        return layer
    raise ExportScriptOptionsException("Layer does not exist")

  def addLayer(self, name):
    if self.layerExists(name):
      raise ExportScriptOptionsException("Layer already exists")
    layer = {"name": name, "number": 1, "cadName": "", "pins": False,\
        "vias": False, "shapes": False, "paths": False}
    self._layers.append(layer)
    return layer

  def removeLayer(self, name):
    layer = self.layerForName(name)
    self._layers.remove(layer)
    return layer

  def moveLayerUp(self, name):
    layer = self.layerForName(name)

    i = self._layers.index(layer) - 1
    i = max(0, i)
    self._layers.remove(layer)
    self._layers.insert(i, layer)

  def moveLayerDown(self, name):
    layer = self.layerForName(name)

    i = self._layers.index(layer) + 1
    i = min(len(self._layers), i)
    self._layers.remove(layer)
    self._layers.insert(i, layer)

  def cadenceLayerNameForLayer(self, name):
    layer = self.layerForName(name)
    return layer["cadName"]

  def setCadenceLayerNameForLayer(self, name, cadName):
    layer = self.layerForName(name)
    layer["cadName"] = cadName.upper()

  def layerNumberForLayer(self, name):
    layer = self.layerForName(name)
    return layer["number"]

  def setLayerNumberForLayer(self, name, num):
    layer = self.layerForName(name)
    layer["number"] = num

  def shouldExportPinsForLayer(self, name):
    layer = self.layerForName(name)
    return layer["pins"]

  def shouldExportViasForLayer(self, name):
    layer = self.layerForName(name)
    return layer["vias"]

  def shouldExportShapesForLayer(self, name):
    layer = self.layerForName(name)
    return layer["shapes"]
  
  def shouldExportPathsForLayer(self, name):
    layer = self.layerForName(name)
    return layer["paths"]

  def setShouldExportPinsForLayer(self, name, val):
    layer = self.layerForName(name)
    layer["pins"] = val

  def setShouldExportViasForLayer(self, name, val):
    layer = self.layerForName(name)
    layer["vias"] = val

  def setShouldExportShapesForLayer(self, name, val):
    layer = self.layerForName(name)
    layer["shapes"] = val

  def setShouldExportPathsForLayer(self, name, val):
    layer = self.layerForName(name)
    layer["paths"] = val

class SIPExportScriptGenerator:
  def _writePreamble(self):
    return """procedure(onyxOutput(filename)
  port = outfile(filename)
  fprintf(port "<?xml version=\\"1.0\\" encoding=\\"UTF-8\\" ?>\\n")
  fprintf(port "<design>\\n")\n\n"""

  def _writePostamble(self):
    return """  fprintf(port "</design>\\n")
  close(port)
)"""

  def _writePackageGeometry(self):
    return """  packageOutline = car(axlDBGetShapes("SUBSTRATE GEOMETRY/PACKAGE_OUTLINE"))
  ll = xCoord(packageOutline->bBox)
  ur = yCoord(packageOutline->bBox)
  fprintf(port "\\t<package_geometry>\\n")
  fprintf(port "\\t\\t<ll>%f, %f</ll>\\n" xCoord(ll) yCoord(ll))
  fprintf(port "\\t\\t<ur>%f, %f</ur>\\n" xCoord(ur) yCoord(ur))
  fprintf(port "\\t</package_geometry>\\n")\n\n"""

  def _writeDieGeometries(self, dieWScribeLayerName):
    return """  dieOutlines = axlDBGetShapes(\"{0}\")
  fprintf(port \"\\t<die_geometries>\\n\")
  foreach(outline dieOutlines
    fprintf(port \"\\t\\t<die_outline>\\n\")
    ll = xCoord(outline->bBox)
    ur = yCoord(outline->bBox)
    fprintf(port \"\\t\\t\\t<ll>%f, %f</ll>\\n\" xCoord(ll) yCoord(ll))
    fprintf(port \"\\t\\t\\t<ur>%f, %f</ur>\\n\" xCoord(ur) yCoord(ur))
    fprintf(port \"\\t\\t</die_outline>\\n\")
  )
  fprintf(port \"\\t</die_geometries>\\n\")\n\n""".format(dieWScribeLayerName)

  def _writePins(self):
    return """      pins = (setof c branch->children c->objType=="pin")
      (foreach pin pins
        (foreach pad (setof p pin->pads (and (member p->layer (mapcar 'car pinlayers)) p->type=="REGULAR"))
          diameter = caadr(pad->bBox) - caar(pad->bBox)
          (if diameter > 0
            fprintf(port "\\t\\t\\t\\t<pad name=\\"%s\\" layer=\\"%s\\" position=\\"%f, %f\\" diameter=\\"%f\\" />\\n" 
              pad->parent->name (cadr (assoc pad->layer pinlayers)) car(pin->xy) cadr(pin->xy) diameter)
          )
        )
      )\n"""

  def _writeVias(self):
    return """      vias = (setof c branch->children c->objType=="via")
      (foreach via vias
        (foreach pad (setof p via->pads (and (member p->layer (mapcar 'car vialayers)) p->type=="REGULAR"))
          diameter = caadr(pad->bBox) - caar(pad->bBox)
          (if diameter > 0
            fprintf(port "\\t\\t\\t\\t<pad name=\\"%s\\" layer=\\"%s\\" position=\\"%f, %f\\" diameter=\\"%f\\" />\\n" 
              pad->parent->name (cadr (assoc pad->layer vialayers)) car(via->xy) cadr(via->xy) diameter)
          )
        )
      )\n"""

  def _writeShapes(self):
    return """      shapes = (setof c branch->children c->objType=="shape")
      (foreach shape (setof s shapes (member s->layer (mapcar 'car shapelayers)))
        fprintf(port "\\t\\t\\t\\t<shape layer=\\"%s\\">\\n" (cadr (assoc shape->layer shapelayers)))
        (foreach segment shape->segments
          (if segment->objType == "line" then
            fprintf(port "\\t\\t\\t\\t\\t<segment start=\\"%f, %f\\" end=\\"%f, %f\\" />\\n" 
              caar(segment->startEnd) cadar(segment->startEnd) caadr(segment->startEnd) cadadr(segment->startEnd))
           else
            dir = "CCW"
            (when segment->isClockwise dir = "CW")
            fprintf(port "\\t\\t\\t\\t\\t<arc start=\\"%f, %f\\" end=\\"%f, %f\\" center=\\"%f, %f\\" dir=\\"%s\\" />\\n" 
              caar(segment->startEnd) cadar(segment->startEnd) caadr(segment->startEnd) cadadr(segment->startEnd)
              xCoord(segment->xy) yCoord(segment->xy) dir)
          )
        )
        fprintf(port "\\t\\t\\t\\t</shape>\\n")
      )\n"""

  def _writePaths(self):
    return """      paths = (setof c branch->children c->objType=="path")
      (foreach path (setof p paths (member p->layer (mapcar 'car pathlayers)))
        fprintf(port "\\t\\t\\t\\t<path layer=\\"%s\\">\\n" (cadr (assoc path->layer pathlayers)))
        (foreach segment path->segments
          (if segment->objType == "line" then
            fprintf(port "\\t\\t\\t\\t\\t<segment width=\\"%f\\" start=\\"%f, %f\\" end=\\"%f, %f\\" />\\n" segment->width 
              caar(segment->startEnd) cadar(segment->startEnd) caadr(segment->startEnd) cadadr(segment->startEnd))
           else
            dir = "CCW"
            (when segment->isClockwise dir = "CW")
            fprintf(port "\\t\\t\\t\\t\\t<arc width=\\"%f\\" start=\\"%f, %f\\" end=\\"%f, %f\\" center=\\"%f, %f\\" dir=\\"%s\\" />\\n" 
              segment->width caar(segment->startEnd) cadar(segment->startEnd) caadr(segment->startEnd) cadadr(segment->startEnd)
              xCoord(segment->xy) yCoord(segment->xy) dir)
          )
        )
        fprintf(port "\\t\\t\\t\\t</path>\\n")
      )\n"""

  def _writeBranch(self):
    out =  """      fprintf(port "\\t\\t\\t<branch>\\n")\n"""
    out += self._writePins()
    out += self._writeVias()
    out += self._writeShapes()
    out += self._writePaths()
    out += """      fprintf(port "\\t\\t\\t</branch>\\n")"""
    return out

  def _writeNet(self):
    out = """    fprintf(port "\\t\\t<net name=\\"%s\\">\\n" net->name)
    (foreach branch net->branches\n"""
    out += self._writeBranch()
    out += """    )
    fprintf(port "\\t\\t</net>\\n")\n"""
    return out

  def _writeNets(self):
    out = """  fprintf(port "\\t<nets>\\n")
  nets = axlDBGetDesign()->nets
  foreach(net nets\n"""
    out += self._writeNet()
    out += """  )
  fprintf(port "\\t</nets>\\n")\n\n"""
    return out

  def _writeLayer(self, name, number, cadName, pins, vias, shapes, paths):
    out = ""

    if pins:
      out += "  pinlayers = (cons '(\"{0}\" \"{1}\") pinlayers)\n".format(cadName, name)
    if vias:
      out += "  vialayers = (cons '(\"{0}\" \"{1}\") vialayers)\n".format(cadName, name)
    if shapes:
      out += "  shapelayers = (cons '(\"{0}\" \"{1}\") shapelayers)\n".format(cadName, name)
    if paths:
      out += "  pathlayers = (cons '(\"{0}\" \"{1}\") pathlayers)\n".format(cadName, name)
      
    out += "  fprintf(port \"\\t\\t<layer name=\\\"{0}\\\" number=\\\"{1}\\\"></layer>\\n\")"\
        .format(name, number)
    return out

  def _writeLayers(self, options):
    out =  """  pinlayers = nil
  vialayers = nil
  shapelayers = nil
  pathlayers = nil
  fprintf(port \"\\t<layers>\\n\")\n"""
    for layer in options.layers():
      out += self._writeLayer(layer["name"], layer["number"], layer["cadName"],\
          layer["pins"], layer["vias"], layer["shapes"], layer["paths"])
    out += "  fprintf(port \"\\t</layers>\\n\")\n\n"
    return out

  def writeExportScript(self, options):
    out = self._writePreamble()
    out += self._writePackageGeometry()
    out += self._writeDieGeometries(options.dieWithScribeLayer())
    out += self._writeLayers(options)
    out += self._writeNets()
    out += self._writePostamble()
    return out


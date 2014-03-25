# GDSSeparator.py
# Created by Craig Bishop on 12 March 2013
#
# pyrite
# Copyright 2013 All Rights Reserved
#

from PySide.QtGui import QMessageBox
import gdsii
import gdsii.library
import gdsii.elements
import gdsii.structure
import copy


class MemoryFile:
  def __init__(self):
    self._data = ""

  def write(self, str):
    self._data += str

  def getData(self):
    return self._data


def getLayerNumbers(struct, layerNums):
  for element in struct:
    if isinstance(element, gdsii.structure.Structure):
      getLayerNumbers(element, layerNums)
    elif isinstance(element, gdsii.elements.SRef) or\
            isinstance(element, gdsii.elements.ARef):
        pass
    else:
      if element.layer not in layerNums:
        layerNums.append(element.layer)


def removeOtherLayersFromStruct(struct, layerNum):
  removals = []
  for element in struct:
    if isinstance(element, gdsii.structure.Structure):
      removeOtherLayersFromStruct(element, layerNum)
    elif isinstance(element, gdsii.elements.SRef) or\
            isinstance(element, gdsii.elements.ARef):
        pass
    else:
      if element.layer != layerNum:
        removals.append(element)
  for element in removals:
    struct.remove(element)


def separatedGDSLayers(filename):
  try:
    lib = gdsii.library.Library.load(open(filename, 'rb'))
  except:
    QMessageBox.critical(None, "Invalid GDS file", "Pyrite could not "
        "parse the selected GDS file.")
    return
  layers = []

  # get all layers in file
  for struct in lib:
    getLayerNumbers(struct, layers)

  # create a copy for each layer
  libsByLayer = {}
  for layerNum in layers:
    libsByLayer[layerNum] = copy.deepcopy(lib)
    libsByLayer[layerNum][0].name = "TOP"

  # remove anything not on its layer
  for layerNum in libsByLayer:
    layerLib = libsByLayer[layerNum]
    for struct in layerLib:
      removeOtherLayersFromStruct(struct, layerNum)

  # write out data
  ret = {}
  for layerNum in libsByLayer:
    mem = MemoryFile()
    libsByLayer[layerNum].save(mem)
    ret[layerNum] = mem.getData()
  return ret

# LayerEditor.py
# Created by Craig Bishop on 28 December 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

from PySide.QtGui import QDialog, QFileDialog, QMessageBox
from PySide.QtCore import QSettings
from Ui_LayerEditor import Ui_LayerEditor
import malachite
from Command import Command
import copy
import os
from GDSSeparator import separatedGDSLayers


def findLayerForName(layers, name):
  try:
    return [layer for layer in layers if layer.name == name][0]
  except IndexError:
    return None


class LayerEditor(QDialog, Ui_LayerEditor):
  def __init__(self, parent, project):
    QDialog.__init__(self, parent)
    self.setupUi(self)
    self.connectActions()

    self._project = project
    self.reloadLayers(self._project)
    self.lstLayers.setCurrentRow(0)
    self.updateProperties()

    self.readWindowSettings()

  def connectActions(self):
    self.lstLayers.itemSelectionChanged.connect(self.selectedLayerChanged)
    self.btnMoveDown.clicked.connect(self.moveLayerDown)
    self.btnMoveUp.clicked.connect(self.moveLayerUp)
    self.btnAdd.clicked.connect(self.addLayer)
    self.btnRemove.clicked.connect(self.removeLayer)
    self.txtLayerName.textEdited.connect(self.txtLayerNameChanged)
    self.txtLayerName.editingFinished.connect(self.txtLayerNameChanged)
    self.txtLayerNumber.textEdited.connect(self.txtLayerNumberChanged)
    self.txtLayerNumber.editingFinished.connect(self.txtLayerNumberChanged)
    self.btnLoad.clicked.connect(self.loadPrestratumGDS)
    self.btnCancel.clicked.connect(self.reject)
    self.btnOK.clicked.connect(self.btnOKClicked)
    self.btnLoadDummy.clicked.connect(self.loadDummyMetalGDS)
    self.btnLoadTemplate.clicked.connect(self.loadWaferTemplateGDS)
    self.btnLoadAllPrestratum.clicked.connect(self.loadPrestratumGDSAllLayers)
    self.btnLoadAllDummy.clicked.connect(self.loadDummyMetalGDSAllLayers)
    self.btnLoadAllWaferTemplate.clicked.connect(
        self.loadWaferTemplateGDSAllLayers)
    self.btnLoadAllOOSUnitDrawing.clicked.connect(
        self.loadOOSUnitDraiwngAllLayers)
    self.btnLoadOOSUnitDrawing.clicked.connect(self.loadOOSUnitDrawing)
    self.btnLoadShiftedPrestratumGDS.clicked.connect(
        self.loadShiftedPrestratumGDS)
    self.btnLoadShiftedPrestratumAllLayers.clicked.connect(
        self.loadShiftedPrestratumGDSAllLayers)
    self.btnLoadFiducialUnitGDS.clicked.connect(
        self.loadShiftedFiducialUnitGDS)
    self.btnLoadFiducialUnitGDSAllLayers.clicked.connect(
        self.loadFiducialUnitGDSAllLayers)
    self.btnUnloadPrestratum.clicked.connect(self.unloadPrestratum)
    self.btnUnloadShiftedPrestratum.clicked.connect(
        self.unloadShiftedPrestratum)
    self.btnUnloadDummyMetal.clicked.connect(self.unloadDummyMetal)
    self.btnUnloadWaferTemplate.clicked.connect(self.unloadWaferTemplate)
    self.btnUnloadOoSUnit.clicked.connect(self.unloadOoSUnit)
    self.btnUnloadFiducialUnit.clicked.connect(self.unloadFiducialUnit)

  def closeEvent(self, event):
    self.writeWindowSettings()
    event.accept()

  def btnOKClicked(self):
    cmd = EditLayersCommand(self._project, self.layers, self._oldLayers)
    self._project.commandHistory.do(cmd)
    self.accept()

  def writeWindowSettings(self):
    settings = QSettings()
    settings.beginGroup("LayerEditor")
    settings.setValue("geometry", self.saveGeometry())
    settings.endGroup()

  def readWindowSettings(self):
    settings = QSettings()
    settings.beginGroup("LayerEditor")
    self.restoreGeometry(settings.value("geometry"))
    settings.endGroup()

  def reloadLayers(self, project):
    self.layers = copy.deepcopy(project.design.package.layers)
    self._oldLayers = copy.deepcopy(project.design.package.layers)
    for layer in self.layers:
      self.lstLayers.addItem(layer.name)

  def updateProperties(self):
    item = self.lstLayers.currentItem()
    if not item or self.lstLayers.count() == 0:
      self.grpProps.setEnabled(False)
      self.txtLayerName.setText("")
      self.txtLayerNumber.setText("")
      self.lblLoad.setText("(NOT LOADED)")
      self.lblLoadDummy.setText("(NOT LOADED)")
      self.lblLoadTemplate.setText("(NOT LOADED)")
      self.lblLoadOOSUnit.setText("(NOT LOADED)")
      self.lblLoadShiftedPrestratumGDS.setText("(NOT LOADED)")
      self.lblLoadFiducialUnitGDS.setText("(NOT LOADED)")
    else:
      layer = findLayerForName(self.layers, item.text())
      self.grpProps.setEnabled(True)
      self.txtLayerName.setText(layer.name)
      self.txtLayerNumber.setText(str(layer.number))
      if layer.prestratum:
        if layer.prestratum.gdsData:
          self.lblLoad.setText("(LOADED)")
          self.btnUnloadPrestratum.setEnabled(True)
        else:
          self.lblLoad.setText("(NOT LOADED)")
          self.btnUnloadPrestratum.setEnabled(False)
      else:
        self.lblLoad.setText("(NOT LOADED)")
        self.btnUnloadPrestratum.setEnabled(False)
      if getattr(layer, "dummyMetalTemplate", None):
        self.lblLoadDummy.setText("(LOADED)")
        self.btnUnloadDummyMetal.setEnabled(True)
      else:
        self.lblLoadDummy.setText("(NOT LOADED)")
        self.btnUnloadDummyMetal.setEnabled(False)
      if getattr(layer, "waferTemplate", None):
        self.lblLoadTemplate.setText("(LOADED)")
        self.btnUnloadWaferTemplate.setEnabled(True)
      else:
        self.lblLoadTemplate.setText("(NOT LOADED)")
        self.btnUnloadWaferTemplate.setEnabled(False)
      if getattr(layer, "outOfSpecUnitDrawing", None):
        self.lblLoadOOSUnit.setText("(LOADED)")
        self.btnUnloadOoSUnit.setEnabled(True)
      else:
        self.lblLoadOOSUnit.setText("(NOT LOADED)")
        self.btnUnloadOoSUnit.setEnabled(False)
      if getattr(layer, "shiftedPrestratum", None):
        self.lblLoadShiftedPrestratumGDS.setText("(LOADED)")
        self.btnUnloadShiftedPrestratum.setEnabled(True)
      else:
        self.lblLoadShiftedPrestratumGDS.setText("(NOT LOADED)")
        self.btnUnloadShiftedPrestratum.setEnabled(False)
      if getattr(layer, "fiducial", None):
        self.lblLoadFiducialUnitGDS.setText("(LOADED)")
        self.btnUnloadFiducialUnit.setEnabled(True)
      else:
        self.lblLoadFiducialUnitGDS.setText("(NOT LOADED)")
        self.btnUnloadFiducialUnit.setEnabled(False)

  def selectedLayerChanged(self):
    self.updateProperties()

  def addLayer(self):
    addedLayer = False
    layerName = "New Layer"
    i = 1
    while not addedLayer:
      layer = findLayerForName(self.layers, layerName)
      if layer:
        layerName = "New Layer {0}".format(i)
        i += 1
      else:
        layer = malachite.Layer()
        layer.package = self._project.design.package
        self.layers.append(layer)
        layer.name = layerName
        self.lstLayers.addItem(layer.name)
        self.lstLayers.setCurrentRow(self.lstLayers.count() - 1)
        addedLayer = True
        self.updateProperties()

  def removeLayer(self):
    item = self.lstLayers.currentItem()
    if not item:
      return
    layer = findLayerForName(self.layers, item.text())
    self.layers.remove(layer)
    item = self.lstLayers.takeItem(self.lstLayers.row(item))
    del(item)
    self.updateProperties()

  def moveLayerUp(self):
    item = self.lstLayers.currentItem()
    if not item:
      return
    lname = item.text()
    layer = findLayerForName(self.layers, lname)
    index = self.layers.index(layer)
    self.layers.remove(layer)
    index = max(0, index - 1)
    self.layers.insert(index, layer)

    row = self.lstLayers.row(item)
    self.lstLayers.takeItem(row)
    row = int(max(0, row - 1))
    self.lstLayers.insertItem(row, item)
    self.lstLayers.setCurrentRow(row)

  def moveLayerDown(self):
    item = self.lstLayers.currentItem()
    if not item:
      return
    lname = item.text()
    layer = findLayerForName(self.layers, lname)
    index = self.layers.index(layer)
    self.layers.remove(layer)
    index = min(len(self.layers), index + 1)
    self.layers.insert(index, layer)

    row = self.lstLayers.row(item)
    self.lstLayers.takeItem(row)
    row = int(min(self.lstLayers.count(), row + 1))
    self.lstLayers.insertItem(row, item)
    self.lstLayers.setCurrentRow(row)

  def txtLayerNameChanged(self):
    newName = self.txtLayerName.text()
    if newName:
      item = self.lstLayers.currentItem()
      layer = findLayerForName(self.layers, item.text())
      layer.name = newName
      item.setText(newName)

  def txtLayerNumberChanged(self):
    txt = self.txtLayerNumber.text()
    if txt.isdigit():
      item = self.lstLayers.currentItem()
      layer = findLayerForName(self.layers, item.text())
      layer.number = int(txt)

  def getLastPrestratumImportDir(self):
    settings = QSettings()
    settings.beginGroup("DefaultDirs")
    dir = str(settings.value("PrestratumImportDir"))
    settings.endGroup()
    if dir:
      return dir
    else:
      return ""

  def saveLastPrestratumImportDir(self, dir):
    settings = QSettings()
    settings.beginGroup("DefaultDirs")
    settings.setValue("PrestratumImportDir", dir)
    settings.endGroup()

  def loadPrestratumGDS(self):
    dir = self.getLastPrestratumImportDir()

    fn, filt = QFileDialog.getOpenFileName(self, "Select Prestratum GDS", dir,
        "GDS Files (*.gds)")
    if not fn:
      return
    self.saveLastPrestratumImportDir(os.path.dirname(fn))

    item = self.lstLayers.currentItem()
    layer = findLayerForName(self.layers, item.text())
    fp = open(fn, 'rb')
    if not getattr(layer, "prestratum", None):
      layer.prestratum = malachite.Prestratum()
    layer.prestratum.gdsData = fp.read()
    fp.close()
    self.updateProperties()

  def loadShiftedPrestratumGDS(self):
    dir = self.getLastPrestratumImportDir()

    fn, filt = QFileDialog.getOpenFileName(self,
        "Select Shifted Prestratum GDS", dir,
        "GDS Files (*.gds)")
    if not fn:
      return
    self.saveLastPrestratumImportDir(os.path.dirname(fn))

    item = self.lstLayers.currentItem()
    layer = findLayerForName(self.layers, item.text())
    fp = open(fn, 'rb')
    if not getattr(layer, "shiftedPrestratum", None):
      layer.shiftedPrestratum = malachite.Prestratum()
      layer.shiftedPrestratum.isShifted = True
    layer.shiftedPrestratum.gdsData = fp.read()
    fp.close()
    self.updateProperties()

  def loadDummyMetalGDS(self):
    dir = self.getLastPrestratumImportDir()

    fn, filt = QFileDialog.getOpenFileName(self, "Select Dummy Metal GDS", dir,
        "GDS Files (*.gds)")
    if not fn:
      return
    self.saveLastPrestratumImportDir(os.path.dirname(fn))

    item = self.lstLayers.currentItem()
    layer = findLayerForName(self.layers, item.text())
    fp = open(fn, 'rb')
    if not getattr(layer, "dummyMetalTemplate", None):
      layer.dummyMetalTemplate = malachite.GDSTemplate(True)
    layer.dummyMetalTemplate.gdsData = fp.read()
    fp.close()
    self.updateProperties()

  def loadWaferTemplateGDS(self):
    dir = self.getLastPrestratumImportDir()

    fn, filt = QFileDialog.getOpenFileName(self, "Select Wafer Template GDS",
        dir, "GDS Files (*.gds)")
    if not fn:
      return
    self.saveLastPrestratumImportDir(os.path.dirname(fn))

    item = self.lstLayers.currentItem()
    layer = findLayerForName(self.layers, item.text())
    fp = open(fn, 'rb')
    if not getattr(layer, "waferTemplate", None):
      layer.waferTemplate = malachite.GDSTemplate(False)
    layer.waferTemplate.gdsData = fp.read()
    fp.close()
    self.updateProperties()

  def loadPrestratumGDSAllLayers(self):
    dir = self.getLastPrestratumImportDir()

    fn, filt = QFileDialog.getOpenFileName(self, "Select Prestratum GDS",
        dir, "GDS Files (*.gds)")
    if not fn:
      return
    self.saveLastPrestratumImportDir(os.path.dirname(fn))
    try:
      gdslayers = separatedGDSLayers(fn)
    except:
      QMessageBox.critical(self, "Invalid GDS file", "Pyrite could not "
          "parse the selected GDS file.")
      return
    for layer in self.layers:
      layerNum = layer.number
      if layerNum in gdslayers:
        if not getattr(layer, "prestratum", None):
          layer.prestratum = malachite.Prestratum()
        layer.prestratum = malachite.Prestratum()
        layer.prestratum.gdsData = gdslayers[layerNum]
    self.updateProperties()

  def loadShiftedPrestratumGDSAllLayers(self):
    dir = self.getLastPrestratumImportDir()

    fn, filt = QFileDialog.getOpenFileName(self,
        "Select Shifted Prestratum GDS",
        dir, "GDS Files (*.gds)")
    if not fn:
      return
    self.saveLastPrestratumImportDir(os.path.dirname(fn))
    try:
      gdslayers = separatedGDSLayers(fn)
    except:
      QMessageBox.critical(self, "Invalid GDS file", "Pyrite could not "
          "parse the selected GDS file.")
      return
    for layer in self.layers:
      layerNum = layer.number
      if layerNum in gdslayers:
        if not getattr(layer, "shiftedPrestratum", None):
          layer.shiftedPrestratum = malachite.Prestratum()
          layer.shiftedPrestratum.isShifted = True
        layer.shiftedPrestratum.gdsData = gdslayers[layerNum]
    self.updateProperties()

  def loadDummyMetalGDSAllLayers(self):
    dir = self.getLastPrestratumImportDir()

    fn, filt = QFileDialog.getOpenFileName(self, "Select Dummy Metal GDS",
        dir, "GDS Files (*.gds)")
    if not fn:
      return
    self.saveLastPrestratumImportDir(os.path.dirname(fn))
    try:
      gdslayers = separatedGDSLayers(fn)
    except:
      QMessageBox.critical(self, "Invalid GDS file", "Pyrite could not "
          "parse the selected GDS file.")
      return
    for layer in self.layers:
      layerNum = layer.number
      if layerNum in gdslayers:
        layer.dummyMetalTemplate = malachite.GDSTemplate(True)
        layer.dummyMetalTemplate.gdsData = gdslayers[layerNum]
    self.updateProperties()

  def loadWaferTemplateGDSAllLayers(self):
    dir = self.getLastPrestratumImportDir()

    fn, filt = QFileDialog.getOpenFileName(self, "Select Dummy Metal GDS",
        dir, "GDS Files (*.gds)")
    if not fn:
      return
    self.saveLastPrestratumImportDir(os.path.dirname(fn))
    try:
      gdslayers = separatedGDSLayers(fn)
    except:
      QMessageBox.critical(self, "Invalid GDS file", "Pyrite could not "
          "parse the selected GDS file.")
      return
    for layer in self.layers:
      layerNum = layer.number
      if layerNum in gdslayers:
        layer.waferTemplate = malachite.GDSTemplate(False)
        layer.waferTemplate.gdsData = gdslayers[layerNum]
    self.updateProperties()

  def loadOOSUnitDrawing(self):
    dir = self.getLastPrestratumImportDir()

    fn, filt = QFileDialog.getOpenFileName(self,
        "Select OoS Unit Drawing GDS", dir,
        "GDS Files (*.gds)")
    if not fn:
      return
    self.saveLastPrestratumImportDir(os.path.dirname(fn))

    item = self.lstLayers.currentItem()
    layer = findLayerForName(self.layers, item.text())
    fp = open(fn, 'rb')
    if not getattr(layer, "outOfSpecUnitDrawing", None):
      layer.outOfSpecUnitDrawing = malachite.Prestratum()
    layer.outOfSpecUnitDrawing.gdsData = fp.read()
    fp.close()
    self.updateProperties()

  def loadOOSUnitDraiwngAllLayers(self):
    dir = self.getLastPrestratumImportDir()

    fn, filt = QFileDialog.getOpenFileName(self, "Select OoS Unit Drawing GDS",
        dir, "GDS Files (*.gds)")
    if not fn:
      return
    self.saveLastPrestratumImportDir(os.path.dirname(fn))
    try:
      gdslayers = separatedGDSLayers(fn)
    except:
      QMessageBox.critical(self, "Invalid GDS file", "Pyrite could not "
          "parse the selected GDS file.")
      return
    for layer in self.layers:
      layerNum = layer.number
      if layerNum in gdslayers:
        if not getattr(layer, "outOfSpecUnitDrawing", None):
          layer.outOfSpecUnitDrawing = malachite.Prestratum()
        layer.outOfSpecUnitDrawing = malachite.Prestratum()
        layer.outOfSpecUnitDrawing.gdsData = gdslayers[layerNum]
    self.updateProperties()

  def loadShiftedFiducialUnitGDS(self):
    dir = self.getLastPrestratumImportDir()

    fn, filt = QFileDialog.getOpenFileName(self,
        "Select Shifted Fiducial Unit GDS", dir,
        "GDS Files (*.gds)")
    if not fn:
      return
    self.saveLastPrestratumImportDir(os.path.dirname(fn))

    item = self.lstLayers.currentItem()
    layer = findLayerForName(self.layers, item.text())
    fp = open(fn, 'rb')
    if not getattr(layer, "fiducial", None):
      layer.fiducial = malachite.Prestratum()
    layer.fiducial.gdsData = fp.read()
    fp.close()
    self.updateProperties()

  def loadFiducialUnitGDSAllLayers(self):
    dir = self.getLastPrestratumImportDir()

    fn, filt = QFileDialog.getOpenFileName(self,
        "Select Shifted Fiducial Unit GDS for All Layers",
        dir, "GDS Files (*.gds)")
    if not fn:
      return
    self.saveLastPrestratumImportDir(os.path.dirname(fn))
    try:
      gdslayers = separatedGDSLayers(fn)
    except:
      QMessageBox.critical(self, "Invalid GDS file", "Pyrite could not "
          "parse the selected GDS file.")
      return
    for layer in self.layers:
      layerNum = layer.number
      if layerNum in gdslayers:
        if not getattr(layer, "fiducial", None):
          layer.fiducial = malachite.Prestratum()
        layer.fiducial.gdsData = gdslayers[layerNum]
    self.updateProperties()

  def unloadPrestratum(self):
    item = self.lstLayers.currentItem()
    layer = findLayerForName(self.layers, item.text())
    layer.prestratum = None
    del(layer.prestratum)
    self.updateProperties()

  def unloadShiftedPrestratum(self):
    item = self.lstLayers.currentItem()
    layer = findLayerForName(self.layers, item.text())
    layer.shiftedPrestratum = None
    del(layer.shiftedPrestratum)
    self.updateProperties()

  def unloadDummyMetal(self):
    item = self.lstLayers.currentItem()
    layer = findLayerForName(self.layers, item.text())
    layer.dummyMetalTemplate = None
    del(layer.dummyMetalTemplate)
    self.updateProperties()

  def unloadWaferTemplate(self):
    item = self.lstLayers.currentItem()
    layer = findLayerForName(self.layers, item.text())
    layer.waferTemplate = None
    del(layer.waferTemplate)
    self.updateProperties()

  def unloadOoSUnit(self):
    item = self.lstLayers.currentItem()
    layer = findLayerForName(self.layers, item.text())
    layer.outOfSpecUnitDrawing = None
    del(layer.outOfSpecUnitDrawing)
    self.updateProperties()

  def unloadFiducialUnit(self):
    item = self.lstLayers.currentItem()
    layer = findLayerForName(self.layers, item.text())
    layer.fiducial = None
    del(layer.fiducial)
    self.updateProperties()


class EditLayersCommand(Command):
  def __init__(self, project, newLayers, oldLayers):
    self._project = project
    self._design = project.design
    self._newLayers = newLayers
    self._oldLayers = oldLayers

  def do(self):
    self._design.package.layers = self._newLayers
    self._project.notifications.layersChanged.emit()
    self._project.setDirty()

  def undo(self):
    self._design.package.layers = self._oldLayers
    self._project.notifications.layersChanged.emit()
    self._project.setDirty()

  def __str__(self):
    return u"Edit Layers"

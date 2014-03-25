# ExportScriptGeneratorDialog.py
# Created by Craig Bishop on 06 July 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

from PySide.QtCore import *
from PySide.QtGui import *
from Ui_ExportScriptGeneratorDialog import Ui_ExportScriptGeneratorDialog
from SIPExport import ExportScriptOptions, ExportScriptOptionsException, SIPExportScriptGenerator

class ExportScriptGeneratorDialog(QDialog, Ui_ExportScriptGeneratorDialog):
  def __init__(self, parent):
    QDialog.__init__(self, parent)
    self.setupUi(self)

    self._exportOptions = ExportScriptOptions()

    self.connectActions()
    self.updatePropertiesControlsEnabling()
    self.updateGenerateExportScriptButtonEnabling()

  def connectActions(self):
    self.btnAdd.clicked.connect(self.btnAddLayerClicked)
    self.btnRemove.clicked.connect(self.btnRemoveLayerClicked)
    self.btnMoveUp.clicked.connect(self.btnMoveUpClicked)
    self.btnMoveDown.clicked.connect(self.btnMoveDownClicked)
    self.txtCadenceLayerName.textChanged.connect(self.txtCadenceLayerNameChanged)
    self.txtCadenceLayerName.editingFinished.connect(self.txtCadenceLayerNameChanged)
    self.chckPins.stateChanged.connect(self.pinsStateChanged)
    self.chckVias.stateChanged.connect(self.viasStateChanged)
    self.chckShapes.stateChanged.connect(self.shapesStateChanged)
    self.chckPaths.stateChanged.connect(self.pathsStateChanged)
    self.txtPyriteLayerName.textChanged.connect(self.txtPyriteLayerNameChanged)
    self.txtPyriteLayerName.editingFinished.connect(self.txtPyriteLayerNameChanged)
    self.txtPyriteLayerNumber.textChanged.connect(self.txtPyriteLayerNumberChanged)
    self.txtPyriteLayerNumber.editingFinished.connect(self.txtPyriteLayerNumberChanged)
    self.lstLayers.currentRowChanged.connect(self.currentRowChanged)
    self.lstLayers.itemSelectionChanged.connect(self.updatePropertiesControlsEnabling)
    self.btnCancel.clicked.connect(self.reject)
    self.btnGenerateExportScript.clicked.connect(self.btnGenerateExportScriptClicked)
    self.txtDieWScribeLayerName.textChanged.connect(self.txtDieWScribeLayerNameChanged)
    self.txtDieWScribeLayerName.editingFinished.connect(self.txtDieWScribeLayerNameChanged)

  def btnAddLayerClicked(self):
    addedLayer = False
    layerName = "New Layer"
    i = 1
    while not addedLayer:
      try:
        layer = self._exportOptions.addLayer(layerName)
        addedLayer = True
        self.lstLayers.addItem(layer["name"])
        self.lstLayers.setCurrentRow(self.lstLayers.count() - 1)
      except(ExportScriptOptionsException):
        layerName = "New Layer {0}".format(i)
        i += 1
    self.updateGenerateExportScriptButtonEnabling()

  def btnRemoveLayerClicked(self):
    for item in self.lstLayers.selectedItems():
      self._exportOptions.removeLayer(item.text())
      self.lstLayers.takeItem(self.lstLayers.row(item))
      del(item)
    self.updateGenerateExportScriptButtonEnabling()

  def btnMoveUpClicked(self):
    item = self.lstLayers.currentItem()
    if not item:
      return
    lname = item.text()
    self._exportOptions.moveLayerUp(lname)
    row = self.lstLayers.row(item)
    self.lstLayers.takeItem(row)
    row = int(min(0, row - 1))
    self.lstLayers.insertItem(row, item)
    self.lstLayers.setCurrentRow(row)

  def btnMoveDownClicked(self):
    item = self.lstLayers.currentItem()
    if not item:
      return
    lname = item.text()
    self._exportOptions.moveLayerUp(lname)
    row = self.lstLayers.row(item)
    self.lstLayers.takeItem(row)
    row = int(max(self.lstLayers.count(), row + 1))
    self.lstLayers.insertItem(row, item)
    self.lstLayers.setCurrentRow(row)

  def txtCadenceLayerNameChanged(self):
    item = self.lstLayers.currentItem()
    if not item:
      return
    layerName = item.text()
    self._exportOptions.setCadenceLayerNameForLayer(layerName, 
        self.txtCadenceLayerName.text())

  def pinsStateChanged(self, s):
    item = self.lstLayers.currentItem()
    if not item:
      return
    layerName = item.text()
    self._exportOptions.setShouldExportPinsForLayer(layerName, 
        self.chckPins.isChecked())

  def viasStateChanged(self, s):
    item = self.lstLayers.currentItem()
    if not item:
      return
    layerName = item.text()
    self._exportOptions.setShouldExportViasForLayer(layerName,
        self.chckVias.isChecked())

  def shapesStateChanged(self, s):
    item = self.lstLayers.currentItem()
    if not item:
      return
    layerName = item.text()
    self._exportOptions.setShouldExportShapesForLayer(layerName,
        self.chckShapes.isChecked())

  def pathsStateChanged(self, s):
    item = self.lstLayers.currentItem()
    if not item:
      return
    layerName = item.text()
    self._exportOptions.setShouldExportPathsForLayer(layerName,
        self.chckPaths.isChecked())

  def txtPyriteLayerNameChanged(self):
    item = self.lstLayers.currentItem()
    if not item:
      return
    layer = self._exportOptions.layerForName(item.text())
    layer["name"] = self.txtPyriteLayerName.text()
    item.setText(layer["name"])

  def txtPyriteLayerNumberChanged(self):
    item = self.lstLayers.currentItem()
    if not item:
      return
    layerName = item.text()
    self._exportOptions.setLayerNumberForLayer(layerName,
        self.txtPyriteLayerNumber.text())

  def currentRowChanged(self, row):
    item = self.lstLayers.currentItem()
    if not item:
      return
    layer = self._exportOptions.layerForName(item.text())
    
    self.txtCadenceLayerName.blockSignals(True)
    self.txtPyriteLayerName.blockSignals(True)
    self.chckPins.blockSignals(True)
    self.chckVias.blockSignals(True)
    self.chckShapes.blockSignals(True)
    self.chckPaths.blockSignals(True)
    self.txtPyriteLayerNumber.blockSignals(True)

    self.txtCadenceLayerName.setText(layer["cadName"])
    self.txtPyriteLayerName.setText(layer["name"])
    self.chckPins.setChecked(layer["pins"])
    self.chckVias.setChecked(layer["vias"])
    self.chckShapes.setChecked(layer["shapes"])
    self.chckPaths.setChecked(layer["paths"])
    self.txtPyriteLayerNumber.setText(str(layer["number"]))

    self.txtCadenceLayerName.blockSignals(False)
    self.txtPyriteLayerName.blockSignals(False)
    self.chckPins.blockSignals(False)
    self.chckVias.blockSignals(False)
    self.chckShapes.blockSignals(False)
    self.chckPaths.blockSignals(False)
    self.txtPyriteLayerNumber.blockSignals(False)

  def updatePropertiesControlsEnabling(self):
    enabled = False
    if len(self.lstLayers.selectedItems()) > 0:
      enabled = True
    self.txtCadenceLayerName.setEnabled(enabled)
    self.chckPins.setEnabled(enabled)
    self.chckVias.setEnabled(enabled)
    self.chckShapes.setEnabled(enabled)
    self.chckPaths.setEnabled(enabled)
    self.txtPyriteLayerName.setEnabled(enabled)
    self.txtPyriteLayerNumber.setEnabled(enabled)

  def updateGenerateExportScriptButtonEnabling(self):
    if self.lstLayers.count() > 0 and self.txtDieWScribeLayerName.text():
      self.btnGenerateExportScript.setEnabled(True)
    else:
      self.btnGenerateExportScript.setEnabled(False)

  def btnGenerateExportScriptClicked(self):
    if len(self._exportOptions.layers()) <= 0:
      raise ExportScriptOptionsException("The export script generator requires at least one layer")

    fn, filt = QFileDialog.getSaveFileName(self, "Save Cadence SiP Export Script",
        "", "Cadence SKILL Script (*.il)")
    if len(fn) <= 0:
      return

    gen = SIPExportScriptGenerator()
    script = gen.writeExportScript(self._exportOptions)

    fp = open(fn, "w")
    fp.write(script)
    fp.close()

    self.accept()

  def txtDieWScribeLayerNameChanged(self):
    self._exportOptions.setDieWithScribeLayer(self.txtDieWScribeLayerName.text())


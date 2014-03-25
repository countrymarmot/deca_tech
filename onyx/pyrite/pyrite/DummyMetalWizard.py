# DummyMetalWizard.py
# Created by Craig Bishop on 11 March 2013
#
# pyrite
# Copyright 2013 All Rights Reserved
#

from PySide.QtGui import QDialog, QFileDialog, QMessageBox, QTableWidgetItem
from PySide.QtCore import QSettings
from Ui_DummyMetalWizard import Ui_DummyMetalWizard
from ExcelRegionSelector import ExcelRegionSelector
import xlrd
import gdsii
import gdsii.library
import gdsii.elements
import gdsii.structure
import copy


class DummyMetalWizard(QDialog, Ui_DummyMetalWizard):
  def __init__(self, parent, project):
    QDialog.__init__(self, parent)
    self.setupUi(self)

    self._nominalData = []
    self._nominalDataLoaded = False
    self._gdsLoaded = False
    self._dummyGDSLib = None

    self.connectActions()

    self._project = project
    self.readWindowSettings()

  def connectActions(self):
    self.btnClose.clicked.connect(self.accept)
    self.btnImportNoms.clicked.connect(self.importNominalPositions)
    self.btnNext1.clicked.connect(self.next)
    self.btnNext2.clicked.connect(self.next)
    self.btnLoadGDS.clicked.connect(self.importDummyGDS)
    self.btnGenerateGDS.clicked.connect(self.generateDummyGDSClicked)
    self.txtOffsetX.editingFinished.connect(self.updateGenerateEnabled)
    self.txtOffsetX.editingFinished.connect(self.updateGenerateEnabled)
    self.txtStepX.editingFinished.connect(self.updateGenerateEnabled)
    self.txtStepY.editingFinished.connect(self.updateGenerateEnabled)
    self.txtDiameter.editingFinished.connect(self.updateGenerateEnabled)

  def closeEvent(self, event):
    self.writeWindowSettings()
    event.accept()

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

  def next(self):
    if self.tabWidget.currentIndex() == 0:
      self.tabWidget.setCurrentIndex(1)
    elif self.tabWidget.currentIndex() == 1:
      self.tabWidget.setCurrentIndex(2)

  def importDummyGDS(self):
    fn, filt = QFileDialog.getOpenFileName(self, "Open GDS File", "",
        "GDS Files(*.gds)")
    if not fn:
      return
    try:
      self._dummyGDSLib = gdsii.library.Library.load(open(fn, 'rb'))
    except:
      QMessageBox.critical(self, "Invalid GDS file", "Pyrite could not "
          "parse the selected GDS file.")
      return
    self.lblLoad.setText("LOADED")
    self._gdsLoaded = True
    self.updateGenerateEnabled()

  def importNominalPositions(self):
    fn, filt = QFileDialog.getOpenFileName(self, "Open Excel File", "",
        "Excel Files(*.xls)")
    if not fn:
      return
    try:
      wb = xlrd.open_workbook(fn)
    except:
      QMessageBox.critical(self, "Invalid Excel file", "Pyrite could not "
          "parse the selected Excel file. Make sure it is the .xls not "
          ".xlsx format.")
      return

    dlg = ExcelRegionSelector(self, wb.sheet_names())
    dlg.exec_()
    if dlg.result() != QDialog.Accepted:
      return
    xRow = dlg.xRow
    xCol = dlg.xCol
    yRow = dlg.yRow
    yCol = dlg.yCol
    count = dlg.count
    sheetName = dlg.sheetName

    sheet = wb.sheet_by_name(sheetName)
    # load the nominal positions
    for i in range(count):
      pos = (float(sheet.cell(xRow + i, xCol).value),
          float(sheet.cell(yRow + i, yCol).value))
      self._nominalData.append(pos)
    self._nominalDataLoaded = True
    self.updateNominalPositionPreview()
    self.updateGenerateEnabled()

  def updateNominalPositionPreview(self):
    self.tblNomPositions.clearContents()
    for i in range(len(self._nominalData)):
      self.tblNomPositions.insertRow(i)
      self.tblNomPositions.setItem(i, 0,
          QTableWidgetItem(str(self._nominalData[i][0])))
      self.tblNomPositions.setItem(i, 1,
          QTableWidgetItem(str(self._nominalData[i][1])))

  def updateGenerateEnabled(self):
    enabled = True
    enabled = enabled and self._nominalDataLoaded
    enabled = enabled and bool(self.txtOffsetX.text())
    enabled = enabled and bool(self.txtOffsetY.text())
    enabled = enabled and bool(self.txtStepX.text())
    enabled = enabled and bool(self.txtStepY.text())
    enabled = enabled and bool(self.txtDiameter.text())
    enabled = enabled and self._gdsLoaded
    self.btnGenerateGDS.setEnabled(enabled)

  def generateDummyGDSClicked(self):
    fn, filt = QFileDialog.getSaveFileName(self, "Save Dummy GDS", "",
        "GDS Files (*.gds)")
    fn = str(fn)
    if not fn:
      return

    dummy_points = self.generateDummyPositions()
    dummyGDSLib = self.generateDummyGDS(dummy_points)
    dummyGDSLib.save(open(fn, 'wb'))

  def generateDummyPositions(self):
    stepX = float(self.txtStepX.text())
    stepY = float(self.txtStepY.text())
    offX = float(self.txtOffsetX.text())
    offY = float(self.txtOffsetY.text())
    radius = (float(self.txtDiameter.text()) / 2.0) + max(stepX, stepY) + 1
    dummy_points = []
    numStepsX = int((radius / stepX)) + 1
    numStepsY = int((radius / stepY)) + 1
    x = (-stepX * numStepsX) + offX
    y = (-stepY * numStepsY) + offY
    for ix in range(2 * numStepsX):
      for iy in range(2 * numStepsY):
        p = (x, y)
        y += stepY

        def eq(a, b, eps=0.001):
          return abs(a - b) < eps
        good = True
        for dp in self._nominalData:
          if eq(dp[0], p[0]) and eq(dp[1], p[1]):
            good = False
            break
        if good:
          dummy_points.append(p)
      x += stepX
      y = (-stepY * numStepsY) + offY
    print(self._nominalData)
    print(dummy_points)
    return dummy_points

  def generateDummyGDS(self, dummy_points):
    lib = copy.deepcopy(self._dummyGDSLib)
    dummy_struct = lib[0]
    dummy_struct.name = "DUMMY_METAL"
    top_struct = gdsii.structure.Structure("TOP")
    lib.insert(0, top_struct)
    for p in dummy_points:
      sref = gdsii.elements.SRef("DUMMY_METAL",
          [(int(p[0] * 1000), int(p[1] * 1000))])
      top_struct.append(sref)
    return lib

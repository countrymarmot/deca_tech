# ExcelRegionSelector.py
# Created by Craig Bishop on 11 March 2013
#
# pyrite
# Copyright 2013 All Rights Reserved
#

from PySide.QtGui import QDialog
from Ui_ExcelRegionSelector import Ui_ExcelRegionSelector
import re


class ExcelRegionSelector(QDialog, Ui_ExcelRegionSelector):
  def __init__(self, parent, sheetNames):
    QDialog.__init__(self)
    self.setupUi(self)
    self.connectActions()
    self.setupSheets(sheetNames)
    self.xRow = 0
    self.xCol = 0
    self.yRow = 0
    self.yCol = 0
    self.count = 0
    self.sheetName = None

  def connectActions(self):
    self.btnOK.clicked.connect(self.ok)
    self.btnCancel.clicked.connect(self.reject)

  def ok(self):
    xCellName = str(self.txtXName.text())
    yCellName = str(self.txtYName.text())
    if (not xCellName) or (not yCellName):
      self.reject()
    try:
      count = int(self.txtCount.text())
    except:
      self.reject()
    self.xRow, self.xCol = self.rowAndColumnForCellName(xCellName)
    self.yRow, self.yCol = self.rowAndColumnForCellName(yCellName)
    self.count = count
    self.sheetName = self.cmboSheet.currentText()
    self.accept()

  def setupSheets(self, sheetNames):
    for name in sheetNames:
      self.cmboSheet.addItem(name)

  def columnForName(self, colName):
    colName = colName.lower()
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    multiplier = 0
    col = 0
    for c in reversed(colName):
      col += (alphabet.index(c) + 1) * max(1, multiplier * 26)
      multiplier += 1
    return col

  def rowAndColumnForCellName(self, cellName):
    grps = re.search('([a-zA-Z]*)([0-9]*)', cellName)
    colName = grps.group(1)
    col = self.columnForName(colName) - 1
    row = int(grps.group(2)) - 1
    return row, col

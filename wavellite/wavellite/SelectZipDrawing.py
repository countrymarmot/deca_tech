# SelectZipDrawing.py
# Created by Craig Bishop on 02 August 2011
#
# Wavellite
# Copyright 2011 All Rights Reserved
#

from PySide import QtCore, QtGui
import Config
from Ui_SelectZipDrawing import Ui_SelectZipDrawing
import os
import zipfile

drawingToFileName = {0: "unit", 1: "wafer", 2: "stencil"}


class SelectZipDrawing(QtGui.QDialog, Ui_SelectZipDrawing):
  def __init__(self):
    QtGui.QDialog.__init__(self)

    # setup the gui from the designer
    self.setupUi(self)

    self.connect(self.btnOK, QtCore.SIGNAL('clicked()'),
        self.btnOKClicked)
    self.connect(self.btnCancel, QtCore.SIGNAL('clicked()'),
        self.btnCancelClicked)
    self.connect(self.cbDrawingType, QtCore.SIGNAL('currentIndexChanged(int)'),
        self.loadSubDirs)

  def loadSubDirs(self):
    for i in range(self.lstSubDirs.count()):
      self.lstSubDirs.takeItem(0)
    searchText = drawingToFileName[self.cbDrawingType.currentIndex()]
    for root, dirs, files in os.walk(self.workingDir.fileDir):
      for dirName in dirs:
        if (searchText in dirName) and root == self.workingDir.fileDir:
          self.lstSubDirs.addItem(QtCore.QString(dirName))

  def btnOKClicked(self):
    if (self.lstSubDirs.count() <= 0):
      return
    if (self.lstSubDirs.currentItem() is None):
      return
    self.subDirName = str(self.lstSubDirs.currentItem().text())

    if self.cbDrawingType.currentIndex() == 0:
      self.doUnitZip()
    else:
      self.doWaferZip()

    self.accept()

  def btnCancelClicked(self):
    self.reject()

  def runZipTemplate(self, tpl):
    inFile = open(tpl, "r")
    contents = inFile.read()
    inFile.close()

    contents = contents.replace("\r", "")
    terms = contents.split("\n")

    files = []

    for t in terms:
      if len(t) <= 0:
        continue
      nf, filt = QtGui.QFileDialog.getOpenFileName(self, t,
          self.workingDir.fileDir + os.sep + self.subDirName, "")
      if len(nf) <= 0:
        continue
      files.append(nf)

    while True:
      r = QtGui.QMessageBox.question(self,
          "Any more?", "Are there any more files you want to include?",
          "Yes", "No", "", 1, 1)
      if (r == 1):
        break
      nf, filt = QtGui.QFileDialog.getOpenFileName(self,
          "Select Additional File",
          self.workingDir.fileDir + os.sep + self.subDirName, "")
      if len(nf) <= 0:
        continue
      files.append(nf)

    return files

  def doUnitZip(self):
    conf = Config.getConfig()
    tpl, filt = QtGui.QFileDialog.getOpenFileName(self,
        "Select Unit Zip Template",
        conf["DefaultUnitZipTemplateDir"], "")

    if (len(tpl) <= 0):
      return

    files = self.runZipTemplate(tpl)

    zFileName, filt = QtGui.QFileDialog.getSaveFileName(self,
        "Save Unit Zip File",
        self.workingDir.fileDir + os.sep + self.subDirName, "")

    if (len(zFileName) <= 0):
      return

    if not zFileName.endswith(".zip"):
      zFileName += ".zip"

    zf = zipfile.ZipFile(zFileName, "w")

    for f in files:
      head, tail = os.path.split(f)
      zf.write(f, tail)

    zf.close()

  def doWaferZip(self):
    conf = Config.getConfig()
    tpl, filt = QtGui.QFileDialog.getOpenFileName(self,
        "Select Wafer Zip Template",
        conf["DefaultWaferZipTemplateDir"], "")

    if (len(tpl) <= 0):
      return

    files = self.runZipTemplate(tpl)

    zFileName, filt = QtGui.QFileDialog.getSaveFileName(self,
        "Save Wafer Zip File",
        self.workingDir.fileDir + os.sep + self.subDirName, "")

    if (len(zFileName) <= 0):
      return

    if not zFileName.endswith(".zip"):
      zFileName += ".zip"

    zf = zipfile.ZipFile(zFileName, "w")

    for f in files:
      head, tail = os.path.split(f)
      zf.write(f, tail)

    zf.close()

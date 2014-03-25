# CreateSubDirs.py
# Created by Craig Bishop on 02 August 2011
#
# Wavellite
# Copyright 2011 All Rights Reserved
#

from PySide import QtCore, QtGui
from Ui_CreateSubDirs import Ui_CreateSubDirs
import os


techToFileName = {0: "3Series", 1: "4Series", 2: "BOP", 3: "MSeries3Layer",
    4: "MSeries4Layer", 5: "MSeries5Layer"}
drawingToFileName = {0: "unit", 1: "wafer", 2: "stencil"}


class CreateSubDirs(QtGui.QDialog, Ui_CreateSubDirs):
  def __init__(self):
    QtGui.QDialog.__init__(self)

    # setup the gui from the designer
    self.setupUi(self)

    self.connect(self.btnCreate, QtCore.SIGNAL('clicked()'),
        self.btnCreateClicked)
    self.connect(self.btnCancel, QtCore.SIGNAL('clicked()'),
        self.btnCancelClicked)

  def loadDefaults(self):
    # fill in the device name fields
    devName = self.workingDir.device["Name"]
    self.txtDev1.setText(devName)
    self.txtDev2.setText(devName)
    self.txtDev3.setText(devName)

  def btnCreateClicked(self):
    newdir = ""
    if (len(str(self.txtPLM1.text())) > 0 and
            len(str(self.txtDev1.text())) > 0):
      newdir += str(self.txtPLM1.text()) + "_"
      newdir += str(self.txtDev1.text()) + "_"
      newdir += techToFileName[self.cbTech1.currentIndex()] + "_"
      newdir += drawingToFileName[self.cbDraw1.currentIndex()]
      os.mkdir(self.workingDir.fileDir + os.sep + newdir)
      self.workingDir.device["PLM_Nums"][newdir] = str(self.txtPLM1.text())
    newdir = ""
    if (len(str(self.txtPLM2.text())) > 0 and
            len(str(self.txtDev2.text())) > 0):
      newdir += str(self.txtPLM2.text()) + "_"
      newdir += str(self.txtDev2.text()) + "_"
      newdir += techToFileName[self.cbTech2.currentIndex()] + "_"
      newdir += drawingToFileName[self.cbDraw2.currentIndex()]
      os.mkdir(self.workingDir.fileDir + os.sep + newdir)
      self.workingDir.device["PLM_Nums"][newdir] = str(self.txtPLM2.text())
    newdir = ""
    if (len(str(self.txtPLM3.text())) > 0 and
            len(str(self.txtDev3.text())) > 0):
      newdir += str(self.txtPLM3.text()) + "_"
      newdir += str(self.txtDev3.text()) + "_"
      newdir += techToFileName[self.cbTech3.currentIndex()] + "_"
      newdir += drawingToFileName[self.cbDraw3.currentIndex()]
      os.mkdir(self.workingDir.fileDir + os.sep + newdir)
      self.workingDir.device["PLM_Nums"][newdir] = str(self.txtPLM3.text())

    self.workingDir.save()
    self.accept()

  def btnCancelClicked(self):
    self.reject()

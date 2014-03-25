# CopyTemplates.py
# Created by Craig Bishop on 02 August 2011
#
# Wavellite
# Copyright 2011 All Rights Reserved
#

from PySide import QtCore, QtGui
import Config
from Ui_CopyTemplates import Ui_CopyTemplates
import os
import shutil

drawingToFileName = {0: "unit", 1: "wafer", 2: "stencil"}


class CopyTemplates(QtGui.QDialog, Ui_CopyTemplates):
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
    subDirName = str(self.lstSubDirs.currentItem().text())

    if (self.cbDrawingType.currentIndex() == 0):
      self.doUnitDrawingTemplateCopy(subDirName)
    elif (self.cbDrawingType.currentIndex() == 1):
      self.doWaferDrawingTemplateCopy(subDirName)
    else:
      self.doStencilDrawingTemplateCopy(subDirName)

    self.accept()

  def btnCancelClicked(self):
    self.reject()

  def doUnitDrawingTemplateCopy(self, subDir):
    conf = Config.getConfig()

    destDir = self.workingDir.fileDir + os.sep + subDir + os.sep
    # prompt to copy three templates
    tpl1, filt = QtGui.QFileDialog.getOpenFileName(self,
        "Select Unit Cadence Template",
        conf["DefaultCadenceUnitTemplateDir"], "")
    tpl2, filt = QtGui.QFileDialog.getOpenFileName(self,
        "Select Unit Design Checklist Template",
        conf["DefaultChecklistUnitTemplateDir"], "")
    tpl3, filt = QtGui.QFileDialog.getOpenFileName(self,
        "Select Unit Design Autocad Template",
        conf["DefaultAutocadUnitTemplateDir"], "")
    tpl4, filt = QtGui.QFileDialog.getOpenFileName(self,
        "Select Unit Design Artwork Parameters Template",
        conf["DefaultArtParamsUnitTemplateDir"], "")

    if (len(tpl1) > 0):
      shutil.copy(tpl1, destDir)
    if (len(tpl2) > 0):
      shutil.copy(tpl2, destDir)
    if (len(tpl3) > 0):
      shutil.copy(tpl3, destDir)
    if (len(tpl4) > 0):
      shutil.copy(tpl4, destDir)

  def doWaferDrawingTemplateCopy(self, subDir):
    conf = Config.getConfig()

    destDir = self.workingDir.fileDir + os.sep + subDir + os.sep
    # prompt to copy three templates
    tpl1, filt = QtGui.QFileDialog.getOpenFileName(self,
        "Select Wafer Cadence Template",
        conf["DefaultCadenceWaferTemplateDir"], "")
    tpl2, filt = QtGui.QFileDialog.getOpenFileName(self,
        "Select Wafer Design Checklist Template",
        conf["DefaultChecklistWaferTemplateDir"], "")
    tpl3, filt = QtGui.QFileDialog.getOpenFileName(self,
        "Select Wafer Design Autocad Template",
        conf["DefaultAutocadWaferTemplateDir"], "")

    if (len(tpl1) > 0):
      waferTemplateDir = destDir + "wafer_template"
      os.mkdir(waferTemplateDir)
      shutil.copy(tpl1, waferTemplateDir + os.sep)
    if (len(tpl2) > 0):
      shutil.copy(tpl2, destDir)
    if (len(tpl3) > 0):
      shutil.copy(tpl3, destDir)

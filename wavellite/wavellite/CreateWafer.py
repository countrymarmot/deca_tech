# CreateWafer.py
# Created by Craig Bishop on 03 August 2011
#
#
# Copyright 2011 All Rights Reserved
#

from PySide import QtCore, QtGui
import Config
from Ui_CreateWafer import Ui_CreateWafer
import os
import shutil
from ClippingRegions import ClippingRegions


class CreateWafer(QtGui.QDialog, Ui_CreateWafer):
  def __init__(self):
    QtGui.QDialog.__init__(self)

    # setup the gui from the designer
    self.setupUi(self)

    self.connect(self.btnDone, QtCore.SIGNAL('clicked()'),
        self.accept)
    self.connect(self.btnCreateStreamOut, QtCore.SIGNAL('clicked()'),
        self.createStreamOutClicked)
    self.connect(self.btnClip, QtCore.SIGNAL('clicked()'),
        self.clipClicked)
    self.connect(self.btnKnockout, QtCore.SIGNAL('clicked()'),
        self.knockoutClicked)
    self.connect(self.btnMergeExport, QtCore.SIGNAL('clicked()'),
        self.mergeAndExportClicked)

  def loadSubDir(self):
    self.lblSelectedDrawing.setText(self.subDir)

  def createStreamOutClicked(self):
    conf = Config.getConfig()
    tpl, filt = QtGui.QFileDialog.getOpenFileName(self,
        "Select Cadence Stream Out Script Template",
        conf["DefaultCadenceStreamOutDir"], "")

    if (len(tpl) <= 0):
      return

    destDir = self.workingDir.fileDir + os.sep + self.subDir
    destDir += os.sep + "wafer_template" + os.sep
    destFile = destDir + "stream_out.scr"

    plmNum = self.workingDir.device["PLM_Nums"][self.subDir]
    filenamerep = plmNum + "_wafer_template"

    inFile = open(tpl, "r")
    inContents = inFile.read()
    inFile.close()

    inContents = inContents.replace("__filename__", filenamerep)

    outFile = open(destFile, "w")
    outFile.write(inContents)
    outFile.close()

  def clipClicked(self):
    conf = Config.getConfig()
    tpl, filt = QtGui.QFileDialog.getOpenFileName(self,
        "Select Clip Script Template",
        conf["DefaultClipScriptDir"], "")

    if (len(tpl) <= 0):
      return

    destDir = self.workingDir.fileDir + os.sep + self.subDir + os.sep

    arrayGDS, filt = QtGui.QFileDialog.getOpenFileName(self,
        "Select Array GDS File",
        destDir, "")

    inFile = open(tpl, "r")
    contents = inFile.read()
    inFile.close()

    tempDir = conf["TempFileDir"] + os.sep

    contents = contents.replace("__tempdir__", tempDir)
    contents = contents.replace("__outdir__", destDir)

    outScriptFile = tempDir + "clip.bat"
    outFile = open(outScriptFile, "w")
    outFile.write(contents)
    outFile.close()

    shutil.copy(arrayGDS, tempDir + "array_all.gds")
    os.system(outScriptFile)

    for root, dirs, files in os.walk(tempDir):
      for filename in files:
        if "after_clip" in filename:
          shutil.copy(root + os.sep + filename, destDir)

    self.workingDir.device["has_clipped"] = True
    self.workingDir.save()

    for root, dirs, files, in os.walk(tempDir):
      for filename in files:
        os.remove(root + os.sep + filename)

  def knockoutClicked(self):
    conf = Config.getConfig()

    #if not "has_clipped" in self.workingDir.device:
      #QtGui.QMessageBox.warning(self, "Must clip before knockout",
        #"You need to run the clip script at least once before knockout.")
      #return

    if (not "knockout_200" in conf) or (not "knockout_300" in conf):
      QtGui.QMessageBox.warning(self, "Must setup wafer clipping regions",
          "You need to setup the default wafer clipping regions in"
          " Preferences first.")

    tpl, filt = QtGui.QFileDialog.getOpenFileName(self,
        "Select Knockout Script Template",
        conf["DefaultKnockoutScriptDir"], "")

    if (len(tpl) <= 0):
      return

    dlg = ClippingRegions()
    dlg.workingDir = self.workingDir
    dlg.subDir = self.subDir
    dlg.tpl = tpl
    dlg.loadRegions()
    dlg.exec_()

  def mergeAndExportClicked(self):
    conf = Config.getConfig()
    tpl, filt = QtGui.QFileDialog.getOpenFileName(self,
        "Select GDS Flt Script Template",
        conf["DefaultFltScriptDir"], "")

    if (len(tpl) <= 0):
      return

    destDir = self.workingDir.fileDir + os.sep + self.subDir + os.sep
    finalDir = destDir + "final" + os.sep
    tempDir = conf["TempFileDir"] + os.sep
    waferTplDir = destDir + "wafer_template" + os.sep

    plmNum = self.workingDir.device["PLM_Nums"][self.subDir]
    streamOutName = plmNum + "_wafer_template"

    inFile = open(tpl, "r")
    contents = inFile.read()
    inFile.close()

    # create the final dir
    if not os.path.exists(finalDir):
      os.mkdir(finalDir)

    contents = contents.replace("__tempdir__", tempDir)
    contents = contents.replace("__finaldir__", finalDir)
    contents = contents.replace("__streamOutName__", streamOutName)
    contents = contents.replace("__filename__", plmNum)

    outScriptFile = tempDir + "flt.bat"
    outFile = open(outScriptFile, "w")
    outFile.write(contents)
    outFile.close()

    for root, dirs, files in os.walk(waferTplDir):
      for filename in files:
        if ".gds" in filename:
          shutil.copy(root + os.sep + filename, tempDir)

    for root, dirs, files in os.walk(destDir):
      for filename in files:
        if "after_knockout.gds" in filename:
          shutil.copy(root + os.sep + filename, tempDir)

    os.system(outScriptFile)

    for root, dirs, files in os.walk(tempDir):
      for filename in files:
        os.remove(root + os.sep + filename)

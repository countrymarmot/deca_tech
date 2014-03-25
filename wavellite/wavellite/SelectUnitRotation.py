# SelectUnitRotation.py
# Created by Craig Bishop on 03 August 2011
#
# Wavellite
# Copyright 2011 All Rights Reserved
#

from PySide import QtCore, QtGui
import Config
from Ui_SelectUnitRotation import Ui_SelectUnitRotation
import os
import shutil


class SelectUnitRotation(QtGui.QDialog, Ui_SelectUnitRotation):
  def __init__(self):
    QtGui.QDialog.__init__(self)

    # setup the gui from the designer
    self.setupUi(self)

    self.connect(self.btnCancel, QtCore.SIGNAL('clicked()'),
        self.reject)
    self.connect(self.btnOK, QtCore.SIGNAL('clicked()'),
        self.btnOKClicked)

  def btnOKClicked(self):
    conf = Config.getConfig()
    rot = 0

    if (self.rbNoRot.isChecked()):
      rot = 0
    elif (self.rbCCRot.isChecked()):
      rot = 90
    elif (self.rb180Rot.isChecked()):
      rot = 180
    elif (self.rbCRot.isChecked()):
      rot = -90

    destDir = self.workingDir.fileDir + os.sep + self.subDir

    gdsFileName = destDir + os.sep +\
        self.workingDir.device["PLM_Nums"][self.subDir]
    gdsFileName += "_" + self.workingDir.device["Name"] + "_unit.gds"

    gdsFile, filt = QtGui.QFileDialog.getSaveFileName(self, "Save Unit GDS",
        gdsFileName, "GDSII File (*.gds)")
    if len(gdsFile) <= 0:
      return

    if not gdsFile.endswith(".gds"):
      gdsFile += ".gds"

    tplfile = open(self.tpl, "r")
    contents = tplfile.read()
    tplfile.close()

    tempDir = conf["TempFileDir"] + os.sep

    contents = contents.replace("ROT", str(rot))
    contents = contents.replace("__tempdir__", tempDir)

    outScriptFile = tempDir + "unit_create_script.bat"
    outF = open(outScriptFile, "w")
    outF.write(contents)
    outF.close()

    for root, dirs, files in\
            os.walk(self.workingDir.fileDir + os.sep + self.subDir):
      for filename in files:
        if ".art" in filename and root == destDir:
          shutil.copy(root + os.sep + filename, tempDir)

    os.system(outScriptFile)
    shutil.copy(tempDir + "unit_create_out.gds", gdsFile)

    # copy other unit gds files from the script
    for root, dirs, files, in os.walk(tempDir):
      for filename in files:
        if "unit" in filename and filename.endswith(".gds"):
          rep = self.workingDir.device["PLM_Nums"][self.subDir]
          rep += "_" + self.workingDir.device["Name"] + "_unit"
          newname = filename.replace("unit", rep)
          shutil.copy(root + os.sep + filename, destDir + os.sep + newname)

    for root, dirs, files, in os.walk(tempDir):
      for filename in files:
        os.remove(root + os.sep + filename)

    self.accept()

  def selectUnitScript(self):
    conf = Config.getConfig()
    self.tpl, filt = QtGui.QFileDialog.getOpenFileName(self,
        "Select Unit Create Unit Script Template",
        conf["DefaultUnitCreateScriptDir"], "")

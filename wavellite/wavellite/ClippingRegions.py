# ClippingRegions.py
# Created by Craig Bishop on 04 August 2011
#
# Wavellite
# Copyright 2011 All Rights Reserved
#

from PySide import QtCore, QtGui
import Config
from Ui_ClippingRegions import Ui_ClippingRegions
import os
import shutil
from WorkingDir import WorkingDir


class ClippingRegions(QtGui.QDialog, Ui_ClippingRegions):
  def __init__(self):
    QtGui.QDialog.__init__(self)

    # setup the gui from the designer
    self.setupUi(self)

    self.connect(self.btnCancel, QtCore.SIGNAL('clicked()'),
        self.reject)
    self.connect(self.btnOK, QtCore.SIGNAL('clicked()'),
        self.OKClicked)
    self.connect(self.btnLoadFrom, QtCore.SIGNAL('clicked()'),
        self.loadFromDevice)

  def loadRegions(self):
    if not "regions" in self.workingDir.device:
      return

    devRegions = self.workingDir.device["regions"]

    for i in range(14):
      t1 = self.__dict__["txtLLX" + str(i + 1)]
      t2 = self.__dict__["txtLLY" + str(i + 1)]
      t3 = self.__dict__["txtURX" + str(i + 1)]
      t4 = self.__dict__["txtURY" + str(i + 1)]

      if i in devRegions:
        r = devRegions[i]
        t1.setText(r[0])
        t2.setText(r[1])
        t3.setText(r[2])
        t4.setText(r[3])

  def OKClicked(self):
    conf = Config.getConfig()

    # grab all the knockout regions real quick
    regions = []

    if (self.rb200mm.isChecked()):
      kwafer = conf["knockout_200"]
    else:
      kwafer = conf["knockout_300"]

    for i in range(6):
      f = "LLX" + str(i + 1)
      if f in kwafer:
        if (len(kwafer[f]) > 0):
          r = []
          r.append(kwafer["LLX" + str(i + 1)])
          r.append(kwafer["LLY" + str(i + 1)])
          r.append(kwafer["URX" + str(i + 1)])
          r.append(kwafer["URY" + str(i + 1)])
          regions.append(r)

    self.workingDir.device["regions"] = {}
    devRegions = self.workingDir.device["regions"]

    for i in range(14):
      t1 = self.__dict__["txtLLX" + str(i + 1)]
      t2 = self.__dict__["txtLLY" + str(i + 1)]
      t3 = self.__dict__["txtURX" + str(i + 1)]
      t4 = self.__dict__["txtURY" + str(i + 1)]

      if (len(str(t1.text())) > 0):
        r = []
        r.append(str(t1.text()))
        r.append(str(t2.text()))
        r.append(str(t3.text()))
        r.append(str(t4.text()))
        regions.append(r)

        devRegions[i] = r

    self.workingDir.save()

    tempDir = conf["TempFileDir"] + os.sep
    destDir = self.workingDir.fileDir + os.sep + self.subDir + os.sep

    includeFile = open(tempDir + "knockout_include.txt", "w")
    for r in regions:
      for i in range(4):
        r[i] = r[i].strip('\n\c')
      includeFile.write(r[0] + ", " + r[1] + ", " + r[2] + ", " + r[3] + "\n")
      print("REGION: " + r[0] + ", " + r[1] + ", " + r[2] + ", " + r[3])
    includeFile.close()

    inFile = open(self.tpl, "r")
    contents = inFile.read()
    inFile.close()

    contents = contents.replace("__tempdir__", tempDir)
    contents = contents.replace("__outdir__", destDir)

    outFile = open(tempDir + "knockout.bat", "w")
    outFile.write(contents)
    outFile.close()

    for root, dirs, files in os.walk(destDir):
      for filename in files:
        if "after_clip.gds" in filename and root in destDir:
          shutil.copy(root + os.sep + filename, tempDir)

    os.system(tempDir + "knockout.bat")

    self.workingDir.device["has_knocked"] = True
    self.workingDir.save()

    for root, dirs, files, in os.walk(tempDir):
      for filename in files:
        os.remove(root + os.sep + filename)

    self.accept()

  def loadFromDevice(self):
    conf = Config.getConfig()
    devPath = QtGui.QFileDialog.getExistingDirectory(self,
        "Select Device File (.wavellite)",
        conf["DefaultDesignDir"], QtGui.QFileDialog.DontResolveSymlinks)

    dev = WorkingDir(devPath)
    devRegions = dev.device["regions"]

    for i in range(14):
      t1 = self.__dict__["txtLLX" + str(i + 1)]
      t2 = self.__dict__["txtLLY" + str(i + 1)]
      t3 = self.__dict__["txtURX" + str(i + 1)]
      t4 = self.__dict__["txtURY" + str(i + 1)]

      if i in devRegions:
        r = devRegions[i]
        t1.setText(r[0])
        t2.setText(r[1])
        t3.setText(r[2])
        t4.setText(r[3])

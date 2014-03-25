# MainWindow.py
# Created by Craig Bishop on 23 May 2011
#
# Wavellite
# Copyright 2011 All Rights Reserved
#

import os
from PySide import QtCore, QtGui
from Ui_MainWindow import Ui_MainWindow
from Preferences import Preferences
from WorkingDir import WorkingDir
from CreateWorkingDir import CreateWorkingDir
from CreateSubDirs import CreateSubDirs
from CopyTemplates import CopyTemplates
from CreateWafer import CreateWafer
from SelectWaferSubDir import SelectWaferSubDir
from SelectUnitRotation import SelectUnitRotation
from SelectUnitSubDir import SelectUnitSubDir
from SelectZipDrawing import SelectZipDrawing
from DesignAttributes import DesignAttributes
import Config


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
  def __init__(self):
    QtGui.QMainWindow.__init__(self)

    #setup the gui from the designer
    self.setupUi(self)

    self.connect(self.actionPreferences, QtCore.SIGNAL('triggered()'),
        self.showPreferences)
    self.connect(self.actionCreate_Working_Directory,
        QtCore.SIGNAL('triggered()'),
        self.createWorkingDirectoryClicked)
    self.connect(self.actionLoad_Working_Directory,
        QtCore.SIGNAL('triggered()'),
        self.loadWorkingDirectoryClicked)
    self.connect(self.actionAdd_Design_Sub_Directories,
        QtCore.SIGNAL('triggered()'),
        self.createSubDirectoriesClicked)
    self.connect(self.actionCopy_Templates, QtCore.SIGNAL('triggered()'),
        self.copyTemplatesClicked)
    self.connect(self.actionExit, QtCore.SIGNAL('triggered()'),
        self.close)
    self.connect(self.actionCreate_Wafer, QtCore.SIGNAL('triggered()'),
        self.createWaferClicked)
    self.connect(self.actionCreate_Unit, QtCore.SIGNAL('triggered()'),
        self.createUnitClicked)
    self.connect(self.btnOpenWorkingDir, QtCore.SIGNAL('clicked()'),
        self.openWorkingDirClicked)
    self.connect(self.actionZip_it_Up, QtCore.SIGNAL('triggered()'),
        self.zipItUpClicked)
    self.connect(self.actionDesignAttributes, QtCore.SIGNAL('triggered()'),
        self.designAttributesClicked)

    self.workingDir = None
    self.loadDefaultWorkingDir()

  def loadDefaultWorkingDir(self):
    conf = Config.getConfig()
    if "LastWorkingDir" in conf:
      lastDir = conf["LastWorkingDir"]
      if os.path.exists(lastDir) is False:
        return
      if lastDir is not None and len(lastDir) >= 0:
        self.workingDir = WorkingDir(lastDir)
        if not self.workingDir.exists:
          self.workingDir = None
          return
        self.txtWorkingDir.setText(self.workingDir.fileDir)
        self.txtDeviceName.setText(self.workingDir.device["Name"])
        self.actionAdd_Design_Sub_Directories.setEnabled(True)
        self.actionCopy_Templates.setEnabled(True)
        self.actionCreate_Wafer.setEnabled(True)
        self.actionCreate_Unit.setEnabled(True)
        self.btnOpenWorkingDir.setEnabled(True)
        self.actionZip_it_Up.setEnabled(True)
        self.actionDesignAttributes.setEnabled(True)

  def showPreferences(self):
    dlg = Preferences()
    dlg.exec_()

  def createWorkingDirectoryClicked(self):
    conf = Config.getConfig()

    dlg = CreateWorkingDir()
    result = dlg.exec_()
    if result == QtGui.QDialog.Rejected:
      return

    # now create the directory and working dir structure
    self.workingDir = WorkingDir(dlg.newWorkingDirName)
    self.workingDir.createOnFileSystem(dlg.newDeviceName)
    self.txtWorkingDir.setText(self.workingDir.fileDir)
    self.txtDeviceName.setText(self.workingDir.device["Name"])
    self.actionAdd_Design_Sub_Directories.setEnabled(True)
    self.actionCopy_Templates.setEnabled(True)
    self.actionCreate_Wafer.setEnabled(True)
    self.actionCreate_Unit.setEnabled(True)
    self.btnOpenWorkingDir.setEnabled(True)
    self.actionZip_it_Up.setEnabled(True)
    self.actionDesignAttributes.setEnabled(True)

    conf["LastWorkingDir"] = self.workingDir.fileDir
    Config.saveConfig(conf)

  def loadWorkingDirectoryClicked(self):
    conf = Config.getConfig()
    newDir = QtGui.QFileDialog.getExistingDirectory(self,
        "Choose Working Directory",
        conf["DefaultDesignDir"], QtGui.QFileDialog.DontResolveSymlinks)

    if (len(newDir) <= 0):
      return

    self.workingDir = WorkingDir(newDir)

    if self.workingDir.exists is False:
      QtGui.QMessageBox.warning(self, "Not a Design Working Directory",
          "The directory you have selected is not a "
          "Wavellite working directory.")
      return

    self.txtWorkingDir.setText(self.workingDir.fileDir)
    self.txtDeviceName.setText(self.workingDir.device["Name"])
    self.actionAdd_Design_Sub_Directories.setEnabled(True)
    self.actionCopy_Templates.setEnabled(True)
    self.actionCreate_Wafer.setEnabled(True)
    self.actionCreate_Unit.setEnabled(True)
    self.btnOpenWorkingDir.setEnabled(True)
    self.actionZip_it_Up.setEnabled(True)
    self.actionDesignAttributes.setEnabled(True)

    conf["LastWorkingDir"] = self.workingDir.fileDir
    Config.saveConfig(conf)

  def createSubDirectoriesClicked(self):
    dlg = CreateSubDirs()
    dlg.workingDir = self.workingDir
    dlg.loadDefaults()
    dlg.exec_()

  def copyTemplatesClicked(self):
    dlg = CopyTemplates()
    dlg.workingDir = self.workingDir
    dlg.loadSubDirs()
    dlg.exec_()

  def createWaferClicked(self):
    sdlg = SelectWaferSubDir()
    sdlg.workingDir = self.workingDir
    sdlg.loadSubDirs()
    result = sdlg.exec_()
    if result == QtGui.QDialog.Rejected:
      return

    dlg = CreateWafer()
    dlg.workingDir = self.workingDir
    dlg.subDir = sdlg.subDirName
    dlg.loadSubDir()
    dlg.exec_()

  def createUnitClicked(self):
    sdlg = SelectUnitSubDir()
    sdlg.workingDir = self.workingDir
    sdlg.loadSubDirs()
    result = sdlg.exec_()
    if result == QtGui.QDialog.Rejected:
      return

    dlg = SelectUnitRotation()
    dlg.workingDir = self.workingDir
    dlg.subDir = sdlg.subDirName
    dlg.selectUnitScript()
    if len(dlg.tpl) <= 0:
      return

    dlg.exec_()

  def openWorkingDirClicked(self):
    os.system("explorer.exe /e, " + self.workingDir.fileDir.replace("/", "\\"))

  def zipItUpClicked(self):
    dlg = SelectZipDrawing()
    dlg.workingDir = self.workingDir
    dlg.loadSubDirs()
    dlg.exec_()

  def designAttributesClicked(self):
    dlg = DesignAttributes()
    dlg.workingDir = self.workingDir
    dlg.loadAttributes()
    dlg.loadTab()
    dlg.exec_()

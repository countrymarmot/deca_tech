# CreateWorkingDir.py
# Created by Craig Bishop on 02 August 2011
#
# Wavellite
# Copyright 2011 All Rights Reserved
#

from PySide import QtCore, QtGui
import Config
from Ui_CreateWorkingDir import Ui_CreateWorkingDir


class CreateWorkingDir(QtGui.QDialog, Ui_CreateWorkingDir):
  def __init__(self):
    QtGui.QDialog.__init__(self)

    # setup the gui from the designer
    self.setupUi(self)

    self.connect(self.btnOK, QtCore.SIGNAL('clicked()'),
        self.btnOKClicked)
    self.connect(self.btnCancel, QtCore.SIGNAL('clicked()'),
        self.btnCancelClicked)
    self.connect(self.btnBrowseDirName, QtCore.SIGNAL('clicked()'),
        self.btnBrowseDirNameClicked)

  def btnOKClicked(self):
    if len(str(self.txtDirName.text())) <= 0 and\
            len(str(self.txtDeviceName.text())) <= 0:
      return
    self.newWorkingDirName = str(self.txtDirName.text())
    self.newDeviceName = str(self.txtDeviceName.text())
    self.accept()

  def btnCancelClicked(self):
    self.reject()

  def btnBrowseDirNameClicked(self):
    configuration = Config.getConfig()
    newDir, filt = QtGui.QFileDialog.getSaveFileName(self,
        "Save New Working Directory",
        configuration["DefaultDesignDir"], "")
    self.txtDirName.setText(newDir)

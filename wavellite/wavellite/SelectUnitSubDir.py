# SelectUnitSubDir.py
# Created by Craig Bishop on 03 August 2011
#
#
# Copyright 2011 All Rights Reserved
#

from PySide import QtCore, QtGui
from Ui_SelectUnitSubDir import Ui_SelectUnitSubDir
import os


class SelectUnitSubDir(QtGui.QDialog, Ui_SelectUnitSubDir):
  def __init__(self):
    QtGui.QDialog.__init__(self)

    # setup the gui from the designer
    self.setupUi(self)

    self.connect(self.btnCancel, QtCore.SIGNAL('clicked()'),
        self.reject)
    self.connect(self.btnOK, QtCore.SIGNAL('clicked()'),
        self.btnOKClicked)

  def loadSubDirs(self):
    for i in range(self.lstSubDirs.count()):
      self.lstSubDirs.takeItem(0)
    searchText = "unit"
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
    self.accept()

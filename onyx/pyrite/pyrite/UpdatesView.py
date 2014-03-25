# UpdatesView.py
# Created by Craig Bishop on 07 January 2013
#
# pyrite
# Copyright 2013 All Rights Reserved
#

import sys
import os
import esky
import version
from PySide.QtCore import Qt
from PySide.QtGui import QDialog, QMessageBox, QProgressDialog
from Ui_UpdatesView import Ui_UpdatesView
# need this for freezer to pick it up
import PySide.QtNetwork


class UpdatesView(QDialog, Ui_UpdatesView):
  def __init__(self, parent, appargs):
    QDialog.__init__(self, parent)
    self.setupUi(self)
    self._app = esky.Esky(sys.executable,
        "http://10.78.55.218/pyrite/downloads")
    self._appargs = appargs

    self.connectActions()
    self.updateView()

  def connectActions(self):
    self.btnCheckForUpdates.clicked.connect(self.updateView)
    self.btnInstallUpdate.clicked.connect(self.installUpdate)
    self.btnClose.clicked.connect(self.reject)

  def updateView(self):
    self.lblCurrentVersion.setText("You are currently running Pyrite version:"
        " {0}".format(version.version))
    update = self._app.find_update()
    if update is not None:
      self.lblAvailableUpdate.setText("Pyrite version {0} is available for"
          " download".format(update))
      self.btnInstallUpdate.setEnabled(True)
    else:
      self.lblAvailableUpdate.setText("There are no new updates available at"
          " this time.")

  def installUpdate(self):
    try:
      # setup progress dialog
      self._progressDlg = QProgressDialog(self)
      self._progressDlg.setWindowModality(Qt.WindowModal)
      self._progressDlg.setAutoClose(True)
      self._progressDlg.setMinimum(0)
      self._progressDlg.setMaximum(100)
      self._progressDlg.setLabelText("Auto-Updating")
      self._progressDlg.setCancelButton(None)
      self._progressDlg.setValue(0)

      self._app.auto_update(self.autoUpdateCallback)

      appexe = esky.util.appexe_from_executable(sys.executable)
      os.execv(appexe, self._appargs)
      QMessageBox.information(None, "Updating", "Update complete!")
      self._app.cleanup()
      self._progressDlg.reset()
      sys.exit()
    except Exception, e:
      print("ERROR AUTO-UPDATING APP: {0}".format(e))

  def autoUpdateCallback(self, status):
    self._progressDlg.setLabelText(status["status"])
    if "size" in status:
      self._progressDlg.setMaximum(int(status["size"]))
    if "received" in status:
      self._progressDlg.setValue(int(status["received"]))

# pyrite.py
# Created by Craig Bishop on 18 June 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

import sys
from PySide.QtGui import QApplication
from MainWindow import MainWindow
from UpdatesView import UpdatesView
import esky


def auto_update():
  if getattr(sys, "frozen", False):
    try:
      app = esky.Esky(sys.executable, "http://10.78.55.218/pyrite/downloads")
      update = app.find_update()
      app.cleanup()
    except Exception, e:
      return

    if update is not None:
      appexe = esky.util.appexe_from_executable(sys.executable)
      updateDialog = UpdatesView(None, [appexe] + sys.argv[1:])
      updateDialog.exec_()


def main():
  app = QApplication(sys.argv)
  try:
    auto_update()
  except:
    pass

  app.setOrganizationName("Deca Technologies")
  app.setOrganizationDomain("decatechnologies.com")
  app.setApplicationName("Pyrite")

  # create app environment
  window = MainWindow()
  window.show()

  # run main application loop
  sys.exit(app.exec_())


if __name__ == "__main__":
  main()

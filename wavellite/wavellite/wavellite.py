# wavellite.py
# Created by Craig Bishop on 23 May 2011
#
# Wavellite
# Copyright 2011 All Rights Reserved
#

import sys
import os
from PySide import QtGui
import MainWindow
# workaround for bdist_esky to import this module
from PySide import QtNetwork
import esky


def autoupdate():
  if getattr(sys, "frozen", False):
    app = esky.Esky(sys.executable,
        "http://10.78.55.224/wavellite/downloads")
    print "You are running: %s" % app.active_version
    try:
      if(app.find_update() is not None):
        print("Found update. Auto-updating now...")
        app.auto_update()
        appexe = esky.util.appexe_from_executable(sys.executable)
        os.execv(appexe, [appexe] + sys.argv[1:])
    except Exception, e:
      print "ERROR UPDATING APP:", e
    app.cleanup()


def main():
  # show the main application window
  app = QtGui.QApplication(sys.argv)

  autoupdate()

  window = MainWindow.MainWindow()
  window.show()

  sys.exit(app.exec_())

if __name__ == "__main__":
  main()

# setup.py
# Created by Craig Bishop on 03 November 2012
#
# wavellite
# Copyright 2012 All Rights Reserved
#

import sys
import os
import shutil
from distutils.core import setup
import esky.util
from esky import bdist_esky
from esky.bdist_esky import Executable
import version


def fixup_mac_app(executable):
  existing_qt_menu = os.path.join(executable.freeze_dir, "Wavellite.app",
      "Contents", "Frameworks", "QtGui.framework", "Resources", "qt_menu.nib")
  qt_menu_dest = os.path.join(executable.freeze_dir, "Wavellite.app",
      "Contents", "Resources", "qt_menu.nib")
  print("copying {0} -> {1}".format(existing_qt_menu, qt_menu_dest))
  shutil.copytree(existing_qt_menu, qt_menu_dest)

  # create empty qt.conf
  qt_conf_path = os.path.join(executable.freeze_dir, "Wavellite.app",
      "Contents", "Resources", "qt.conf")
  print("creating empy qt config file: {0}".format(qt_conf_path))
  open(qt_conf_path, 'w').close()

# create list of asset files
assets = []
for dir, dirnames, filenames in os.walk(os.path.join("ui", "assets")):
  assets = filenames
for i in range(len(assets)):
  assets[i] = os.path.join("ui", "assets", assets[i])

if sys.platform in ['win32', 'cygwin', 'win64']:
  setup(
      name="Wavellite",
      version=version.version,
      package_dir={'wavellite': 'release/wavellite'},
      packages=['wavellite', 'wavellite.assets'],
      data_files=[('assets', assets)],
      scripts=["Wavellite.py"],
      options={
          "bdist_esky": {
              "freezer_module": "py2exe"
          }
      }
  )
elif sys.platform == 'darwin':
  setup(
      name="Wavellite",
      version=version.version,
      package_dir={'wavellite': 'release/wavellite'},
      packages=['wavellite', 'wavellite.assets'],
      data_files=[('assets', assets)],
      scripts=["Wavellite.py"],
      options={
          "bdist_esky": {
              "freezer_module": "py2app",
              "pre_zip_callback": fixup_mac_app
          }
      }
  )

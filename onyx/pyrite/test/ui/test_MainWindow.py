# test_MainWindow.py
# Created by Craig Bishop on 09 July 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

import unittest
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtTest import QTest
import QAPP
from pyrite.MainWindow import MainWindow
from pyrite.DesignView import DesignView

class TestMainWindowDesignView(unittest.TestCase):
  def setUp(self):
    self.app = QAPP.QT_APP
    self.mainWindow = MainWindow()
    self.mainWindow.show()

  def tearDown(self):
    del(self.mainWindow)

  def testMainWindowHasDesignView(self):
    self.assertIsInstance(self.mainWindow.centralWidget(), DesignView)


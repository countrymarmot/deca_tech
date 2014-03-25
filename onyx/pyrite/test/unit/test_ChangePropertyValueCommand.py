# test_ChangePropertyValueCommand.py
# Created by Craig Bishop on 06 July 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

import unittest
from pyrite.malachite.Design import DesignObject
from pyrite.ChangePropertyValueCommand import ChangePropertyValueCommand

class testChangePropertyValueCommandText(unittest.TestCase):
  def setUp(self):
    self.do = DesignObject("TEST")
    self.do.name = "Unnamed Package"
    self.do._defineProperty("name", "Name")
    self.cmd = ChangePropertyValueCommand(self.do, "name", "HELLO")

  def testDo(self):
    self.cmd.do()
    self.assertEqual(self.do.propertyValue("name"), "HELLO",
        "command did not execute properly")

  def testUndo(self):
    self.cmd.do()
    self.cmd.undo()
    self.assertEqual(self.do.propertyValue("name"), "Unnamed Package",
        "command did not undo properly")

class testChangePropertyValueCommandNumber(unittest.TestCase):
  def setUp(self):
    self.do = DesignObject("TEST")
    self.do.number = 5
    self.do._defineProperty("number", "Number")

    self.cmd = ChangePropertyValueCommand(self.do, "number", 10)

  def testDo(self):
    self.cmd.do()
    self.assertEqual(self.do.propertyValue("number"), 10,
        "command did not execute properly")

  def testUndo(self):
    self.cmd.do()
    self.cmd.undo()
    self.assertEqual(self.do.propertyValue("number"), 5,
        "command did not undo properly")


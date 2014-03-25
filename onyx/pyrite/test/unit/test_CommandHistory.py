# test_CommandHistory.py
# Created by Craig Bishop on 06 July 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

import unittest
from pyrite.Command import Command
from pyrite.Command import CommandHistory

class TestCommand(Command):
  def __init__(self, name, obj):
    self.name = name
    self.obj = obj
    self.textBefore = self.obj.testText

  def do(self):
    self.obj.testText = "TestCommand1"

  def undo(self):
    self.obj.testText = self.textBefore

  def __str__(self):
    return name

class TestCommandHistoryStack(unittest.TestCase):
  def setUp(self):
    self.commandHistory = CommandHistory()
    self.testText = "Blah"

  def testDo(self):
    cmd = TestCommand("Change Text", self)
    self.commandHistory.do(cmd)
    self.assertEqual(self.testText, "TestCommand1",
        "command did not execute do()")

  def testUndo(self):
    cmd = TestCommand("Change Text", self)
    self.commandHistory.do(cmd)
    self.commandHistory.undo()
    self.assertEqual(self.testText, "Blah",
        "command did not undo change")

  def testRedo(self):
    cmd = TestCommand("Change Text", self)
    self.commandHistory.do(cmd)
    self.commandHistory.undo()
    self.commandHistory.redo()
    self.assertEqual(self.testText, "TestCommand1",
        "command did not redo change")

  def testCanUndo(self):
    self.assertFalse(self.commandHistory.canUndo(),
        "cannot undo an empty stack")
    cmd = TestCommand("test", self)
    self.commandHistory.do(cmd)
    self.assertTrue(self.commandHistory.canUndo(),
        "should be able to undo")

  def testCanRedo(self):
    self.assertFalse(self.commandHistory.canRedo(),
        "cannot redo an empty stack")
    cmd = TestCommand("test", self)
    self.commandHistory.do(cmd)
    self.commandHistory.undo()
    self.assertTrue(self.commandHistory.canRedo(),
        "should be able to redo")


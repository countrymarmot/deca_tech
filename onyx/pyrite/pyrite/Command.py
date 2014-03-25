# Command.py
# Created by Craig Bishop on 18 June 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

class CommandHistory:
  def __init__(self):
    self.notifications = None
    self.commands = []
    self.redoStack = []

  def canUndo(self):
    return len(self.commands) > 0

  def canRedo(self):
    return len(self.redoStack) > 0

  def nextUndoText(self):
    if self.canUndo():
      return u"Undo " + self.commands[len(self.commands) - 1].__str__()
    else:
      raise RuntimeError("Cannot get undo text for empty command history")

  def nextRedoText(self):
    if self.canRedo():
      return u"Redo " + self.redoStack[len(self.redoStack) - 1].__str__()
    else:
      raise RuntimeError("Cannot get redo text for empty redo stack")

  def do(self, cmd):
    cmd.do()
    self.commands.append(cmd)
    self.redoStack = []
    if (self.notifications):
      self.notifications.commandHistoryChanged.emit(self)

  def undo(self):
    if self.canUndo():
      cmd = self.commands.pop()
      cmd.undo()
      self.redoStack.append(cmd)
      if (self.notifications):
        self.notifications.commandHistoryChanged.emit(self)
      return True
    else:
      return False

  def redo(self):
    if self.canRedo():
      cmd = self.redoStack.pop()
      cmd.do()
      self.commands.append(cmd)
      if (self.notifications):
        self.notifications.commandHistoryChanged.emit(self)
      return True
    else:
      return False


class Command:
  def do(self):
    return NotImplemented

  def undo(self):
    return NotImplemented

  def __str__(self):
    return NotImplemented

class CommandGroup(Command):
  def __init__(self, name):
    self._commands = []
    self._name = name

  def addCommand(self, cmd):
    self._commands.append(cmd)

  def do(self):
    for cmd in self._commands:
      cmd.do()

  def undo(self):
    for cmd in reversed(self._commands):
      cmd.undo()

  def __str__(self):
    return name



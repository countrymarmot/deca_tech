# Project.py
# Created by Craig Bishop on 19 June 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

from PySide.QtCore import QObject, Signal
import pickle
import copy
from Command import CommandHistory
from malachite.Design import Design


class Notifications(QObject):
  projectChanged = Signal(object)
  designHierarchyChanged = Signal()
  commandHistoryChanged = Signal(object)
  layersChanged = Signal()

  def __init__(self):
    QObject.__init__(self)


class Project():
  def __init__(self):
    self.notifications = Notifications()
    self.commandHistory = CommandHistory()
    self.commandHistory.notifications = self.notifications

    self.isSaved = False
    self.fileName = "Untitled.pyrite"
    self.dirty = False
    self.design = Design()

  @classmethod
  def fromFile(cls, fileName):
    proj = pickle.load(open(fileName, "rb"))
    proj.notifications = Notifications()
    proj.commandHistory = CommandHistory()
    proj.commandHistory.notifications = proj.notifications
    proj.dirty = False
    proj.isSaved = True
    proj.fileName = fileName
    return proj

  def saveToFile(self):
    if self.isSaved:
      projCopy = copy.copy(self)
      del(projCopy.notifications)
      del(projCopy.commandHistory)
      pickle.dump(projCopy, open(self.fileName, "wb"), protocol=2)
      self.dirty = False
      self.notifications.projectChanged.emit(self)
    else:
      raise RuntimeError("Cannot save without filename")

  def isActive(self):
    return self.isSaved or self.dirty

  def setDirty(self):
    self.dirty = True
    self.notifications.projectChanged.emit(self)

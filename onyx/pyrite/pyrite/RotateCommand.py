# RotateCommand.py
# Created by Craig Bishop on 11 March 2013
#
# pyrite
# Copyright 2013 All Rights Reserved
#

from Command import Command
import malachite
import copy


class RotateCommand(Command):
  CLOCKWISE = malachite.CLOCKWISE
  COUNTERCLOCKWISE = malachite.COUNTERCLOCKWISE

  def __init__(self, project, dir):
    self.project = project
    self.dir = dir
    self.oldDesign = copy.deepcopy(project.design)

  def do(self):
    self.project.design = malachite.rotated(self.project.design, self.dir)
    self.project.setDirty()
    self.project.notifications.designHierarchyChanged.emit()

  def undo(self):
    self.project.design = self.oldDesign
    self.project.setDirty()
    self.project.notifications.designHierarchyChanged.emit()

  def __str__(self):
    if self.dir == self.CLOCKWISE:
      return u"Rotate Clockwise"
    else:
      return "rotate Counter-Clockwise"

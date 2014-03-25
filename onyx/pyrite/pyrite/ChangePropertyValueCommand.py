# ChangePropertyValueCommand.py
# Created by Craig Bishop on 06 July 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

from Command import Command

class ChangePropertyValueCommand(Command):
  def __init__(self, dobj, propName, newValue, model=None, index=None):
    self.designObj = dobj
    self.propName = propName
    self.newValue = newValue
    self.oldValue = self.designObj.propertyValue(self.propName)
    self.model = model
    self.index = index

  def do(self):
    self.designObj.setPropertyValue(self.propName, self.newValue)
    if self.model:
      self.model.dataChanged.emit(self.index, self.index)

  def undo(self):
    self.designObj.setPropertyValue(self.propName, self.oldValue)
    if self.model:
      self.model.dataChanged.emit(self.index, self.index)

  def __str__(self):
    return u"Change " + self.designObj.propertyText(self.propName)


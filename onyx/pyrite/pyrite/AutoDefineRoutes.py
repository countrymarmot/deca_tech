# AutoDefineRoutes.py
# Created by Craig Bishop on 10 October 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

from Command import Command
from malachite import createShortestRouteDefinitionsForDesign
import copy

class AutoDefineRoutesCommand(Command):
  def __init__(self, project):
    self.project = project
    self.oldDesign = copy.deepcopy(project.design)

  def do(self):
    routeDefs = createShortestRouteDefinitionsForDesign(self.project.design)
    self.project.design.routeDefinitions = routeDefs
    self.project.setDirty()
    self.project.notifications.designHierarchyChanged.emit()

  def undo(self):
    self.project.design = self.oldDesign
    self.project.setDirty()
    self.project.notifications.designHierarchyChanged.emit()

  def __str__(self):
    return u"Auto-Define Routes"


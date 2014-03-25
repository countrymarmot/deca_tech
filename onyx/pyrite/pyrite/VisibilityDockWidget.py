# VisibilityDockWidget.py
# Created by Craig Bishop on 23 October 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

from PySide.QtCore import *
from PySide.QtGui import *
from Ui_Visibility import Ui_Visibility

class VisibilityDockWidget(QDockWidget, Ui_Visibility):
  visibilityChanged = Signal(object)

  def __init__(self, parent):
    QDockWidget.__init__(self, parent)
    self.setupUi(self)
    self.project = None

    self.tableVisibility.itemChanged.connect(self.tableVisibilityItemChanged)

  def setProject(self, proj):
    self.project = proj

    self.blockSignals(True)
    self.tableVisibility.setRowCount(len(proj.design.package.layers))
    row = 0
    for layer in proj.design.package.layers:
      labelItem = QTableWidgetItem(layer.name)
      labelItem.setFlags(labelItem.flags() & (~Qt.ItemIsEditable))
      self.tableVisibility.setItem(row, 0, labelItem)
      visibleItem = QTableWidgetItem()
      visibleItem.setCheckState(Qt.Checked)
      visibleItem.setFlags(visibleItem.flags() & (~Qt.ItemIsEditable))
      visibleItem.setData(Qt.ItemDataRole, layer)
      self.tableVisibility.setItem(row, 1, visibleItem)
      row += 1
    self.blockSignals(False)
    self.project.notifications.layersChanged.connect(self.layersChanged)

  def tableVisibilityItemChanged(self, item):
    if item.column() != 1:
      return

    layerVisibility = {}
    for i in range(self.tableVisibility.rowCount()):
      visibleItem = self.tableVisibility.item(i, 1)
      if not visibleItem:
        continue
      layer = visibleItem.data(Qt.ItemDataRole)
      visible = (visibleItem.checkState() == Qt.Checked)
      layerVisibility[layer.name] = visible

    self.visibilityChanged.emit(layerVisibility)

  def layersChanged(self):
    self.setProject(self.project)


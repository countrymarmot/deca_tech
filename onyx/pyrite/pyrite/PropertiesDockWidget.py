# PropertiesDockWidget.py
# Created by Craig Bishop on 19 June 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

from PySide.QtCore import *
from PySide.QtGui import *
from Ui_Properties import Ui_Properties
from Command import *
from ChangePropertyValueCommand import *
from ObjectProxy import ObjectProxy

class PropertiesDockWidget(QDockWidget, Ui_Properties):
  def __init__(self, parent):
    QDockWidget.__init__(self, parent)
    self.setupUi(self)
    self.project = None

  def setProject(self, proj):
    self.project = proj
    self.packageModel = PropertiesItemModel(proj.design.package, self.project)
    self.packagePropertiesView.setModel(self.packageModel)
    self.packageModel.dataChanged.connect(self.modelDataChanged)
    self.project.notifications.projectChanged.connect(self.projectChanged)

  def projectChanged(self):
    self.packageModel = PropertiesItemModel(self.project.design.package, self.project)
    self.packagePropertiesView.setModel(self.packageModel)

  def modelDataChanged(self, topLeft, bottomRight):
    self.project.setDirty()

  def setSelectedDesignObject(self, dobj):
    if dobj:
      self.selectedDOModel = PropertiesItemModel(dobj, self.project)
      self.selectedObjectPropertiesView.setModel(self.selectedDOModel)
      self.selectedDOModel.dataChanged.connect(self.modelDataChanged)
    else:
      self.selectedObjectPropertiesView.setModel(None)

class PropertiesItemModel(QAbstractItemModel):
  def __init__(self, obj, project):
    QAbstractItemModel.__init__(self)
    self.project = project
    self.obj = ObjectProxy.proxyForObject(obj)

  def index(self, row, col, parent):
    if parent.isValid():
      return QModelIndex()
    else:
      return self.createIndex(row, col, self.obj.propertyNames()[row])

  def parent(self, child):
    return QModelIndex()

  def headerData(self, section, orientation, role):
    if role == Qt.DisplayRole:
      if section == 0:
        return "Property"
      elif section == 1:
        return "Value"

  def columnCount(self, parent):
    if not parent.isValid():
      return 2
    else:
      return 0

  def rowCount(self, parent):
    if not parent.isValid():
      return len(self.obj.propertyNames())
    else:
      return 0

  def data(self, index, role):
    propName = index.internalPointer()
    datatype = self.obj.propertyType(propName)
    if role == Qt.DisplayRole or role == Qt.EditRole:
      if index.column() == 0:
        return self.obj.propertyText(index.internalPointer())
      elif index.column() == 1:
        val = self.obj.propertyValue(index.internalPointer())
        if val is None:
          return ""
        if datatype == "BOOL":
          return None
        else:
          return str(val)
    elif role == Qt.CheckStateRole:
      val = self.obj.propertyValue(index.internalPointer())
      if index.column() == 1:
        if datatype == "BOOL":
          if val:
            return Qt.Checked
          else:
            return Qt.Unchecked
    return None;

  def setData(self, index, value, role):
    valid = False
    propName = index.internalPointer()
    datatype = self.obj.propertyType(propName)
    if index.isValid() and role == Qt.EditRole:
      if datatype == "TEXT":
        self.project.commandHistory.do(ChangePropertyValueCommand(self.obj,
          propName, str(value), self, index))
        valid = True
      elif datatype == "NUMBER":
        try:
          self.project.commandHistory.do(ChangePropertyValueCommand(self.obj,
            propName, float(value), self, index))
          valid = True
        except ValueError:
          valid = False
      elif datatype == "BOOL":
        try:
          self.project.commandHistory.do(ChangePropertyValueCommand(self.obj,
            propName, bool(value), self, index))
          valid = True
        except ValueError:
          valid = False
    elif index.isValid() and role == Qt.CheckStateRole:
      if value == Qt.Checked:
        newVal = True
      else:
        newVal = False
      try:
        self.project.commandHistory.do(ChangePropertyValueCommand(self.obj,
          propName, newVal, self, index))
        valid = True
      except ValueError:
        valid = False

    if valid:
      self.dataChanged.emit(index, index)
      return True
    return False

  def flags(self, index):
    flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
    propName = index.internalPointer()
    if index.column() == 1:
      if not self.obj.propertyReadOnly(index.internalPointer()):
        flags |= Qt.ItemIsEditable
      if self.obj.propertyType(propName) == "BOOL":
        flags |= Qt.ItemIsUserCheckable

    return flags


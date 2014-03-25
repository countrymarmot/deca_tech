# MainWindow.py
# Created by Craig Bishop on 18 June 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

from PySide.QtCore import *
from PySide.QtGui import *
from Ui_MainWindow import Ui_MainWindow
from PropertiesDockWidget import PropertiesDockWidget
from VisibilityDockWidget import VisibilityDockWidget
from ExportScriptGeneratorDialog import ExportScriptGeneratorDialog
from Project import Project
from SIPImport import SIPImportCommand
from DesignView import DesignView
from AutoDefineRoutes import AutoDefineRoutesCommand
from DVActionSystem import DVZoomAreaAction, DVChangeNetAction,\
    DVDefineRouteAction, DeleteRouteCommand
import malachite
from Command import CommandGroup
from ObjectProxy import ObjectProxy
from ChangePropertyValueCommand import ChangePropertyValueCommand
from LayerEditor import LayerEditor
from RotateCommand import RotateCommand
from DummyMetalWizard import DummyMetalWizard
import ShiftDataImporter
import version
import os.path


class MainWindow(QMainWindow, Ui_MainWindow):
  def __init__(self):
    QMainWindow.__init__(self)
    self.setupUi(self)

    # create all dockwidgets
    self.propertiesDockWidget = PropertiesDockWidget(self)
    self.visibilityDockWidget = VisibilityDockWidget(self)
    self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,
        self.visibilityDockWidget)
    self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,
        self.propertiesDockWidget)

    # create design view as central widget
    self.designView = DesignView(self)
    self.setCentralWidget(self.designView)
    self.designView.setFocus(Qt.OtherFocusReason)

    self.connectActionSignals()
    self.connectDesignViewSignals()
    self.project = None
    self.newProject()

    self.readWindowSettings()

  def closeEvent(self, event):
    self.writeWindowSettings()

    if self.project:
      if self.project.dirty:
        # ask about save
        msgBox = QMessageBox()
        msgBox.setText("The design has been modified.")
        msgBox.setInformativeText("Do you want to save your changes?")
        msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard |
            QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Save)
        ret = msgBox.exec_()

        if ret == QMessageBox.Save:
          if self.save():
            event.accept()
          else:
            event.ignore()
        elif ret == QMessageBox.Discard:
          event.accept()
        else:
          event.ignore()

    else:
      self.writeWindowSettings()
      event.accept()
    self.writeWindowSettings()

  def writeWindowSettings(self):
    settings = QSettings()
    settings.beginGroup("MainWindow")
    settings.setValue("geometry", self.saveGeometry())
    settings.setValue("windowState", self.saveState())
    settings.endGroup()

  def readWindowSettings(self):
    settings = QSettings()
    settings.beginGroup("MainWindow")
    self.restoreGeometry(settings.value("geometry"))
    self.restoreState(settings.value("windowState"))
    settings.endGroup()

  def connectActionSignals(self):
    self.actionClose.triggered.connect(self.close)
    self.actionAbout.triggered.connect(self.aboutBox)
    self.actionNew.triggered.connect(self.newProject)
    self.actionSave.triggered.connect(self.saveProject)
    self.actionSave_As.triggered.connect(self.saveProjectAs)
    self.actionOpen.triggered.connect(self.openProject)
    self.actionUndo.triggered.connect(self.undo)
    self.actionRedo.triggered.connect(self.redo)
    self.actionCreate_Export_Script.triggered.connect(
        self.showCreateExportScriptDialog)
    self.actionImport.triggered.connect(self.importDesign)
    self.actionAuto_Define_Routes.triggered.connect(self.autoDefineRoutes)
    self.actionZoom_Fit_All.triggered.connect(self.zoomFitAll)
    self.actionZoom_Area.toggled.connect(self.zoomArea)
    self.actionZoom_In.triggered.connect(self.zoomIn)
    self.actionZoom_Out.triggered.connect(self.zoomOut)
    self.actionChange_Net.toggled.connect(self.changeNet)
    self.actionDefine_Route.toggled.connect(self.defineRoute)
    self.actionExport.triggered.connect(self.exportForOnyx)
    self.actionVia_Filter.triggered.connect(self.filterVias)
    self.actionLayer_Editor.triggered.connect(self.editLayers)
    self.actionRotate_Clockwise.triggered.connect(self.rotateClockwise)
    self.actionRotate_Counter_Clockwise.triggered.connect(
        self.rotateCounterClockwise)
    self.actionDummy_Metal_Wizard.triggered.connect(self.dummyMetalWizard)
    self.actionImport_Shift_Data.triggered.connect(self.importShiftData)
    self.actionDelete.triggered.connect(self.deleteSelected)

  def connectDesignViewSignals(self):
    self.designView.selectionChanged.connect(self.designViewConnectionChanged)
    self.visibilityDockWidget.visibilityChanged.connect(
        self.designView.setLayerVisibility)

  def connectProjectSignals(self):
    self.project.notifications.projectChanged.connect(
        self.updateControlEnabling)
    self.project.notifications.projectChanged.connect(
        self.updateWindowTitleBar)
    self.project.notifications.commandHistoryChanged.connect(
        self.updateUndoAndRedo)
    self.project.notifications.designHierarchyChanged.connect(
        self.updateDesignViewDesign)

  def emitInitializationSignals(self):
    self.project.notifications.projectChanged.emit(self.project)
    self.project.notifications.commandHistoryChanged.emit(
        self.project.commandHistory)
    self.project.notifications.designHierarchyChanged.emit()
    self.propertiesDockWidget.setProject(self.project)
    self.visibilityDockWidget.setProject(self.project)

  def aboutBox(self):
    QMessageBox.about(self, "About",
        "Pyrite version {0}".format(version.version))

  def newProject(self):
    # only create a new design window if the current one is used
    if not self.project:
      self.project = Project()
      self.connectProjectSignals()
      self.setWindowTitle("")
      self.emitInitializationSignals()
    else:
      if not self.project.isActive():
        self.project = Project()
        self.connectProjectSignals()
        self.setWindowTitle("")
        self.emitInitializationSignals()
      else:
        # prompt to save changes and then create new project
        msgBox = QMessageBox()
        msgBox.setText("The design has been modified.")
        msgBox.setInformativeText("Do you want to save your changes?")
        msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard |
            QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Save)
        ret = msgBox.exec_()

        if ret == QMessageBox.Save:
          if not self.save():
            return
        elif ret == QMessageBox.Cancel:
          return
        self.project = Project()
        self.connectProjectSignals()
        self.setWindowTitle("")
        self.emitInitializationSignals()

  def saveProjectAs(self):
    fn, filt = QFileDialog.getSaveFileName(self, "Save Project", "",
        "Pyrite Projects (*.pyrite)")
    fn = str(fn)
    if len(fn) <= 0:
      return False

    if not fn.upper().endswith(".PYRITE"):
      fn += ".pyrite"

    self.project.fileName = fn
    self.project.isSaved = True
    self.project.saveToFile()
    return True

  def saveProject(self):
    if not self.project.isSaved:
      return self.saveProjectAs()
    else:
      self.project.saveToFile()
      return True

  def openProject(self):
    if self.project.isActive():
      # prompt to save changes and then open project
      msgBox = QMessageBox()
      msgBox.setText("The design has been modified.")
      msgBox.setInformativeText("Do you want to save your changes?")
      msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard |
          QMessageBox.Cancel)
      msgBox.setDefaultButton(QMessageBox.Save)
      ret = msgBox.exec_()

      if ret == QMessageBox.Save:
        if not self.save():
          return
      elif ret == QMessageBox.Cancel:
        return

    settings = QSettings()
    dir = ""
    if settings.contains("mainwindow/lastopendir"):
      dir = str(settings.value("mainwindow/lastopendir"))
    fn, filt = QFileDialog.getOpenFileName(self, "Open Project", dir,
        "Pyrite Projects (*.pyrite)")
    fn = str(fn)
    if len(fn) <= 0:
      return False

    settings.setValue("mainwindow/lastopendir", os.path.dirname(fn))

    self.project = Project.fromFile(fn)
    self.connectProjectSignals()
    self.setWindowTitle("")
    self.emitInitializationSignals()

    return True

  def exportForOnyx(self):
    fn, filt = QFileDialog.getSaveFileName(self, "Export to Onyx", "",
        "Onyx Package File (*.onyx)")
    fn = str(fn)
    if len(fn) <= 0:
      return
    fp = open(fn, 'wb')
    fp.write(malachite.ExportDesignToZinc(self.project.design))
    fp.close()

  def undo(self):
    if self.project.commandHistory.undo():
      self.project.setDirty()

  def redo(self):
    if self.project.commandHistory.redo():
      self.project.setDirty()

  def showCreateExportScriptDialog(self):
    dlg = ExportScriptGeneratorDialog(self)
    dlg.exec_()

  def importDesign(self):
    fn, filt = QFileDialog.getOpenFileName(self, "Import SiP Design", "",
        "Onyx Import Files (*.onyximport)")
    if not fn:
      return

    cmd = SIPImportCommand(self.project, fn)
    self.project.commandHistory.do(cmd)
    self.project.setDirty()
    self.visibilityDockWidget.setProject(self.project)

  def zoomFitAll(self):
    self.designView.zoomFitAll()

  def zoomArea(self, checked):
    if checked:
      self.designView.setActiveAction(
          DVZoomAreaAction(self.actionZoom_Area, self.designView))
    else:
      self.designView.cancelActiveAction()

  def zoomIn(self):
    self.designView.zoomIn()

  def zoomOut(self):
    self.designView.zoomOut()

  def changeNet(self, checked):
    if checked:
      self.designView.setActiveAction(DVChangeNetAction(self.actionChange_Net,
          self.designView, self.project))
    else:
      self.designView.cancelActiveAction()

  def defineRoute(self, checked):
    if checked:
      self.designView.setActiveAction(DVDefineRouteAction(
          self.actionDefine_Route,
          self.designView, self.project))
    else:
      self.designView.cancelActiveAction()

  def filterVias(self):
    # show an input dialog to get the text to search for in pad names
    text, ok = QInputDialog.getText(self, 'Via Filter',
        'The pads with this text in their padstack names will '
        'be set to shift with the dies')
    if ok:
      cmdGrp = CommandGroup(u"Filter Vias")
      pads = malachite.findAllPads(self.project.design)
      pads = [ObjectProxy.proxyForObject(pad) for pad in pads
          if text in pad.name]
      for pad in pads:
        cmdGrp.addCommand(ChangePropertyValueCommand(pad, "shifts", True))
      self.project.commandHistory.do(cmdGrp)
      QMessageBox.information(self,
          "Via Filter", "{0} pads set to shift".format(len(pads)))

  def editLayers(self):
    dlg = LayerEditor(self, self.project)
    dlg.exec_()

  def rotateClockwise(self):
    cmd = RotateCommand(self.project, RotateCommand.CLOCKWISE)
    self.project.commandHistory.do(cmd)

  def rotateCounterClockwise(self):
    cmd = RotateCommand(self.project, RotateCommand.COUNTERCLOCKWISE)
    self.project.commandHistory.do(cmd)

  def dummyMetalWizard(self):
    dlg = DummyMetalWizard(self, self.project)
    dlg.exec_()

  def importShiftData(self):
    ShiftDataImporter.importShiftData(self)

  def deleteSelected(self):
    do = self.designView.selectedDesignObject()
    if do and do.objType == "ROUTEDEFINITION":
      cmd = DeleteRouteCommand(self.project, do)
      self.project.commandHistory.do(cmd)

  def keyPressEvent(self, event):
    QMainWindow.keyPressEvent(self, event)
    # if escape, cancel the action
    if event.key() == Qt.Key_Escape:
      self.designView.cancelActiveAction()

  def designViewConnectionChanged(self, designObject):
    self.propertiesDockWidget.setSelectedDesignObject(designObject)

  def updateDesignViewDesign(self):
    self.designView.setDesign(self.project.design)

  def updateWindowTitleBar(self, project):
    if project != self.project:
      return

    self.setWindowModified(self.project.dirty)

    if self.project.isSaved:
      fi = QFileInfo(self.project.fileName)
      self.setWindowFilePath(fi.fileName())
    else:
      self.setWindowFilePath(self.project.fileName)

  def updateUndoAndRedo(self, commandHistory):
    if commandHistory != self.project.commandHistory:
      return

    if commandHistory.canUndo():
      self.actionUndo.setEnabled(True)
      self.actionUndo.setText(commandHistory.nextUndoText())
    else:
      self.actionUndo.setEnabled(False)
      self.actionUndo.setText("Undo")

    if commandHistory.canRedo():
      self.actionRedo.setEnabled(True)
      self.actionRedo.setText(commandHistory.nextRedoText())
    else:
      self.actionRedo.setEnabled(False)
      self.actionRedo.setText("Redo")

  def updateControlEnabling(self, project):
    if project != self.project:
      return

    enabled = False
    if self.project:
      enabled = True

    if self.project:
      self.actionSave.setEnabled(self.project.dirty or
          (not self.project.isSaved))
    else:
      self.actionSave.setEnabled(enabled)
    self.actionSave_As.setEnabled(enabled)
    self.actionImport.setEnabled(enabled)
    self.actionDelete.setEnabled(enabled)
    self.actionZoom_Fit_All.setEnabled(enabled)
    self.actionZoom_Area.setEnabled(enabled)
    self.actionZoom_In.setEnabled(enabled)
    self.actionZoom_Out.setEnabled(enabled)
    self.actionDefine_Route.setEnabled(enabled)
    self.actionChange_Net.setEnabled(enabled)
    self.actionExport.setEnabled(enabled)
    self.actionVia_Filter.setEnabled(enabled)
    self.actionLayer_Editor.setEnabled(enabled)
    self.actionRotate_Clockwise.setEnabled(enabled)
    self.actionRotate_Counter_Clockwise.setEnabled(enabled)

  def autoDefineRoutes(self):
    cmd = AutoDefineRoutesCommand(self.project)
    self.project.commandHistory.do(cmd)

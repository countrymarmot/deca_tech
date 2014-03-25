# Preferences.py
# Created by Craig Bishop on 01 August 2011
#
# Wavellite
# Copyright 2011 All Rights Reserved
#

from PySide import QtCore, QtGui
import Config
from Ui_Preferences import Ui_Preferences


class Preferences(QtGui.QDialog, Ui_Preferences):
  def __init__(self):
    QtGui.QDialog.__init__(self)

    # setup the gui from the designer
    self.setupUi(self)

    self.connect(self.btnOK, QtCore.SIGNAL('clicked()'),
        self.btnOKClicked)
    self.connect(self.btnCancel, QtCore.SIGNAL('clicked()'),
        self.btnCancelClicked)

    self.connect(self.btnBrowseDesignDir, QtCore.SIGNAL('clicked()'),
        self.btnBrowseDesignDirClicked)
    self.connect(self.btnBrowseTempFileDir, QtCore.SIGNAL('clicked()'),
        self.btnBrowseTempFileDirClicked)

    self.connect(self.btnBrowseUnitCadence, QtCore.SIGNAL('clicked()'),
        self.btnBrowseUnitCadenceClicked)
    self.connect(self.btnBrowseUnitChecklist, QtCore.SIGNAL('clicked()'),
        self.btnBrowseUnitChecklistClicked)
    self.connect(self.btnBrowseUnitAutocad, QtCore.SIGNAL('clicked()'),
        self.btnBrowseUnitAutocadClicked)
    self.connect(self.btnBrowseUnitArtParams, QtCore.SIGNAL('clicked()'),
        self.btnBrowseUnitArtParamsClicked)

    self.connect(self.btnBrowseWaferCadence, QtCore.SIGNAL('clicked()'),
        self.btnBrowseWaferCadenceClicked)
    self.connect(self.btnBrowseWaferChecklist, QtCore.SIGNAL('clicked()'),
        self.btnBrowseWaferChecklistClicked)
    self.connect(self.btnBrowseWaferAutocad, QtCore.SIGNAL('clicked()'),
        self.btnBrowseWaferAutocadClicked)

    self.connect(self.btnBrowseCadenceStreamOutDir, QtCore.SIGNAL('clicked()'),
        self.btnBrowseCadenceStreamOutDirClicked)
    self.connect(self.btnBrowseUnitCreateScriptDir, QtCore.SIGNAL('clicked()'),
        self.btnBrowseUnitCreateScriptDirClicked)
    self.connect(self.btnBrowseWaferClipTemplateDir,
        QtCore.SIGNAL('clicked()'),
        self.btnBrowseWaferClipScriptDirClicked)
    self.connect(self.btnBrowseWaferKnockoutTemplateDir,
        QtCore.SIGNAL('clicked()'),
        self.btnBrowseWaferKnockoutScriptDirClicked)
    self.connect(self.btnBrowseWaferFltTemplateDir, QtCore.SIGNAL('clicked()'),
        self.btnBrowseWaferFltTemplateDirClicked)
    self.connect(self.btnBrowseUnitZipTemplateDir, QtCore.SIGNAL('clicked()'),
        self.btnBrowseUnitZipTemplateDirClicked)
    self.connect(self.btnBrowseWaferZipTemplateDir, QtCore.SIGNAL('clicked()'),
        self.btnBrowseWaferZipTemplateDirClicked)

    configuration = Config.getConfig()
    self.txtDefaultDesignDir.setText(configuration["DefaultDesignDir"])
    self.txtTempFileDir.setText(configuration["TempFileDir"])

    self.txtUnitCadenceTemplate.setText(
        configuration["DefaultCadenceUnitTemplateDir"])
    self.txtUnitChecklistTemplate.setText(
        configuration["DefaultChecklistUnitTemplateDir"])
    self.txtUnitAutocadTemplate.setText(
        configuration["DefaultAutocadUnitTemplateDir"])
    self.txtUnitArtParamsTemplate.setText(
        configuration["DefaultArtParamsUnitTemplateDir"])

    self.txtWaferCadenceTemplate.setText(
        configuration["DefaultCadenceWaferTemplateDir"])
    self.txtWaferChecklistTemplate.setText(
        configuration["DefaultChecklistWaferTemplateDir"])
    self.txtWaferAutocadTemplate.setText(
        configuration["DefaultAutocadWaferTemplateDir"])

    self.txtCadenceStreamOutDir.setText(
        configuration["DefaultCadenceStreamOutDir"])
    self.txtUnitCreateScriptDir.setText(
        configuration["DefaultUnitCreateScriptDir"])
    self.txtWaferClipTemplateDir.setText(
        configuration["DefaultClipScriptDir"])
    self.txtWaferKnockoutTemplateDir.setText(
        configuration["DefaultKnockoutScriptDir"])
    self.txtWaferFltTemplateDir.setText(
        configuration["DefaultFltScriptDir"])

    self.txtUnitZipTemplateDir.setText(
        configuration["DefaultUnitZipTemplateDir"])
    self.txtWaferZipTemplateDir.setText(
        configuration["DefaultWaferZipTemplateDir"])

    # load the default knockout regions
    if "knockout_200" in configuration:
      k200 = configuration["knockout_200"]
      for i in range(6):
        f = "LLX" + str(i + 1)
        if f in k200:
          self.__dict__["txt200LLXK" + str(i + 1)].setText(k200[f])
        f = "LLY" + str(i + 1)
        if f in k200:
          self.__dict__["txt200LLYK" + str(i + 1)].setText(k200[f])
        f = "URX" + str(i + 1)
        if f in k200:
          self.__dict__["txt200URXK" + str(i + 1)].setText(k200[f])
        f = "URY" + str(i + 1)
        if f in k200:
          self.__dict__["txt200URYK" + str(i + 1)].setText(k200[f])

    if "knockout_300" in configuration:
      k300 = configuration["knockout_300"]
      for i in range(6):
        f = "LLX" + str(i + 1)
        if f in k300:
          self.__dict__["txt300LLXK" + str(i + 1)].setText(k300[f])
        f = "LLY" + str(i + 1)
        if f in k300:
          self.__dict__["txt300LLYK" + str(i + 1)].setText(k300[f])
        f = "URX" + str(i + 1)
        if f in k300:
          self.__dict__["txt300URXK" + str(i + 1)].setText(k300[f])
        f = "URY" + str(i + 1)
        if f in k300:
          self.__dict__["txt300URYK" + str(i + 1)].setText(k300[f])

  def btnOKClicked(self):
    print("Saving preferences...")

    configuration = Config.getConfig()

    configuration["DefaultDesignDir"] =\
        str(self.txtDefaultDesignDir.displayText())
    configuration["TempFileDir"] = str(self.txtTempFileDir.displayText())

    configuration["DefaultCadenceUnitTemplateDir"] =\
        str(self.txtUnitCadenceTemplate.text())
    configuration["DefaultChecklistUnitTemplateDir"] =\
        str(self.txtUnitChecklistTemplate.text())
    configuration["DefaultAutocadUnitTemplateDir"] =\
        str(self.txtUnitAutocadTemplate.text())
    configuration["DefaultArtParamsUnitTemplateDir"] =\
        str(self.txtUnitArtParamsTemplate.text())

    configuration["DefaultCadenceWaferTemplateDir"] =\
        str(self.txtWaferCadenceTemplate.text())
    configuration["DefaultChecklistWaferTemplateDir"] =\
        str(self.txtWaferChecklistTemplate.text())
    configuration["DefaultAutocadWaferTemplateDir"] =\
        str(self.txtWaferAutocadTemplate.text())

    configuration["DefaultCadenceStreamOutDir"] =\
        str(self.txtCadenceStreamOutDir.text())
    configuration["DefaultUnitCreateScriptDir"] =\
        str(self.txtUnitCreateScriptDir.text())
    configuration["DefaultClipScriptDir"] =\
        str(self.txtWaferClipTemplateDir.text())
    configuration["DefaultKnockoutScriptDir"] =\
        str(self.txtWaferKnockoutTemplateDir.text())
    configuration["DefaultFltScriptDir"] =\
        str(self.txtWaferFltTemplateDir.text())

    configuration["DefaultUnitZipTemplateDir"] =\
        str(self.txtUnitZipTemplateDir.text())
    configuration["DefaultWaferZipTemplateDir"] =\
        str(self.txtWaferZipTemplateDir.text())

    # save default knockout regions
    if not "knockout_200" in configuration:
      configuration["knockout_200"] = {}
    k200 = configuration["knockout_200"]

    for i in range(6):
      t1 = "txt200LLXK" + str(i + 1)
      t2 = "txt200LLYK" + str(i + 1)
      t3 = "txt200URXK" + str(i + 1)
      t4 = "txt200URYK" + str(i + 1)
      f1 = "LLX" + str(i + 1)
      f2 = "LLY" + str(i + 1)
      f3 = "URX" + str(i + 1)
      f4 = "URY" + str(i + 1)

      k200[f1] = str(self.__dict__[t1].text())
      k200[f2] = str(self.__dict__[t2].text())
      k200[f3] = str(self.__dict__[t3].text())
      k200[f4] = str(self.__dict__[t4].text())

    if not "knockout_300" in configuration:
      configuration["knockout_300"] = {}
    k300 = configuration["knockout_300"]

    for i in range(6):
      t1 = "txt300LLXK" + str(i + 1)
      t2 = "txt300LLYK" + str(i + 1)
      t3 = "txt300URXK" + str(i + 1)
      t4 = "txt300URYK" + str(i + 1)
      f1 = "LLX" + str(i + 1)
      f2 = "LLY" + str(i + 1)
      f3 = "URX" + str(i + 1)
      f4 = "URY" + str(i + 1)

      k300[f1] = str(self.__dict__[t1].text())
      k300[f2] = str(self.__dict__[t2].text())
      k300[f3] = str(self.__dict__[t3].text())
      k300[f4] = str(self.__dict__[t4].text())

    Config.saveConfig(configuration)

    self.accept()

  def btnCancelClicked(self):
    self.reject()

  def btnBrowseDesignDirClicked(self):
    newDir = QtGui.QFileDialog.getExistingDirectory(self,
        "Choose Default Design Directory",
        self.txtDefaultDesignDir.text(), QtGui.QFileDialog.DontResolveSymlinks)
    if len(str(newDir)) <= 0:
      return
    self.txtDefaultDesignDir.setText(newDir)

  def btnBrowseTempFileDirClicked(self):
    newDir = QtGui.QFileDialog.getExistingDirectory(self,
        "Choose Temporary File Directory",
        self.txtTempFileDir.text(), QtGui.QFileDialog.DontResolveSymlinks)
    if len(str(newDir)) <= 0:
      return
    self.txtTempFileDir.setText(newDir)

  def btnBrowseUnitCadenceClicked(self):
    newDir = QtGui.QFileDialog.getExistingDirectory(self,
        "Choose Default Unit Cadence Template Directory",
        self.txtUnitCadenceTemplate.text(),
        QtGui.QFileDialog.DontResolveSymlinks)
    if len(str(newDir)) <= 0:
      return
    self.txtUnitCadenceTemplate.setText(newDir)

  def btnBrowseUnitChecklistClicked(self):
    newDir = QtGui.QFileDialog.getExistingDirectory(self,
        "Choose Default Unit Checklist Template Directory",
        self.txtUnitChecklistTemplate.text(),
        QtGui.QFileDialog.DontResolveSymlinks)
    if len(str(newDir)) <= 0:
      return
    self.txtUnitChecklistTemplate.setText(newDir)

  def btnBrowseUnitAutocadClicked(self):
    newDir = QtGui.QFileDialog.getExistingDirectory(self,
        "Choose Default Unit Autocad Template Directory",
        self.txtUnitAutocadTemplate.text(),
        QtGui.QFileDialog.DontResolveSymlinks)
    if len(str(newDir)) <= 0:
      return
    self.txtUnitAutocadTemplate.setText(newDir)

  def btnBrowseUnitArtParamsClicked(self):
    newDir = QtGui.QFileDialog.getExistingDirectory(self,
        "Choose Default Unit Art Params Template Directory",
        self.txtUnitArtParamsTemplate.text(),
        QtGui.QFileDialog.DontResolveSymlinks)
    if len(str(newDir)) <= 0:
      return
    self.txtUnitArtParamsTemplate.setText(newDir)

  def btnBrowseWaferCadenceClicked(self):
    newDir = QtGui.QFileDialog.getExistingDirectory(self,
        "Choose Default Wafer Cadence Template Directory",
        self.txtWaferCadenceTemplate.text(),
        QtGui.QFileDialog.DontResolveSymlinks)
    if len(str(newDir)) <= 0:
      return
    self.txtWaferCadenceTemplate.setText(newDir)

  def btnBrowseWaferChecklistClicked(self):
    newDir = QtGui.QFileDialog.getExistingDirectory(self,
        "Choose Default Wafer Checklist Template Directory",
        self.txtWaferChecklistTemplate.text(),
        QtGui.QFileDialog.DontResolveSymlinks)
    if len(str(newDir)) <= 0:
      return
    self.txtWaferChecklistTemplate.setText(newDir)

  def btnBrowseWaferAutocadClicked(self):
    newDir = QtGui.QFileDialog.getExistingDirectory(self,
        "Choose Default Wafer Autocad Template Directory",
        self.txtWaferAutocadTemplate.text(),
        QtGui.QFileDialog.DontResolveSymlinks)
    if len(str(newDir)) <= 0:
      return
    self.txtWaferAutocadTemplate.setText(newDir)

  def btnBrowseCadenceStreamOutDirClicked(self):
    newDir = QtGui.QFileDialog.getExistingDirectory(self,
        "Choose Default Cadence Stream Out Script Template Directory",
        self.txtCadenceStreamOutDir.text(),
        QtGui.QFileDialog.DontResolveSymlinks)
    if len(str(newDir)) <= 0:
      return
    self.txtCadenceStreamOutDir.setText(newDir)

  def btnBrowseUnitCreateScriptDirClicked(self):
    newDir = QtGui.QFileDialog.getExistingDirectory(self,
        "Choose Default Unit Create Script Template Directory",
        self.txtUnitCreateScriptDir.text(),
        QtGui.QFileDialog.DontResolveSymlinks)
    if len(str(newDir)) <= 0:
      return
    self.txtUnitCreateScriptDir.setText(newDir)

  def btnBrowseWaferClipScriptDirClicked(self):
    newDir = QtGui.QFileDialog.getExistingDirectory(self,
        "Choose Default Clip Script Template Directory",
        self.txtWaferClipTemplateDir.text(),
        QtGui.QFileDialog.DontResolveSymlinks)
    if len(str(newDir)) <= 0:
      return
    self.txtWaferClipTemplateDir.setText(newDir)

  def btnBrowseWaferKnockoutScriptDirClicked(self):
    newDir = QtGui.QFileDialog.getExistingDirectory(self,
        "Choose Default Knockout Script Template Directory",
        self.txtWaferKnockoutTemplateDir.text(),
        QtGui.QFileDialog.DontResolveSymlinks)
    if len(str(newDir)) <= 0:
      return
    self.txtWaferKnockoutTemplateDir.setText(newDir)

  def btnBrowseWaferFltTemplateDirClicked(self):
    newDir = QtGui.QFileDialog.getExistingDirectory(self,
        "Choose Default Wafer Flt Script Template Directory",
        self.txtWaferFltTemplateDir.text(),
        QtGui.QFileDialog.DontResolveSymlinks)
    if len(str(newDir)) <= 0:
      return
    self.txtWaferFltTemplateDir.setText(newDir)

  def btnBrowseUnitZipTemplateDirClicked(self):
    newDir = QtGui.QFileDialog.getExistingDirectory(self,
        "Choose Default Unit Zip Template Directory",
        self.txtUnitZipTemplateDir.text(),
        QtGui.QFileDialog.DontResolveSymlinks)
    if len(str(newDir)) <= 0:
      return
    self.txtUnitZipTemplateDir.setText(newDir)

  def btnBrowseWaferZipTemplateDirClicked(self):
    newDir = QtGui.QFileDialog.getExistingDirectory(self,
        "Choose Default Wafer Zip Template Directory",
        self.txtWaferZipTemplateDir.text(),
        QtGui.QFileDialog.DontResolveSymlinks)
    if len(str(newDir)) <= 0:
      return
    self.txtWaferZipTemplateDir.setText(newDir)

# DesignAttributes.py
# Created by Craig Bishop on 03 January 2012
# Wavellite
#
# Copyright 2012 All Rights Reserved
#

from PySide import QtCore, QtGui
from Ui_DesignAttributes import Ui_DesignAttributes
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdftypes import resolve1
import PLMExport


class DesignAttributes(QtGui.QDialog, Ui_DesignAttributes):
  def __init__(self):
    QtGui.QDialog.__init__(self)

    # setup the gui from the designer
    self.setupUi(self)

    self.connect(self.btnOK, QtCore.SIGNAL('clicked()'),
        self.btnOkClicked)
    self.connect(self.btnCancel, QtCore.SIGNAL('clicked()'),
        self.btnCancelClicked)
    self.connect(self.btnImportFromDRForm, QtCore.SIGNAL('clicked()'),
        self.btnImportFromDRFormClicked)
    self.connect(self.btnExportForPLM, QtCore.SIGNAL('clicked()'),
        self.btnExportForPLMClicked)

  def btnOkClicked(self):
    self.saveAttributes()
    self.saveTab()
    self.accept()

  def btnCancelClicked(self):
    self.saveTab()
    self.reject()

  def loadAttributes(self):
    devAttrs = self.workingDir.device.get("attributes")
    if devAttrs is None:
      print "No attributes yet."
      return

    for k, v in devAttrs.items():
      if k == "TypeOfDesign":
        for i in range(2):
          txt = self.__dict__.get("txtTypeOfDesign" + str(i))
          if str(txt.text()) == v:
            txt.setChecked(True)
        continue
      elif k == "Orientation":
        for i in range(4):
          txt = self.__dict__.get("txtOrientation" + str(i))
          if str(txt.text()) == v:
            txt.setChecked(True)
        continue

      txt = self.__dict__.get("txt" + str(k))
      if txt is None:
        continue

      # could be a combobox, so check
      if isinstance(txt, QtGui.QComboBox):
        # pick correct item
        for i in range(txt.count()):
          if txt.itemText(i) == v:
            txt.setCurrentIndex(i)
      elif isinstance(txt, QtGui.QTextEdit):
        txt.setPlainText(v)
      else:
        txt.setText(v)

  def saveAttributes(self):
    devAttrs = self.workingDir.device.get("attributes")
    if devAttrs is None:
      self.workingDir.device['attributes'] = {}
    devAttrs = self.workingDir.device.get("attributes")

    for i in range(2):
      txt = self.__dict__.get("txtTypeOfDesign" + str(i))
      if txt.isChecked():
        devAttrs['TypeOfDesign'] = str(txt.text())

    for i in range(4):
      txt = self.__dict__.get("txtOrientation" + str(i))
      if txt.isChecked():
        devAttrs['Orientation'] = str(txt.text())

    for k, v in self.__dict__.items():
      if k.startswith('txt'):
        attrname = k.replace('txt', '')
        txt = self.__dict__[k]

        # if combobox, save the item text
        if isinstance(txt, QtGui.QComboBox):
          devAttrs[attrname] = str(txt.itemText(txt.currentIndex()))
        elif isinstance(txt, QtGui.QTextEdit):
          devAttrs[attrname] = str(txt.toPlainText())
        else:
          devAttrs[attrname] = str(txt.text())
    self.workingDir.save()

  def loadTab(self):
    tab = self.workingDir.device.get('DesignAttributesTab')
    if tab is not None:
      self.tabWidget.setCurrentIndex(tab)

  def saveTab(self):
    self.workingDir.device['DesignAttributesTab'] =\
        self.tabWidget.currentIndex()
    self.workingDir.save()

  def btnImportFromDRFormClicked(self):
    path, filt = QtGui.QFileDialog.getOpenFileName(self,
        "Select Design Requirements Form",
        "", "")

    if (len(path) <= 0):
      QtGui.QMessageBox.warning(self, "Must select a Design Requirements Form",
          "You need to select a valid design requirements PDF form.")
      return

    devAttrs = self.workingDir.device.get("attributes")
    if devAttrs is None:
      self.workingDir.device['attributes'] = {}
    devAttrs = self.workingDir.device.get("attributes")

    # load mappings
    mappings = {}
    mapFilename = "DRFormMappings.txt"
    mapfile = open(mapFilename, 'r')
    for line in mapfile:
      if line.startswith('//'):
        continue
      line = line.replace('\n', '')
      toks = line.split(' = ')
      mappings[toks[0]] = toks[1]
    mapfile.close()

    # now parse PDF
    pdffile = open(path, 'rb')
    parser = PDFParser(pdffile)
    doc = PDFDocument()
    parser.set_document(doc)
    doc.set_parser(parser)
    doc.initialize()

    fields = resolve1(doc.catalog['AcroForm'])['Fields']
    for f in fields:
      fr = resolve1(f)
      mapkey = mappings.get(str(fr['T']))
      v = str(fr['V'])
      if mapkey is None:
        continue

      # could be a radio button
      if mapkey == "TypeOfDesign":
        v = v.replace('/', '')
        n = int(v)
        txt = self.__dict__.get("txtTypeOfDesign" + str(n))
        txt.setChecked(True)
        continue
      elif mapkey == "Orientation":
        v = v.replace('/', '')
        n = int(v)
        txt = self.__dict__.get("txtOrientation" + str(n))
        txt.setChecked(True)
        continue

      txt = self.__dict__.get("txt" + mapkey)
      if txt is None:
        continue

      # could be a combobox, so check
      if isinstance(txt, QtGui.QComboBox):
        # pick correct item
        for i in range(txt.count()):
          if txt.itemText(i) == v:
            txt.setCurrentIndex(i)
      elif isinstance(txt, QtGui.QTextEdit):
        v = v.decode('U16').encode('ascii', 'ignore')
        txt.setPlainText(v)
      else:
        txt.setText(v)

    pdffile.close()

  def btnExportForPLMClicked(self):
    self.saveAttributes()
    tplpath, filt = QtGui.QFileDialog.getOpenFileName(self,
        "Select Agile PLM Excel Template",
        "", "")
    outPath, filt = QtGui.QFileDialog.getSaveFileName(self,
        "Save Agile PLM Excel File",
        self.workingDir.fileDir, "")
    mapPath = "PLMMappings.txt"
    PLMExport.exportXLS(self.workingDir.device.get('attributes'), mapPath,
        tplpath, outPath)

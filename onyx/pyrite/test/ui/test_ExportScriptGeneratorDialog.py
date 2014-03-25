# test_ExportScriptGeneratorDialog.py
# Created by Craig Bishop on 06 July 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

import unittest
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtTest import QTest
import QAPP
from pyrite.ExportScriptGeneratorDialog import ExportScriptGeneratorDialog

class TestExportScriptGeneratorDialogExists(unittest.TestCase):
  def setUp(self):
    self.app = QAPP.QT_APP
    self.dummyWidget = QWidget()

  def tearDown(self):
    del(self.dummyWidget)

  def testDialogShows(self):
    dlg = ExportScriptGeneratorDialog(self.dummyWidget)
    dlg.show()
    self.assertIsNotNone(dlg)

class TestExportScriptGeneratorDialogLayerOptions(unittest.TestCase):
  def setUp(self):
    self.app = QAPP.QT_APP
    self.dlg = ExportScriptGeneratorDialog(None)
    self.dlg.show()

  def tearDown(self):
    self.dlg.hide()
    del(self.dlg)

  def testExportOptionsExist(self):
    self.assertIsNotNone(self.dlg._exportOptions)

  def testAddLayer(self):
    self.dlg.btnAdd.click()
    self.assertEqual(self.dlg.lstLayers.count(), 1,
        "add button did not add a layer")

  def testAddTwoLayers(self):
    self.dlg.btnAdd.click()
    self.dlg.btnAdd.click()
    self.assertEqual(self.dlg.lstLayers.count(), 2,
        "add button did not add a second layer")

  def testRemoveLayer(self):
    self.dlg.btnAdd.click()
    self.dlg.lstLayers.setCurrentRow(0)
    self.dlg.btnRemove.click()
    self.assertEqual(self.dlg.lstLayers.count(), 0,
        "remove button did not delete layer")

  def testMoveLayerUp(self):
    self.dlg.btnAdd.click()
    self.dlg.btnAdd.click()
    item1 = self.dlg.lstLayers.item(0)
    item2 = self.dlg.lstLayers.item(1)

    self.dlg.lstLayers.setCurrentRow(1)
    self.dlg.btnMoveUp.click()

    self.assertEqual(self.dlg.lstLayers.row(item1), 1,
        "did not move item2 up")
    self.assertEqual(self.dlg.lstLayers.row(item2), 0,
        "did not move item2 up")

  def testMoveLayerDown(self):
    self.dlg.btnAdd.click()
    self.dlg.btnAdd.click()
    item1 = self.dlg.lstLayers.item(0)
    item2 = self.dlg.lstLayers.item(1)

    self.dlg.lstLayers.setCurrentRow(0)
    self.dlg.btnMoveDown.click()

    self.assertEqual(self.dlg.lstLayers.row(item1), 1,
        "did not move item2 down")
    self.assertEqual(self.dlg.lstLayers.row(item2), 0,
        "did not move item2 down")

class TestExportScriptGeneratorDialogLayerFeatures(unittest.TestCase):
  def setUp(self):
    self.dlg = ExportScriptGeneratorDialog(None)
    self.dlg.show()
    self.dlg.btnAdd.click()
    self.dlg.lstLayers.setCurrentRow(0)
    self.item = self.dlg.lstLayers.item(0)

  def tearDown(self):
    self.dlg.hide()
    del(self.dlg)

  def testChangeCadenceLayerName(self):
    self.dlg.txtCadenceLayerName.setText("")
    QTest.keyClicks(self.dlg.txtCadenceLayerName, "RDL")
    self.assertEqual(self.dlg._exportOptions.layers()[0]["cadName"], "RDL",
        "CAD name was not set")

  def testPins(self):
    self.dlg.chckPins.click()
    self.assertTrue(self.dlg._exportOptions.layers()[0]["pins"],
        "did not change pins export setting")

  def testVias(self):
    self.dlg.chckVias.click()
    self.assertTrue(self.dlg._exportOptions.layers()[0]["vias"],
        "did not change vias export setting")

  def testShapes(self):
    self.dlg.chckShapes.click()
    self.assertTrue(self.dlg._exportOptions.layers()[0]["shapes"],
        "did not change shapes export setting")

  def testPaths(self):
    self.dlg.chckPaths.click()
    self.assertTrue(self.dlg._exportOptions.layers()[0]["paths"],
        "did not change paths export setting")

  def testLayerName(self):
    self.dlg.txtPyriteLayerName.setText("")
    QTest.keyClicks(self.dlg.txtPyriteLayerName, "RDL")
    self.assertEqual(self.dlg._exportOptions.layers()[0]["name"], "RDL",
        "did not change layer name setting")
    self.assertEqual(self.item.text(), "RDL",
        "did not change layer name setting")

  def testLayerNumber(self):
    self.dlg.txtPyriteLayerNumber.setText("")
    QTest.keyClicks(self.dlg.txtPyriteLayerNumber, "30")
    self.assertEqual(self.dlg._exportOptions.layers()[0]["number"], "30",
        "did not change layer number setting")

class TestExportScriptGeneratorDialogSwitchLayer(unittest.TestCase):
  def setUp(self):
    self.dlg = ExportScriptGeneratorDialog(None)
    self.dlg.show()
    self.dlg.btnAdd.click()
    self.dlg.btnAdd.click()

    self.dlg.lstLayers.setCurrentRow(0)
    self.dlg.txtCadenceLayerName.setText("RDL-FO")
    self.dlg.txtPyriteLayerName.setText("RDL")
    self.dlg.chckPins.click()
    self.dlg.chckVias.click()
    self.dlg.txtPyriteLayerNumber.setText("30")

    self.dlg.lstLayers.setCurrentRow(1)
    self.dlg.txtCadenceLayerName.setText("VIA-11")
    self.dlg.txtPyriteLayerName.setText("VIA1")
    self.dlg.chckShapes.click()
    self.dlg.chckPaths.click()
    self.dlg.txtPyriteLayerNumber.setText("10")

  def tearDown(self):
    self.dlg.hide()
    del(self.dlg)

  def testSwitchSelection0(self):
    self.dlg.lstLayers.setCurrentRow(0)
    self.assertEqual(self.dlg.txtCadenceLayerName.text(), "RDL-FO")
    self.assertEqual(self.dlg.txtPyriteLayerName.text(), "RDL")
    self.assertTrue(self.dlg.chckPins.isChecked())
    self.assertTrue(self.dlg.chckVias.isChecked())
    self.assertFalse(self.dlg.chckShapes.isChecked())
    self.assertFalse(self.dlg.chckPaths.isChecked())
    self.assertEqual(self.dlg.txtPyriteLayerNumber.text(), "30")


  def testSwitchSelection0(self):
    self.dlg.lstLayers.setCurrentRow(1)
    self.assertEqual(self.dlg.txtCadenceLayerName.text(), "VIA-11")
    self.assertEqual(self.dlg.txtPyriteLayerName.text(), "VIA1")
    self.assertFalse(self.dlg.chckPins.isChecked())
    self.assertFalse(self.dlg.chckVias.isChecked())
    self.assertTrue(self.dlg.chckShapes.isChecked())
    self.assertTrue(self.dlg.chckPaths.isChecked())
    self.assertEqual(self.dlg.txtPyriteLayerNumber.text(), "10")

class TestExportScriptGeneratorDialogLayerPropertiesEnabling(unittest.TestCase):
  def setUp(self):
    self.dlg = ExportScriptGeneratorDialog(None)
    self.dlg.show()

  def tearDown(self):
    self.dlg.hide()
    del(self.dlg)

  def testDefaultDisabled(self):
    self.assertFalse(self.dlg.txtCadenceLayerName.isEnabled(),
        "layer properties should default to disabled")
    self.assertFalse(self.dlg.chckPins.isEnabled(),
        "layer properties should default to disabled")
    self.assertFalse(self.dlg.chckVias.isEnabled(),
        "layer properties should default to disabled")
    self.assertFalse(self.dlg.chckShapes.isEnabled(),
        "layer properties should default to disabled")
    self.assertFalse(self.dlg.chckPaths.isEnabled(),
        "layer properties should default to disabled")
    self.assertFalse(self.dlg.txtPyriteLayerName.isEnabled(),
        "layer properties should default to disabled")
    self.assertFalse(self.dlg.txtPyriteLayerNumber.isEnabled(),
        "layer properties should default to disabled")

  def testEnabledOnSelection(self):
    self.dlg.btnAdd.click()
    self.dlg.btnAdd.click()
    self.dlg.lstLayers.setCurrentRow(0)

    self.assertTrue(self.dlg.txtCadenceLayerName.isEnabled(),
        "layer properties should be enabled on selection")
    self.assertTrue(self.dlg.chckPins.isEnabled(),
        "layer properties should be enabled on selection")
    self.assertTrue(self.dlg.chckVias.isEnabled(),
        "layer properties should be enabled on selection")
    self.assertTrue(self.dlg.chckShapes.isEnabled(),
        "layer properties should be enabled on selection")
    self.assertTrue(self.dlg.chckPaths.isEnabled(),
        "layer properties should be enabled on selection")
    self.assertTrue(self.dlg.txtPyriteLayerName.isEnabled(),
        "layer properties should be enabled on selection")
    self.assertTrue(self.dlg.txtPyriteLayerNumber.isEnabled(),
        "layer properties should be enabled on selection")

class TestExportScriptGeneratorDialogSelectsOnAddLayer(unittest.TestCase):
  def setUp(self):
    self.dlg = ExportScriptGeneratorDialog(None)
    self.dlg.show()

  def tearDown(self):
    self.dlg.hide()
    del(self.dlg)

  def testSelectsNewLayerOnAddLayer(self):
    self.dlg.btnAdd.click()
    self.assertGreater(len(self.dlg.lstLayers.selectedItems()), 0,
        "the new layer should be selected")
    self.assertEqual(self.dlg.lstLayers.currentRow(), 0,
        "the new layer should be selected")

class TestExportScriptGeneratorDialogCloseOnCancel(unittest.TestCase):
  def setUp(self):
    self.dlg = ExportScriptGeneratorDialog(None)
    self.dlg.show()

  def tearDown(self):
    self.dlg.hide()
    del(self.dlg)

  def testDialogClosesOnCancelClick(self):
    self.dlg.btnCancel.click()
    self.assertFalse(self.dlg.isVisible(),
        "dialog should be closed on cancel button click")

class TestExportScriptGeneratorDialogGeneratorButtonEnabling(unittest.TestCase):
  def setUp(self):
    self.dlg = ExportScriptGeneratorDialog(None)
    self.dlg.show()

  def tearDown(self):
    self.dlg.hide()
    del(self.dlg)

  def testDefaultDisabled(self):
    self.assertFalse(self.dlg.btnGenerateExportScript.isEnabled(),
        "generate button should be disabled without any layers")

  def testEnabledWithLayers(self):
    self.dlg.txtDieWScribeLayerName.setText("BLAH")
    self.dlg.btnAdd.click()
    self.assertTrue(self.dlg.btnGenerateExportScript.isEnabled(),
        "generate button should be enabled with layers")

  def testDisabledAfterRemoveLayer(self):
    self.dlg.btnAdd.click()
    self.dlg.btnRemove.click()
    self.assertFalse(self.dlg.btnGenerateExportScript.isEnabled(),
        "generate button should be disabled without any layers")

  def testDisabledWithoutDieWScribe(self):
    self.dlg.btnAdd.click()
    self.assertFalse(self.dlg.btnGenerateExportScript.isEnabled(),
        "generate button should be disabled without diewscribe")

class TestExportScriptGeneratorDialogLoadsUpperCaseCadLayerName(unittest.TestCase):
  def setUp(self):
    self.dlg = ExportScriptGeneratorDialog(None)
    self.dlg.show()
    self.dlg.btnAdd.click()
    self.dlg.btnAdd.click()

  def tearDown(self):
    self.dlg.hide()
    del(self.dlg)
    
  def testCadLayerNameBecomesUpper(self):
    self.dlg.lstLayers.setCurrentRow(0)
    self.dlg.txtCadenceLayerName.setText("conductor/rdl-fo")
    self.dlg.lstLayers.setCurrentRow(1)
    self.dlg.lstLayers.setCurrentRow(0)
    self.assertEqual(self.dlg.txtCadenceLayerName.text(),
        "CONDUCTOR/RDL-FO")

class TestExportScriptGeneratorDialogDieWScribeLayerName(unittest.TestCase):
  def setUp(self):
    self.dlg = ExportScriptGeneratorDialog(None)
    self.dlg.show()

  def tearDown(self):
    self.dlg.hide()
    del(self.dlg)

  def testDefaultText(self):
    self.assertEqual(self.dlg.txtDieWScribeLayerName.text(), "",
        "default diewscribe layer name should be blank")

  def testSetLayer(self):
    self.dlg.txtDieWScribeLayerName.setText("COMPONENT GEOMETRY/DIEWSCRIBE")
    self.assertEqual(self.dlg._exportOptions.dieWithScribeLayer(),
        "COMPONENT GEOMETRY/DIEWSCRIBE",
        "dialog did not set the diewscribe in the options")

class TestExportScriptGeneratorDialogNewLayerNames(unittest.TestCase):
  def setUp(self):
    self.dlg = ExportScriptGeneratorDialog(None)
    self.dlg.show()

  def tearDown(self):
    self.dlg.hide()
    del(self.dlg)

  def testNewLayerNames(self):
    self.dlg.btnAdd.click()
    self.dlg.btnAdd.click()
    self.dlg.btnAdd.click()
    self.assertEqual(self.dlg.lstLayers.item(0).text(), "New Layer",
        "new layer name is incorrect")
    self.assertEqual(self.dlg.lstLayers.item(1).text(), "New Layer 1",
        "new layer name is incorrect")
    self.assertEqual(self.dlg.lstLayers.item(2).text(), "New Layer 2",
        "new layer name is incorrect")


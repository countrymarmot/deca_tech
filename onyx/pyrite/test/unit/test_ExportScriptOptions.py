# test_ExportScriptOptions.py
# Created by Craig Bishop on 06 July 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

import unittest
from pyrite.SIPExport import ExportScriptOptions

class TestExportScriptOptionsLayers(unittest.TestCase):
  def setUp(self):
    self.exportOptions = ExportScriptOptions()

  def testDefaultLayers(self):
    self.assertEqual(len(self.exportOptions.layers()), 0,
        "export script should default to no layers")

  def testAddLayer(self):
    self.exportOptions.addLayer("RDL")
    self.assertEqual(len(self.exportOptions.layers()), 1,
        "added layer is not present")
    self.assertTrue(self.exportOptions.layerExists("RDL"),
        "RDL layer should exist")

  def testRemoveLayer(self):
    self.exportOptions.addLayer("RDL")
    self.exportOptions.removeLayer("RDL")
    self.assertEqual(len(self.exportOptions.layers()), 0,
        "export script have no layers")

  def testLayerForName(self):
    self.layer = self.exportOptions.addLayer("RDL")
    self.assertEqual(self.layer, self.exportOptions.layerForName("RDL"))

  def testMoveLayerUp(self):
    self.exportOptions.addLayer("RDL")
    self.exportOptions.addLayer("VIA-1")
    self.exportOptions.moveLayerUp("VIA-1")
    self.assertEqual(self.exportOptions.layers().index(
      self.exportOptions.layerForName("VIA-1")), 0,
      "VIA-1 layer should be at index 0")

  def testMoveLayerDown(self):
    self.exportOptions.addLayer("RDL")
    self.exportOptions.addLayer("VIA-1")
    self.exportOptions.moveLayerDown("RDL")
    self.assertEqual(self.exportOptions.layers().index(
      self.exportOptions.layerForName("RDL")), 1,
      "RDL layer should be at index 1")


class TestExportScriptOptionsLayerProperties(unittest.TestCase):
  def setUp(self):
    self.exportOptions = ExportScriptOptions()
    self.layer = self.exportOptions.addLayer("RDL")

  def testDefaultCadenceLayerName(self):
    self.assertEqual(self.exportOptions.cadenceLayerNameForLayer("RDL"), "",
      "default cadence layer name is non-blank")

  def testSetCadenceLayerNameForLayer(self):
    self.exportOptions.setCadenceLayerNameForLayer("RDL", "RDL-FO")
    self.assertEqual(self.exportOptions.cadenceLayerNameForLayer("RDL"), "RDL-FO",
      "cadence layer name was not set")

  def testDefaultLayerNumber(self):
    self.assertEqual(self.exportOptions.layerNumberForLayer("RDL"), 1,
        "default layer number is not 10")

  def testSetLayerNumber(self):
    self.exportOptions.setLayerNumberForLayer("RDL", 30)
    self.assertEqual(self.exportOptions.layerNumberForLayer("RDL"), 30,
        "layer number was not set")

  def testDefaultFeatureOptions(self):
    self.assertFalse(self.exportOptions.shouldExportPinsForLayer("RDL"),
      "default pins export setting is True")
    self.assertFalse(self.exportOptions.shouldExportViasForLayer("RDL"),
      "default vias export setting is True")
    self.assertFalse(self.exportOptions.shouldExportShapesForLayer("RDL"),
      "default shapes export setting is True")
    self.assertFalse(self.exportOptions.shouldExportPathsForLayer("RDL"),
      "default paths export setting is True")

  def testSetPinsExport(self):
    self.exportOptions.setShouldExportPinsForLayer("RDL", True)
    self.assertTrue(self.exportOptions.shouldExportPinsForLayer("RDL"),
      "pins export setting was not set to True")

  def testSetViasExport(self):
    self.exportOptions.setShouldExportViasForLayer("RDL", True)
    self.assertTrue(self.exportOptions.shouldExportViasForLayer("RDL"),
      "vias export setting was not set to True")
    
  def testSetShapesExport(self):
    self.exportOptions.setShouldExportShapesForLayer("RDL", True)
    self.assertTrue(self.exportOptions.shouldExportShapesForLayer("RDL"),
      "shapes export setting was not set to True")

  def testSetPathsExport(self):
    self.exportOptions.setShouldExportPathsForLayer("RDL", True)
    self.assertTrue(self.exportOptions.shouldExportPathsForLayer("RDL"),
      "paths export setting was not set to True")


class TestExportScriptOptionsCadenceLayerNameIsUpper(unittest.TestCase):
  def setUp(self):
    self.exportOptions = ExportScriptOptions()
    self.layer = self.exportOptions.addLayer("RDL")

  def testCadenceLayerNameIsCaps(self):
    self.exportOptions.setCadenceLayerNameForLayer("RDL", "conductor/rdl")
    self.assertEqual(self.exportOptions.cadenceLayerNameForLayer("RDL"), "CONDUCTOR/RDL",
        "Cadence layer name must be all upper case")


class TestExportScriptOptionsDieWScribeLayer(unittest.TestCase):
  def setUp(self):
    self.exportOptions = ExportScriptOptions()

  def testDefaultLayer(self):
    self.assertEqual(self.exportOptions.dieWithScribeLayer(), "",
        "default diewscribe layer is not blank")

  def testSetLayer(self):
    self.exportOptions.setDieWithScribeLayer("COMPONENT GEOMETRY/DIEWSCRIBE")
    self.assertEqual(self.exportOptions.dieWithScribeLayer(),
        "COMPONENT GEOMETRY/DIEWSCRIBE",
        "diewscribe layer was not set")


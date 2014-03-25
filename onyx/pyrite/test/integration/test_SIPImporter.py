# test_SIPImporter.py
# Created by Craig Bishop on 12 July 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

import unittest
from pyrite.SIPImport import SIPImporter, SIPImportCommand
from pyrite.Project import Project
from pyrite.malachite import Design
from pyrite.malachite.Geom import Point

class TestSIPImporterDesign(unittest.TestCase):
  def setUp(self):
    importer = SIPImporter()
    self.design = importer.designFromXML(xml)

  def testDesign(self):
    self.assertEqual(self.design.objType, "DESIGN")

  def testPackage(self):
    package = self.design.package
    self.assertEqual(package.objType, "PACKAGE")
    self.assertEqual(package.center, Point.fromXY(-1, -1))
    self.assertEqual(package.width, 5000)
    self.assertEqual(package.height, 5000)

  def testDies(self):
    die = self.design.package.dies[0]
    self.assertEqual(die.objType, "DIE")
    self.assertEqual(die.center, Point.fromXY(0, 0))
    self.assertEqual(die.width, 3820)
    self.assertEqual(die.height, 3910)

  def testLayers(self):
    layers = self.design.package.layers
    self.assertEqual(len(layers), 2,
        "should be RDL and VIA-1 layers")
    layerNames = [layer.name for layer in layers]
    self.assertIn("VIA-1", layerNames)
    self.assertIn("RDL", layerNames)
    layerNumbers = [layer.number for layer in layers]
    self.assertIn(30, layerNumbers)
    self.assertIn(10, layerNumbers)

  def testLayersByName(self):
    rdlLayer = self.design.package.layerForName("RDL")
    self.assertEqual(rdlLayer.number, 30)
    rdlLayer = self.design.package.layerForName("VIA-1")
    self.assertEqual(rdlLayer.number, 10)

  def testNets(self):
    nets = self.design.package.nets
    netNames = [net.name for net in nets]
    self.assertIn("P0_0", netNames)
    self.assertIn("P0_1", netNames)

  def testBranches(self):
    netP0_0 = [net for net in self.design.package.nets if net.name == "P0_0"][0]
    self.assertEqual(len(netP0_0.branches), 2)

    netP0_1 = [net for net in self.design.package.nets if net.name == "P0_1"][0]
    self.assertEqual(len(netP0_1.branches), 1)

  def testPads(self):
    netP0_0 = [net for net in self.design.package.nets if net.name == "P0_0"][0]
    branch = [branch for branch in netP0_0.branches if len(branch.children) > 0][0]
    pads = [child for child in branch.children if child.objType == "PAD"]
    rdlLayer = self.design.package.layerForName("RDL")
    rdlPad = [pad for pad in pads if pad.layer == rdlLayer][0]
    self.assertEqual(rdlPad.center, Point.fromXY(-301.4, -1688.4))
    self.assertEqual(rdlPad.diameter, 38.5)
    self.assertEqual(rdlPad.name, "CU_PILLAR_80")

    viaLayer = self.design.package.layerForName("VIA-1")
    viaPad = [pad for pad in pads if pad.layer == viaLayer][0]
    self.assertEqual(viaPad.center, Point.fromXY(-302.4, -1788.4))
    self.assertEqual(viaPad.diameter, 20.0)
    self.assertEqual(viaPad.name, "CU_PILLAR_80")

  def testShapes(self):
    netP0_0 = [net for net in self.design.package.nets if net.name == "P0_0"][0]
    branch = [branch for branch in netP0_0.branches if len(branch.children) > 0][0]
    shape = [child for child in branch.children if child.objType == "SHAPE"][0]
    rdlLayer = self.design.package.layerForName("RDL")
    self.assertEqual(shape.layer, rdlLayer)
    self.assertEqual(len(shape.segments), 3)

    seg0 = shape.segments[0]
    self.assertEqual(seg0.p1, Point.fromXY(-427.84, -1815.31))
    self.assertEqual(seg0.p2, Point.fromXY(-558.94, -1879.4))

    seg1 = shape.segments[1]
    self.assertEqual(seg1.p1, Point.fromXY(-558.94, -1879.4))
    self.assertEqual(seg1.p2, Point.fromXY(-558.94, -1879.4))

    arc = shape.segments[2]
    self.assertEqual(arc.p1, Point.fromXY(-558.94, -1879.4))
    self.assertEqual(arc.p2, Point.fromXY(-300, -1400))
    self.assertEqual(arc.center, Point.fromXY(444, 333))
    self.assertEqual(arc.cw, False)

  def testPaths(self):
    netP0_0 = [net for net in self.design.package.nets if net.name == "P0_0"][0]
    branch = [branch for branch in netP0_0.branches if len(branch.children) > 0][0]
    path = [child for child in branch.children if child.objType == "PATH"][0]
    rdlLayer = self.design.package.layerForName("RDL")
    self.assertEqual(path.layer, rdlLayer)
    self.assertEqual(len(path.segments), 3)

    seg0 = path.segments[0]
    self.assertEqual(seg0.p1, Point.fromXY(-301.2, -1308.8))
    self.assertEqual(seg0.p2, Point.fromXY(-558.94, -1879.4))
    self.assertEqual(seg0.traceWidth, 20.0)
    
    seg1 = path.segments[1]
    self.assertEqual(seg1.p1, Point.fromXY(-180.7, -1429.3))
    self.assertEqual(seg1.p2, Point.fromXY(-558.94, -1879.4))
    self.assertEqual(seg1.traceWidth, 30.0)

    arc = path.segments[2]
    self.assertEqual(arc.p1, Point.fromXY(-558.94, -1879.4))
    self.assertEqual(arc.p2, Point.fromXY(-300, -1400))
    self.assertEqual(arc.center, Point.fromXY(444, 333))
    self.assertEqual(arc.cw, True)
    

xml = """<?xml version="1.0" encoding="UTF-8" ?>
<design>
	<package_geometry>
		<ll>-2501.000000, -2501.000000</ll>
		<ur>2499.000000, 2499.000000</ur>
	</package_geometry>
	<die_geometries>
		<die_outline>
			<ll>-1910.000000, -1955.000000</ll>
			<ur>1910.000000, 1955.000000</ur>
		</die_outline>
	</die_geometries>
	<layers>
		<layer name="RDL" number="30"></layer>
		<layer name="VIA-1" number="10"></layer>
	</layers>
  <nets>
      <net name="P0_0">
        <branch>
          <pad layer="RDL" name="CU_PILLAR_80" position="-301.400000, -1688.400000" diameter="38.500000" />
          <pad layer="VIA-1" name="CU_PILLAR_80" position="-302.400000, -1788.400000" diameter="20.000000" />
          <shape layer="RDL">
            <segment start="-427.840000, -1815.310000" end="-558.940000, -1879.400000" />
            <segment start="-558.940000, -1879.400000" end="-558.940000, -1879.400000" />
            <arc start="-558.94, -1879.4" end="-300, -1400" center="444, 333" dir="CCW" />
          </shape>
          <path layer="RDL">
            <segment width="20.0" start="-301.200000, -1308.800000" end="-558.940000, -1879.400000" />
            <segment width="30.0" start="-180.700000, -1429.300000" end="-558.940000, -1879.400000" />
            <arc width = "40.0" start="-558.94, -1879.4" end="-300, -1400" center="444, 333" dir="CW" />
          </path>
        </branch>
        <branch>
        </branch>
      </net>
      <net name="P0_1">
        <branch>
        </branch>
      </net>
  </nets>
</design>
"""


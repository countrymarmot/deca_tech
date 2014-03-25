# test_DesignView.py
# Created by Craig Bishop on 18 July 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

import unittest
from pyrite.malachite.Design import DesignObject, Design, Package, Die
from pyrite.DesignView import DesignView, DesignObjectGraphicsItem,\
  PackageGraphicsItem, DieGraphicsItem
from pyrite.malachite.Geom import Point
import QAPP

class TestDesignView(unittest.TestCase):
  def setUp(self):
    self.app = QAPP.QT_APP
    self.designView = DesignView(None)

    # create a test design hierarchy
    self.design = Design()
    self.design.package.center = Point.fromXY(0, 0)
    self.design.package.width = 5000
    self.design.package.height = 5000

    die = Die()
    die.center = Point.fromXY(0, 0)
    die.width = 3000
    die.height = 3000
    self.design.package.dies.append(die)

    self.designView.setDesign(self.design)

  def testHasPackageItem(self):
    items = self.designView.scene().items()
    pkgitem = [item for item in items if isinstance(item, PackageGraphicsItem)]
    self.assertEqual(len(pkgitem), 1,
        "No package graphics item in the QScene for Design View")

  def testHasDieItem(self):
    items = self.designView.scene().items()
    pkgitem = [item for item in items if isinstance(item, DieGraphicsItem)]
    self.assertEqual(len(pkgitem), 1,
        "No die graphics item in the QScene for Design View")


class TestDesignObjectGraphicsItemSingularity(unittest.TestCase):
  def setUp(self):
    self.do1 = DesignObject("TEST")

  def testReturnsValidItems(self):
    gItem1 = DesignObjectGraphicsItem.graphicsItemForDesignObject(self.do1)
    self.assertIsNotNone(gItem1)

  def testSingularity(self):
    gItem1 = DesignObjectGraphicsItem.graphicsItemForDesignObject(self.do1)
    gItem2 = DesignObjectGraphicsItem.graphicsItemForDesignObject(self.do1)
    self.assertEqual(gItem1, gItem2)


class TestDesignObjectGraphicsItemFactory(unittest.TestCase):
  def testPackage(self):
    do = Package()
    gitem = DesignObjectGraphicsItem.graphicsItemForDesignObject(do)
    self.assertIsInstance(gitem, PackageGraphicsItem)

  def testDie(self):
    do = Die()
    gitem = DesignObjectGraphicsItem.graphicsItemForDesignObject(do)
    self.assertIsInstance(gitem, DieGraphicsItem)


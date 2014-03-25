# test_DesignProxy.py
# Created by Craig Bishop on 19 July 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

import unittest
from pyrite.malachite import DesignObject
from pyrite.ObjectProxy import ObjectProxy, CallbackProxy

class TestSubObject:
  def __init__(self):
    self.thing = 11


class TestDO(DesignObject):
  def __init__(self):
    DesignObject.__init__(self, "TEST")
    self.a = 2
    self.b = "HI"
    self.c = TestSubObject()
    self.d = [1, 2]
    self.e = DesignObject("SUBTEST")
    self.f = [DesignObject("LSTI"), DesignObject("LISTI")]

  def retSomething(self):
    return [1, 2, 3]


class TestDesignObjectProxyAttributes(unittest.TestCase):
  def setUp(self):
    self.do = TestDO()
    self.proxy = ObjectProxy.proxyForObject(self.do)

  def testAttributes(self):
    self.proxy.a = 3
    self.proxy.b = "HELLO"
    self.assertEqual(self.do.a, 3)
    self.assertEqual(self.do.b, "HELLO")


class TestDesignObjectProxyAttributeNotification(unittest.TestCase):
  def setUp(self):
    self.do = TestDO()
    self.proxy = ObjectProxy.proxyForObject(self.do)
    self.calledA = False
    self.calledB = False

  def callbackA(self, obj, attr):
    self.calledA = True

  def callbackB(self, obj, attr):
    self.calledB = True

  def testNormalAttributeNotification(self):
    self.proxy.addObserver(self.callbackA, attr='a')
    self.proxy.addObserver(self.callbackB, attr='b')
    self.proxy.a = 3
    self.proxy.b = "HELLO"
    self.assertEqual(self.proxy.a, 3)
    self.assertEqual(self.proxy.b, "HELLO")
    self.assertTrue(self.calledA)
    self.assertTrue(self.calledB)


class TestDesignObjectProxySingularity(unittest.TestCase):
  def setUp(self):
    self.do = TestDO()
    self.called1 = False
    self.called2 = False

  def testSingularity(self):
    proxy1 = ObjectProxy.proxyForObject(self.do)
    proxy2 = ObjectProxy.proxyForObject(self.do)
    self.assertEqual(proxy1, proxy2)

  def callback1(self, obj, attr):
    self.called1 = True

  def callback2(self, obj, attr):
    self.called2 = True

  def testSingularNotification(self):
    proxy1 = ObjectProxy.proxyForObject(self.do)
    proxy2 = ObjectProxy.proxyForObject(self.do)
    proxy1.addObserver(self.callback1)
    proxy2.addObserver(self.callback2)

    proxy2.a = 4
 
    self.assertEqual(proxy1.a, 4)
    self.assertEqual(proxy2.a, 4)
    self.assertTrue(self.called1)
    self.assertTrue(self.called2)


class TestDesignObjectProxySubObjectNotification(unittest.TestCase):
  def setUp(self):
    self.do = TestDO()
    self.proxy = ObjectProxy.proxyForObject(self.do)
    self.called = False

  def callback(self, obj, attr):
    self.called = True

  def testSubObjectNotification(self):
    self.proxy.addObserver(self.callback, attr='c')
    self.proxy.c.thing = 12
    self.assertEqual(self.do.c.thing, 12)
    self.assertTrue(self.called)

  def testSubListNotification(self):
    self.proxy.addObserver(self.callback, attr='d')
    self.proxy.d.append(3)
    self.assertEqual(len(self.do.d), 3)
    self.assertTrue(self.called)


class TestDesignObjectSubDesignObjects(unittest.TestCase):
  def setUp(self):
    self.do = TestDO()
    self.proxy = ObjectProxy.proxyForObject(self.do)

  def testDOSubDOAttribute(self):
    self.assertIsInstance(self.proxy.e, ObjectProxy)

  def testDOSubList(self):
    for do in self.proxy.f:
      self.assertIsInstance(do, ObjectProxy)


class TestCallbackProxyReturnValues(unittest.TestCase):
  def setUp(self):
    self.obj = TestDO()
    self.callbackProxy = CallbackProxy(self.obj.retSomething)

  def testReturnValue(self):
    ret = self.callbackProxy()
    self.assertEqual(len(ret), 3)
    self.assertEqual(ret[0], 1)
    self.assertEqual(ret[1], 2)
    self.assertEqual(ret[2], 3)


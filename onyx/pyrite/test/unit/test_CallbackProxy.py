# test_CallbackProxy.py
# Created by Craig Bishop on 19 July 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

import unittest
from pyrite.ObjectProxy import CallbackProxy

class TestObject:
  def __init__(self):
    self.a = 12


class TestCallbackProxyAttributes(unittest.TestCase):
  def setUp(self):
    self.obj = TestObject()
    self.proxy = CallbackProxy(self.obj)

  def testAttribute(self):
    self.proxy.a = 13
    self.assertEqual(self.obj.a, 13)
    self.assertEqual(self.proxy.a, 13)


class TestCallbackProxyNotification(unittest.TestCase):
  def setUp(self):
    self.obj = TestObject()
    self.proxy = CallbackProxy(self.obj, self.callback)
    self.called = False

  def callback(self, obj, attr):
    self.called = True

  def testNotification(self):
    self.proxy.a = 13
    self.assertTrue(self.called)


class TestCallbackProxyDictionary(unittest.TestCase):
  def setUp(self):
    self.obj = {'a': 3}
    self.proxy = CallbackProxy(self.obj, self.callback)
    self.called = False

  def callback(self, obj, attr):
    self.called = True

  def testDictNotification(self):
   self.proxy['a'] = 4
   self.assertEqual(self.obj['a'], 4)
   self.assertTrue(self.called)


class TestCallbackProxyList(unittest.TestCase):
  def setUp(self):
    self.obj = [1, 2]
    self.proxy = CallbackProxy(self.obj, self.callback)
    self.called = False

  def callback(self, obj, attr):
    self.called = True

  def testAppendNotification(self):
    self.proxy.append(3)
    self.assertTrue(self.called)

  def testDelNotification(self):
    del(self.proxy[0])
    self.assertTrue(self.called)


class TestCallbackProxyCallable(unittest.TestCase):
  def setUp(self):
    self.proxy = CallbackProxy(self.callable, self.callback)
    self.notified = False
    self.called = False
    self.msg = None

  def callable(self, msg):
    self.called = True
    self.msg = msg

  def callback(self, obj, attr):
    self.notified = True

  def testNotification(self):
    self.proxy("HI")
    self.assertTrue(self.called)
    self.assertTrue(self.notified)
    self.assertEqual(self.msg, "HI")


class TestSubObject:
  def __init__(self):
    self.thing = 110
    self.dict = {'a': 3}
    self.lst = [1, 2]

class TestTopObject:
  def __init__(self):
    self.sub = TestSubObject()


class TestCallbackProxySubObjectAttrNotification(unittest.TestCase):
  def setUp(self):
    self.obj = TestTopObject()
    self.proxy = CallbackProxy(self.obj, self.callback)
    self.called = False

  def callback(self, obj, attr):
    self.called = True

  def testNotification(self):
    self.proxy.sub.thing = 130
    self.assertEqual(self.proxy.sub.thing, 130)
    self.assertTrue(self.called)

  def testDictNotification(self):
    self.proxy.sub.dict['a'] = 1
    self.assertEqual(self.proxy.sub.dict['a'], 1)
    self.assertTrue(self.called)

  def testSubListAppendNotification(self):
    self.proxy.sub.lst.append(3)
    self.assertEqual(len(self.proxy.sub.lst), 3)
    self.assertTrue(self.called)

  def testSubListDelNotification(self):
    del(self.proxy.sub.lst[0])
    self.assertEqual(len(self.proxy.sub.lst), 1)
    self.assertTrue(self.called)


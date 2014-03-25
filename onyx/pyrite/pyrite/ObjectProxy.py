# ObjectProxy.py
# Created by Craig Bishop on 18 July 2012
#
# pyrite
# Copyright 2012 All Rights Reserved
#

import weakref
from malachite import DesignObject

class ObjectProxy:
  _proxies = {}

  @classmethod
  def proxyForObject(cls, obj):
    wkr = weakref.ref(obj)
    if wkr in cls._proxies:
      return cls._proxies[wkr]()
    else:
      proxy = ObjectProxy(obj)
      cls._proxies[wkr] = weakref.ref(proxy)
      return proxy

  def __init__(self, dobj):
    self._obj = dobj
    self._observers = []

  def addObserver(self, callback, attr=None):
    obs = { 'callback': callback,
            'attr': attr }
    self._observers.append(obs)

  def removeObserver(self, callback):
    obs = [ob for ob in self._observers if ob['callback'] == callback]
    for o in obs:
      self._observers.remove(o)

  def notifyObservers(self, obj, attr):
    obs = [o for o in self._observers if o['attr'] == attr or o['attr'] is None]
    for o in obs:
      try:
        o['callback'](self, attr)
      except:
        pass

  def __getattr__(self, name):
    if hasattr(self._obj, name):
      attr = getattr(self._obj, name)
      if isinstance(attr, DesignObject):
        return self.proxyForObject(attr)
      elif type(attr) in [list, dict] or hasattr(attr, '__dict__')\
        or hasattr(attr, '__call__'):
        return CallbackProxy(attr, callback=self.notifyObservers, name=name)
      else:
        return attr
    else:
      return self.__dict__.get(name)

  def __setattr__(self, name, value):
    if hasattr(self, '_obj'):
      if hasattr(self._obj, name):
        setattr(self._obj, name, value)
        self.notifyObservers(self, name)
        return
    self.__dict__[name] = value

  def __del__(self):
    wkr = weakref.ref(self._obj)
    if wkr in self._proxies:
      del(self._proxies[wkr])

  def __eq__(self, other):
    return self._obj == other._obj

  def __repr__(self):
    return str(self._obj)

  def __str__(self):
    return str(self._obj)


class CallbackProxy:
  def __init__(self, obj, callback=None, name=None):
    self._obj = obj
    self._callback = callback
    self._name = name

  def notify(self, obj, attr):
    if self._callback:
      self._callback(self, self._name)

  def __getattr__(self, name):
    if hasattr(self._obj, name):
      attr = getattr(self._obj, name)
      if isinstance(attr, DesignObject):
        return ObjectProxy.proxyForObject(attr)
      elif type(attr) in [list, dict] or hasattr(attr, '__dict__')\
        or hasattr(attr, '__call__'):
        return CallbackProxy(attr, callback=self.notify)
      else:
        return attr
    else:
      return self.__dict__.get(name)

  def __setattr__(self, name, value):
    if hasattr(self, '_obj'):
      if hasattr(self._obj, name):
        setattr(self._obj, name, value)
        self.notify(self, name)
        return
    self.__dict__[name] = value

  def __getitem__(self, name):
    return self._obj.__getitem__(name)

  def __setitem__(self, name, value):
    self._obj.__setitem__(name, value)
    self.notify(self, '__setitem__')

  def __delitem__(self, name):
    self._obj.__delitem__(name)
    self.notify(self, '__delitem__')

  def __call__(self, *args, **kwargs):
    ret = self._obj.__call__(*args, **kwargs)
    self.notify(self, '__call__')
    return ret

  def __len__(self):
    if hasattr(self._obj, '__len__'):
      return self._obj.__len__()
    else:
      return None

  def __iter__(self):
    for o in self._obj:
      if isinstance(o, DesignObject):
        yield ObjectProxy.proxyForObject(o)
      elif type(o) in [list, dict] or hasattr(o, '__dict__')\
        or hasattr(o, '__call__'):
        yield CallbackProxy(o, callback=self.notify)
      else:
        yield o     

  def __repr__(self):
    return str(self._obj)


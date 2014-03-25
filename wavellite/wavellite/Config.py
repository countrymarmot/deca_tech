# Config.py
# Created by Craig Bishop on 01 August 2011
#
# Wavellite
# Copyright 2011 All Rights Reserved
#

import cPickle as pickle
import os


def getDocDir():
  return os.getenv("USERPROFILE") or os.getenv("HOME") + os.sep


def getConfig():
  defconfiguration = {"DefaultDesignDir": "C:\\",
      "DefaultCadenceUnitTemplateDir": "C:\\",
      "TempFileDir": "C:\\", "DefaultAutocadUnitTemplateDir": "C:\\",
      "DefaultChecklistUnitTemplateDir": "C:\\",
      "DefaultArtParamsUnitTemplateDir": "C:\\",
      "DefaultCadenceWaferTemplateDir": "C:\\",
      "DefaultChecklistWaferTemplateDir": "C:\\",
      "DefaultAutocadWaferTemplateDir": "C:\\",
      "DefaultCadenceStreamOutDir": "C:\\",
      "DefaultUnitCreateScriptDir": "C:\\",
      "DefaultClipScriptDir": "C:\\",
      "DefaultKnockoutScriptDir": "C:\\",
      "DefaultFltScriptDir": "C:\\",
      "DefaultUnitZipTemplateDir": "C:\\",
      "DefaultWaferZipTemplateDir": "C:\\"}

  try:
    cf = open(getDocDir() + os.sep + "wave_config.wavellite", "r")
  except IOError:
    print("Using default configuration.")
    return defconfiguration

  print("Doc Dir: " + getDocDir())
  configuration = pickle.load(cf)
  cf.close()

  for k in defconfiguration:
    if not k in configuration:
      configuration[k] = defconfiguration[k]

  return configuration


def saveConfig(conf):
  print("Doc Dir: " + getDocDir())
  cf = open(getDocDir() + os.sep + "wave_config.wavellite", "wb")
  pickle.dump(conf, cf)
  cf.close()

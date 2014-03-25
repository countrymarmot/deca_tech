# WorkingDir.py
# Created by Craig Bishop on 02 August 2011
#
# Wavellite
# Copyright 2011 All Rights Reserved
#

import os
import cPickle as pickle


class WorkingDir:
  def __init__(self, fileDir):
    self.fileDir = fileDir

    if (os.path.exists(self.fileDir) is False):
      return

    dfilename = ""
    for root, dirs, files in os.walk(self.fileDir):
      for filename in files:
        if (".wavellite" in filename):
          dfilename = filename

    if len(dfilename) <= 0:
      self.exists = False
      return

    # load the info out of it
    df = open(self.fileDir + os.sep + dfilename, "r")
    self.device = pickle.load(df)
    df.close()
    self.exists = True

  def createOnFileSystem(self, deviceName):
    deviceFile = {"Name": deviceName, "PLM_Nums": {}}

    if not os.path.exists(self.fileDir):
      os.mkdir(self.fileDir)

    for root, dirs, files in os.walk(self.fileDir):
      for dirName in dirs:
        if ("wafer" in dirName or "unit" in dirName or "stencil" in dirName):
          endNum = dirName.find("_")
          endNum = dirName.find("_", endNum)
          plmNum = dirName[:endNum]
          deviceFile["PLM_Nums"][dirName] = plmNum

    df = open(self.fileDir + os.sep + deviceName + ".wavellite", "wb")
    pickle.dump(deviceFile, df)
    df.close()

    self.device = deviceFile
    self.exists = True

  def save(self):
    df = open(self.fileDir + os.sep + self.device["Name"] + ".wavellite", "wb")
    pickle.dump(self.device, df)
    df.close()

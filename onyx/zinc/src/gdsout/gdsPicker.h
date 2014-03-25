//
// gdsPicker.h
// Archerite
//
// Created by Craig Bishop on 18 August 2011
// Copyright 2011 All rights reserved
//

#ifndef GDS_PICKER_H
#define GDS_PICKER_H

#include "gdsii/builder.h"
#include "gdsii/creator.h"
#include <string>

using namespace Gdsii;

class gdsPicker : public GdsBuilder
{
public:
  virtual void  setLocator (const GdsLocator* locator);
  virtual void  gdsVersion (int version);

  virtual void  beginLibrary (const char* libName,
        const GdsDate& modTime,
        const GdsDate& accTime,
        const GdsUnits& units,
        const GdsLibraryOptions& options);
  virtual void  endLibrary();

  virtual void  beginStructure (const char* structureName,
            const GdsDate& createTime,
            const GdsDate& modTime,
            const GdsStructureOptions& options);
  virtual void  endStructure();


  virtual void  beginBoundary (int layer, int datatype,
           const GdsPointList& points,
           const GdsElementOptions& options);

  virtual void  beginPath (int layer, int datatype,
             const GdsPointList& points,
             const GdsPathOptions& options);

  virtual void  beginSref (const char* sname,
             int x, int y,
             const GdsTransform& strans,
             const GdsElementOptions& options);

  virtual void  beginAref (const char* sname,
             Uint numCols, Uint numRows,
             const GdsPointList& points,
             const GdsTransform& strans,
             const GdsElementOptions& options);

  virtual void  beginNode (int layer, int nodetype,
             const GdsPointList& points,
             const GdsElementOptions& options);

  virtual void  beginBox (int layer, int boxtype,
            const GdsPointList& points,
            const GdsElementOptions& options);

  virtual void  beginText (int layer, int texttype,
             int x, int y,
             const char* text,
             const GdsTransform& strans,
             const GdsTextOptions& options);

  virtual void  addProperty (int attr, const char* value);

  virtual void  endElement();

  GdsCreator* creator;
  GdsDate modTime, accTime;
  std::string replace;
};

#endif


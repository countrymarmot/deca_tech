//
// gdsPicker.cpp
// Archerite
//
// Created by Craig Bishop on 18 August 2011
// Copyright 2011 All rights reserved
//

#include "gdsPicker.h"

void gdsPicker::setLocator(const GdsLocator* locator)
{
}

void gdsPicker::gdsVersion(int version)
{
}

void gdsPicker::beginLibrary(const char* libName,
			const GdsDate& modTime,
			const GdsDate& accTime,
			const GdsUnits& units,
			const GdsLibraryOptions& options)
{
}

void gdsPicker::endLibrary()
{
}

void gdsPicker::beginStructure(const char* structureName,
			  const GdsDate& createTime,
			  const GdsDate& modTime,
			  const GdsStructureOptions& options)
{
	char* stName = (char*)structureName;
	if (strcmp(structureName, "TOP") == 0)
  {
		stName = (char*)replace.c_str();
  }


	creator->beginStructure(stName, modTime, accTime,
				GdsStructureOptions());
}

void gdsPicker::endStructure()
{
	creator->endStructure();
}


void gdsPicker::beginBoundary(int layer, int datatype,
			 const GdsPointList& points,
			 const GdsElementOptions& options)
{
	creator->beginBoundary(layer, datatype,
				points,
				options);
}

void gdsPicker::beginPath(int layer, int datatype,
		     const GdsPointList& points,
		     const GdsPathOptions& options)
{
	creator->beginPath(layer, datatype,
				points,
				options);
}

void gdsPicker::beginSref(const char* sname,
		     int x, int y,
		     const GdsTransform& strans,
		     const GdsElementOptions& options)
{
	creator->beginSref(sname, x, y,
				strans,
				options);
}

void gdsPicker::beginAref(const char* sname,
		     Uint numCols, Uint numRows,
		     const GdsPointList& points,
		     const GdsTransform& strans,
		     const GdsElementOptions& options)
{
	creator->beginAref(sname, numCols, numRows,
				points, strans,
				options);
}

void gdsPicker::beginNode(int layer, int nodetype,
		     const GdsPointList& points,
		     const GdsElementOptions& options)
{
	creator->beginNode(layer, nodetype,
				points, options);
}

void gdsPicker::beginBox(int layer, int boxtype,
		    const GdsPointList& points,
		    const GdsElementOptions& options)
{
	creator->beginBox(layer, boxtype, points, options);
}

void gdsPicker::beginText(int layer, int texttype,
		     int x, int y,
		     const char* text,
		     const GdsTransform& strans,
		     const GdsTextOptions& options)
{
	creator->beginText(layer, texttype, x, y, text, strans, options);
}

void gdsPicker::addProperty(int attr, const char* value)
{
	creator->addProperty(attr, value);
}

void gdsPicker::endElement()
{
	creator->endElement();
}


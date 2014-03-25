//
// gds_output_stage.cpp
// zinc
//
// Created by Craig Bishop on 01 January 2013
// Copyright 2013 All rights reserved
//

#include "gds_output_stage.h"
#include "gdsii/creator.h"
#include "misc/utils.h"
#include "gdsii/parser.h"
#include "gdsPicker.h"
#include <time.h>
#include <stdio.h>
#include <vector>
#include <zlib.h>

using namespace Gdsii;

static const int kReferenceDieOffset = 100;
static const double kDegPerRad = 57.2957795f;

/*
 * Writes debug shift text to GDS for each unit
 *
 * @param shifts zinc::Shifts message with all shifts
 * @param gdsfile Initialized GdsCreator with a structure started
 * @param debugLayer Layer number to draw debug info on
 */
void writeDebugInfos(const zinc::Shifts& shifts, GdsCreator& gdsfile,
    int debugLayer)
{
  for (int unitIndex = 0; unitIndex < shifts.units_size(); unitIndex++)
  {
    for (int dieIndex = 0; dieIndex < shifts.units(unitIndex).die_size(); dieIndex++)
    {
      const zinc::DieShift& die = shifts.units(unitIndex).die(dieIndex);
      char buf[200];
      sprintf(buf, "%.1f, %.1f, %.3fdeg.\n", die.shift().x(),
          die.shift().y(), die.theta());
      float x = die.nominalxy().x() + shifts.globaloffset().x();
      float y = die.nominalxy().y() + shifts.globaloffset().y();
      gdsfile.beginText(debugLayer, 0, x * 1000, y * 1000, buf,
          GdsTransform(), GdsTextOptions());
      gdsfile.endElement();
    }
  }
}

bool DecompressGDSFromDataToFile(const char* data, const size_t dataSize,
    const size_t uncompressed_size, FILE* fp)
{
  char* uncompressed = new char[uncompressed_size];
  size_t out_len = uncompressed_size;
  int result = uncompress((Bytef*)uncompressed, (uLongf*)&out_len,
      (const Bytef*)data, dataSize);
  if (result != Z_OK)
  {
    delete[] uncompressed;
    return false;
  }
  fwrite(uncompressed, 1, out_len, fp);
  delete[] uncompressed;
  return true;
}

/*
 * Imports a "TOP" structure from another GDS file into the current one
 * and renames the TOP structure to struct_name; used for embedding the
 * prestratums and GDS templates for Srefs
 *
 * @param struct_name Name to assign imported TOP structure
 * @param gdsFile GdsCreator object to write structure to
 * @param gdsdata Raw bytes of GDS file to import
 * @return true on success, false on failure
 */
bool importGDSStructureFromData(std::string struct_name, GdsCreator& gdsFile,
    std::string gdsdata, size_t uncompressedSize)
{
    //write prestratum to temp file
    char tmpFile[512];
    tmpnam(tmpFile);
    FILE* fp = fopen(tmpFile, "wb");
    if (!DecompressGDSFromDataToFile(gdsdata.c_str(), gdsdata.size(),
          uncompressedSize, fp))
    {
      fclose(fp);
      return false;
    }
    fwrite(gdsdata.c_str(), 1, gdsdata.size(), fp);
    fclose(fp);

    // parse it into the current GDS structure
    GdsParser parser(tmpFile, FileHandle::FileTypeAuto);
    gdsPicker picker;
    picker.creator = &gdsFile;
    time_t now = time(NULL);
    picker.modTime.setTime(now);
    picker.accTime.setTime(now);
    picker.replace = struct_name;
    parser.parseFile(&picker);
    return true;
}

/// Contains names of GDS structures for a DieLayer
struct DieStructureNames
{
  std::vector<std::string> fixedPrestratums;
  std::vector<std::string> shiftedPrestratums;
};

/// Contains names of GDS structures for a Layer
struct LayerStructureNames
{
  std::vector<std::string> fixedPrestratums;
  std::string outOfspecPrestratum;
  std::string dummyPrestratum;
  std::vector<std::string> gdsTemplates;
  std::map<int, DieStructureNames> dieStructures;
};

/*
 * Generates structure names for importing GDS structures for a DieLayer
 *
 * @param layerName Name of layer of dieLayer
 * @param dieIndex Integer index of the Die which dieLayer is from
 * @param structureNames Reference to structure to fill
 */
void generateStructureNamesForDieLayer(std::string layerName, int dieIndex,
    const zinc::DieLayer& dieLayer, DieStructureNames& structureNames)
{
  char struct_name[1024];
  // fixed prestratums
  for (int i = 0; i < dieLayer.fixedprestratums_size(); i++)
  {
    sprintf(struct_name, "%s_D_%i_PRSTM_FIX_%i", layerName.c_str(),
        dieIndex, i + 1);
    structureNames.fixedPrestratums.push_back(std::string(struct_name));
  }

  // shifted prestratums
  for (int i = 0; i < dieLayer.shiftedprestratums_size(); i++)
  {
    sprintf(struct_name, "%s_D_%i_PRSTM_SFT_%i", layerName.c_str(),
        dieIndex, i + 1);
    structureNames.shiftedPrestratums.push_back(std::string(struct_name));
  }
}

/*
 * Generates structure names for importing GDS structures for a Layer
 *
 * @param layer zinc::Layer to generate structure names for
 * @param design zinc::Design message object
 * @param structureNames Reference to a structure to fill
 */
void generateStructureNamesForLayer(const zinc::Layer& layer, const zinc::Design& design,
    LayerStructureNames& structureNames)
{
  char struct_name[1024];
  //fixed prestratums for layer
  for (int i = 0; i < layer.fixedprestratums_size(); i++)
  {
    sprintf(struct_name, "%s_PKG_PRSTM_FIX_%i", layer.name().c_str(), i + 1);
    structureNames.fixedPrestratums.push_back(std::string(struct_name));
  }

  // out of spec prestratum for layer
  if (layer.has_outofspecprestratum())
  {
    sprintf(struct_name, "%s_PKG_OOS", layer.name().c_str());
    structureNames.outOfspecPrestratum = std::string(struct_name);
  }

  // dummy prestratum
  if (layer.has_dummyprestratum())
  {
    sprintf(struct_name, "%s_PKG_DUMMY", layer.name().c_str());
    structureNames.dummyPrestratum = std::string(struct_name);
  }

  // GDS templates
  for (int i = 0; i < layer.gdstemplates_size(); i++)
  {
    sprintf(struct_name, "%s_TPLT_%i", layer.name().c_str(), i + 1);
    structureNames.gdsTemplates.push_back(std::string(struct_name));
  }

  // Find and generate names for DieLayer structures
  for (int dieIndex = 0; dieIndex < design.unitdie_size(); dieIndex++)
  {
    for (int dieLayerIndex = 0; dieLayerIndex < design.unitdie(dieIndex).dielayers_size();
        dieLayerIndex++)
    {
      const zinc::DieLayer& dieLayer = design.unitdie(dieIndex).dielayers(dieLayerIndex);
      if (dieLayer.number() == layer.number())
      {
        DieStructureNames dieStructureNames;
        generateStructureNamesForDieLayer(layer.name(), dieIndex, dieLayer,
            dieStructureNames);
        structureNames.dieStructures[dieIndex] = dieStructureNames;
      }
    }
  }

  // Find and generate names for the reference DieLayer structures
  for (int dieIndex = 0; dieIndex < design.referencedie_size(); dieIndex++)
  {
    for (int dieLayerIndex = 0; dieLayerIndex < design.referencedie(dieIndex).dielayers_size();
        dieLayerIndex++)
    {
      const zinc::DieLayer& dieLayer = design.referencedie(dieIndex).dielayers(dieLayerIndex);
      if (dieLayer.number() == layer.number())
      {
        DieStructureNames dieStructureNames;
        generateStructureNamesForDieLayer(layer.name(), dieIndex + kReferenceDieOffset, dieLayer,
            dieStructureNames);
        structureNames.dieStructures[dieIndex + kReferenceDieOffset] = dieStructureNames;
      }
    }
  }
}

/*
 * Imports all GDS structures needed for each die into the output GDS file
 *
 * @param layer Layer to import structures for
 * @param dieLayer DieLayer to import structures from
 * @param gdsFile GdsCreator object to import structures into
 * @param structureNames DieStructureNames to use for renaming imported structures
 */
bool importStructuresForDie(const zinc::Layer& layer, const zinc::DieLayer& dieLayer,
    GdsCreator& gdsFile, const DieStructureNames& structureNames)
{
  // fixed prestratums
  for (int i = 0; i < dieLayer.fixedprestratums_size(); i++)
  {
    if (!importGDSStructureFromData(structureNames.fixedPrestratums[i], gdsFile,
        dieLayer.fixedprestratums(i).gdsdata(),
        dieLayer.fixedprestratums(i).uncompressedsize()))
      return false;
  }

  // shifted prestratums
  for (int i = 0; i < dieLayer.shiftedprestratums_size(); i++)
  {
    if (!importGDSStructureFromData(structureNames.shiftedPrestratums[i], gdsFile,
        dieLayer.shiftedprestratums(i).gdsdata(),
        dieLayer.shiftedprestratums(i).uncompressedsize()))
      return false;
  }
  return true;
}

/*
 * Imports all GDS structures needed for a layer into the output GDS file
 *
 * @param layer Layer to import structures for
 * @param design zinc::Design message object
 * @param gdsFile GdsCreator object to import structures into
 * @param structureNames LayerStructureNames to use for renaming imported structures
 */
bool importStructuresForLayer(const zinc::Layer& layer, const zinc::Design& design,
    GdsCreator& gdsFile, const LayerStructureNames& structureNames)
{
  // fixed prestratum for layer
  for (int i = 0; i < layer.fixedprestratums_size(); i++)
  {
    if (!importGDSStructureFromData(structureNames.fixedPrestratums[i], gdsFile,
        layer.fixedprestratums(i).gdsdata(),
        layer.fixedprestratums(i).uncompressedsize()))
      return false;
  }

  // out of spec prestratum for layer
  if (layer.has_outofspecprestratum())
  {
    if (!importGDSStructureFromData(structureNames.outOfspecPrestratum, gdsFile,
        layer.outofspecprestratum().gdsdata(),
        layer.outofspecprestratum().uncompressedsize()))
      return false;
  }

  // dummy prestratum
  if (layer.has_dummyprestratum())
  {
    if (!importGDSStructureFromData(structureNames.dummyPrestratum, gdsFile,
        layer.dummyprestratum().gdsdata(),
        layer.dummyprestratum().uncompressedsize()))
      return false;
  }

  // GDS templates
  for (int i = 0; i < layer.gdstemplates_size(); i++)
  {
    if (!importGDSStructureFromData(structureNames.gdsTemplates[i], gdsFile,
        layer.gdstemplates(i).gdsdata(),
        layer.gdstemplates(i).uncompressedsize()))
      return false;
  }

  // live die
  for (int dieIndex = 0; dieIndex < design.unitdie_size(); dieIndex++)
  {
    const zinc::Die& die = design.unitdie(dieIndex);
    for (int layerIndex = 0; layerIndex < die.dielayers_size(); layerIndex++)
    {
      const zinc::DieLayer& dieLayer = die.dielayers(layerIndex);
      if (dieLayer.number() == layer.number())
      {
        const DieStructureNames& dieStructureNames =
          structureNames.dieStructures.at(dieIndex);
        if (!importStructuresForDie(layer, dieLayer, gdsFile, dieStructureNames))
          return false;
      }
    }
  }

  // reference die
  for (int dieIndex = 0; dieIndex < design.referencedie_size(); dieIndex++)
  {
    const zinc::Die& die = design.referencedie(dieIndex);
    for (int layerIndex = 0; layerIndex < die.dielayers_size(); layerIndex++)
    {
      const zinc::DieLayer& dieLayer = die.dielayers(layerIndex);
      if (dieLayer.number() == layer.number())
      {
        const DieStructureNames& dieStructureNames =
          structureNames.dieStructures.at(dieIndex + kReferenceDieOffset);
        if (!importStructuresForDie(layer, dieLayer, gdsFile, dieStructureNames))
          return false;
      }
    }
  }

  return true;
}

/*
 * Writes the prestratums for a single die in a single unit to the output GDS file
 *
 * @param dieLayer DieLayer to output prestratums for
 * @param shifts zinc::Shifts message with global offset info
 * @param gdsFile GdsCreator object to write Srefs to
 * @param dieShift DieShift object for this die
 * @param structureNames DieStructureNames for referencing imported structures
 */
void writeDiePrestratums(const zinc::DieLayer& dieLayer, const zinc::Shifts& shifts,
    GdsCreator& gdsFile, const zinc::DieShift& dieShift,
    const DieStructureNames& structureNames)
{
  float globalOffsetX = shifts.globaloffset().x();
  float globalOffsetY = shifts.globaloffset().y();

  for (int i = 0; i < dieLayer.fixedprestratums_size(); i++)
  {
    gdsFile.beginSref(structureNames.fixedPrestratums[i].c_str(),
              (dieShift.nominalxy().x() + globalOffsetX) * 1000.0,
              (dieShift.nominalxy().y() + globalOffsetY) * 1000.0,
              GdsTransform(), GdsElementOptions());
    gdsFile.endElement();
  }
  for (int i = 0; i < dieLayer.shiftedprestratums_size(); i++)
  {
    GdsTransform transform;
    transform.setStrans(false, false, false);
    transform.setAngle(dieShift.theta() * kDegPerRad);
    gdsFile.beginSref(structureNames.shiftedPrestratums[i].c_str(),
              (dieShift.nominalxy().x() + dieShift.shift().x() + globalOffsetX) * 1000.0,
              (dieShift.nominalxy().y() + dieShift.shift().y() + globalOffsetY) * 1000.0,
              transform, GdsElementOptions());
    gdsFile.endElement();
  }
}

/*
 * Writes the prestratums for a layer to the output GDS file
 *
 * @param design zinc::Design message
 * @param shifts zinc::Shifts message with all shifts for the panel
 * @param gdsfile GdsCreator object to write to
 * @param layer Layer to output to the GDS file
 * @param structureNames LayerStructureNames for referencing imported structures
 */
void writeLayerPrestratums(const zinc::Design& design, const zinc::Shifts& shifts,
    GdsCreator& gdsfile, const zinc::Layer& layer,
    const LayerStructureNames& structureNames)
{
  float globalOffsetX = shifts.globaloffset().x();
  float globalOffsetY = shifts.globaloffset().y();

  for (int unitIndex = 0; unitIndex < shifts.units_size(); unitIndex++)
  {
    for (int dieIndex = 0; dieIndex < shifts.units(unitIndex).die_size(); dieIndex++)
    {
      const zinc::Unit& unit = shifts.units(unitIndex);
      const zinc::DieShift& dieShift = unit.die(dieIndex);
      if (unit.inspec())
      {
        // write fixed prestratum srefs for each unit
        for (int i = 0; i < layer.fixedprestratums_size(); i++)
        {
          gdsfile.beginSref(structureNames.fixedPrestratums[i].c_str(),
              (unit.center().x() + globalOffsetX) * 1000.0,
              (unit.center().y() + globalOffsetY) * 1000.0,
              GdsTransform(), GdsElementOptions());
          gdsfile.endElement();
        }
      }
      else
      {
        if (layer.has_outofspecprestratum())
        {
          gdsfile.beginSref(structureNames.outOfspecPrestratum.c_str(),
                (unit.center().x() + globalOffsetX) * 1000.0,
                (unit.center().y() + globalOffsetY) * 1000.0,
                GdsTransform(), GdsElementOptions());
          gdsfile.endElement();
        }
      }

      const zinc::Die& die = design.unitdie(dieIndex);
      for (int dieLayerIndex = 0; dieLayerIndex < die.dielayers_size(); dieLayerIndex++)
      {
        const zinc::DieLayer& dieLayer = die.dielayers(dieLayerIndex);
        if (dieLayer.number() == layer.number() && unit.inspec())
        {
          const DieStructureNames& dieStructureNames =
            structureNames.dieStructures.at(dieIndex);
          writeDiePrestratums(dieLayer, shifts, gdsfile, dieShift,
              dieStructureNames);
        }
      }
    }
  }
}

/*
 * Writes GDS templates for a layer to the output GDS file
 *
 * @param design zinc::Design message
 * @param shifts zinc::Shifts message with all shifts for the panel
 * @param gdsfile GdsCreator object to write to
 * @param layer Layer to output into the GDS file
 * @param structureNames LayerStructureNames for referencing imported structures
 */
void writeTemplates(const zinc::Design& design, const zinc::Shifts& shifts,
    GdsCreator& gdsfile, const zinc::Layer& layer,
    const LayerStructureNames& structureNames)
{
  for (int i = 0; i < layer.gdstemplates_size(); i++)
  {
    const zinc::GDSTemplate& gdsTemplate = layer.gdstemplates(i);
    float x = 0, y = 0;
    if (gdsTemplate.hasglobaloffset())
    {
      x += shifts.globaloffset().x();
      y += shifts.globaloffset().y();
    }

    gdsfile.beginSref(structureNames.gdsTemplates[i].c_str(),
        x * 1000.0, y * 1000.0, GdsTransform(), GdsElementOptions());
    gdsfile.endElement();
  }
}

/*
 * Writes routes for a RoutedLayer to output GDS file
 *
 * @param routedLayer zinc::RoutedLayer to output
 * @param design zinc::Design message object
 * @param shifts zinc::Shifts message with shifts for entire panel
 * @param gdsFile GdsCreator object to output routes into
 * @param layer Layer to output routes onto
 * @param routedUnit zinc::RoutedUnit for which this RoutedLayer is part of
 */
void writeRoutesForRoutedLayer(const zinc::RoutedLayer& routedLayer, const zinc::Design& design,
    const zinc::Shifts& shifts, GdsCreator& gdsFile, const zinc::Layer& layer,
    const zinc::RoutedUnit& routedUnit)
{
  float globalOffsetX = shifts.globaloffset().x();
  float globalOffsetY = shifts.globaloffset().y();
  float packageX = routedUnit.unit().center().x();
  float packageY = routedUnit.unit().center().y();

  for (int i = 0; i < routedLayer.routes_size(); i++)
  {
    const zinc::Route& route = routedLayer.routes(i);
    int numPoints = route.points_size();
    if (numPoints <= 0)
      continue;
    GdsPathOptions pathOptions;
    pathOptions.setPathtype(PathtypeRound);
    pathOptions.setWidth(layer.routedefinitions(i).tracewidth() * 1000.0);
    GdsPointList routePoints;
    float x, y;
    for (int j = 0; j < numPoints; j++)
    {
      x = route.points(j).x() + packageX + globalOffsetX;
      y = route.points(j).y() + packageY + globalOffsetY;
      routePoints.addPoint(x * 1000.0, y * 1000.0);
    }
    gdsFile.beginPath(layer.number(), 20, routePoints, pathOptions);
    gdsFile.endElement();
  }
}

/*
 * Writes routes for a RoutedUnit to the output GDS file
 *
 * @param routedUnit zinc::RoutedUnit to output
 * @param design zinc::Design message object
 * @param shifts zinc::Shifts message with shifts for entire panel
 * @param gdsFile GdsCreator object to write output to
 * @param layer zinc::Layer to write routes onto
 */
void writeRoutesForUnit(const zinc::RoutedUnit& routedUnit, const zinc::Design& design,
    const zinc::Shifts& shifts, GdsCreator& gdsFile, const zinc::Layer& layer)
{
  for (int i = 0; i < routedUnit.routedlayers_size(); i++)
  {
    const zinc::RoutedLayer& routedLayer = routedUnit.routedlayers(i);
    if (routedLayer.layernumber() == layer.number())
      writeRoutesForRoutedLayer(routedLayer, design, shifts, gdsFile, layer, routedUnit);
  }
}

/*
 * Writes all routes for a layer to the output GDS file
 *
 * @param workItem zinc::CreateGDSWorkItem with RouteUnits
 * @param design zinc::Design message object
 * @param shifts zinc::Shifts message with shifts for entire panel
 * @param gdsFile GdsCreator object to output to
 * @param layer Layer to write routes onto
 */
void writeRoutesForLayer(const zinc::CreateGDSWorkItem& workItem, const zinc::Design& design,
    const zinc::Shifts& shifts, GdsCreator& gdsFile, const zinc::Layer& layer)
{
  for (int unitIndex = 0; unitIndex < workItem.routedunits_size(); unitIndex++)
  {
    const zinc::RoutedUnit& routedUnit = workItem.routedunits(unitIndex);
    if (routedUnit.routinggood())
    {
      writeRoutesForUnit(routedUnit, design, shifts, gdsFile, layer);
    }
  }
}

/*
 * Writes SRefs for reference die included in the shift data
 *
 * @param design zinc::Design message object
 * @param shifts zinc::Shifts message object with reference die measurements
 * @param gdsFile GdsCreator object to write the results into
 * @param layer zinc::Layer to output onto
 * @param structureNames Structure names for imported GDS files
 */
void writeReferenceDie(const zinc::Design& design, const zinc::Shifts& shifts,
    GdsCreator& gdsFile, const zinc::Layer& layer,
    const LayerStructureNames& structureNames)
{
  for (int unitIndex = 0; unitIndex < shifts.referenceunits_size(); unitIndex++)
  {
    const zinc::Unit& unit = shifts.referenceunits(unitIndex);
    const zinc::DieShift& dieShift = unit.die(0);
    const zinc::Die& die = design.referencedie(0);

    // find the die layer
    for (int dieLayerIndex = 0; dieLayerIndex < die.dielayers_size(); dieLayerIndex++)
    {
      const zinc::DieLayer& dieLayer = die.dielayers(dieLayerIndex);
      if (dieLayer.number() == layer.number() && unit.inspec())
      {
        const DieStructureNames& dieStructureNames =
          structureNames.dieStructures.at(0 + kReferenceDieOffset);
        writeDiePrestratums(dieLayer, shifts, gdsFile, dieShift,
            dieStructureNames);
      }
    }
  }
}

/*
 * Compresses gdsData and then writes the compressed data to gdsFile
 *
 * @param gdsData Pointer to raw GDS data bytes
 * @param dataSize Size of gdsData buffer
 * @param gdsFile zinc::File objects to write compressed data to
 * @return true on success, false on error
 */
bool compressOutputLayerIntoGdsFile(const char* gdsData, size_t dataSize,
    zinc::File& gdsFile)
{
  // zlib requires source size * 1.1 + 12 bytes
  size_t compressionBufferLen = dataSize + (dataSize * 0.1) + 12;
  char* compressionBuffer = new char[compressionBufferLen];
  int result = compress2((Bytef*)compressionBuffer, (uLongf*)&compressionBufferLen,
      (Bytef*)gdsData, dataSize, Z_BEST_COMPRESSION);
  if (result != Z_OK)
  {
    delete[] compressionBuffer;
    return false;
  }
  gdsFile.set_data((const void*)compressionBuffer, compressionBufferLen);
  gdsFile.set_uncompressedsize(dataSize);
  delete[] compressionBuffer;
  return true;
}

/*
 * Outputs specified layer to a zinc::File message object
 *
 * @param workItem zinc::CreateGDSWorkItem with design information
 *                 and routed units
 * @param layerIndex Index of layer to output in design.layers
 * @param gdsFile zinc::File message object to fill
 */
bool outputLayerGDS(const zinc::CreateGDSWorkItem& workItem,
    int layerIndex, zinc::File& gdsFile)
{
  const zinc::Layer& layer = workItem.design().layers(layerIndex);
  char tmpGDSFileName[512];
  tmpnam(tmpGDSFileName);
	GdsCreator gdsfile(tmpGDSFileName, FileHandle::FileTypeAuto);
	gdsfile.gdsVersion(0);
  GdsDate modTime, accTime;
	time_t now = time(NULL);
	modTime.setTime(now);
	accTime.setTime(now);
	GdsUnits units(1e-3, 1e-9);
	gdsfile.beginLibrary(layer.name().c_str(), modTime, accTime, units, GdsLibraryOptions());

  LayerStructureNames structureNames;
  generateStructureNamesForLayer(layer, workItem.design(), structureNames);

  gdsfile.beginStructure("TOP", modTime, accTime, GdsStructureOptions());
  writeLayerPrestratums(workItem.design(), workItem.shifts(), gdsfile,
      layer, structureNames);
  writeTemplates(workItem.design(), workItem.shifts(), gdsfile,
      layer, structureNames);
  writeRoutesForLayer(workItem, workItem.design(), workItem.shifts(), gdsfile, layer);
  writeReferenceDie(workItem.design(), workItem.shifts(), gdsfile, layer,
      structureNames);

  gdsfile.endStructure();

  if (!importStructuresForLayer(layer, workItem.design(), gdsfile, structureNames))
    return false;

	gdsfile.endLibrary();

  // read bytes from tmpfile into GDSFile message
  char filename[100];
  sprintf(filename, "%s_%i_%s.gds", layer.name().c_str(), layer.number(),
      workItem.shifts().panelid().c_str());
  gdsFile.set_filename(std::string(filename));
  FILE* fp = fopen(tmpGDSFileName, "rb");
  if (!fp)
    return false;
  // get file size
  fseek(fp, 0, SEEK_END);
  size_t gdsFileSize = ftell(fp);
  fseek(fp, 0, SEEK_SET);
  char* buffer = new char[gdsFileSize];
  fread(buffer, 1, gdsFileSize, fp);
  fclose(fp);

  if (!compressOutputLayerIntoGdsFile(buffer, gdsFileSize, gdsFile))
  {
    delete[] buffer;
    return false;
  }

  delete[] buffer;
  return true;
}

/*
 * Writes the absolute location of the reference die to a text file
 *
 * @param shifts zinc::Shifts message object
 * @param file zinc::File to write the data to
 * @return true on success, false on failure
 */
bool writeReferenceLocations(const zinc::Shifts& shifts,
    zinc::File& file)
{
  float globalOffsetX = shifts.globaloffset().x();
  float globalOffsetY = shifts.globaloffset().y();
  std::string contents("#\t\tX\t\tY\r\n");
  char buf[512];
  for (int i = 0; i < shifts.referenceunits_size(); i++)
  {
    const zinc::DieShift& dieShift = shifts.referenceunits(i).die(0);
    float x = dieShift.nominalxy().x() + dieShift.shift().x() + globalOffsetX;
    float y = dieShift.nominalxy().y() + dieShift.shift().y() + globalOffsetY;
    sprintf(buf, "%i\t\t%.2f\t\t%.2f\r\n", i + 1, x, y);
    contents = contents + std::string(buf);
  }
  sprintf(buf, "FIDUCIALS_%s.txt", shifts.panelid().c_str());
  file.set_filename(buf);
  if (!compressOutputLayerIntoGdsFile(contents.c_str(), contents.size(), file))
    return false;
  return true;
}

bool gds_output_stage(const zinc::CreateGDSWorkItem& workItem,
    zinc::CreateGDSWorkResults* workResults, bool verbose)

{
  workResults->set_panelid(workItem.panelid());

  int numLayers = workItem.design().layers_size();
  for (int layerIndex = 0; layerIndex < numLayers; layerIndex++)
  {
    const zinc::Layer& layer = workItem.design().layers(layerIndex);
    if (verbose)
      printf("Outputing layer %s:%i\n", layer.name().c_str(), layer.number());
    zinc::File* file = workResults->add_files();
    if (!outputLayerGDS(workItem, layerIndex, *file))
      return false;
  }

  // write the text file with reference die coordinates
  zinc::File* coordFile = workResults->add_files();
  writeReferenceLocations(workItem.shifts(), *coordFile);

  workResults->set_panelid(workItem.shifts().panelid());
  return true;
}


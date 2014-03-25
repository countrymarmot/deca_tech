# PLMExport.py
# Created by Craig Bishop on 04 January 2012
#
# Wavellite
# Copyright 2012 All Rights Reserved
#

import xlrd
import xlutils.copy


def _getOutCell(outSheet, rowIndex, colIndex):
  row = outSheet._Worksheet__rows.get(rowIndex)
  if not row:
    return None
  cell = row._Row__cells.get(colIndex)
  return cell


def _writeOutCell(outSheet, rowIndex, colIndex, val):
  prevCell = _getOutCell(outSheet, rowIndex, colIndex)
  outSheet.write(rowIndex, colIndex, val)
  newCell = _getOutCell(outSheet, rowIndex, colIndex)
  newCell.xf_idx = prevCell.xf_idx


def exportXLS(designAttributes, mappingFilename, tplFilename, outputFilename):
  # load all the mappings in first
  mapfile = open(mappingFilename, 'r')
  mappings = {}
  currentSheet = None
  for line in mapfile:
    if len(line.replace('\n', '')) <= 0:
      continue

    if line.startswith("!!"):
      currentSheet = line.replace("!!SHEET ", '').replace('\n', '')
      mappings[currentSheet] = {}
      continue

    if currentSheet is None:
      continue

    toks = line.replace('\n', '').split(' = ')
    mappings[currentSheet][toks[0]] = toks[1]
  mapfile.close()

  # open the template workbook
  tplbook = xlrd.open_workbook(tplFilename, formatting_info=True)
  # create a map of the sheet names to indices
  sheetmap = {}
  for i in range(tplbook.nsheets):
    sheet = tplbook.sheet_by_index(i)
    sheetmap[str(sheet.name)] = i

  # create output workbook
  wb = xlutils.copy.copy(tplbook)

  for sheetName, curMap in mappings.items():
    headSheet = tplbook.sheet_by_index(sheetmap[sheetName])
    headIndex = 0
    headCell = headSheet.cell(0, headIndex)

    ws = wb.get_sheet(sheetmap[sheetName])

    while (headCell.ctype != xlrd.XL_CELL_EMPTY and
            headCell.ctype != xlrd.XL_CELL_BLANK):
      mapval = curMap.get(str(headCell.value))
      if mapval is not None:
        if mapval.startswith('#'):
          if mapval != "#-":
            attrname = mapval.replace('#', '')
            attrval = designAttributes.get(attrname)
            if attrval is not None:
              _writeOutCell(ws, 1, headIndex, attrval)
        else:
          _writeOutCell(ws, 1, headIndex, curMap[str(headCell.value)])

      headIndex += 1
      try:
        headCell = headSheet.cell(0, headIndex)
      except:
        break

  wb.get_sheet(0)
  wb.save(outputFilename)

"""
parser.py parses various die measurement formats
Created by Craig Bishop on 21 March 2014

siderite
Copyright Deca Technologies 2014 All Rights Reserved.
"""

import os.path
from parsers import viewmetrology


def determine_format_from_path(path):
  """
  Tries to determine the format of the measurements file from the file name
  """
  file_name = os.path.basename(path)
  if file_name.endswith(".csv") or file_name.endswith(".txt"):
    return "ViewMetrology"
  return None


def shifts_from_data(data, onyx_design, panel_id, format):
    if format == "ViewMetrology":
        return viewmetrology.shifts_from_data(data, onyx_design, panel_id)
    else:
        return None

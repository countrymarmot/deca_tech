"""
viewmetrology.py parses die measurements in the View Metrology csv format
Created by Craig Bishop on 21 March 2014

siderite
Copyright Deca Technologies 2014 All Rights Reserved.
"""


from painite import zinc_pb2
import re
import math


CAD_FILENAME_RE = re.compile("(CAD File Name)[\s]*,[\s]*(D[0-9]{6}_[a-zA-Z]+)")
HEADER_REQS = ["Overall Status", "Type", "XCenter Nom.", "YCenter Nom.",
               "XCenter Devi.", "YCenter Devi.", "Angle Act."]


class DrawingNumberMismatchException(Exception):
    """
    Drawing number inside the raw data did not match the panel drawing passed
    in.
    """
    pass


class NoMeasurementDataHeaderException(Exception):
    """
    Raw measurement data from DMS did not contain a correct header
    """
    pass


def shifts_from_data(raw_data, onyx_design, panel_id):
    """
    Parses shift data from raw DMS output file data.

    raw_data should be the raw file contents of the file from DMS. onyx_design
    should be a zinc_pb2.Design object from the .onyx package file
    corresponding to the design. shifts_from_data returns a zinc_pb2.Shifts
    object.
    """
    shifts = zinc_pb2.Shifts()
    shifts.designNumber = onyx_design.designNumber
    shifts.designRevision = onyx_design.designRevision
    shifts.panelID = panel_id

    # for shifts from view metrology, no global offset
    shifts.globalOffset.x, shifts.globalOffset.y = 0.0, 0.0

    data = preprocess_raw_data(raw_data)
    drawing_number = parse_report_header(data)
    if drawing_number != (shifts.designNumber + "_" + shifts.designRevision):
        raise DrawingNumberMismatchException()
    parse_data(data, shifts, onyx_design)
    return shifts


def preprocess_raw_data(data):
    """
    Performs any adjustments necessary to the raw data before it is parsed.

    Changes Microsoft style \\r line-breaks into \\n line breaks. Removes \\n
    characters from the beginning and end of the file data.
    """
    data = data.replace('\r', '\n')
    data = data.strip('\n')
    return data


def parse_report_header(data):
    """
    Parses the report header and returns the drawing number and rev
    """
    match = CAD_FILENAME_RE.search(data)
    if not match:
        return None
    return match.groups()[1]


def parse_data_header(lines):
    map = {}
    first_row = None
    header = None
    for i in range(len(lines)):
        line = lines[i]
        if i == len(lines) - 1:
            raise NoMeasurementDataHeaderException()
        is_header = True
        for item in HEADER_REQS:
            is_header = is_header and (item in line)
        if is_header:
            header = line
            first_row = i + 1
            break
    header_items = header.split(',')
    for item in HEADER_REQS:
        map[item] = header_items.index(item)
    return map, first_row


def create_die_type_map(onyx_design):
    map = {}
    for die in onyx_design.unitDie:
        map[die.name] = ("LIVE", die, die.index)
    for die in onyx_design.referenceDie:
        map[die.name] = ("REF", die, die.index)
    return map


def parse_data(data, shifts, onyx_design):
    lines = data.split('\n')
    die_type_map = create_die_type_map(onyx_design)
    column_map, first_data_row = parse_data_header(lines)
    live_units, ref_units = {}, {}
    for line in lines[first_data_row:]:
        items = [i.strip(' ') for i in line.split(',')]
        type = items[column_map["Type"]]
        status = items[column_map['Overall Status']]
        nominal_die_x = float(items[column_map['XCenter Nom.']])
        nominal_die_y = float(items[column_map['YCenter Nom.']])
        if status == "OK":
            die_shift_x = float(items[column_map['XCenter Devi.']])
            die_shift_y = float(items[column_map['YCenter Devi.']])
            raw_angle = items[column_map['Angle Act.']]
            try:
                die_theta = math.radians(float(raw_angle))
            except:
                die_theta = 0.0
        die_offset = die_type_map[type][1].outline.center
        unit_x = nominal_die_x - die_offset.x
        unit_y = nominal_die_y - die_offset.y
        unit_nom = (unit_x, unit_y)
        if die_type_map[type][0] == "LIVE":
            if unit_nom not in live_units:
                live_units[unit_nom] = shifts.units.add()
                live_units[unit_nom].number = len(live_units)
                live_units[unit_nom].center.x = unit_x
                live_units[unit_nom].center.y = unit_y
                for i in range(len(onyx_design.unitDie)):
                    live_units[unit_nom].die.add()
            unit = live_units[unit_nom]
        elif die_type_map[type][0] == "REF":
            if unit_nom not in ref_units:
                ref_units[unit_nom] = shifts.referenceUnits.add()
                ref_units[unit_nom].number = len(ref_units)
                ref_units[unit_nom].center.x = unit_x
                ref_units[unit_nom].center.y = unit_y
                for i in range(len(onyx_design.referenceDie)):
                    ref_units[unit_nom].die.add()
            unit = ref_units[unit_nom]
        die_index = die_type_map[type][2]
        die = unit.die[die_index]
        die.name = die_type_map[type][1].name
        die.nominalXY.x, die.nominalXY.y = nominal_die_x, nominal_die_y
        die.shift.x, die.shift.y = die_shift_x, die_shift_y
        die.theta = die_theta

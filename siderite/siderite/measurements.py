"""
measurements.py parses various die measurement formats and marks units as
in-spec or out of spec
Created by Craig Bishop on 23 March 2014

siderite
Copyright Deca Technologies 2014 All Rights Reserved.
"""

import parser
import math


class InvalidMeasurementFormat(Exception):
    pass


class InvalidMeasurementData(Exception):
    pass


def file_name_for_onyxshifts(shifts):
    """
    Creates onyxshifts file name for parsed shifts. Use this file name
    for saving onyxshifts files.
    """
    return "{0}_{1}_{2}.onyxshifts".format(shifts.designNumber,
        shifts.designRevision, shifts.panelID)


def shifts_for_measurement_data(data, path, onyx_design, panel_id):
    """
    Parses raw shift data into a Shifts protobuf object.

    data should be the raw contents of the measurements file read
    in using binary file mode. path should at least contain the file name and
    extension; it's used to determine what measurement file format is used.
    onyx_design should be a protobuf Design object, and panel_id should be
    the panel ID corresponding to the measurement data.
    """
    format = parser.determine_format_from_path(path)
    if not format:
        raise InvalidMeasurementFormat()
    shifts = parser.shifts_from_data(data, onyx_design, panel_id, format)
    if not shifts:
        raise InvalidMeasurementData()
    mark_shifts_spec(shifts, onyx_design)
    return shifts


def create_die_name_map(onyx_design):
    map = {}
    for die in onyx_design.unitDie:
        map[die.name] = die
    for die in onyx_design.referenceDie:
        map[die.name] = die
    return map


def calculate_radial_shift(shift_x, shift_y, theta, constraint_x,
        constraint_y):
    rotated_x = ((constraint_x * math.cos(theta)) -
        (constraint_y * math.sin(theta)))
    rotated_y = ((constraint_y * math.cos(theta)) +
        (constraint_x * math.sin(theta)))
    total_x = abs(shift_x) + abs(rotated_x - constraint_x)
    total_y = abs(shift_y) + abs(rotated_y - constraint_y)
    return math.sqrt(math.pow(total_x, 2) + math.pow(total_y, 2))


def die_shift_in_spec(die_shift, die_name_map):
    design_die = die_name_map[die_shift.name]
    in_spec = True
    for constraint in design_die.shiftConstraints:
        radial_shift = calculate_radial_shift(die_shift.shift.x,
            die_shift.shift.y, die_shift.theta, constraint.constraintX,
            constraint.constraintY)
        in_spec = in_spec and (radial_shift < constraint.maxRadialShift)
    return in_spec


def mark_shifts_spec(shifts, onyx_design):
    die_map = create_die_name_map(onyx_design)
    for unit in shifts.units:
        in_spec = True
        for die in unit.die:
            in_spec = in_spec and die_shift_in_spec(die, die_map)
        unit.inSpec = in_spec

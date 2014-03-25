"""
onyxutil.py provides onyx utility methods.
Created by Craig Bishop on 17 July 2013

archerite
Copyright Deca Technologies 2013 All Rights Reserved.
"""


from painite import zinc_pb2
from google.protobuf import text_format
import tempfile


# The size of the range used to block onyx work.
WORK_BLOCK_SIZE = 400


class DesignDataMisMatchException(Exception):
    """
    There is no data, a bad design number or revision number.
    """
    pass


class ShiftDataMisMatchException(Exception):
    """
    There is a mismatched panel_id when merging shift data.
    """
    pass


def design_from_data(design_number=None,
                     design_rev=None,
                     design_file_data=None):
    """
    Returns a Design protobuf object from the design_number, design_rev and
    design_file_data.

    If there is no data raise a DesignDataMisMatchException. If there
    is a design number and revision then check the formatting. If there
    is a problem raise a DesignDataMisMatchException. Otherwise return
    a new design containing the data.
    """
    design = zinc_pb2.Design()
    if not design_file_data:
        raise DesignDataMisMatchException("No data!")
    design.ParseFromString(design_file_data)
    if design_number and design_rev:
        if design.designNumber.lower() != design_number.lower() or\
           design.designRevision.lower() != design_rev.lower():
            raise DesignDataMisMatchException(
                "Design {0}_{1} does not match .onyx file for {2}_{3}!".format(
                    design.designNumber, design.designRevision,
                    design_number, design_rev))
    return design


def shifts_from_data(design_number, design_rev, panel_id, shift_file_data):
    """
    Returns a Shifts protobuf object merged with the data.

    Create a Shifts protobuf object merge it with shift_file_data. If
    the panel_id doesn't match raise a ShiftDataMisMatchException,
    otherwise return the shifts protobuf object.
    """
    shifts = zinc_pb2.Shifts()
    text_format.Merge(shift_file_data, shifts)
    if panel_id.lower() != shifts.panelID.lower():
        raise ShiftDataMisMatchException(
            "Panel ID {0} in shift file does not match {1}_{2}_{3}!".format(
                shifts.panelID, design_number, design_rev, panel_id))
    return shifts


def requires_autorouting(design):
    """
    Return True when a design requires autorouting, otherwise False.

    If any layer has route definitions return True, otherwise return False.
    """
    for layer in design.layers:
        if len(layer.routeDefinitions) > 0:
            return True
    return False


def workranges_for_units(num_units):
    """
    Return a list of unit ranges.

    Create a list of 2-tuples of ranges between 0 and num_units - 1.
    The chunk size is configured using WORK_BLOCK_SIZE.
    """
    ranges = []
    start = 0
    i = 0
    while start < num_units:
        end = min(start + WORK_BLOCK_SIZE - 1, num_units - 1)
        ranges.append((i, start, end))
        start += WORK_BLOCK_SIZE
        i += 1
    return ranges


def error_work_result(work_type, error_msg):
    """
    Return an error WorkResult protobuf object.

    Create a WorkResult protobuf object and set the workType,
    errorMessage and success.
    """
    result = zinc_pb2.WorkResult()
    result.workType = work_type
    result.errorMessage = error_msg
    result.success = False
    return result


def zinc_routing_work_item(design, shifts, start, end):
    """
    Return a routing WorkItem protobuf object.

    Create a WorkItem protobuf object. Set the
    workType to ROUTING, panelID, start and end attributes.
    Copy the design and shifts objects. Return the WorkItem.
    """
    work_item = zinc_pb2.WorkItem()
    work_item.workType = zinc_pb2.ROUTING
    work_item.routingWorkItem.panelID = shifts.panelID
    work_item.routingWorkItem.design.CopyFrom(design)
    work_item.routingWorkItem.shifts.CopyFrom(shifts)
    work_item.routingWorkItem.workRange.start = start
    work_item.routingWorkItem.workRange.end = end
    return work_item


def zinc_create_gds_work_item(design, shifts):
    """
    Return a Create GDS WorkItem protobuf object.

    Create a WorkItem protobuf object. Set the
    workType to CREATE_GDS, panelID attributes. Copy the design and
    shifts objects. Return the WorkItem.
    """
    work_item = zinc_pb2.WorkItem()
    work_item.workType = zinc_pb2.CREATE_GDS
    work_item.createGDSWorkItem.panelID = shifts.panelID
    work_item.createGDSWorkItem.design.CopyFrom(design)
    work_item.createGDSWorkItem.shifts.CopyFrom(shifts)
    return work_item


def zinc_routed_units_from_result_data(result_data):
    """
    Return the routed units from zinc data.

    Create a WorkResult using the zinc_work_result_from_data method.
    Return the routed units from the WorkResult.
    """
    result = zinc_work_result_from_data(result_data)
    return result.routingWorkResults.routedUnits


def zinc_work_result_from_data(data):
    """
    Return a WorkResult protobuf object using zinc data.

    Create a WorkResult protobuf object, parse the data and return it.
    """
    result = zinc_pb2.WorkResult()
    result.ParseFromString(data)
    return result


def tmpfile_for_workitem(work_item):
    """
    Create a temp file containing work_item.

    Serialize and write work_item to a tempfile and return it.
    """
    handle, path = tempfile.mkstemp()
    with open(path, 'wb') as file:
        file.write(work_item.SerializeToString())
    return path


def work_result_from_data(data):
    """
    Return a work result containing data.

    Create a work result and try to parse the data. If the data isn't
    parsable return None. Otherwise return the new work result.
    """
    result = zinc_pb2.WorkResult()
    try:
        result.ParseFromString(data)
    except:
        return None
    return result

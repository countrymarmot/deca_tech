"""
model.py provides SQLAlchemy models for archerite and related projects.
Created by Craig Bishop on 16 July 2013

archerite
Copyright Deca Technologies 2013 All Rights Reserved.
"""


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime,\
    ForeignKey
from sqlalchemy.orm import relationship


Base = declarative_base()


class NetworkLocation(Base):
    """
    Single folder on a SAMABA network share.
    """

    __tablename__ = 'network_locations'

    id = Column(Integer, primary_key=True)
    server_ip = Column(String(256))
    share_name = Column(String(256))
    path = Column(String(1024))
    username = Column(String(1024), default="")
    password = Column(String(1024), default="")


class Watch(Base):
    """
    Where to find measurements and where to put results.
    """

    __tablename__ = 'watches'

    id = Column(Integer, primary_key=True)
    measurement_location_id = Column(Integer,
                                     ForeignKey('network_locations.id'))
    measurement_location = relationship("NetworkLocation", uselist=False,
                                        foreign_keys=[measurement_location_id])
    panel_gds_location_id = Column(Integer, ForeignKey('network_locations.id'))
    panel_gds_location = relationship("NetworkLocation", uselist=False,
                                      foreign_keys=[panel_gds_location_id])


class DesignLocation(Base):
    """
    Location of design on a SAMBA network share.
    """

    __tablename__ = 'design_locations'

    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey('network_locations.id'))
    location = relationship("NetworkLocation", uselist=False)


class MeasurementFile(Base):
    """
    MeasurementFile represents data and metadata about a measurement
    file. MeasurementFiles are found in watch locations and their data is
    used to create Shifts.
    """

    __tablename__ = 'measurement_files'

    id = Column(Integer, primary_key=True)
    watch_id = Column(Integer, ForeignKey('watches.id'))
    watch = relationship("Watch", uselist=False)
    file_name = Column(String(256))
    design_number = Column(String(128))
    design_rev = Column(String(4))
    panel_id = Column(String(256))
    valid = Column(Boolean)
    status = Column(String(256))
    found_time = Column(DateTime)


class Job(Base):
    """
    Jobs represent tasks related to a measurement_file(s) and an onyx_file.
    """
    STATUS_ERROR = -1
    STATUS_LAUNCHED = 1
    STATUS_QUEUED = 2
    STATUS_STARTED = 3
    STATUS_COMPLETE = 4

    SUBSTATUS_FETCHING_ONYX_FILE = 1
    SUBSTATUS_FETCHING_MEASUREMENTS = 2
    SUBSTATUS_ROUTING = 3
    SUBSTATUS_CREATING_GDS = 4
    SUBSTATUS_COMPLETE = 5

    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    measurement_file_id = Column(Integer, ForeignKey('measurement_files.id'))
    measurement_file = relationship("MeasurementFile", uselist=False)
    onyx_file = Column(String(256))
    onyx_file_checksum = Column('onyx_file_checksum', String(40),
                                nullable=False, unique=False)
    status = Column(Integer, default=1)
    sub_status = Column(Integer, default=0)
    launched_time = Column(DateTime)
    started_time = Column(DateTime)
    finished_time = Column(DateTime)
    work_items = Column(Integer)
    work_items_done = Column(Integer, default=0)
    unit_count = Column(Integer)
    units_good = Column(Integer)
    final_yield = Column(Float)


def job_status_to_string(status):
    if status == Job.STATUS_LAUNCHED:
        return "LAUNCHED"
    elif status == Job.STATUS_QUEUED:
        return "QUEUED"
    elif status == Job.STATUS_STARTED:
        return "RUNNING"
    elif status == Job.STATUS_COMPLETE:
        return "COMPLETE"
    else:
        return "ERROR"


def job_sub_status_to_string(status):
    if status == Job.SUBSTATUS_ROUTING:
        return "Routing units"
    elif status == Job.SUBSTATUS_FETCHING_ONYX_FILE:
        return "Fetching Onyx file"
    elif status == Job.SUBSTATUS_FETCHING_MEASUREMENTS:
        return "Fetching measurements file"
    elif status == Job.SUBSTATUS_CREATING_GDS:
        return "Creating GDS"
    elif status == Job.SUBSTATUS_COMPLETE:
        return "Complete"
    else:
        return ""

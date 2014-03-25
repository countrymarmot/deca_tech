"""
contasks.py Provides controller orchestration and functionality for
archerite.
Created by Craig Bishop on 22 July 2013

archerite
Copyright Deca Technologies 2013 All Rights Reserved.
"""
from datetime import datetime
import re
import socket
import zlib

from celery import chord

import bernhard

from purpurite.celeryapp import celery
from purpurite import model
from purpurite import shareutil
from purpurite import dbutil
from purpurite import redisutil
from purpurite import onyxutil
from purpurite import config
from purpurite.riemann import log

from xenotime import nodetasks


MEASUREMENT_FILE_FORM = re.compile("(D[0-9]{6})_([a-zA-Z]+)_(.+)\.onyxshifts")
ONYX_FILE_FORM = "{0}_{1}.onyx"
SCAN_LOCK_NAME = "measurement_scan_lock"
JOB_LOCK_NAME = "queue_jobs_lock"
LOCK_TIME = 10
SHIFTS_EXPIRE_TIME = 60 * 50
NOT_LOADED = 0
FETCHING = 1
FETCHED = 2
riemann = bernhard.Client(host=config.RIEMANN_HOST, port=config.RIEMANN_PORT)


@celery.task(name="archerite.contasks.process_new_measurements",
             timelimit=10)
@log
def process_new_measurements(watch_id):
    """
    Process new measurement files in the watch_id Watch directory.

    Acquire a measurement scan lock, otherwise return. Create a database
    session and get the Watch object. Try to get files in the measurement
    location, otherwise release the lock. If the file already exists as
    measurement in the database continue, otherwise if it matches the
    MEASUREMENT_FILE_FORM regex process the new measurement file, add
    a new job and release the lock.
    """
    riemann.send({"host": config.HOST,
                  "service": "contasks.process_new_measurements",
                  "description": str(watch_id)})
    if redisutil.acquire_lock(SCAN_LOCK_NAME, LOCK_TIME):
        print("Scanning for new measurements...")
        db = dbutil.create_db_session()
        db.commit()
        watch = db.query(model.Watch).filter_by(id=watch_id).first()
        try:
            file_names = shareutil.file_names_in_location(
                watch.measurement_location)
        except shareutil.RemoteNameException:
            redisutil.release_lock(SCAN_LOCK_NAME)
            return
        for file_name in file_names:
            if db.query(model.MeasurementFile)\
                 .filter_by(watch=watch,
                            file_name=file_name)\
                 .first():
                continue
            if MEASUREMENT_FILE_FORM.match(file_name):
                measurement_file = process_new_file(db, watch, file_name)
                add_job_for_file(db, measurement_file)
        db.close()
        redisutil.release_lock(SCAN_LOCK_NAME)


@celery.task(name="archerite.contasks.queue_new_jobs",
             timelimit=10)
@log
def queue_new_jobs():
    """
    Queue any new stepwise tasks for new Jobs.

    Acquire a job lock, otherwise return. Set the launched_job variable
    to False. Create a database session and get all Job objects with
    the status LAUNCHED. If the onyx file status is NOT_LOADED then
    delay the fetch_onyx_file task. Otherwise if the measurement file
    status is NOT_LOADED then delay the fetch_shifts_file task.
    Otherwise if launched_jobs is False, no jobs have been launched
    yet so reexpire_shifts and change the job status to QUEUED. If there
    is routing required for the onyx file then delay the launch_routing
    task. Otherwise delay the create_gds task and set launched_job to
    True. Commit and close the database and release the job lock.
    """
    if redisutil.acquire_lock(JOB_LOCK_NAME, LOCK_TIME):
        print("Launching new jobs...")
        launched_job = False
        db = dbutil.create_db_session()
        db.commit()
        new_jobs = db.query(model.Job).filter_by(
            status=model.Job.STATUS_LAUNCHED).all()
        riemann.send({"host": config.HOST,
                      "service": "contasks.queue_new_jobs",
                      "description": str(["start", str(new_jobs)])})
        for job in new_jobs:
            if redisutil.onyx_file_status(job.onyx_file) == NOT_LOADED:
                job.sub_status = model.Job.SUBSTATUS_FETCHING_ONYX_FILE
                fetch_onyx_file.delay(job)
            elif (redisutil.measurement_file_status(job.measurement_file) ==
                  NOT_LOADED):
                job.sub_status = model.Job.SUBSTATUS_FETCHING_MEASUREMENTS
                fetch_shifts_file.delay(job.measurement_file.id)
            elif not launched_job:
                reexpire_shifts(job.measurement_file)
                job.status = model.Job.STATUS_QUEUED
                work = 2
                if redisutil.onyx_file_requires_routing(job.onyx_file):
                    launch_routing.delay(job.id)
                    count = int(redisutil.measurement_file_count(
                        job.measurement_file))
                    workranges = onyxutil.workranges_for_units(count)
                    work += len(workranges)
                else:
                    nodetasks.create_gds.delay(job_id=job.id, gds_only=True)
                job.work_items = work
                launched_job = True
        db.commit()
        db.close()
        redisutil.release_lock(JOB_LOCK_NAME)


@celery.task(name="archerite.contasks.fetch_onyx_file",
             default_retry_delay=30)
@log
def fetch_onyx_file(job):
    """
    Get the onyx design file data and set redis keys in preparation for
    launching routing.

    Create a redis connection. If the onyx_file_status_key doesn't
    exist then set it to FETCHING and continue otherwise return.
    Create a database connnection and get the design file data using
    that connenction. Set the onyx_file_key to the design file data.
    Set the onyx_file_requires_routing_key to whether the design
    requires routing. Set the onyx_file_status_key to FETCHED.
    """
    try:
        r = redisutil.redis_connect()
        onyx_file_name = job.onyx_file
        checksum = job.onyx_file_checksum
        status_key = redisutil.onyx_file_status_key(onyx_file_name)
        if r.setnx(status_key, FETCHING):
            print("Fetching Onyx file {0}...".format(onyx_file_name))
            db = dbutil.create_db_session()
            data = shareutil.data_for_design_file(db,
                                                  onyx_file_name,
                                                  checksum=checksum)
            key = redisutil.onyx_file_key(onyx_file_name)
            r.set(key, data)
            design = onyxutil.design_from_data(design_file_data=data)
            r.set(redisutil.onyx_file_requires_routing_key(onyx_file_name),
                  onyxutil.requires_autorouting(design))
            r.set(status_key, FETCHED)
            db.close()
    except Exception as e:
        riemann.send({"host": config.HOST,
                      "service": "contasks.fetch_onyx_file",
                      "state": "failed",
                      "description":
                      "job.onyx_file: %s" % job.onyx_file})
        fetch_onyx_file.retry(job)


@celery.task(name="archerite.contasks.fetch_shifts_file",
             default_retry_delay=30)
@log
def fetch_shifts_file(measurement_file_id):
    """
    Use the MeasurementFile object and data to get the Shifts and
    add them to redis.

    Create a database session. Get the first MeasurementFile object.
    Create a redis connection. If the measurement_file_status_key
    doesn't exist then set it to FETCHING and continue otherwise
    return. Get the data for the measurement file. Get the Shifts
    using the MeasurementFile and data.
    """
    try:
        db = dbutil.create_db_session()
        measurement_file = db.query(model.MeasurementFile)\
                             .filter_by(id=measurement_file_id).first()
        r = redisutil.redis_connect()
        status_key = redisutil.measurement_file_status_key(measurement_file)
        if r.setnx(status_key, FETCHING):
            print("Fetching measurements file {0}_{1}_{2}...".format(
                measurement_file.design_number, measurement_file.design_rev,
                measurement_file.panel_id))
            data = shareutil.data_for_measurement_file(measurement_file)
            shifts = onyxutil.shifts_from_data(measurement_file.design_number,
                                               measurement_file.design_rev,
                                               measurement_file.panel_id,
                                               data)
            count_key = redisutil.measurement_file_count_key(measurement_file)
            r.set(count_key, number_units_shifts(shifts))
            r.expire(count_key, SHIFTS_EXPIRE_TIME)
            key = redisutil.measurement_file_key(measurement_file)
            r.set(key, data)
            r.expire(key, SHIFTS_EXPIRE_TIME)
            r.set(status_key, FETCHED)
            r.expire(status_key, SHIFTS_EXPIRE_TIME)
            riemann.send({"host": config.HOST,
                          "service": "contasks.fetch_shifts_file",
                          "description": str(["set", {"key", key}])})
            db.close()
    except Exception as e:
        riemann.send({"host": config.HOST,
                      "service": "contasks.fetch_shifts_file",
                      "state": "failed",
                      "description":
                      "measurement_file_id: %s" % measurement_file_id})
        fetch_shifts_file.retry(measurement_file_id)


@celery.task(name="archerite.contasks.launch_routing",
             default_retry_delay=2)
@log
def launch_routing(job_id):
    """
    Launch routing and create_gds subtasks for job_id Job.

    Create a database session. Get the first Job object filtered by
    job_id. Get the count, range 2-tuples and create routing subtasks.
    Create a celery chord of the list of routing tasks and a create_gds
    subtask. If there is an error retry twice. Commit and close the
    database session.
    """
    db, job = dbutil.get_db_job(job_id)
    print("Launching routing for {0}_{1}_{2}".format(
        job.measurement_file.design_number,
        job.measurement_file.design_rev,
        job.measurement_file.panel_id))
    try:
        riemann.send({"host": config.HOST,
                      "service": "contasks.launch_routing",
                      "state": "start"})
        count = int(redisutil.measurement_file_count(job.measurement_file))
        workranges = onyxutil.workranges_for_units(count)
        routing = [nodetasks.route.subtask([job.id, workrange])
                   for workrange in workranges]
        create_gds = nodetasks.create_gds.subtask([job.id, len(workranges)])
        print("Launched {0} routing jobs".format(len(routing)))
        chord(routing)(create_gds)
    except TypeError as exc:
        riemann.send({"host": config.HOST,
                      "service": "contasks.launch_routing",
                      "state": "failed",
                      "description": exc.message})
        raise launch_routing.retry(exc=exc)
    db.commit()
    db.close()


@log
def reexpire_shifts(measurement_file):
    """
    Extend the expire time on redis keys related to the measurement
    file by SHIFTS_EXPIRE_TIME seconds.

    Create a redis connection. Get the status, count and data keys.
    Change the expire time using SHIFTS_EXPIRE_TIME.
    """
    print("Re-expiring measurement files...")
    r = redisutil.redis_connect()
    statuskey = redisutil.measurement_file_status_key(measurement_file)
    countkey = redisutil.measurement_file_count_key(measurement_file)
    datakey = redisutil.measurement_file_key(measurement_file)
    r.expire(statuskey, SHIFTS_EXPIRE_TIME)
    r.expire(countkey, SHIFTS_EXPIRE_TIME)
    r.expire(datakey, SHIFTS_EXPIRE_TIME)


@log
def number_units_shifts(shifts):
    """
    Returns the number of units in a Shifts object.
    """
    return len(shifts.units)


@log
def process_new_file(db, watch, file_name):
    """
    Returns a MeasurementFile object given a database, watch
    and file name.

    Get the design number, design revision and panel_id using the
    MEASUREMENT_FILE_FORM regex. Create a MeasurementFile object.
    Assign the watch, file name, design number, design revision and
    panel_id. Set the status to DISCOVERED and found_time to now.
    Add it to the database and commit it. Return the MeasurementFile
    object.
    """
    design_num, design_rev, panel_id =\
        MEASUREMENT_FILE_FORM.match(file_name).groups()
    measurement_file = model.MeasurementFile()
    measurement_file.watch = watch
    measurement_file.file_name = file_name
    measurement_file.design_number = design_num
    measurement_file.design_rev = design_rev
    measurement_file.panel_id = panel_id
    measurement_file.valid = True
    measurement_file.status = "DISCOVERED"
    measurement_file.found_time = datetime.now()
    db.add(measurement_file)
    db.commit()
    riemann.send({"host": config.HOST,
                  "service": "contasks.process_new_file",
                  "description": str({"measurement_file":
                                      "%s %s" %
                                      (measurement_file.watch.id,
                                       measurement_file.file_name)})})
    return measurement_file


@log
def add_job_for_file(db, measurement_file):
    """
    Create, save and commit a new job using the measurement_file data.

    Create a Job object. Assign the measurement_file and onyx_file.
    Assign the status to "LAUNCHED" and the launched_time to now. Add
    it and commmit it to the database.
    """
    job = model.Job()
    job.measurement_file = measurement_file
    job.onyx_file = onyx_file_name(measurement_file.design_number,
                                   measurement_file.design_rev)
    job.status = model.Job.STATUS_LAUNCHED
    job.launched_time = datetime.now()
    shareutil.set_checksum(db, job)
    db.add(job)
    db.commit()
    return job


@log
def onyx_file_name(design_number, design_rev):
    """
    Returns an onyx file name string given a design number and design
    revision.
    """
    return ONYX_FILE_FORM.format(design_number, design_rev)

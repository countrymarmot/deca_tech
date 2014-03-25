"""
nodetasks.py Provides worker orchestration and functionality for
archerite.
Created by Craig Bishop on 22 July 2013

archerite
Copyright Deca Technologies 2013 All Rights Reserved.
"""


from datetime import datetime
import logging
import os
import subprocess
import tempfile
import zlib

from purpurite.celeryapp import celery
from purpurite import model
from purpurite import dbutil
from purpurite import redisutil
from purpurite import onyxutil
from purpurite import redisutil
from purpurite import shareutil
import design_cache


RESULTS_EXPIRE_TIME = 60 * 50
GDS_EXPIRE_TIME = 60 * 50


class RoutingException(Exception):
    """
    Unable to complete routing.

    No job_id, no data returned from zinc.
    """
    pass


class GDSGenerationException(Exception):
    """
    No data found to generate GDS.
    """
    pass


def route_command(work_item):
    """
    Call the zinc command with arguments to route.

    Create a temporary file containing the data from WorkItem. Create
    another temporary file for zinc's route output. Build the command
    and create a subprocess. Block until it's complete. Read the output
    temporary file. Return the data and delete the temporary files.
    """
    result_data = None
    inpath = onyxutil.tmpfile_for_workitem(work_item)
    h, outpath = tempfile.mkstemp()
    print("Input file: {0}\nOutput file: {1}\n".format(inpath, outpath))
    cmd = ["/usr/bin/zinc", "-i", inpath, "-o", outpath, "-d"]
    p = subprocess.Popen(cmd)
    p.wait()
    # read results
    with open(outpath, 'rb') as file:
        result_data = file.read()
    os.remove(inpath)
    os.remove(outpath)
    return result_data


@celery.task(name="xenotime.route",
             priority=9, acks_late=True, max_retries=3)
def route(job_id, workrange):
    """
    Create route data and put it in redis.

    Create a database session. Get the first Job filtered by the job_id.
    If no job is found raise a RoutingException. Set the started_time if
    it's not already set. Set the job status to RUNNING. Get the design
    data and create a Design. Get the measurement file data and create
    Shifts. Create a WorkItem using the Design and Shifts. Call the
    route zinc command to get data. Put the data in redis. Close the
    database session.
    """
    db, job = dbutil.get_db_job(job_id,
                                model.Job.STATUS_STARTED,
                                model.Job.SUBSTATUS_ROUTING)
    print("{0}) Route {1} to {2}".format(workrange[0],
                                         workrange[1],
                                         workrange[2]))
    if not job:
        raise RoutingException("Could not load job from database!")
    if not job.started_time:
        job.started_time = datetime.now()
    db.commit()

    design, design_data = get_design(job)

    shifts, shift_data = get_shifts(job)

    work_item = onyxutil.zinc_routing_work_item(design,
                                                shifts,
                                                workrange[1],
                                                workrange[2])

    if not shift_data:
        logging.debug("shift_data is None.")
        logging.debug("job = %s" % str(job.measurement_file))
        logging.debug("job = %s" % str(job))

    result_data = route_command(work_item)
    if not result_data:
        print("COULD NOT READ RESULTS")
        exc = RoutingException("Coud not read results from file!")
        raise route.retry(exc=exc)
    results_key = redisutil.routing_results_key(job, workrange)
    r = redisutil.redis_connect()
    r.set(results_key, result_data)
    r.expire(results_key, RESULTS_EXPIRE_TIME)
    job.work_items_done += 1
    db.commit()
    db.close()
    return results_key


def create_gds_command(work_item):
    """
    Call the zinc command with arguments to create_gds.

    Create a temporary file containing the data from WorkItem. Create
    another temporary file for zinc's create_gds output. Build the
    command and create a subprocess. Block until it's complete. Read
    the output temporary file. If there is no data create a
    RoutingException. Otherwise return the data and delete the temporary
    files.
    """
    inpath = onyxutil.tmpfile_for_workitem(work_item)
    h, outpath = tempfile.mkstemp()
    cmd = ["/usr/bin/zinc", "-i", inpath, "-o", outpath, "-d"]
    p = subprocess.Popen(cmd)
    p.wait()
    # read results
    with open(outpath, 'rb') as file:
        result_data = file.read()
    if not result_data:
        raise RoutingException("Coud not parse results from file!")
    os.remove(inpath)
    os.remove(outpath)
    return result_data


def get_design(job):
    design_data = design_cache.get_onyx_design_data(job.onyx_file)
    design = onyxutil.design_from_data(job.measurement_file.design_number,
                                       job.measurement_file.design_rev,
                                       design_data)
    return (design, design_data)


def get_shifts(job):
    shift_data = redisutil.measurement_file_data(job.measurement_file)
    shifts = onyxutil.shifts_from_data(job.measurement_file.design_number,
                                       job.measurement_file.design_rev,
                                       job.measurement_file.panel_id,
                                       shift_data)
    return (shifts, shift_data)


@celery.task(name="xenotime.create_gds",
             priority=0, acks_late=True)
def create_gds(result_keys=[], job_id=None,
               workrange_count=None, gds_only=False):
    """
    Create GDS data and put it in redis.

    If there is no job_id raise a RoutingException. Create a database
    session. Get the first Job filtered by job_id. Get the design data
    from the design_cache and create a Design. Get the measurement file
    data and create Shifts. Create a WorkItem using the Design and
    Shifts. If gds_only is False then get all the routed units and add
    them to the WorkItem. If there is no data raise a
    GDSGenerationException. Call the create_gds zinc command to get the
    data. Put the data in redis. Close the database session and delay
    a task to save the output files.
    """
    if not job_id:
        raise RoutingException("No job id provided!")
    db, job = dbutil.get_db_job(job_id,
                                sub_status=model.Job.SUBSTATUS_CREATING_GDS)

    print("Create GDS")

    design, design_data = get_design(job)

    shifts, shift_data = get_shifts(job)

    work_item = onyxutil.zinc_create_gds_work_item(design, shifts)

    print("Creating Work Item")
    if not gds_only:
        # aggregate all results
        r = redisutil.redis_connect()
        for result_key in result_keys:
            print("Loading result data")
            result_data = r.get(result_key)
            print("Aggregating routes")
            if not result_data:
                print("Result data is None!")
                raise GDSGenerationException("Result for {0} is missing!".
                                             format(result_key))
            routed_units = onyxutil.zinc_routed_units_from_result_data(
                result_data)
            work_item.createGDSWorkItem.routedUnits.extend(routed_units)

    num_units = len(shifts.units)
    good_units = len([unit for unit in work_item.createGDSWorkItem.routedUnits
        if unit.routingGood])
    job.unit_count = num_units
    job.good_units = good_units
    job.final_yield = float(good_units) / float(num_units)
    db.commit()

    result_data = create_gds_command(work_item)
    results_key = redisutil.gds_results_key(job)
    r.set(results_key, result_data)
    r.expire(results_key, GDS_EXPIRE_TIME)

    job.work_items_done += 1
    db.commit()
    db.close()
    # launch task to write back into share
    output_files.delay(job.id, results_key)


def get_results(result_key):
    r = redisutil.redis_connect()
    results_data = r.get(result_key)
    results = onyxutil.zinc_work_result_from_data(results_data)
    return (results, results_data)


def get_job_details(job_id):
    db, job = dbutil.get_db_job(job_id)

    store_location = job.measurement_file.watch.panel_gds_location
    prefix = "{0}_{1}_".format(job.measurement_file.design_number,
                               job.measurement_file.design_rev)
    db.commit()
    db.close()
    return (store_location, prefix)


def set_job_details(job_id):
    db, job = dbutil.get_db_job(job_id,
                                model.Job.STATUS_COMPLETE,
                                model.Job.SUBSTATUS_COMPLETES)
    job.finished_time = datetime.now()
    job.work_items_done += 1
    db.commit()
    db.close()


@celery.task(name="xenotime.output_files")
def output_files(job_id, result_key):
    """
    Create the GDS output files using the job_id Job and redis
    results_key.

    Create a database session. Get the first Job object filtered by
    job_id. Create a redis connection. Get the results data from redis.
    Create a WorkResult object from the data. Get the GDS location from
    the Job. Delete any pre-existing result files. Write and decompress
    the data to the GDS location. Set the job status to COMPLETE and
    finshed_time to now. Commit and close the database session.
    """
    print("Outputting GDS files to share...")
    results, results_data = get_results(result_key)
    store_location, prefix = get_job_details(job_id)

    for file in results.createGDSWorkResults.files:
        try:
            shareutil.delete_existing_file(store_location,
                                           prefix + file.fileName)
        except:
            pass
        shareutil.write_data_to_share(store_location, prefix + file.fileName,
                                      zlib.decompress(file.data))
    
    set_job_details(job_id)

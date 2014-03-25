"""
redisutil.py provides helper methods for redis.
Created by Craig Bishop on 22 July 2013

archerite
Copyright Deca Technologies 2013 All Rights Reserved.
"""


import redis
import config


def redis_connect():
    """
    Create a connection to the redis server using config.
    """
    return redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT,
                             db=config.REDIS_DB)


def acquire_lock(lock_name, lock_time):
    """
    Create a lock lock_name.

    SETNX and EXPIRE using lock_name and lock_time.
    """
    r = redis_connect()
    if r.setnx(lock_name, 1):
        r.expire(lock_name, lock_time)
        return True
    return False


def release_lock(lock_name):
    """
    Release a lock.

    DELETE a lock lock_name.
    """
    r = redis_connect()
    r.delete(lock_name)


def routing_results_key(job, workrange):
    """
    Returns the key value for routing results.
    """
    return "results.{0}_{1}_{2}.{3}".format(job.measurement_file.design_number,
                                            job.measurement_file.design_rev,
                                            job.measurement_file.panel_id,
                                            workrange[0])


def gds_results_key(job):
    """
    Returns the key value for GDS results.
    """
    return "gds.{0}_{1}_{2}".format(job.measurement_file.design_number,
                                    job.measurement_file.design_rev,
                                    job.measurement_file.panel_id)


def measurement_file_data(measurement_file):
    """
    Get the measurement file data.

    Connect and GET data using the measurement_file_key method
    to get the key.
    """
    key = measurement_file_key(measurement_file)
    r = redis_connect()
    return r.get(key)


def measurement_file_status(measurement_file):
    """
    Get the measurement file status.

    Connect and GET data using measurement_file_status_key method
    to get the key.
    """
    key = measurement_file_status_key(measurement_file)
    r = redis_connect()
    status = r.get(key)
    if not status:
        return 0
    return int(status)


def measurement_file_count(measurement_file):
    """
    Get the measurement file count.

    Connect and GET measurement file count data using the key.
    """
    r = redis_connect()
    return r.get(measurement_file_count_key(measurement_file))


def measurement_file_count_key(measurement_file):
    """
    Get the measurement file count key.
    """
    return measurement_file_key(measurement_file) + '.count'


def measurement_file_status_key(measurement_file):
    """
    Get the measurement file status key.
    """
    return measurement_file_key(measurement_file) + '.status'


def measurement_file_key(measurement_file):
    """
    Get the measurement file key.
    """
    return 'shifts.' + measurement_file.design_number +\
        measurement_file.design_rev + measurement_file.panel_id


def onyx_file_status(onyx_file_name):
    """
    Get the onyx file status data.

    Connect and GET the onyx file status data.
    """
    key = onyx_file_status_key(onyx_file_name)
    r = redis_connect()
    status = r.get(key)
    if not status:
        return 0
    return int(status)


def onyx_file_requires_routing(onyx_file_name):
    """
    Returns True if the onyx file status exists, False otherwise.

    Connect and GET the onyx file status and return a bool.
    """
    key = onyx_file_status_key(onyx_file_name)
    r = redis_connect()
    return bool(r.get(key))


def onyx_file_requires_routing_key(onyx_file_name):
    """
    Returns the key value for an onyx file routing.
    """
    return onyx_file_key(onyx_file_name) + '.requires_routing'


def onyx_file_status_key(onyx_file_name):
    """
    Returns the key value for an onyx file status.
    """
    return onyx_file_key(onyx_file_name) + '.status'


def onyx_file_key(onyx_file_name):
    """
    Returns the key value for an onyx file.
    """
    return 'design.' + onyx_file_name

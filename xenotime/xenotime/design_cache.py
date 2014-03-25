"""
design_cache.py provide caching for designs.
Created by Craig Bishop on 17 July 2013

archerite
Copyright Deca Technologies 2013 All Rights Reserved.
"""


import pickle
import os
import os.path

from purpurite import redisutil
from purpurite import shareutil


# max size of cache in bytes (512M)
MAX_CACHE_SIZE = 512 * (1024 * 1024)
CACHE_DIR = "/var/data/onyx_designs"
CACHE_META_FILE = ".onyxlru"


# size, list of filenames with LRU files at front
cache_data = [0, []]
if os.path.exists(os.path.join(CACHE_DIR, CACHE_META_FILE)):
    with open(os.path.join(CACHE_DIR, CACHE_META_FILE), 'rb') as file:
        cache_data = pickle.load(file)


class DesignCacheFetchException(Exception):
    """
    Unable to fetch a design cache.
    """
    pass


class DesignCacheAccessException(Exception):
    """
    A design cache file is not accessible.
    """
    pass


def write_back(cache_data):
    """
    Write the cache data to disk.

    Using CACHE_DIR and CACHE_META_FILE create a file. Serialize the
    data and write it to the file.
    """
    with open(os.path.join(CACHE_DIR, CACHE_META_FILE), 'wb') as file:
        pickle.dump(cache_data, file)


def prune_cache():
    """
    Prune the cache.

    While the cache size is greater than MAX_CACHE_SIZE remove designs
    from the cache directory. Delete the meta cache file and write
    it again.
    """
    global cache_data
    file_name = None
    while cache_data[0] > MAX_CACHE_SIZE:
        file_name = cache_data[1][0]
        filepath = os.path.join(CACHE_DIR, file_name)
        size = os.path.getsize(filepath)
        cache_data[0] -= size
        cache_data[1].remove(file_name)
    try:
        if os.path.exists(filepath) and os.path.isfile(filepath):
            os.remove(filepath)
    except:
        raise DesignCacheAccessException(
            "Could not remove cache file {0}!".format(file_name))
    write_back(cache_data)


def fetch_from_redis(onyx_file_name):
    """
    Fetch a cached design file.


    Fetch a cached design file from redis, write it to disk as a new
    file and update the cache meta file.
    """
    global cache_data
    r = redisutil.redis_connect()
    data = r.get(redisutil.onyx_file_key(onyx_file_name))
    if not data:
        raise DesignCacheFetchException("Could not fetch {0} into cache!".
                                        format(onyx_file_name))
    filepath = os.path.join(CACHE_DIR, onyx_file_name)
    with open(filepath, 'wb') as file:
        file.write(data)
    cache_data[1].append(onyx_file_name)
    cache_data[0] += os.path.getsize(filepath)
    prune_cache()
    return True


def cache_size():
    """
    Gets the size in bytes of all cached design files.
    """
    return cache_data[0]


def set_mru(onyx_file_name):
    """
    Update the cache meta design file to reverse MRU order.

    Pop and append the design file name and write it to disk.
    """
    global cache_data
    i = cache_data[1].index(onyx_file_name)
    cache_data[1].pop(i)
    cache_data[1].append(onyx_file_name)
    write_back(cache_data)


def get_onyx_design_data(onyx_file_name):
    """
    Get design data.

    If the design data is already cached then open the file, update
    the cache order and return the data. If the file is not in the
    cache then fetch it from redis. If it's not in redis or the design
    file doesn't exist then raise a DesignCacheAccessException.
    """
    if onyx_file_name not in cache_data[1]:
        if not fetch_from_redis(onyx_file_name):
            return None
    if not onyx_file_name in cache_data[1]:
        raise DesignCacheAccessException(
            "Could not find {0} in cache when it should be!".format(
                onyx_file_name))
    filepath = os.path.join(CACHE_DIR, onyx_file_name)
    if not os.path.exists(filepath):
        raise DesignCacheAccessException(
            "File {0} is missing from the cache".format(
                onyx_file_name))
    with open(filepath, 'rb') as file:
        data = file.read()
    set_mru(onyx_file_name)
    return data

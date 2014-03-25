"""
onyxcontroller.py
Created by Craig Bishop on 22 July 2013

archerite
Copyright Deca Technologies 2013 All Rights Reserved.
"""


import time

from purpurite import model
from purpurite import dbutil

from purpurite import config
from purpurite.riemann import log

from contasks import process_new_measurements, queue_new_jobs


scan_results = {}


@log
def scan_watches(db):
    """
    Create new measurement workflow for watches.
    Loop through the watches and if there are any
    new measurement files begin to process them.
    """
    global scan_results
    watches = db.query(model.Watch).all()
    for watch in watches:
        scan_results[watch.id] = process_new_measurements.delay(watch.id)


@log
def main():
    """
    """
    db = dbutil.create_db_session()
    riemann.send({"host": config.HOST,
                  "service": "onyxcontroller.main",
                  "state": "start"})
    try:
        while 1:
            scan_watches(db)
            queue_new_jobs.delay()
            time.sleep(1)
    except Exception:
        riemann.send({"host": config.HOST,
                      "service": "onyxcontroller.main",
                      "state": "stop"})


# Start main() when executed from the command line.
if __name__ == "__main__":
    main()

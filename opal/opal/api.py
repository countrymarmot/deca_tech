"""
api.py is a web app for archerite.
Created by Craig Bishop on 24 July 2013

archerite
Copyright Deca Technologies 2013 All Rights Reserved.
"""


from flask import Flask, redirect, render_template
from purpurite import model, dbutil
import json
from datetime import datetime


app = Flask("archerite", static_url_path='')


def serializable_job(job):
    """
    Return a dictionary representation of a job.

    Return a dictionary representation of job with string
    representations of timestamps, wait_time and job_time in total
    seconds and None when it's not calculable.
    """
    launch_timestamp = None
    start_timestamp = None
    finish_timestamp = None
    job_time = None
    wait_time = None
    if job.launched_time:
        launch_timestamp = job.launched_time.strftime("%m/%d/%Y %I:%M:%S")
    if job.started_time:
        start_timestamp = job.started_time.strftime("%m/%d/%Y %I:%M:%S")
    if job.finished_time:
        finish_timestamp = job.finished_time.strftime("%m/%d/%Y %I:%M:%S")
    if job.started_time and job.launched_time:
        wait_time = (job.started_time - job.launched_time).total_seconds()
    if job.finished_time and job.started_time:
        job_time = (job.finished_time - job.started_time).total_seconds()
    return {
        'id': job.id,
        'measurement_file_id': job.measurement_file_id,
        'design_number': job.measurement_file.design_number,
        'design_rev': job.measurement_file.design_rev,
        'panel_id': job.measurement_file.panel_id,
        'onyx_file': job.onyx_file,
        'status': model.job_status_to_string(job.status),
        'sub_status': model.job_sub_status_to_string(job.sub_status),
        'launched_time': launch_timestamp or None,
        'started_time': start_timestamp or None,
        'finished_time': finish_timestamp or None,
        'wait_time': wait_time or None,
        'run_time': job_time or None,
        'work_items': job.work_items,
        'work_items_done': job.work_items_done,
        'unit_count': job.unit_count,
        'units_good': job.units_good,
        'final_yield': "{0:.3f}%".format((job.final_yield or 0) * 100.0)
    }


@app.route("/")
@app.route("/opal/")
def index():
    """
    The index of the web app.

    Redirect the root domain to index.html.
    """
    return redirect("/opal/jobs")


@app.route("/jobs")
@app.route("/opal/jobs")
def jobs():
    return render_template("template.html", body_template="jobs.html")


@app.route("/api/jobs")
@app.route("/api/jobs/<min_id>")
@app.route("/opal/api/jobs")
@app.route("/opal/api/jobs/<min_id>")
def list_jobs(min_id=-1):
    """
    Return a json representation of jobs.

    Create a database session. Query the database for jobs ordered by
    launched_time ascending. Create serializable python dictionaries
    and return a json representation.
    """
    min_id_int = int(min_id)
    db = dbutil.create_db_session()
    jobs = db.query(model.Job).filter(model.Job.id >= min_id_int).order_by(
        model.Job.launched_time.asc()).all()
    serializable_jobs = [serializable_job(job) for job in jobs]
    db.close()
    return json.dumps(serializable_jobs)


@app.route("/api/job/<id>/restart")
@app.route("/opal/api/job/<id>/restart")
def restart_job(id):
    """
    Restart a specific job.

    Create a database session. Query the database for a specific job
    using the id. Create a new job model and set the measurement_file
    onyx_file and status to the old job. Set the launched_time to now.
    Add the new job to the database, commit and close the database session.
    """
    db = dbutil.create_db_session()
    job = db.query(model.Job).filter_by(id=id).first()
    new_job = model.Job()
    new_job.measurement_file = job.measurement_file
    new_job.onyx_file = job.onyx_file
    new_job.status = model.Job.STATUS_LAUNCHED
    new_job.launched_time = datetime.now()
    new_job.onyx_file_checksum = job.onyx_file_checksum
    db.add(new_job)
    db.commit()
    db.close()
    return "OK"


# If run the command line use default host, port and debug.
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)

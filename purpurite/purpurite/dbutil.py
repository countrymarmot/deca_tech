"""
dbutil.py provides helper methods for the database.
Created by Craig Bishop on 16 July 2013

archerite
Copyright Deca Technologies 2013 All Rights Reserved.
"""


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
import model


engine = None


def create_db_session():
    """
    Create a SQLAlchemy session.

    Use SQLAlchemy's create_engine, config.DATABASE_URL and sessionmaker.
    """
    global engine
    if not engine:
        engine = create_engine(config.DATABASE_URL,
                               pool_recycle=config.DATABASE_CONNECTION_TIMEOUT)
    session = sessionmaker(bind=engine)()
    return session

def get_db_job(job_id, status=None, sub_status=None):
    db = create_db_session()
    job = db.query(model.Job).filter_by(id=job_id).first()
    if job and sub_status or status:
        if status:
            job.status = status
        if sub_status:
            job.sub_status = sub_status
        db.commit()
    return (db, job)

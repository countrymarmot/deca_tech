"""
celeryapp.py create a celery server using the config module for
configuration.
Created by Craig Bishop on 22 July 2013

archerite
Copyright Deca Technologies 2013 All Rights Reserved.
"""


from __future__ import absolute_import
from celery import Celery
from purpurite import config


celery = Celery()


# Configuration, see the application user guide.
celery.config_from_object(config)


if __name__ == '__main__':
    celery.start()

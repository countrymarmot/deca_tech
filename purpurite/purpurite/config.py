"""
config.py provides configuration for archerite.
Created by Craig Bishop on 22 July 2013

archerite
Copyright Deca Technologies 2013 All Rights Reserved
"""
import socket


# Broker settings.
BROKER_URL = "redis://10.78.56.3:6379/0"

# Backend setting
CELERY_RESULT_BACKEND = "redis://10.78.56.3/0"

# Only prefetch the current task
CELERYD_PREFETCH_MULTIPLIER = 1

# List of modules to import when celery starts.
CELERY_IMPORTS = ("xenotime.nodetasks", "archerite.contasks", )

# Database connection for SQLAlchemy
DATABASE_URL = "mysql://rubidium:Blue52hut@10.78.56.4/rubidium"

# Database connection time-out for SQLAlchemy
DATABASE_CONNECTION_TIMEOUT = 3600  # 1 hour

# Route all control tasks to the controller node only
CELERY_ROUTES = {
    'archerite.contasks.process_new_measurements': {'queue': 'controller'},
    'archerite.contasks.queue_new_jobs': {'queue': 'controller'},
    'archerite.contasks.fetch_onyx_file': {'queue': 'controller'},
    'archerite.contasks.fetch_shifts_file': {'queue': 'controller'},
    'archerite.contasks.launch_routing': {'queue': 'controller'},
    'archerite.contasks.output_files': {'queue': 'controller'}
}

# Redis connection info
REDIS_HOST = "10.78.56.3"
REDIS_PORT = 6379
REDIS_DB = 0

# Riemann connection info
RIEMANN_HOST = "10.78.56.4"
RIEMANN_PORT = 5555

HOST = socket.gethostbyname(socket.gethostname())


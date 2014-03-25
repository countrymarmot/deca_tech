"""
Riemann utility methods.
"""
import config
from functools import wraps

import bernhard


riemann = None


def build_client():
    try:
        global riemann
        riemann = bernhard.Client(host=config.RIEMANN_HOST,
                                  port=config.RIEMANN_PORT)
    except:
        pass


def log(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        service_name = method.__module__ + "." + method.__name__
        try:
            if not riemann:
                build_client()
            riemann.send({"host": config.HOST,
                          "service": service_name,
                          "state": "begin"})
        except:
            pass
        m = method(*args, **kwargs)
        try:
            riemann.send({"host": config.HOST,
                          "service": service_name,
                          "state": "end"})
        except:
            pass
        return m
    return wrapper

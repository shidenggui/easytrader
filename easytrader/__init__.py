# -*- coding: utf-8 -*-
import urllib3

from . import exceptions
from .api import use, follower
import jsonpickle

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

__version__ = "0.18.4"
__author__ = "shidenggui"


try:
    from time import process_time
except:
    from time import clock as process_time
import timeit
#from decorator import decorator
import logging

internal_logger = logging.getLogger("PERF")

# Decorator
def perf_clock(logger=None):
    if logger is None:
        logger = internal_logger

    def perf_decorator(method):

        #@decorator
        def timed(*args, **kw):
            ts = timeit.default_timer()
            cs = process_time()
            ex = None
            result = None
            try:
                result = method(*args, **kw)
            except Exception as ex1:
                ex = ex1

            te = timeit.default_timer()
            ce =  process_time()
            logger.info('%r consume %2.4f sec, cpu %2.4f sec. args %s, extra args %s' % (method.__name__, te-ts, ce-cs, jsonpickle.dumps(args[1:]), jsonpickle.dumps(kw)))
            if ex is not None:
                raise ex
            return result
        return timed
    return perf_decorator
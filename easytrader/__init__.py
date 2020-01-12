# -*- coding: utf-8 -*-
import urllib3

from .log import logger
from . import exceptions
from .api import use, follower

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

__version__ = "0.18.5"
__author__ = "shidenggui"

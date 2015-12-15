__author__ = 'shidenggui'

from .webtrader import WebTrader
from .yjbtrader import YJBTrader
from .httrader import HTTrader
from .api import *

import logging
log_format = '%(asctime)-15s [%(levelname)s] %(filename)s:%(lineno)s %(message)s'
logging.basicConfig(level=logging.WARNING, format=log_format)

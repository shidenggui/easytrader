# coding:utf8
import logging
import os


log = logging.getLogger('easytrader')
log.setLevel(logging.DEBUG)

fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s %(lineno)s: %(message)s')
ch = logging.StreamHandler()

ch.setFormatter(fmt)
log.handlers.append(ch)

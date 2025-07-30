# -*- coding: utf-8 -*-
import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger("easytrader")
logger.setLevel(logging.DEBUG)
logger.propagate = False

fmt = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(filename)s %(lineno)s: %(message)s"
)
ch = logging.StreamHandler()

ch.setFormatter(fmt)
ch.setLevel(logging.INFO)
logger.handlers.append(ch)

# 创建一个处理器，每天切割日志文件，保留7天
handler = TimedRotatingFileHandler(
    "./logs/easytrader.log",  # 日志文件名
    when="midnight",  # 每天的午夜切割
    interval=1,  # 每隔一天切割
    backupCount=30,  # 保留7个备份
    encoding='utf-8'  # 指定编码
)
handler.setLevel(logging.DEBUG)
handler.setFormatter(fmt)
logger.addHandler(handler)

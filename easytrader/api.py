# coding=utf-8
import logging

from .gftrader import GFTrader
from .httrader import HTTrader
from .joinquant import JoinQuantFollower
from .log import log
from .xqtrader import XueQiuTrader
from .yhtrader import YHTrader
from .yjbtrader import YJBTrader


def use(broker, debug=True, **kwargs):
    """用于生成特定的券商对象
    :param broker:券商名支持 ['ht', 'HT', '华泰’] ['yjb', 'YJB', ’佣金宝'] ['yh', 'YH', '银河'] ['gf', 'GF', '广发']
    :param debug: 控制 debug 日志的显示, 默认为 True
    :param remove_zero: ht 可用参数，是否移除 08 账户开头的 0, 默认 True
    :return the class of trader

    Usage::

        >>> import easytrader
        >>> user = easytrader.use('ht')
        >>> user.prepare('ht.json')
    """
    if not debug:
        log.setLevel(logging.INFO)
    if broker.lower() in ['ht', '华泰']:
        return HTTrader(**kwargs)
    if broker.lower() in ['yjb', '佣金宝']:
        return YJBTrader()
    if broker.lower() in ['yh', '银河']:
        return YHTrader()
    if broker.lower() in ['xq', '雪球']:
        return XueQiuTrader()
    if broker.lower() in ['gf', '广发']:
        return GFTrader()


def follower(platform, **kwargs):
    """用于生成特定的券商对象
    :param platform:平台支持 ['jq', 'joinquant', '聚宽’]
    :return the class of follower

    Usage::

        >>> import easytrader
        >>> user = easytrader.use('xq')
        >>> user.prepare('xq.json')
        >>> jq = easytrader.follower('jq')
        >>> jq.login(user='username', password='password')
        >>> jq.follow(users=user, strategies=['strategies_link'])
    """
    if platform.lower() in ['jq', 'joinquant', '聚宽']:
        return JoinQuantFollower()

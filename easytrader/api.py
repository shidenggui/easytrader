# -*- coding: utf-8 -*-
import logging
import sys

import six

from easytrader.joinquant_follower import JoinQuantFollower
from easytrader.log import logger
from easytrader.ricequant_follower import RiceQuantFollower
from easytrader.xq_follower import XueQiuFollower
from easytrader.xqtrader import XueQiuTrader

if sys.version_info <= (3, 5):
    raise TypeError("不支持 Python3.5 及以下版本，请升级")


def use(broker, debug=False, **kwargs):
    """用于生成特定的券商对象
    :param broker: 券商名支持 
        例如 ['miniqmt', 'xq', '雪球', 'gj_client', '国金客户端', "universal_client", "通用同花顺客户端", "ths", "同花顺客户端"] 等
    :param debug: 控制 debug 日志的显示, 默认为 False
    :param initial_assets: [雪球参数] 控制雪球初始资金，默认为一百万
    :return the class of trader

    Usage::

        >>> import easytrader
        >>> user = easytrader.use('xq')
        >>> user.prepare('xq.json')
    """
    if debug:
        logger.setLevel(logging.DEBUG)

    if broker.lower() in ["xq", "雪球"]:
        return XueQiuTrader(**kwargs)

    if broker.lower() in ["yh_client", "银河客户端"]:
        from .yh_clienttrader import YHClientTrader

        return YHClientTrader()

    if broker.lower() in ["ht_client", "华泰客户端"]:
        from .ht_clienttrader import HTClientTrader

        return HTClientTrader()

    if broker.lower() in ["wk_client", "五矿客户端"]:
        from easytrader.wk_clienttrader import WKClientTrader

        return WKClientTrader()

    if broker.lower() in ["htzq_client", "海通证券客户端"]:
        from easytrader.htzq_clienttrader import HTZQClientTrader

        return HTZQClientTrader()

    if broker.lower() in ["gj_client", "国金客户端"]:
        from .gj_clienttrader import GJClientTrader

        return GJClientTrader()

    if broker.lower() in ["gf_client", "广发客户端"]:
        from .gf_clienttrader import GFClientTrader

        return GFClientTrader()

    if broker.lower() in ["universal_client", "通用同花顺客户端"]:
        from easytrader.universal_clienttrader import UniversalClientTrader

        return UniversalClientTrader()

    if broker.lower() in ["ths", "同花顺客户端"]:
        from .clienttrader import ClientTrader

        return ClientTrader()
    
    if broker.lower() in ["miniqmt"]:
        try:
            import xtquant
        except:
            logger.error("miniqmt 相关组件 xtqimt 未安装, 请执行 pip install easytrader[xtquant]安装")
        from easytrader.miniqmt.miniqmt_trader import MiniqmtTrader

        return MiniqmtTrader()

    raise NotImplementedError


def follower(platform, **kwargs):
    """用于生成特定的券商对象
    :param platform:平台支持 ['jq', 'joinquant', '聚宽’]
    :param initial_assets: [雪球参数] 控制雪球初始资金，默认为一万,
        总资金由 initial_assets * 组合当前净值 得出
    :param total_assets: [雪球参数] 控制雪球总资金，无默认值,
        若设置则覆盖 initial_assets
    :return the class of follower

    Usage::

        >>> import easytrader
        >>> user = easytrader.use('xq')
        >>> user.prepare('xq.json')
        >>> jq = easytrader.follower('jq')
        >>> jq.login(user='username', password='password')
        >>> jq.follow(users=user, strategies=['strategies_link'])
    """
    if platform.lower() in ["rq", "ricequant", "米筐"]:
        return RiceQuantFollower()
    if platform.lower() in ["jq", "joinquant", "聚宽"]:
        return JoinQuantFollower()
    if platform.lower() in ["xq", "xueqiu", "雪球"]:
        return XueQiuFollower(**kwargs)
    raise NotImplementedError

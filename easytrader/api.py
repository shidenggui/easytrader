# coding=utf-8
from .gftrader import GFTrader
from .helpers import disable_log
from .httrader import HTTrader
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
        disable_log()
    if broker.lower() in ['ht', 'HT', '华泰']:
        return HTTrader(**kwargs)
    if broker.lower() in ['yjb', 'YJB', '佣金宝']:
        return YJBTrader()
    if broker.lower() in ['yh', 'YH', '银河']:
        return YHTrader()
    if broker.lower() in ['xq', 'XQ', '雪球']:
        return XueQiuTrader()
    if broker.lower() in ['gf', 'GF', '广发']:
        return GFTrader()

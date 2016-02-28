# coding=utf-8
from .helpers import disable_log
from .httrader import HTTrader
from .yhtrader import YHTrader
from .yjbtrader import YJBTrader
from .xqtrader import XueQiuTrader


def use(broker, debug=True):
    """用于生成特定的券商对象
    :param broker:券商名支持 ['ht', 'HT', '华泰’] ['yjb', 'YJB', ’佣金宝'] ['yh', 'YH', '银河']
    :return the class of trader

    Usage::

        >>> import easytrader
        >>> user = easytrader.use('ht')
        >>> user.prepare('ht.json')
    """
    if not debug:
        disable_log()
    if broker.lower() in ['ht', 'HT', '华泰']:
        return HTTrader()
    if broker.lower() in ['yjb', 'YJB', '佣金宝']:
        return YJBTrader()
    if broker.lower() in ['yh', 'YH', '银河']:
        return YHTrader()
    if broker.lower() in ['xq', 'XQ', '雪球']:
        return XueQiuTrader()

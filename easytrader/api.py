# coding=utf-8
from .yjbtrader import YJBTrader
from .httrader import HTTrader


def use(broker):
    """用于生成特定的券商对象
    :param broker:券商名支持 ['ht', 'HT', '华泰’] ['yjb', 'YJB', ’佣金宝']
    :return the class of trader

    Usage::

        >>> import easytrader
        >>> user = easytrader.use('ht')
        >>> user.prepare('ht.json')
    """
    if broker.lower() in ['ht', 'HT', '华泰']:
        return HTTrader()
    if broker.lower() in ['yjb', 'YJB', '佣金宝']:
        return YJBTrader()


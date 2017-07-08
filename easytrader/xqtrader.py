# -*- coding: utf-8 -*-
import json
import os
import re
import time
from numbers import Number

import requests

from .log import log
from .webtrader import NotLoginError, TradeError
from .webtrader import WebTrader


class XueQiuTrader(WebTrader):
    config_path = os.path.dirname(__file__) + '/config/xq.json'

    def __init__(self, **kwargs):
        super(XueQiuTrader, self).__init__()

        # 资金换算倍数
        self.multiple = kwargs['initial_assets'] if 'initial_assets' in kwargs else 1000000
        if not isinstance(self.multiple, Number):
            raise TypeError('initial assets must be number(int, float)')
        if self.multiple < 1e3:
            raise ValueError('雪球初始资产不能小于1000元，当前预设值 {}'.format(self.multiple))

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:32.0) Gecko/20100101 Firefox/32.0',
            'Host': 'xueqiu.com',
            'Pragma': 'no-cache',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Cache-Control': 'no-cache',
            'Referer': 'http://xueqiu.com/P/ZH003694',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept-Language': 'zh-CN,zh;q=0.8'
        }
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.account_config = None

    def autologin(self, **kwargs):
        """
        重写自动登录方法
        避免重试导致的帐号封停
        :return:
        """
        self.login()

    def login(self, throw=False):
        """
        登录
        :param throw:
        :return:
        """
        login_status, result = self.post_login_data()
        if login_status is False and throw:
            raise NotLoginError(result)
        log.debug('login status: %s' % result)
        return login_status

    def _prepare_account(self, user='', password='', **kwargs):
        """
        转换参数到登录所需的字典格式
        :param user: 雪球邮箱(邮箱手机二选一)
        :param password: 雪球密码
        :param account: 雪球手机号(邮箱手机二选一)
        :param portfolio_code: 组合代码
        :param portfolio_market: 交易市场， 可选['cn', 'us', 'hk'] 默认 'cn'
        :return:
        """
        if 'portfolio_code' not in kwargs:
            raise TypeError('雪球登录需要设置 portfolio_code(组合代码) 参数')
        if 'portfolio_market' not in kwargs:
            kwargs['portfolio_market'] = 'cn'
        if 'account' not in kwargs:
            kwargs['account'] = ''
        self.account_config = {
            'username': user,
            'account': kwargs['account'],
            'password': password,
            'portfolio_code': kwargs['portfolio_code'],
            'portfolio_market': kwargs['portfolio_market']
        }

    def post_login_data(self):
        login_post_data = {
            'username': self.account_config.get('username', ''),
            'areacode': '86',
            'telephone': self.account_config['account'],
            'remember_me': '0',
            'password': self.account_config['password']
        }
        login_response = self.session.post(self.config['login_api'], data=login_post_data)
        login_status = login_response.json()
        if 'error_description' in login_status:
            return False, login_status['error_description']
        return True, "SUCCESS"

    def __virtual_to_balance(self, virtual):
        """
        虚拟净值转化为资金
        :param virtual: 雪球组合净值
        :return: 换算的资金
        """
        return virtual * self.multiple

    def __get_html(self, url):
        return self.session.get(url).text

    def __search_stock_info(self, code):
        """
        通过雪球的接口获取股票详细信息
        :param code: 股票代码 000001
        :return: 查询到的股票 {u'stock_id': 1000279, u'code': u'SH600325',
        u'name': u'华发股份', u'ind_color': u'#d9633b', u'chg': -1.09,
         u'ind_id': 100014, u'percent': -9.31, u'current': 10.62, u'hasexist': None,
          u'flag': 1, u'ind_name': u'房地产', u'type': None, u'enName': None}
            ** flag : 未上市(0)、正常(1)、停牌(2)、涨跌停(3)、退市(4)
        """
        data = {
            'code': str(code),
            'size': '300',
            'key': '47bce5c74f',
            'market': self.account_config['portfolio_market'],
        }
        r = self.session.get(self.config['search_stock_url'], params=data)
        stocks = json.loads(r.text)
        stocks = stocks['stocks']
        stock = None
        if len(stocks) > 0:
            stock = stocks[0]
        return stock

    def __get_portfolio_info(self, portfolio_code):
        """
        获取组合信息
        :return: 字典
        """
        url = self.config['portfolio_url'] + portfolio_code
        html = self.__get_html(url)
        match_info = re.search(r'(?<=SNB.cubeInfo = ).*(?=;\n)', html)
        if match_info is None:
            raise Exception('cant get portfolio info, portfolio html : {}'.format(html))
        try:
            portfolio_info = json.loads(match_info.group())
        except Exception as e:
            raise Exception('get portfolio info error: {}'.format(e))
        return portfolio_info

    def get_balance(self):
        """
        获取账户资金状况
        :return:
        """
        portfolio_code = self.account_config.get('portfolio_code', 'ch')  # 组合代码
        portfolio_info = self.__get_portfolio_info(portfolio_code)  # 组合信息
        asset_balance = self.__virtual_to_balance(float(portfolio_info['net_value']))  # 总资产
        position = portfolio_info['view_rebalancing']  # 仓位结构
        cash = asset_balance * float(position['cash']) / 100
        market = asset_balance - cash
        return [{'asset_balance': asset_balance,
                 'current_balance': cash,
                 'enable_balance': cash,
                 'market_value': market,
                 'money_type': u'人民币',
                 'pre_interest': 0.25}]

    def __get_position(self):
        """
        获取雪球持仓
        :return:
        """
        portfolio_code = self.account_config['portfolio_code']  # 组合代码
        portfolio_info = self.__get_portfolio_info(portfolio_code)  # 组合信息
        position = portfolio_info['view_rebalancing']  # 仓位结构
        stocks = position['holdings']  # 持仓股票
        return stocks

    @staticmethod
    def __time_strftime(time_stamp):
        try:
            local_time = time.localtime(time_stamp / 1000)
            return time.strftime("%Y-%m-%d %H:%M:%S", local_time)
        except:
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def get_position(self):
        """
        获取持仓
        :return:
        """
        xq_positions = self.__get_position()
        balance = self.get_balance()[0]
        position_list = []
        for pos in xq_positions:
            volume = pos['weight'] * balance['asset_balance'] / 100
            position_list.append({'cost_price': volume / 100,
                                  'current_amount': 100,
                                  'enable_amount': 100,
                                  'income_balance': 0,
                                  'keep_cost_price': volume / 100,
                                  'last_price': volume / 100,
                                  'market_value': volume,
                                  'position_str': 'random',
                                  'stock_code': pos['stock_symbol'],
                                  'stock_name': pos['stock_name']
                                  })
        return position_list

    def __get_xq_history(self):
        """
        获取雪球调仓历史
        :param instance:
        :param owner:
        :return:
        """
        data = {
            "cube_symbol": str(self.account_config['portfolio_code']),
            'count': 5,
            'page': 1
        }
        r = self.session.get(self.config['history_url'], params=data)
        r = json.loads(r.text)
        return r['list']

    @property
    def history(self):
        return self.__get_xq_history()

    def get_entrust(self):
        """
        获取委托单(目前返回5次调仓的结果)
        操作数量都按1手模拟换算的
        :return:
        """
        xq_entrust_list = self.__get_xq_history()
        entrust_list = []
        for xq_entrusts in xq_entrust_list:
            status = xq_entrusts['status']  # 调仓状态
            if status == 'pending':
                status = "已报"
            elif status == 'canceled':
                status = "废单"
            else:
                status = "已成"
            for entrust in xq_entrusts['rebalancing_histories']:
                volume = abs(entrust['target_weight'] - entrust['weight']) * self.multiple / 10000
                entrust_list.append({
                    'entrust_no': entrust['id'],
                    'entrust_bs': u"买入" if entrust['target_weight'] > entrust['weight'] else u"卖出",
                    'report_time': self.__time_strftime(entrust['updated_at']),
                    'entrust_status': status,
                    'stock_code': entrust['stock_symbol'],
                    'stock_name': entrust['stock_name'],
                    'business_amount': 100,
                    'business_price': volume,
                    'entrust_amount': 100,
                    'entrust_price': volume,
                })
        return entrust_list

    def cancel_entrust(self, entrust_no):
        """
        对未成交的调仓进行伪撤单
        :param entrust_no:
        :return:
        """
        xq_entrust_list = self.__get_xq_history()
        is_have = False
        for xq_entrusts in xq_entrust_list:
            status = xq_entrusts['status']  # 调仓状态
            for entrust in xq_entrusts['rebalancing_histories']:
                if entrust['id'] == entrust_no and status == 'pending':
                    is_have = True
                    bs = 'buy' if entrust['target_weight'] < entrust['weight'] else 'sell'
                    if entrust['target_weight'] == 0 and entrust['weight'] == 0:
                        raise TradeError(u"移除的股票操作无法撤销,建议重新买入")
                    balance = self.get_balance()[0]
                    volume = abs(entrust['target_weight'] - entrust['weight']) * balance['asset_balance'] / 100
                    r = self.__trade(stock_code=entrust['stock_symbol'], volume=volume, entrust_bs=bs)
                    if len(r) > 0 and 'error_info' in r[0]:
                        raise TradeError(u"撤销失败!%s" % ('error_info' in r[0]))
        if not is_have:
            raise TradeError(u"撤销对象已失效")
        return True

    def adjust_weight(self, stock_code, weight):
        """
        雪球组合调仓, weight 为调整后的仓位比例
        :param stock_code: str 股票代码
        :param weight: float 调整之后的持仓百分比， 0 - 100 之间的浮点数
        """

        stock = self.__search_stock_info(stock_code)
        if stock is None:
            raise TradeError(u"没有查询要操作的股票信息")
        if stock['flag'] != 1:
            raise TradeError(u"未上市、停牌、涨跌停、退市的股票无法操作。")

        # 仓位比例向下取两位数
        weight = round(weight, 2)
        # 获取原有仓位信息
        position_list = self.__get_position()

        # 调整后的持仓
        for position in position_list:
            if position['stock_id'] == stock['stock_id']:
                position['proactive'] = True
                position['weight'] = weight

        if weight != 0 and stock['stock_id'] not in [k['stock_id'] for k in position_list]:
            position_list.append({
                "code": stock['code'],
                "name": stock['name'],
                "enName": stock['enName'],
                "hasexist": stock['hasexist'],
                "flag": stock['flag'],
                "type": stock['type'],
                "current": stock['current'],
                "chg": stock['chg'],
                "percent": str(stock['percent']),
                "stock_id": stock['stock_id'],
                "ind_id": stock['ind_id'],
                "ind_name": stock['ind_name'],
                "ind_color": stock['ind_color'],
                "textname": stock['name'],
                "segment_name": stock['ind_name'],
                "weight": weight,
                "url": "/S/" + stock['code'],
                "proactive": True,
                "price": str(stock['current'])
            })

        remain_weight = 100 - sum(i.get('weight') for i in position_list)
        cash = round(remain_weight, 2)
        log.debug("调仓比例:%f, 剩余持仓 :%f" % (weight, remain_weight))
        data = {
            "cash": cash,
            "holdings": str(json.dumps(position_list)),
            "cube_symbol": str(self.account_config['portfolio_code']),
            'segment': 'true',
            'comment': ""
        }

        try:
            rebalance_res = self.session.post(self.config['rebalance_url'], data=data)
        except Exception as e:
            log.warn('调仓失败: %s ' % e)
            return
        else:
            log.debug('调仓 %s: 持仓比例%d' % (stock['name'], weight))
            rebalance_status = json.loads(rebalance_res.text)
            if 'error_description' in rebalance_status.keys() and rebalance_res.status_code != 200:
                log.error('调仓错误: %s' % (rebalance_status['error_description']))
                return [{'error_no': rebalance_status['error_code'],
                         'error_info': rebalance_status['error_description']}]
            else:
                log.debug('调仓成功 %s: 持仓比例%d' % (stock['name'], weight))

    def __trade(self, stock_code, price=0, amount=0, volume=0, entrust_bs='buy'):
        """
        调仓
        :param stock_code:
        :param price:
        :param amount:
        :param volume:
        :param entrust_bs:
        :return:
        """
        stock = self.__search_stock_info(stock_code)
        balance = self.get_balance()[0]
        if stock is None:
            raise TradeError(u"没有查询要操作的股票信息")
        if not volume:
            volume = int(float(price) * amount)  # 可能要取整数
        if balance['current_balance'] < volume and entrust_bs == 'buy':
            raise TradeError(u"没有足够的现金进行操作")
        if stock['flag'] != 1:
            raise TradeError(u"未上市、停牌、涨跌停、退市的股票无法操作。")
        if volume == 0:
            raise TradeError(u"操作金额不能为零")

        # 计算调仓调仓份额
        weight = volume / balance['asset_balance'] * 100
        weight = round(weight, 2)

        # 获取原有仓位信息
        position_list = self.__get_position()

        # 调整后的持仓
        is_have = False
        for position in position_list:
            if position['stock_id'] == stock['stock_id']:
                is_have = True
                position['proactive'] = True
                old_weight = position['weight']
                if entrust_bs == 'buy':
                    position['weight'] = weight + old_weight
                else:
                    if weight > old_weight:
                        raise TradeError(u"操作数量大于实际可卖出数量")
                    else:
                        position['weight'] = old_weight - weight
                position['weight'] = round(position['weight'], 2)
        if not is_have:
            if entrust_bs == 'buy':
                position_list.append({
                    "code": stock['code'],
                    "name": stock['name'],
                    "enName": stock['enName'],
                    "hasexist": stock['hasexist'],
                    "flag": stock['flag'],
                    "type": stock['type'],
                    "current": stock['current'],
                    "chg": stock['chg'],
                    "percent": str(stock['percent']),
                    "stock_id": stock['stock_id'],
                    "ind_id": stock['ind_id'],
                    "ind_name": stock['ind_name'],
                    "ind_color": stock['ind_color'],
                    "textname": stock['name'],
                    "segment_name": stock['ind_name'],
                    "weight": round(weight, 2),
                    "url": "/S/" + stock['code'],
                    "proactive": True,
                    "price": str(stock['current'])
                })
            else:
                raise TradeError(u"没有持有要卖出的股票")

        if entrust_bs == 'buy':
            cash = (balance['current_balance'] - volume) / balance['asset_balance'] * 100
        else:
            cash = (balance['current_balance'] + volume) / balance['asset_balance'] * 100
        cash = round(cash, 2)
        log.debug("weight:%f, cash:%f" % (weight, cash))

        data = {
            "cash": cash,
            "holdings": str(json.dumps(position_list)),
            "cube_symbol": str(self.account_config['portfolio_code']),
            'segment': 1,
            'comment': ""
        }

        try:
            rebalance_res = self.session.post(self.config['rebalance_url'], data=data)
        except Exception as e:
            log.warn('调仓失败: %s ' % e)
            return
        else:
            log.debug('调仓 %s%s: %d' % (entrust_bs, stock['name'], rebalance_res.status_code))
            rebalance_status = json.loads(rebalance_res.text)
            if 'error_description' in rebalance_status and rebalance_res.status_code != 200:
                log.error('调仓错误: %s' % (rebalance_status['error_description']))
                return [{'error_no': rebalance_status['error_code'],
                         'error_info': rebalance_status['error_description']}]
            else:
                return [{'entrust_no': rebalance_status['id'],
                         'init_date': self.__time_strftime(rebalance_status['created_at']),
                         'batch_no': '委托批号',
                         'report_no': '申报号',
                         'seat_no': '席位编号',
                         'entrust_time': self.__time_strftime(rebalance_status['updated_at']),
                         'entrust_price': price,
                         'entrust_amount': amount,
                         'stock_code': stock_code,
                         'entrust_bs': '买入',
                         'entrust_type': '雪球虚拟委托',
                         'entrust_status': '-'}]

    def buy(self, stock_code, price=0, amount=0, volume=0, entrust_prop=0):
        """买入卖出股票
        :param stock_code: 股票代码
        :param price: 买入价格
        :param amount: 买入股数
        :param volume: 买入总金额 由 volume / price 取整， 若指定 price 则此参数无效
        :param entrust_prop:
        """
        return self.__trade(stock_code, price, amount, volume, 'buy')

    def sell(self, stock_code, price=0, amount=0, volume=0, entrust_prop=0):
        """卖出股票
        :param stock_code: 股票代码
        :param price: 卖出价格
        :param amount: 卖出股数
        :param volume: 卖出总金额 由 volume / price 取整， 若指定 price 则此参数无效
        :param entrust_prop:
        """
        return self.__trade(stock_code, price, amount, volume, 'sell')

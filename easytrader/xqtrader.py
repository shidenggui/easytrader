# -*- coding: utf-8 -*-

import os
import requests
import json
import urllib
import time
import six

from . import helpers
from .webtrader import NotLoginError
from .webtrader import WebTrader

if six.PY2:
    import urllib2

log = helpers.get_logger(__file__)


class TraderError(Exception):
    def __init__(self, result=None):
        super(TraderError, self).__init__()
        self.result = result


class XueQiuTrader(WebTrader):
    config_path = os.path.dirname(__file__) + '/config/xq.json'

    def __init__(self):
        super(XueQiuTrader, self).__init__()
        self.cookies = {}
        self.requests = requests
        self.account_config = None
        self.multiple = 1000000  # 资金换算倍数

    def autologin(self):
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
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:32.0) Gecko/20100101 Firefox/32.0',
            'Host': 'xueqiu.com',
            'Pragma': 'no-cache',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Cache-Conrol': 'no-cache',
            'Referer': 'http://xueqiu.com/P/ZH003694',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept-Language': 'zh-CN,zh;q=0.8'
        }
        # self.__pre_fetch()
        login_status, result = self.post_login_data()
        if login_status == False and throw:
            raise NotLoginError(result)
        log.debug('login status: %s' % result)
        return login_status

    def __pre_fetch(self):
        """
        headers测试
        :return:
        """
        fetch_res = self.requests.get('http://www.xueqiu.com/', cookies=self.cookies, headers=self.headers)
        return fetch_res.status_code

    def post_login_data(self):
        login_post_data = {
            'username': self.account_config.get('username', ''),
            'areacode': '86',
            'telephone': self.account_config['account'],
            'remember_me': '0',
            'password': self.account_config['password']
        }
        login_response = self.requests.post(self.config['login_api'], cookies=self.cookies, data=login_post_data,
                                            headers=self.headers)
        self.cookies = login_response.cookies
        login_status = json.loads(login_response.text)
        if 'error_description' in login_status.keys():
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
        send_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Host': 'xueqiu.com',
            'Cookie': r'xxxxxx',
        }

        if six.PY2:
            req = urllib2.Request(url, headers=send_headers)
            resp = urllib2.urlopen(req)
        else:
            req = urllib.request.Request(url, headers=send_headers)
            resp = urllib.request.urlopen(req)
        html = resp.read().decode('UTF-8')
        return html

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
            'market': 'cn',
        }
        r = self.requests.get(self.config['search_stock_url'], headers=self.headers, cookies=self.cookies, params=data)
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
        pos_start = html.find('SNB.cubeInfo = ') + 15
        pos_end = html.find('SNB.cubePieData')
        json_data = html[pos_start:pos_end]
        portfolio_info = json.loads(json_data)
        return portfolio_info

    def get_balance(self):
        """
        获取账户资金状况
        :return:
        """
        portfolio_code = self.account_config['portfolio_code']  # 组合代码
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

    def __time_strftime(self, time_stamp):
        try:
            ltime = time.localtime(time_stamp/1000)
            return time.strftime("%Y-%m-%d %H:%M:%S", ltime)
        except :
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
                                  'position_str': 'xxxxxx',
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
        r = self.requests.get(self.config['history_url'], headers=self.headers, cookies=self.cookies, params=data)
        r = json.loads(r.text)
        return r['list']

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

    def cancel_entrust(self, entrust_no, stock_code):
        """
        对未成交的调仓进行伪撤单
        :param entrust_no:
        :param stock_code:
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
                        raise TraderError(u"移除的股票操作无法撤销,建议重新买入")
                    balance = self.get_balance()[0]
                    volume = abs(entrust['target_weight'] - entrust['weight']) * balance['asset_balance'] / 100
                    r = self.__trade(stock_code=entrust['stock_symbol'], volume=volume, entrust_bs=bs)
                    if len(r) > 0 and r[0].has_key('error_info'):
                        raise TraderError(u"撤销失败!%s" % (r[0].has_key('error_info')))
        if not is_have:
            raise TraderError(u"撤销对象已失效")
        return True

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
        if stock == None:
            raise TraderError(u"没有查询要操作的股票信息")
        if not volume:
            volume = int(price * amount)  # 可能要取整数
        if balance['current_balance'] < volume and entrust_bs == 'buy':
            raise TraderError(u"没有足够的现金进行操作")
        if stock['flag'] != 1:
            raise TraderError(u"未上市、停牌、涨跌停、退市的股票无法操作。")
        if volume==0:
            raise TraderError(u"操作金额不能为零")

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
                        raise TraderError(u"操作数量大于实际可卖出数量")
                    else:
                        position['weight'] = old_weight - weight
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
                    "weight": weight,
                    "url": "/S/" + stock['code'],
                    "proactive": True,
                    "price": str(stock['current'])
                })
            else:
                raise TraderError(u"没有持有要卖出的股票")

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
        if six.PY2:
            data = (urllib.urlencode(data))
        else:
            data = (urllib.parse.urlencode(data))

        self.headers['Referer'] = self.config['referer'] % self.account_config['portfolio_code']

        try:
            rebalance_res = self.requests.session().post(self.config['rebalance_url'], headers=self.headers,
                                                         cookies=self.cookies,
                                                         params=data)
        except Exception as e:
            log.warn('调仓失败: %s ' % e)
            return
        else:
            log.debug('调仓 %s%s: %d' % (entrust_bs, stock['name'], rebalance_res.status_code))
            rebalance_status = json.loads(rebalance_res.text)
            if 'error_description' in rebalance_status.keys() and rebalance_res.status_code != 200:
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
        :param entrust_prop: 雪球直接市价
        """
        return self.__trade(stock_code, price, amount, volume, 'buy')

    def sell(self, stock_code, price=0, amount=0, volume=0, entrust_prop=0):
        """卖出股票
        :param stock_code:
        :param price:
        :param amount:
        :param volume:
        :param entrust_prop:
        :return:
        """
        return self.__trade(stock_code, price, amount, volume, 'sell')

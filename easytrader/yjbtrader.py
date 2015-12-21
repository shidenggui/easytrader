# coding: utf-8
import json
import random
import re
import requests
import os
from . import helpers
from .webtrader import WebTrader
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class YJBTrader(WebTrader):
    config_path = os.path.dirname(__file__) + '/config/yjb.json'

    def __init__(self):
        super().__init__()
        self.cookie = None

    @property
    def token(self):
        return self.cookie['JSESSIONID']

    @token.setter
    def token(self, token):
        self.cookie = dict(JSESSIONID=token)
        self.keepalive()

    # TODO: 实现撤单
    def cancel_order(self):
        pass

    # TODO: 实现买入卖出的各种委托类型
    def buy(self, stock_code, price, amount=0, volume=0, entrust_prop=0):
        """买入卖出股票
        :param stock_code: 股票代码
        :param price: 卖出价格
        :param amount: 卖出总金额 由 volume / price 取整， 若指定 price 则此参数无效
        :param entrust_prop: 委托类型，暂未实现，默认为限价委托
        """
        params = dict(
            self.config['buy'],
            entrust_bs=1,  # 买入1 卖出2
            entrust_amount=amount if amount else volume // price // 100 * 100
        )
        return self.__trade(stock_code, price, entrust_prop=entrust_prop, other=params)

    def sell(self, stock_code, price, amount=0, volume=0, entrust_prop=0):
        """卖出股票
        :param stock_code: 股票代码
        :param price: 卖出价格
        :param amount: 卖出总金额 由 volume / price 取整， 若指定 price 则此参数无效
        :param entrust_prop: 委托类型，暂未实现，默认为限价委托
        """
        params = dict(
            self.config['sell'],
            entrust_bs=2,  # 买入1 卖出2
            entrust_amount=amount if amount else volume // price
        )
        return self.__trade(stock_code, price, entrust_prop=entrust_prop, other=params)

    def __trade(self, stock_code, price, entrust_prop, other):
        # 检查是否已经掉线
        if not self.heart_thread.is_alive():
            check_data = self.get_balance()
            if type(check_data) == dict:
                return check_data
        need_info = self.__get_trade_need_info(stock_code)
        return self.do(dict(
                other,
                stock_account=need_info['stock_account'],  # '沪深帐号'
                exchange_type=need_info['exchange_type'],  # '沪市1 深市2'
                entrust_prop=entrust_prop,  # 委托方式
                stock_code='{:0>6}'.format(stock_code),  # 股票代码, 右对齐宽为6左侧填充0
                elig_riskmatch_flag=1,  # 用户风险等级
                entrust_price=price,
            ))

    def __get_trade_need_info(self, stock_code):
        """获取股票对应的证券市场和帐号"""
        # 获取股票对应的证券市场
        sh_exchange_type = 1
        sz_exchange_type = 2
        exchange_type = sh_exchange_type if helpers.get_stock_type(stock_code) == 'sh' else sz_exchange_type
        # 获取股票对应的证券帐号
        if not hasattr(self, 'exchange_stock_account'):
            self.exchange_stock_account = dict()
        if exchange_type not in self.exchange_stock_account:
            stock_account_index = 0
            response_data = self.do(dict(
                    self.config['account4stock'],
                    exchange_type=exchange_type,
                    stock_code=stock_code
                ))[stock_account_index]
            self.exchange_stock_account[exchange_type] = response_data['stock_account']
        return dict(
            exchange_type=exchange_type,
            stock_account=self.exchange_stock_account[exchange_type]
        )

    def do(self, params):
        """发起对 api 的请求并过滤返回结果"""
        request_params = self.__create_basic_params()
        request_params.update(params)
        data = self.__request(request_params)
        data = self.__format_response_data(data)
        return self.__fix_error_data(data)

    def __create_basic_params(self):
        """生成基本的参数"""
        basic_params = dict(
            CSRF_Token='undefined',
            timestamp=random.random(),
        )
        return basic_params

    def __request(self, params):
        """请求并获取 JSON 数据"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
        }
        r = requests.get(self.trade_prefix, params=params, cookies=self.cookie, headers=headers)
        return r.text

    def __format_response_data(self, data, header=False):
        """格式化返回的 json 数据"""
        # 获取 returnJSON
        return_json = json.loads(data)['returnJson']
        add_key_quote = re.sub('\w+:', lambda x: '"%s":' % x.group().rstrip(':'), return_json)
        # 替换所有单引号到双引号
        change_single_double_quote = add_key_quote.replace("'", '"')
        raw_json_data = json.loads(change_single_double_quote)
        fun_data = raw_json_data['Func%s' % raw_json_data['function_id']]
        header_index = 1
        return fun_data if header else fun_data[header_index:]

    def __fix_error_data(self, data):
        """若是返回错误移除外层的列表"""
        error_index = 0
        return data[error_index] if type(data) == list and data[error_index].get('error_no') != None else data

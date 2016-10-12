# coding: utf-8
from __future__ import division

import json
import os
import random
import tempfile
import urllib

import demjson
import requests
import six

from . import helpers
from .log import log
from .webtrader import NotLoginError
from .webtrader import WebTrader


class YJBTrader(WebTrader):
    config_path = os.path.dirname(__file__) + '/config/yjb.json'

    def __init__(self):
        super(YJBTrader, self).__init__()
        self.account_config = None
        self.s = requests.session()
        self.s.mount('https://', helpers.Ssl3HttpAdapter())

    def login(self, throw=False):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
        }
        self.s.headers.update(headers)

        self.s.get(self.config['login_page'])

        verify_code = self.handle_recognize_code()
        if not verify_code:
            return False
        login_status, result = self.post_login_data(verify_code)
        if login_status is False and throw:
            raise NotLoginError(result)
        return login_status

    def handle_recognize_code(self):
        """获取并识别返回的验证码
        :return:失败返回 False 成功返回 验证码"""
        # 获取验证码
        verify_code_response = self.s.get(self.config['verify_code_api'], params=dict(randomStamp=random.random()))
        # 保存验证码
        image_path = os.path.join(tempfile.gettempdir(), 'vcode_%d' % os.getpid())
        with open(image_path, 'wb') as f:
            f.write(verify_code_response.content)

        verify_code = helpers.recognize_verify_code(image_path, 'yjb')
        log.debug('verify code detect result: %s' % verify_code)
        os.remove(image_path)

        ht_verify_code_length = 4
        if len(verify_code) != ht_verify_code_length:
            return False
        return verify_code

    def post_login_data(self, verify_code):
        if six.PY2:
            password = urllib.unquote(self.account_config['password'])
        else:
            password = urllib.parse.unquote(self.account_config['password'])
        login_params = dict(
            self.config['login'],
            mac_addr=helpers.get_mac(),
            account_content=self.account_config['account'],
            password=password,
            validateCode=verify_code
        )
        login_response = self.s.post(self.config['login_api'], params=login_params)
        log.debug('login response: %s' % login_response.text)

        if login_response.text.find('上次登陆') != -1:
            return True, None
        return False, login_response.text

    def cancel_entrust(self, entrust_no, stock_code):
        """撤单
        :param entrust_no: 委托单号
        :param stock_code: 股票代码"""
        cancel_params = dict(
            self.config['cancel_entrust'],
            entrust_no=entrust_no,
            stock_code=stock_code
        )
        return self.do(cancel_params)

    @property
    def current_deal(self):
        return self.get_current_deal()

    def get_current_deal(self):
        """获取当日成交列表"""
        """
        [{'business_amount': '成交数量',
        'business_price': '成交价格',
        'entrust_amount': '委托数量',
        'entrust_bs': '买卖方向',
        'stock_account': '证券帐号',
        'fund_account': '资金帐号',
        'position_str': '定位串',
        'business_status': '成交状态',
        'date': '发生日期',
        'business_type': '成交类别',
        'business_time': '成交时间',
        'stock_code': '证券代码',
        'stock_name': '证券名称'}]
        """
        return self.do(self.config['current_deal'])

    # TODO: 实现买入卖出的各种委托类型
    def buy(self, stock_code, price, amount=0, volume=0, entrust_prop=0):
        """买入卖出股票
        :param stock_code: 股票代码
        :param price: 卖出价格
        :param amount: 卖出股数
        :param volume: 卖出总金额 由 volume / price 取整， 若指定 price 则此参数无效
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
        :param amount: 卖出股数
        :param volume: 卖出总金额 由 volume / price 取整， 若指定 amount 则此参数无效
        :param entrust_prop: 委托类型，暂未实现，默认为限价委托
        """
        params = dict(
            self.config['sell'],
            entrust_bs=2,  # 买入1 卖出2
            entrust_amount=amount if amount else volume // price
        )
        return self.__trade(stock_code, price, entrust_prop=entrust_prop, other=params)

    def get_ipo_limit(self, stock_code):
        """
        查询新股申购额度申购上限
        :param stock_code: 申购代码!!!
        :return: high_amount(最高申购股数) enable_amount(申购额度) last_price(发行价)
        """
        need_info = self.__get_trade_need_info(stock_code)
        params = dict(
            self.config['ipo_enable_amount'],
            CSRF_Token='undefined',
            timestamp=random.random(),
            stock_account=need_info['stock_account'],  # '沪深帐号'
            exchange_type=need_info['exchange_type'],  # '沪市1 深市2'
            entrust_prop=0,
            stock_code=stock_code
        )
        data = self.do(params)
        if 'error_no' in data.keys() and data['error_no'] != "0":
            log.debug('查询错误: %s' % (data['error_info']))
            return None
        return dict(high_amount=float(data['high_amount']), enable_amount=data['enable_amount'],
                    last_price=float(data['last_price']))

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

    def create_basic_params(self):
        basic_params = dict(
            CSRF_Token='undefined',
            timestamp=random.random(),
        )
        return basic_params

    def request(self, params):
        r = self.s.get(self.trade_prefix, params=params)
        return r.text

    def format_response_data(self, data):
        # 获取 returnJSON
        return_json = json.loads(data)['returnJson']
        raw_json_data = demjson.decode(return_json)
        fun_data = raw_json_data['Func%s' % raw_json_data['function_id']]
        header_index = 1
        remove_header_data = fun_data[header_index:]
        return self.format_response_data_type(remove_header_data)

    def fix_error_data(self, data):
        error_index = 0
        return data[error_index] if type(data) == list and data[error_index].get('error_no') is not None else data

    def check_login_status(self, return_data):
        if hasattr(return_data, 'get') and return_data.get('error_no') == '-1':
            raise NotLoginError

    def check_account_live(self, response):
        if hasattr(response, 'get') and response.get('error_no') == '-1':
            self.heart_active = False

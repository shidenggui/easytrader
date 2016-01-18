# coding: utf-8
import json
import random
import urllib
import re
import os
import sys
import ssl
import requests
import logbook
from logbook import Logger, StreamHandler
from . import helpers
from .webtrader import WebTrader
from .webtrader import NotLoginError
from requests import Request, Session

logbook.set_datetime_format('local')
StreamHandler(sys.stdout).push_application()
log = Logger(os.path.basename(__file__))

VERIFY_CODE_POS = 0
BALANCE_NUM = 7

class YHTrader(WebTrader):
    config_path = os.path.dirname(__file__) + '/config/yh.json'

    def __init__(self):
        super().__init__()
        self.cookie = None
        self.account_config = None
        self.s = None

    def login(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        }
        if self.s is not None:
            self.s.get(self.config['logout_api'])
        self.s = requests.session()
        self.s.headers.update(headers)
        data = self.s.get(self.config['login_page'])

        #查找验证码
        search_result = re.search(r'src=\"verifyCodeImage.jsp\?rd=([0-9]{4})\"', data.text)
        if not search_result:
            log.debug("Can not find verify code, stop login")
            return False

        verify_code = search_result.groups()[VERIFY_CODE_POS]

        if not verify_code:
            return False

        login_status = self.post_login_data(verify_code)
        return login_status

    def post_login_data(self, verify_code):
        login_params = dict(
                self.config['login'],
                mac=helpers.get_mac(),
                clientip='',
                inputaccount=self.account_config['inputaccount'],
                trdpwd=self.account_config['trdpwd'],
                checkword=verify_code
        )
        log.debug('login params: %s' % login_params)
        s = Session()
        req = Request('POST', self.config['login_api'], data=login_params, headers=self.s.headers)
        preped = s.prepare_request(req)
        log.debug(preped.body)
        log.debug(preped.headers)
        login_response = self.s.post(self.config['login_api'], params=login_params)
        log.debug('login response: %s' % login_response.text)
        if login_response.text.find('success') != -1:
            return True
        return False

    @property
    def token(self):
        return self.cookie['JSESSIONID']

    @token.setter
    def token(self, token):
        self.cookie = dict(JSESSIONID=token)
        self.keepalive()

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
        url = self.trade_prefix + params['service_jsp']
        r = self.s.get(url, cookies=self.cookie)
        return r.text

    def format_response_data(self, data):
        # 获取原始data的html源码并且解析得到一个可读json格式 
        search_result = re.findall(r'<td nowrap=\"nowrap\">(.*)&nbsp;</td>', data) 
        if len(search_result) < BALANCE_NUM:
            log.error("Can not fetch balance info")
            retdata = json.dumps(search_result)
            retjsonobj = json.loads(retdata)
        else:
            retdict = dict()
            retdict['account'] = search_result[0]
            retdict['currency'] = search_result[1]
            retdict['fundbalance'] = search_result[2]
            retdict['available'] = search_result[3]
            retdict['refmarket'] = search_result[4]
            retdict['totalasset'] = search_result[5]
            retdict['refratio'] = search_result[6]
            retdata = json.dumps(retdict)
            retjsonobj = json.loads(retdata)
        return retjsonobj

    def fix_error_data(self, data):
        return data

    def check_login_status(self, return_data):
        pass

    def check_account_live(self, response):
        if hasattr(response, 'get') and response.get('error_no') == '-1':
            self.heart_active = False

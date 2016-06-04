# coding: utf-8
from __future__ import division

import os
import random
import re

import requests

from . import helpers
from .helpers import EntrustProp
from .webtrader import WebTrader, NotLoginError

log = helpers.get_logger(__file__)

VERIFY_CODE_POS = 0
TRADE_MARKET = 1
HOLDER_NAME = 0


class YHTrader(WebTrader):
    config_path = os.path.dirname(__file__) + '/config/yh.json'

    def __init__(self):
        super(YHTrader, self).__init__()
        self.cookie = None
        self.account_config = None
        self.s = None
        self.exchange_stock_account = dict()

    def login(self, throw=False):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        }
        if self.s is not None:
            self.s.get(self.config['logout_api'])
        self.s = requests.session()
        self.s.headers.update(headers)
        data = self.s.get(self.config['login_page'])

        # 查找验证码
        verify_code = self.handle_recognize_code()

        if not verify_code:
            return False

        login_status, result = self.post_login_data(verify_code)
        if login_status is False and throw:
            raise NotLoginError(result)

        accounts = self.do(self.config['account4stock'])
        if len(accounts) < 2:
            raise Exception('无法获取沪深 A 股账户: %s' % accounts)
        for account in accounts:
            if account['交易市场'] == '深A':
                self.exchange_stock_account['0'] = account['股东代码'][0:10]
            else:
                self.exchange_stock_account['1'] = account['股东代码'][0:10]
        return login_status

    def handle_recognize_code(self):
        """获取并识别返回的验证码
        :return:失败返回 False 成功返回 验证码"""
        # 获取验证码
        verify_code_response = self.s.get(self.config['verify_code_api'], params=dict(randomStamp=random.random()))
        # 保存验证码
        image_path = os.path.join(os.getcwd(), 'vcode')
        with open(image_path, 'wb') as f:
            f.write(verify_code_response.content)

        verify_code = helpers.recognize_verify_code(image_path, 'yh')
        log.debug('verify code detect result: %s' % verify_code)

        ht_verify_code_length = 4
        if len(verify_code) != ht_verify_code_length:
            return False
        return verify_code

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
        login_response = self.s.post(self.config['login_api'], params=login_params)
        log.debug('login response: %s' % login_response.text)

        if login_response.text.find('success') != -1:
            return True, None
        return False, login_response.text

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
        need_info = self.__get_trade_need_info(stock_code)
        cancel_params = dict(
                self.config['cancel_entrust'],
                orderSno=entrust_no,
                secuid=need_info['stock_account']
        )
        cancel_response = self.s.post(self.config['trade_api'], params=cancel_params)
        log.debug('cancel trust: %s' % cancel_response.text)
        return True

    @property
    def current_deal(self):
        return self.get_current_deal()

    def get_current_deal(self):
        """获取当日成交列表."""
        return self.do(self.config['current_deal'])

    def buy(self, stock_code, price, amount=0, volume=0, entrust_prop=EntrustProp.Limit):
        """买入股票
        :param stock_code: 股票代码
        :param price: 买入价格
        :param amount: 买入股数
        :param volume: 买入总金额 由 volume / price 取整， 若指定 price 则此参数无效
        :param entrust_prop: 委托类型
        """
        market_type = helpers.get_stock_type(stock_code)
        if entrust_prop == EntrustProp.Limit:
            bsflag = '0B'
        elif market_type == 'sh':
            bsflag = '0q'
        elif market_type == 'sz':
            bsflag = '0a'

        params = dict(
                self.config['buy'],
                bsflag=bsflag,
                qty=amount if amount else volume // price // 100 * 100
        )
        return self.__trade(stock_code, price, entrust_prop=entrust_prop, other=params)

    def sell(self, stock_code, price, amount=0, volume=0, entrust_prop=EntrustProp.Limit):
        """卖出股票
        :param stock_code: 股票代码
        :param price: 卖出价格
        :param amount: 卖出股数
        :param volume: 卖出总金额 由 volume / price 取整， 若指定 amount 则此参数无效
        :param entrust_prop: 委托类型
        """
        market_type = helpers.get_stock_type(stock_code)
        if entrust_prop == EntrustProp.Limit:
            bsflag = '0S'
        elif market_type == 'sh':
            bsflag = '0r'
        elif market_type == 'sz':
            bsflag = '0f'

        params = dict(
                self.config['sell'],
                bsflag=bsflag,
                qty=amount if amount else volume // price
        )
        return self.__trade(stock_code, price, entrust_prop=entrust_prop, other=params)

    def fundpurchase(self, stock_code, amount=0):
        """基金申购
        :param stock_code: 基金代码
        :param amount: 申购份额
        """
        params = dict(
                self.config['fundpurchase'],
                price=1,  # 价格默认为1
                qty=amount
        )
        return self.__tradefund(stock_code, other=params)

    def fundredemption(self, stock_code, amount=0):
        """基金赎回
        :param stock_code: 基金代码
        :param amount: 赎回份额
        """
        params = dict(
                self.config['fundredemption'],
                price=1,  # 价格默认为1
                qty=amount
        )
        return self.__tradefund(stock_code, other=params)

    def fundsubscribe(self, stock_code, amount=0):
        """基金认购
        :param stock_code: 基金代码
        :param amount: 认购份额
        """
        params = dict(
                self.config['fundsubscribe'],
                price=1,  # 价格默认为1
                qty=amount
        )
        return self.__tradefund(stock_code, other=params)

    def fundsplit(self, stock_code, amount=0):
        """基金分拆
        :param stock_code: 母份额基金代码
        :param amount: 分拆份额
        """
        params = dict(
                self.config['fundsplit'],
                qty=amount
        )
        return self.__tradefund(stock_code, other=params)

    def fundmerge(self, stock_code, amount=0):
        """基金合并
        :param stock_code: 母份额基金代码
        :param amount: 合并份额
        """
        params = dict(
                self.config['fundmerge'],
                qty=amount
        )
        return self.__tradefund(stock_code, other=params)

    def __tradefund(self, stock_code, other):
        # 检查是否已经掉线
        if not self.heart_thread.is_alive():
            check_data = self.get_balance()
            if type(check_data) == dict:
                return check_data
        need_info = self.__get_trade_need_info(stock_code)
        trade_params = dict(
                other,
                stockCode=stock_code,
                market=need_info['exchange_type'],
                secuid=need_info['stock_account']
        )

        trade_response = self.s.post(self.config['trade_api'], params=trade_params)
        log.debug('trade response: %s' % trade_response.text)
        return trade_response.json()

    def __trade(self, stock_code, price, entrust_prop, other):
        # 检查是否已经掉线
        if not self.heart_thread.is_alive():
            check_data = self.get_balance()
            if type(check_data) == dict:
                return check_data
        need_info = self.__get_trade_need_info(stock_code)
        trade_params = dict(
                other,
                stockCode=stock_code,
                price=price,
                market=need_info['exchange_type'],
                secuid=need_info['stock_account']
        )
        trade_response = self.s.post(self.config['trade_api'], params=trade_params)
        log.debug('trade response: %s' % trade_response.text)
        return trade_response.json()

    def __get_trade_need_info(self, stock_code):
        """获取股票对应的证券市场和帐号"""
        sh_exchange_type = '1'
        sz_exchange_type = '0'
        exchange_type = sh_exchange_type if helpers.get_stock_type(stock_code) == 'sh' else sz_exchange_type
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
        if params['service_jsp'] == '/trade/webtrade/stock/stock_zjgf_query.jsp':
            if params['service_type'] == 2:
                rptext = r.text[0:r.text.find('操作')]
                return rptext
            else:
                rbtext = r.text[r.text.find('操作'):]
                rbtext += 'yhposition'
                return rbtext
        else:
            return r.text

    def format_response_data(self, data):
        # 需要对于银河持仓情况特殊处理
        if data.find('yhposition') != -1:
            search_result_name = re.findall(r'<td nowrap=\"nowrap\" class=\"head(?:\w{0,5})\">(.*)</td>', data)
            search_result_content = []
            search_result_content_tmp = re.findall(r'<td nowrap=\"nowrap\" ( |style.*)>(.*)</td>', data)
            for item in search_result_content_tmp:
                s = item[-1] if type(item) is not str else item
                k = re.findall(">(.*)<", s)
                if len(k) > 0:
                    s = k[-1]
                search_result_content.append(s)
        else:
            # 获取原始data的html源码并且解析得到一个可读json格式 
            search_result_name = re.findall(r'<td nowrap=\"nowrap\" class=\"head(?:\w{0,5})\">(.*)</td>', data)
            search_result_content = re.findall(r'<td nowrap=\"nowrap\">(.*)&nbsp;</td>', data)

        col_len = len(search_result_name)
        if col_len == 0 or len(search_result_content) % col_len != 0:
            if len(search_result_content) == 0:
                return list()
            raise Exception("Get Data Error: col_num: {}, Data: {}".format(col_len, search_result_content))
        else:
            row_len = len(search_result_content) // col_len
            res = list()
            for row in range(row_len):
                item = dict()
                for col in range(col_len):
                    col_name = search_result_name[col]
                    item[col_name] = search_result_content[row * col_len + col]
                res.append(item)

        return self.format_response_data_type(res)

    def check_account_live(self, response):
        if hasattr(response, 'get') and response.get('error_no') == '-1':
            self.heart_active = False

    def heartbeat(self):
        heartbeat_params = dict(
                ftype='bsn'
        )
        self.s.post(self.config['heart_beat'], params=heartbeat_params)

    def unlockscreen(self):
        unlock_params = dict(
                password=self.account_config['trdpwd'],
                mainAccount=self.account_config['inputaccount'],
                ftype='bsn'
        )
        log.debug('unlock params: %s' % unlock_params)
        unlock_resp = self.s.post(self.config['unlock'], params=unlock_params)
        log.debug('unlock resp: %s' % unlock_resp.text)

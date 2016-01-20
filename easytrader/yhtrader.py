# coding: utf-8
import json
import random
import re
import os
import requests
from . import helpers
from .webtrader import WebTrader

log = helpers.get_logger(__file__)

VERIFY_CODE_POS = 0
TRADE_MARKET = 1
HOLDER_NAME = 0


class YHTrader(WebTrader):
    config_path = os.path.dirname(__file__) + '/config/yh.json'

    def __init__(self):
        super().__init__()
        self.cookie = None
        self.account_config = None
        self.s = None
        self.exchange_stock_account = dict()

    def login(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        }
        if self.s is not None:
            self.s.get(self.config['logout_api'])
        self.s = requests.session()
        self.s.headers.update(headers)
        data = self.s.get(self.config['login_page'])

        # 查找验证码
        search_result = re.search(r'src=\"verifyCodeImage.jsp\?rd=([0-9]{4})\"', data.text)
        if not search_result:
            log.debug("Can not find verify code, stop login")
            return False

        verify_code = search_result.groups()[VERIFY_CODE_POS]

        if not verify_code:
            return False

        login_status = self.post_login_data(verify_code)
        exchangeinfo = list((self.do(dict(self.config['account4stock']))))
        if len(exchangeinfo) >= 2:
            for i in range(2):
                if exchangeinfo[i][TRADE_MARKET]['交易市场'] == '深A':
                    self.exchange_stock_account['0'] = exchangeinfo[i][HOLDER_NAME]['股东代码'][0:10]
                else:
                    self.exchange_stock_account['1'] = exchangeinfo[i][HOLDER_NAME]['股东代码'][0:10]
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
        need_info = self.__get_trade_need_info(stock_code)
        cancel_params = dict(
            self.config['cancel_entrust'],
            orderSno=entrust_no,
            secuid=need_info['stock_account']
        )
        cancel_response = self.s.post(self.config['trade_api'], params=cancel_params)
        log.debug('cancel trust: %s' % cancel_response.text)
        return True

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
            bsflag='0B',  # 买入0B 卖出0S
            qty=amount if amount else volume // price // 100 * 100
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
            bsflag='0S',  # 买入0B 卖出0S
            qty=amount if amount else volume // price
        )
        return self.__trade(stock_code, price, entrust_prop=entrust_prop, other=params)

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
        return True
                  
    def __get_trade_need_info(self, stock_code):
        """获取股票对应的证券市场和帐号"""
        # 获取股票对应的证券市场
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
        return r.text

    def format_response_data(self, data):
        # 获取原始data的html源码并且解析得到一个可读json格式 
        search_result_name = re.findall(r'<td nowrap=\"nowrap\" class=\"head(?:\w{0,5})\">(.*)</td>', data)
        search_result_content = re.findall(r'<td nowrap=\"nowrap\">(.*)&nbsp;</td>', data) 
        columnlen = len(search_result_name)
        if len(search_result_content) % columnlen != 0:
            log.error("Can not fetch balance info")
            retdata = json.dumps(search_result_name)
            retjsonobj = json.loads(retdata)
        else:
            rowlen = len(search_result_content) // columnlen
            retdata = list()
            for i in range(rowlen):
                retrowdata = list()
                for j in range(columnlen):
                    retdict = dict()
                    retdict[search_result_name[j]] = search_result_content[i * columnlen + j]
                    retrowdata.append(retdict)
                retdata.append(retrowdata)
            retlist = json.dumps(retdata)
            retjsonobj = json.loads(retlist)
        return retjsonobj

    def fix_error_data(self, data):
        return data

    def check_login_status(self, return_data):
        pass

    def check_account_live(self, response):
        if hasattr(response, 'get') and response.get('error_no') == '-1':
            self.heart_active = False

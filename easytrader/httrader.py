# coding: utf-8
import json
import random
import re
import requests
import os
import uuid
import socket
import base64
import urllib
import threading
from collections import OrderedDict
from . import helpers
from .webtrader import WebTrader

log = helpers.get_logger(__file__)

# 移除心跳线程产生的日志
debug_log = log.debug


def remove_heart_log(*args, **kwargs):
    if threading.currentThread().name == "MainThread":
        debug_log(*args, **kwargs)

log.debug = remove_heart_log


class HTTrader(WebTrader):
    config_path = os.path.dirname(__file__) + '/config/ht.json'

    def __init__(self):
        super(HTTrader, self).__init__()
        self.account_config = None
        self.s = None

        self.__set_ip_and_mac()
        self.fund_account = None

    def __set_ip_and_mac(self):
        """获取本机IP和MAC地址"""
        # 获取ip
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("baidu.com", 80))
        self.__ip = s.getsockname()[0]
        s.close()

        # 获取mac地址 link: http://stackoverflow.com/questions/28927958/python-get-mac-address
        self.__mac = ("".join(c + "-" if i % 2 else c for i, c in enumerate(hex(
                uuid.getnode())[2:].zfill(12)))[:-1]).upper()

    def __get_user_name(self):
        # 华泰账户以 08 开头的需移除 fund_account 开头的 0
        raw_name = self.account_config['userName']
        use_index_start = 1
        return raw_name[use_index_start:] if raw_name.startswith('08') else raw_name

    def prepare(self, need_data):
        """登录的统一接口
        :param need_data 登录所需数据"""
        self.read_config(need_data)
        self.fund_account = self.__get_user_name()
        self.autologin()

    def login(self):
        """实现华泰的自动登录"""
        self.__go_login_page()

        verify_code = self.__handle_recognize_code()
        if not verify_code:
            return False

        is_login = self.__check_login_status(verify_code)
        if not is_login:
            return False

        trade_info = self.__get_trade_info()
        if not trade_info:
            return False

        self.__set_trade_need_info(trade_info)

        return True

    def __go_login_page(self):
        """访问登录页面获取 cookie"""
        if self.s is not None:
            self.s.get(self.config['logout_api'])
        self.s = requests.session()
        self.s.get(self.config['login_page'])

    def __handle_recognize_code(self):
        """获取并识别返回的验证码
        :return:失败返回 False 成功返回 验证码"""
        # 获取验证码
        verify_code_response = self.s.get(self.config['verify_code_api'])
        # 保存验证码
        image_path = os.path.join(os.getcwd(), 'vcode')
        with open(image_path, 'wb') as f:
            f.write(verify_code_response.content)

        verify_code = helpers.recognize_verify_code(image_path)
        log.debug('verify code detect result: %s' % verify_code)
        os.remove(image_path)

        ht_verify_code_length = 4
        if len(verify_code) != ht_verify_code_length:
            return False
        return verify_code

    def __check_login_status(self, verify_code):
        # 设置登录所需参数
        params = dict(
                userName=self.account_config['userName'],
                trdpwd=self.account_config['trdpwd'],
                trdpwdEns=self.account_config['trdpwd'],
                servicePwd=self.account_config['servicePwd'],
                macaddr=self.__mac,
                lipInfo=self.__ip,
                vcode=verify_code
        )
        params.update(self.config['login'])

        log.debug('login params: %s' % params)
        login_api_response = self.s.post(self.config['login_api'], params)

        if login_api_response.text.find(u'欢迎您') == -1:
            return False
        return True

    def __get_trade_info(self):
        """ 请求页面获取交易所需的 uid 和 password """
        trade_info_response = self.s.get(self.config['trade_info_page'])

        # 查找登录信息
        search_result = re.search(r'var data = "([/=\w\+]+)"', trade_info_response.text)
        if not search_result:
            return False

        need_data_index = 0
        need_data = search_result.groups()[need_data_index]
        bytes_data = base64.b64decode(need_data)
        log.debug('trade info bytes data: ', bytes_data)
        try:
            str_data = bytes_data.decode('gbk')
        except UnicodeDecodeError:
            str_data = bytes_data.decode('gb2312', errors='ignore')
        log.debug('trade info: %s' % str_data)
        json_data = json.loads(str_data)
        return json_data

    def __set_trade_need_info(self, json_data):
        """设置交易所需的一些基本参数
        :param json_data:登录成功返回的json数据
        """
        for account_info in json_data['item']:
            if account_info['stock_account'].startswith('A'):
                self.__sh_exchange_type = account_info['exchange_type']
                self.__sh_stock_account = account_info['stock_account']
                log.debug('sh stock account %s' % self.__sh_stock_account)
            elif account_info['stock_account'].isdigit():
                self.__sz_exchange_type = account_info['exchange_type']
                self.__sz_stock_account = account_info['stock_account']
                log.debug('sz stock account %s' % self.__sz_stock_account)

        self.__fund_account = json_data['fund_account']
        self.__client_risklevel = json_data['branch_no']
        self.__op_station = json_data['op_station']
        self.__trdpwd = json_data['trdpwd']
        self.__uid = json_data['uid']
        self.__branch_no = json_data['branch_no']

    def cancel_entrust(self, entrust_no):
        """撤单
        :param entrust_no: 委托单号"""
        cancel_params = dict(
            self.config['cancel_entrust'],
            password=self.__trdpwd,
            entrust_no=entrust_no
        )
        return self.do(cancel_params)

    # TODO: 实现买入卖出的各种委托类型
    def buy(self, stock_code, price, amount=0, volume=0, entrust_prop=0):
        """买入卖出股票
        :param stock_code: 股票代码
        :param price: 买入价格
        :param amount: 买入股数
        :param volume: 买入总金额 由 volume / price 取 100 的整数， 若指定 amount 则此参数无效
        :param entrust_prop: 委托类型，暂未实现，默认为限价委托
        """
        params = dict(
                self.config['buy'],
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
                entrust_amount=amount if amount else volume // price
        )
        return self.__trade(stock_code, price, entrust_prop=entrust_prop, other=params)

    def __trade(self, stock_code, price, entrust_prop, other):
        need_info = self.__get_trade_need_info(stock_code)
        return self.do(dict(
                other,
                stock_account=need_info['stock_account'],  # '沪深帐号'
                exchange_type=need_info['exchange_type'],  # '沪市1 深市2'
                entrust_prop=entrust_prop,  # 委托方式
                stock_code='{:0>6}'.format(stock_code),  # 股票代码, 右对齐宽为6左侧填充0
                entrust_price=price
        ))

    def __get_trade_need_info(self, stock_code):
        """获取股票对应的证券市场和帐号"""
        # 获取股票对应的证券市场
        exchange_type = self.__sh_exchange_type if helpers.get_stock_type(stock_code) == 'sh' \
            else self.__sz_exchange_type
        # 获取股票对应的证券帐号
        stock_account = self.__sh_stock_account if exchange_type == self.__sh_exchange_type \
            else self.__sz_stock_account
        return dict(
                exchange_type=exchange_type,
                stock_account=stock_account
        )

    def create_basic_params(self):
        basic_params = OrderedDict(
                uid=self.__uid,
                version=1,
                custid=self.account_config['userName'],
                op_branch_no=self.__branch_no,
                branch_no=self.__branch_no,
                op_entrust_way=7,
                op_station=self.__op_station,
                fund_account=self.fund_account,
                password=self.__trdpwd,
                identity_type='',
                ram=random.random()
        )
        return basic_params

    def request(self, params):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
        }

        key = "ram"
        val = params[key]
        del params[key]
        params[key] = val

        params_str = urllib.urlencode(params)
        unquote_str = urllib.unquote(params_str)
        log.debug('request params: %s' % unquote_str)
        b64params = base64.b64encode(unquote_str.encode()).decode()
        r = self.s.get('{prefix}/?{b64params}'.format(prefix=self.trade_prefix, b64params=b64params), headers=headers)
        return r.content

    def format_response_data(self, data):
        bytes_str = base64.b64decode(data)
        gbk_str = bytes_str.decode('gbk')
        log.debug('response data before format: %s' % gbk_str)
        filter_empty_list = gbk_str.replace('[]', 'null')
        filter_return = filter_empty_list.replace('\n', '')
        log.debug('response data: %s' % filter_return)
        response_data = json.loads(filter_return)
        if response_data['cssweb_code'] == 'error' or response_data['item'] is None:
            return response_data
        return_data = self.format_response_data_type(response_data['item'])
        log.debug('response data: %s' % return_data)
        return return_data

    def fix_error_data(self, data):
        last_no_use_info_index = -1
        return data if hasattr(data, 'get') else data[:last_no_use_info_index]

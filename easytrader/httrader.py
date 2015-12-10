
# coding: utf-8
import json
import random
import re
import requests
import time
import os
from multiprocessing import Process
from easytrader import WebTrader
from . import helpers
import uuid
import socket
import base64
import urllib
from logbook import Logger, StreamHandler
import sys


class HTTrader(WebTrader):
    config_path = os.path.dirname(__file__) + '/config/ht.json'

    def __init__(self, account='', password=''):
        super().__init__()
        self.__set_ip_and_mac()
        StreamHandler(sys.stdout).push_application()
        self.log = Logger('HTTrader')

    def read_config(self, path):
        account_config = helpers.file2dict(path)
        self.__account = account_config['userName']
        self.__encrypted_password = account_config['trdpwd']
        self.__service_password = account_config['servicePwd']

    def autologin(self):
        """实现华泰的自动登录"""
        self.s = requests.session()
        # 进入华泰登录页面
        login_page_response = self.s.get(self.config['login_page'])
        # 获取验证码
        verify_code_response = self.s.get(self.config['verify_code_api'], data=dict(ran=random.random))
        # 保存验证码
        with open('vcode', 'wb') as f:
            f.write(verify_code_response.content)
        # 调用tesseract识别
        os.system('export TESSDATA_PREFIX="/usr/share/tesseract-ocr/tessdata/"; tesseract vcode result')
        # os.system('tesseract vcode result')

        # 获取识别的验证码
        with open('result.txt') as f:
            vcode = f.readline()
            # 移除空格和换行符
            vcode = vcode.replace(' ', '')[:-1]
            if len(vcode) != 4:
                return False

        os.remove('result.txt')
        os.remove('vcode')

        # 设置登录所需参数
        params = dict(
            userName=self.__account,
            trdpwd=self.__encrypted_password,
            trdpwdEns=self.__encrypted_password,
            servicePwd=self.__service_password,
            macaddr=self.__mac,
            lipInfo=self.__ip,
            vcode=vcode
        )
        params.update(self.config['login'])

        login_api_response = self.s.post(self.config['login_api'], params)

        if login_api_response.text.find('欢迎您登录') == -1:
            return False

        # 请求下列页面获取交易所需的 uid 和 password
        trade_info_response = self.s.get(self.config['trade_info_page'])

        # 查找登录信息
        search_data = re.search('var data = "([=\w\+]+)"', trade_info_response.text)
        if search_data == None:
            return False

        need_data = search_data.groups()[0]
        bytes_data = base64.b64decode(need_data)
        str_data = bytes_data.decode('gbk')
        json_data = json.loads(str_data)

        self.__fund_account = json_data['fund_account']
        self.__client_risklevel = json_data['branch_no']
        self.__sh_stock_account = json_data['item'][0]['stock_account']
        self.__sh_exchange_type = json_data['item'][0]['exchange_type']
        self.__sz_stock_account = json_data['item'][1]['stock_account']
        self.__sz_exchange_type = json_data['item'][1]['exchange_type']
        self.__op_station = json_data['op_station']
        self.__trdpwd = json_data['trdpwd']
        self.__uid = json_data['uid']
        self.__branch_no = json_data['branch_no']

        return True

    def __set_ip_and_mac(self):
        """获取本机IP和MAC地址"""
        # 获取ip
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("baidu.com",80))
        self.__ip = s.getsockname()[0]
        s.close()

        # 获取mac地址
        self.__mac = ("".join(c + "-" if i % 2 else c for i, c in enumerate(hex(uuid.getnode())[2:].zfill(12)))[:-1]).upper()

    def __keepalive(self):
        """启动保持在线的进程 """
        self.heart_process = Process(target=self.__send_heartbeat)
        self.heart_process.start()

    def __send_heartbeat(self):
        """每隔30秒查询指定接口保持 token 的有效性"""
        while True:
            data = self.get_balance()
            if type(data) == dict and data.get('error_no'):
                break
            time.sleep(30)

    def exit(self):
        """结束保持 token 在线的进程"""
        if self.heart_process.is_alive():
            self.heart_process.terminate()

    @property
    def balance(self):
        return self.get_balance()

    def get_balance(self):
        """获取账户资金状况"""
        return self.__do(self.config['balance'])

    @property
    def position(self):
        return self.get_position()

    def get_position(self):
        """获取持仓"""
        return self.__do(self.config['position'])

    @property
    def entrust(self):
        return self.get_entrust()

    def get_entrust(self):
        """获取当日委托列表"""
        return self.__do(self.config['entrust'])

    # TODO: 实现撤单
    def cancel_order(self):
        pass

    # TODO: 实现买入卖出的各种委托类型
    def buy(self, stock_code, price, amount=0, volume=0, entrust_prop=0):
        """买入卖出股票
        :param stock_code: 股票代码
        :param price: 卖出价格
        :param amount: 卖出总金额 由 volume / price 取 100 整数， 若指定 price 则此参数无效
        :param entrust_prop: 委托类型，暂未实现，默认为限价委托
        """
        params = dict(
            self.config['buy'],
            entrust_amount=amount if amount else volume // price // 100 * 100
        )
        return self.__buy_or_sell(stock_code, price, entrust_prop=entrust_prop, other=params)

    def sell(self, stock_code, price, amount=0, volume=0, entrust_prop=0):
        """卖出股票
        :param stock_code: 股票代码
        :param price: 卖出价格
        :param amount: 卖出总金额 由 volume / price 取整， 若指定 price 则此参数无效
        :param entrust_prop: 委托类型，暂未实现，默认为限价委托
        """
        params = dict(
            self.config['sell'],
            entrust_amount=amount if amount else volume // price
        )
        return self.__buy_or_sell(stock_code, price, entrust_prop=entrust_prop, other=params)


    def __buy_or_sell(self, stock_code, price, entrust_prop, other):
        need_info = self.__get_trade_need_info(stock_code)
        return self.__do(dict(
                other,
                stock_account=need_info['stock_account'],  # '沪深帐号'
                exchange_type=need_info['exchange_type'],  # '沪市1 深市2'
                entrust_prop=0,  # 委托方式
                stock_code='{:0>6}'.format(stock_code),  # 股票代码, 右对齐宽为6左侧填充0
                entrust_price=price,
            ))

    def __get_trade_need_info(self, stock_code):
        """获取股票对应的证券市场和帐号"""
        # 获取股票对应的证券市场
        exchange_type = self.__sh_exchange_type if helpers.get_stock_type(stock_code) == 'sh' else self.__sz_exchange_type
        # 获取股票对应的证券帐号
        stock_account = self.__sh_stock_account if exchange_type == self.__sh_exchange_type else self.__sz_exchange_type
        return dict(
            exchange_type=exchange_type,
            stock_account=stock_account
        )

    def __do(self, params):
        """发起对 api 的请求并过滤返回结果"""
        basic_params = self.__create_basic_params()
        basic_params.update(params)
        data = self.__request(basic_params)
        data = self.__format_reponse_data(data)
        return self.__fix_error_data(data)

    def __create_basic_params(self):
        """生成基本的参数"""
        basic_params = dict(
            uid=self.__uid,
            version=1,
            custid=self.__account,
            op_branch_no=self.__branch_no,
            branch_no=self.__branch_no,
            op_entrust_way=7,
            op_station=self.__op_station,
            fund_account=self.__account,
            password=self.__trdpwd,
            identity_type='',
            ram=random.random()
        )
        return basic_params

    def __request(self, params):
        """请求并获取 JSON 数据"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
        }
        params_str = urllib.parse.urlencode(params)
        unquote_str = urllib.parse.unquote(params_str)

        self.log.debug(unquote_str)

        b64params = base64.b64encode(unquote_str.encode()).decode()
        r = self.s.get('{prefix}/?{b64params}'.format(prefix=self.trade_prefix, b64params=b64params), headers=headers)
        self.log.debug(r.url)
        return r.content

    def __format_reponse_data(self, data):
        """格式化返回的 json 数据"""
        bytes_str = base64.b64decode(data)
        self.log.debug(bytes_str)
        gbk_str = bytes_str.decode('gbk')
        return json.loads(gbk_str)

    def __fix_error_data(self, data):
        """若是返回错误移除外层的列表"""
        if data['cssweb_code'] == 'error':
            return data
        t1 = data['item']
        return t1[:-1]


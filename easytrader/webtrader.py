# coding: utf-8
import time
import os
import re
from threading import Thread
import json
from . import helpers

# 解决字符编码
import sys
reload(sys)
sys.setdefaultencoding("utf8")
log = helpers.get_logger(__file__)


class NotLoginError(Exception):
    pass


class WebTrader(object):
    global_config_path = os.path.dirname(__file__) + '/config/global.json'
    config_path = ''

    def __init__(self):
        self.__read_config()
        self.trade_prefix = self.config['prefix']
        self.account_config = ''
        self.heart_active = True
        # 2.7版本
        self.heart_thread = Thread(target=self.send_heartbeat, name='heart')
        self.heart_thread.setDaemon(True)

    def read_config(self, path):
        try:
            self.account_config = helpers.file2dict(path)
        except json.JSONDecodeError:
            log.error('配置文件格式有误，请勿使用记事本编辑，推荐使用 notepad++ 或者 sublime text')
        for v in self.account_config:
            if type(v) is int:
                log.warn('配置文件的值最好使用双引号包裹，使用字符串类型，否则可能导致不可知的问题')

    def prepare(self, need_data):
        """登录的统一接口
        :param need_data 登录所需数据"""
        self.read_config(need_data)
        self.autologin()

    def autologin(self):
        """实现自动登录"""
        is_login_ok = self.login()
        if not is_login_ok:
            self.autologin()
        self.keepalive()

    def login(self):
        pass

    def keepalive(self):
        """启动保持在线的进程 """
        if self.heart_thread.is_alive():
            self.heart_active = True
        else:
            self.heart_thread.start()

    def send_heartbeat(self):
        """每隔10秒查询指定接口保持 token 的有效性"""
        while True:
            if self.heart_active:
                try:
                    response = self.balance
                except:
                    pass
                self.check_account_live(response)
                time.sleep(10)
            else:
                time.sleep(1)

    def check_account_live(self, response):
        pass

    def exit(self):
        """结束保持 token 在线的进程"""
        self.heart_active = False

    def __read_config(self):
        """读取 config"""
        self.config = helpers.file2dict(self.config_path)
        self.global_config = helpers.file2dict(self.global_config_path)
        self.config.update(self.global_config)

    @property
    def balance(self):
        return self.get_balance()

    def get_balance(self):
        """获取账户资金状况"""
        return self.do(self.config['balance'])

    @property
    def position(self):
        return self.get_position()

    def get_position(self):
        """获取持仓"""
        return self.do(self.config['position'])

    @property
    def entrust(self):
        return self.get_entrust()

    def get_entrust(self):
        """获取当日委托列表"""
        return self.do(self.config['entrust'])

    def do(self, params):
        """发起对 api 的请求并过滤返回结果
        :param params: 交易所需的动态参数"""
        request_params = self.create_basic_params()
        request_params.update(params)
        response_data = self.request(request_params)
        format_json_data = self.format_response_data(response_data)
        return_data = self.fix_error_data(format_json_data)
        try:
            self.check_login_status(return_data)
        except NotLoginError:
            self.autologin()
        return return_data

    def create_basic_params(self):
        """生成基本的参数"""
        pass

    def request(self, params):
        """请求并获取 JSON 数据
        :param params: Get 参数"""
        pass

    def format_response_data(self, data):
        """格式化返回的 json 数据
        :param data: 请求返回的数据 """
        pass

    def fix_error_data(self, data):
        """若是返回错误移除外层的列表
        :param data: 需要判断是否包含错误信息的数据"""
        pass

    def format_response_data_type(self, response_data):
        """格式化返回的值为正确的类型
        :param response_data: 返回的数据
        """
        if type(response_data) is not list:
            return response_data

        int_match_str = '|'.join(self.config['response_format']['int'])
        float_match_str = '|'.join(self.config['response_format']['float'])
        for item in response_data:
            for key in item:
                try:
                    if re.search(int_match_str, key) is not None:
                        item[key] = helpers.str2num(item[key], 'int')
                    elif re.search(float_match_str, key) is not None:
                        item[key] = helpers.str2num(item[key], 'float')
                except ValueError:
                    continue
        return response_data

    def check_login_status(self, return_data):
        pass

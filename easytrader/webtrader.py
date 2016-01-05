# coding: utf-8
import time
import os
import re
from threading import Thread
from . import helpers


class NotLoginError(Exception):
    pass


class WebTrader:
    global_config_path = os.path.dirname(__file__) + '/config/global.json'

    def __init__(self):
        self.__read_config()
        self.trade_prefix = self.config['prefix']
        self.heart_active = True
        self.heart_thread = Thread(target=self.send_heartbeat, daemon=True)

    def read_config(self, path):
        self.account_config = helpers.file2dict(path)

    def prepare(self, need_data):
        """登录的统一接口"""
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
                response = self.get_balance()
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
        """格式化返回的值为正确的类型"""
        if type(response_data) is not list:
            return response_data

        int_match_str = '|'.join(self.config['response_format']['int'])
        float_match_str = '|'.join(self.config['response_format']['float'])
        for item in response_data:
            for key in item:
                try:
                    if re.search(int_match_str, key) is not None:
                        item[key] = int(float(item[key]))
                    elif re.search(float_match_str, key) is not None:
                        item[key] = float(item[key])
                except ValueError:
                    break
        return response_data

    def check_login_status(self, return_data):
        pass

# coding: utf-8
import logging
import os
import re
import time
from threading import Thread

import six
import requests

from . import helpers
from .log import log

if six.PY2:
    import sys

    stdi, stdo, stde = sys.stdin, sys.stdout, sys.stderr  # 获取标准输入、标准输出和标准错误输出
    reload(sys)
    sys.stdin, sys.stdout, sys.stderr = stdi, stdo, stde  # 保持标准输入、标准输出和标准错误输出
    sys.setdefaultencoding('utf8')


class NotLoginError(Exception):

    def __init__(self, result=None):
        super(NotLoginError, self).__init__()
        self.result = result


class TradeError(Exception):

    def __init__(self, message=None):
        super(TradeError, self).__init__()
        self.message = message


class WebTrader(object):
    global_config_path = os.path.dirname(__file__) + '/config/global.json'
    config_path = ''

    def __init__(self, debug=True):
        self.__read_config()
        self.trade_prefix = self.config['prefix']
        self.account_config = ''
        self.heart_active = True
        self.heart_thread = Thread(target=self.send_heartbeat)
        self.heart_thread.setDaemon(True)

        self.log_level = logging.DEBUG if debug else logging.INFO

    def read_config(self, path):
        try:
            self.account_config = helpers.file2dict(path)
        except ValueError:
            log.error('配置文件格式有误，请勿使用记事本编辑，推荐使用 notepad++ 或者 sublime text')
        for v in self.account_config:
            if type(v) is int:
                log.warn('配置文件的值最好使用双引号包裹，使用字符串类型，否则可能导致不可知的问题')

    def prepare(self, config_file=None, user=None, password=None, **kwargs):
        """登录的统一接口
        :param config_file 登录数据文件，若无则选择参数登录模式
        :param user: 各家券商的账号或者雪球的用户名
        :param password: 密码, 券商为加密后的密码，雪球为明文密码
        :param account: [雪球登录需要]雪球手机号(邮箱手机二选一)
        :param portfolio_code: [雪球登录需要]组合代码
        :param portfolio_market: [雪球登录需要]交易市场， 可选['cn', 'us', 'hk'] 默认 'cn'
        """
        if config_file is not None:
            self.read_config(config_file)
        else:
            self._prepare_account(user, password, **kwargs)
        self.autologin()

    def _prepare_account(self, user, password, **kwargs):
        """映射用户名密码到对应的字段"""
        raise Exception('支持参数登录需要实现此方法')

    def autologin(self, limit=10):
        """实现自动登录
        :param limit: 登录次数限制
        """
        for _ in range(limit):
            if self.login():
                break
        else:
            raise NotLoginError('登录失败次数过多, 请检查密码是否正确 / 券商服务器是否处于维护中 / 网络连接是否正常')
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
                self.check_login()
            else:
                time.sleep(1)

    def check_login(self, sleepy=30):
        log.setLevel(logging.ERROR)
        try:
            response = self.heartbeat()
            self.check_account_live(response)
        except requests.exceptions.ConnectionError:
            pass
        except Exception as e:
            log.setLevel(self.log_level)
            log.error('心跳线程发现账户出现错误: {} {}, 尝试重新登陆'.format(e.__class__, e))
            self.autologin()
        finally:
            log.setLevel(self.log_level)
        time.sleep(sleepy)

    def heartbeat(self):
        return self.balance

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

    @property
    def current_deal(self):
        return self.get_current_deal()

    def get_current_deal(self):
        """获取当日委托列表"""
        # return self.do(self.config['current_deal'])
        log.warning('目前仅在 佣金宝/银河子类 中实现, 其余券商需要补充')

    @property
    def exchangebill(self):
        """
        默认提供最近30天的交割单, 通常只能返回查询日期内最新的 90 天数据。
        :return:
        """
        # TODO 目前仅在 华泰子类 中实现
        start_date, end_date = helpers.get_30_date()
        return self.get_exchangebill(start_date, end_date)

    def get_exchangebill(self, start_date, end_date):
        """
        查询指定日期内的交割单
        :param start_date: 20160211
        :param end_date: 20160211
        :return:
        """
        log.warning('目前仅在 华泰子类 中实现, 其余券商需要补充')

    def get_ipo_limit(self, stock_code):
        """
        查询新股申购额度申购上限
        :param stock_code: 申购代码 ID
        :return:
        """
        log.warning('目前仅在 佣金宝子类 中实现, 其余券商需要补充')

    def do(self, params):
        """发起对 api 的请求并过滤返回结果
        :param params: 交易所需的动态参数"""
        request_params = self.create_basic_params()
        request_params.update(params)
        response_data = self.request(request_params)
        try:
            format_json_data = self.format_response_data(response_data)
        except:
            # Caused by server force logged out
            return None
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
        return data

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

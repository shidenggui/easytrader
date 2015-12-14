# coding: utf-8
import json
import random
import re
import requests
import time
import os
from multiprocessing import Process
from .webtrader import WebTrader
import logging

log = logging.getLogger(__name__)

class YJBTrader(WebTrader):
    config_path = os.path.dirname(__file__) + '/config/yjb.json'

    def __init__(self, token=''):
        super().__init__()
        self.cookie = dict(JSESSIONID=token)
        self.__keepalive()

    @property
    def token(self):
        return self.cookie['JSESSIONID']

    @token.setter
    def token(self, token):
        self.exit()
        self.cookie = dict(JSESSIONID=token)
        self.__keepalive()

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
            time.sleep(10)

    def exit(self):
        """结束保持 token 在线的进程"""
        if self.heart_process.is_alive():
            self.heart_process.terminate()

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
        if not self.heart_process.is_alive():
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
        # TODO: 如果知道股票代码跟沪深的关系可以优化省略一次请求，同理先获取沪深帐号也可以省略一次请求
        # 获取股票对应的证券市场
        response_data = self.do(dict(
                self.config['exchangetype4stock'],
                stock_code=stock_code
            ))[0]
        exchange_type = response_data['exchange_type']
        # 获取股票对应的证券帐号
        response_data = self.do(dict(
                self.config['account4stock'],
                exchange_type=exchange_type,
                stock_code=stock_code
            ))[0]
        stock_account = response_data['stock_account']
        return dict(
            exchange_type=exchange_type,
            stock_account=stock_account
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

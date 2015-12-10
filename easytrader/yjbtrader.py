# coding: utf-8
import json
import random
import re
import requests
import time
import os
from multiprocessing import Process
from easytrader import WebTrader


class YJBTrader(WebTrader):
    config_path = os.path.dirname(__file__) + '/config/yjb.json'

    def __init__(self, token=''):
        super().__init__()
        self.url = self.config['prefix']
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
        :param amount: 卖出总金额 由 volume / price 取整， 若指定 price 则此参数无效
        :param entrust_prop: 委托类型，暂未实现，默认为限价委托
        """
        params = dict(
            self.config['buy'],
            entrust_bs=1,  # 买入1 卖出2
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
            entrust_bs=2,  # 买入1 卖出2
            entrust_amount=amount if amount else volume // price
        )
        return self.__buy_or_sell(stock_code, price, entrust_prop=entrust_prop, other=params)


    def __buy_or_sell(self, stock_code, price, entrust_prop, other):
        # 检查是否已经掉线
        if not self.heart_process.is_alive():
            check_data = self.get_balance()
            if type(check_data) == dict:
                return check_data
        need_info = self.__get_trade_need_info(stock_code)
        return self.__do(dict(
                other,
                stock_account=need_info['stock_account'],  # '沪深帐号'
                exchange_type=need_info['exchange_type'],  # '沪市1 深市2'
                entrust_prop=0,  # 委托方式
                stock_code='{:0>6}'.format(stock_code),  # 股票代码, 右对齐宽为6左侧填充0
                elig_riskmatch_flag=1,  # 用户风险等级
                entrust_price=price,
            ))

    def __get_trade_need_info(self, stock_code):
        """获取股票对应的证券市场和帐号"""
        # TODO: 如果知道股票代码跟沪深的关系可以优化省略一次请求，同理先获取沪深帐号也可以省略一次请求
        # 获取股票对应的证券市场
        response_data = self.__do(dict(
                self.config['exchangetype4stock'],
                stock_code=stock_code
            ))[0]
        exchange_type = response_data['exchange_type']
        # 获取股票对应的证券帐号
        response_data = self.__do(dict(
                self.config['account4stock'],
                exchange_type=exchange_type,
                stock_code=stock_code
            ))[0]
        stock_account = response_data['stock_account']
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
            CSRF_Token='undefined',
            timestamp=random.random(),
        )
        return basic_params

    def __request(self, params):
        """请求并获取 JSON 数据"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
        }
        r = requests.get(self.url, params=params, cookies=self.cookie, headers=headers)
        return r.text

    def __format_reponse_data(self, data, header=False):
        """格式化返回的 json 数据"""
        # 获取 returnJSON
        returnJson = json.loads(data)['returnJson']
        # 为 key 添加双引号
        t1 = re.sub('\w+:', lambda x: '"%s":' % x.group().rstrip(':'), returnJson)
        # 替换所有单引号到双引号
        t2 = t1.replace("'", '"')
        t3 = json.loads(t2)
        fun_data = t3['Func%s' % t3['function_id']]
        return fun_data if header else fun_data[1:]

    def __fix_error_data(self, data):
        """若是返回错误移除外层的列表"""
        return data[0] if type(data) == list and data[0].get('error_no') != None else data


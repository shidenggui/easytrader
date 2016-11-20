# coding:utf8
from __future__ import unicode_literals, print_function, division

import re
from datetime import datetime
from numbers import Number
from threading import Thread

from .follower import BaseFollower
from .log import log
from .webtrader import NotLoginError


class XueQiuFollower(BaseFollower):
    LOGIN_PAGE = 'https://www.xueqiu.com'
    LOGIN_API = 'https://xueqiu.com/user/login'
    TRANSACTION_API = 'https://xueqiu.com/cubes/rebalancing/history.json'
    PORTFOLIO_URL = 'https://xueqiu.com/p/'
    WEB_REFERER = 'https://www.xueqiu.com'

    def __init__(self):
        super(XueQiuFollower, self).__init__()

    def check_login_success(self, login_status):
        if 'error_description' in login_status:
            raise NotLoginError(login_status['error_description'])

    def create_login_params(self, user, password, **kwargs):
        params = {
            'username': user,
            'areacode': '86',
            'telephone': kwargs.get('account', ''),
            'remember_me': '0',
            'password': password
        }
        return params

    def follow(self, users, strategies, total_assets=10000, initial_assets=None, track_interval=10,
               trade_cmd_expire_seconds=120, cmd_cache=True):
        """跟踪joinquant对应的模拟交易，支持多用户多策略
        :param users: 支持easytrader的用户对象，支持使用 [] 指定多个用户
        :param strategies: 雪球组合名, 类似 ZH123450
        :param total_assets: 雪球组合对应的总资产， 格式 [ 组合1对应资金, 组合2对应资金 ]
            若 strategies=['ZH000001', 'ZH000002'] 设置 total_assets=[10000, 10000], 则表明每个组合对应的资产为 1w 元，
            假设组合 ZH000001 加仓 价格为 p 股票 A 10%, 则对应的交易指令为 买入 股票 A 价格 P 股数 1w * 10% / p 并按 100 取整
        :param initial_assets:雪球组合对应的初始资产, 格式 [ 组合1对应资金, 组合2对应资金 ]
            总资产由 初始资产 × 组合净值 算得， total_assets 会覆盖此参数
        :param track_interval: 轮训模拟交易时间，单位为秒
        :param trade_cmd_expire_seconds: 交易指令过期时间, 单位为秒
        :param cmd_cache: 是否读取存储历史执行过的指令，防止重启时重复执行已经交易过的指令
        """
        users = self.warp_list(users)
        strategies = self.warp_list(strategies)
        total_assets = self.warp_list(total_assets)
        initial_assets = self.warp_list(initial_assets)

        if cmd_cache:
            self.load_expired_cmd_cache()

        self.start_trader_thread(users, trade_cmd_expire_seconds)

        for strategy_url, strategy_total_assets, strategy_initial_assets in zip(strategies, total_assets,
                                                                                initial_assets):
            assets = self.calculate_assets(strategy_url, strategy_total_assets, strategy_initial_assets)
            try:
                strategy_id = self.extract_strategy_id(strategy_url)
                strategy_name = self.extract_strategy_name(strategy_url)
            except:
                log.error('抽取交易id和策略名失败, 无效的模拟交易url: {}'.format(strategy_url))
                raise
            strategy_worker = Thread(target=self.track_strategy_worker, args=[strategy_id, strategy_name],
                                     kwargs={'interval': track_interval, 'assets': assets})
            strategy_worker.start()
            log.info('开始跟踪策略: {}'.format(strategy_name))

    def calculate_assets(self, strategy_url, total_assets=None, initial_assets=None):
        # 都设置时优先选择 total_assets
        if total_assets is None and initial_assets is not None:
            net_value = self._get_portfolio_net_value(strategy_url)
            total_assets = initial_assets * net_value
        if not isinstance(total_assets, Number):
            raise TypeError('input assets type must be number(int, float)')
        if total_assets < 1e3:
            raise ValueError('雪球总资产不能小于1000元，当前预设值 {}'.format(total_assets))
        return total_assets

    @staticmethod
    def extract_strategy_id(strategy_url):
        if len(strategy_url) != 8:
            raise ValueError('雪球组合名格式不对, 类似 ZH123456, 设置值: {}'.format(strategy_url))
        return strategy_url

    def extract_strategy_name(self, strategy_url):
        url = 'https://xueqiu.com/cubes/nav_daily/all.json?cube_symbol={}'.format(strategy_url)
        rep = self.s.get(url)
        info_index = 0
        return rep.json()[info_index]['name']

    def extract_transactions(self, history):
        print(history)
        if history['count'] <= 0:
            return []
        rebalancing_index = 0
        transactions = history['list'][rebalancing_index]['rebalancing_histories']
        return transactions

    def create_query_transaction_params(self, strategy):
        params = {
            'cube_symbol': strategy,
            'page': 1,
            'count': 1
        }
        return params

    def project_transactions(self, transactions, assets):
        for t in transactions:
            weight_diff = t['weight'] - t['prev_weight']

            initial_amount = abs(weight_diff) / 100 * assets / t['price']
            t['amount'] = int(round(initial_amount, -2))

            t['datetime'] = datetime.fromtimestamp(t['created_at'] // 1000)

            t['stock_code'] = t['stock_symbol'].lower()

            t['action'] = 'buy' if weight_diff > 0 else 'sell'

    def _get_portfolio_info(self, portfolio_code):
        """
        获取组合信息
        """
        url = self.PORTFOLIO_URL + portfolio_code
        portfolio_page = self.s.get(url)
        match_info = re.search(r'(?<=SNB.cubeInfo = ).*(?=;\n)', portfolio_page.text)
        if match_info is None:
            raise Exception('cant get portfolio info, portfolio url : {}'.format(url))
        try:
            portfolio_info = json.loads(match_info.group())
        except Exception as e:
            raise Exception('get portfolio info error: {}'.format(e))
        return portfolio_info

    def _get_portfolio_net_value(self, portfolio_code):
        """
        获取组合信息
        """
        portfolio_info = self._get_portfolio_info(portfolio_code)
        return portfolio_info['net_value']

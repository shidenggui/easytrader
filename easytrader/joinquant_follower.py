# coding:utf8
from __future__ import unicode_literals

import re
import time
from datetime import datetime
from threading import Thread

from .follower import BaseFollower
from .log import log
from .webtrader import NotLoginError


class JoinQuantFollower(BaseFollower):
    LOGIN_PAGE = 'https://www.joinquant.com'
    LOGIN_API = 'https://www.joinquant.com/user/login/doLogin?ajax=1'
    TRANSACTION_API = 'https://www.joinquant.com/algorithm/live/transactionDetail'
    WEB_REFERER = 'https://www.joinquant.com/user/login/index'
    WEB_ORIGIN = 'https://www.joinquant.com'

    def create_login_params(self, user, password):
        params = {
            'CyLoginForm[username]': user,
            'CyLoginForm[pwd]': password,
            'ajax': 1
        }
        return params

    def check_login_success(self, rep):
        set_cookie = rep.headers['set-cookie']
        if len(set_cookie) < 100:
            raise NotLoginError('登录失败，请检查用户名和密码')
        self.s.headers.update({
            'cookie': set_cookie
        })

    def follow(self, users, strategies, track_interval=1, trade_cmd_expire_seconds=120, cmd_cache=True):
        """跟踪joinquant对应的模拟交易，支持多用户多策略
        :param users: 支持easytrader的用户对象，支持使用 [] 指定多个用户
        :param strategies: joinquant 的模拟交易地址，支持使用 [] 指定多个模拟交易,
            地址类似 https://www.joinquant.com/algorithm/live/index?backtestId=xxx
        :param track_interval: 轮训模拟交易时间，单位为秒
        :param trade_cmd_expire_seconds: 交易指令过期时间, 单位为秒
        :param cmd_cache: 是否读取存储历史执行过的指令，防止重启时重复执行已经交易过的指令
        """
        users = self.warp_list(users)
        strategies = self.warp_list(strategies)

        if cmd_cache:
            self.load_expired_cmd_cache()

        self.start_trader_thread(users, trade_cmd_expire_seconds)

        workers = []
        for strategy_url in strategies:
            try:
                strategy_id = self.extract_strategy_id(strategy_url)
                strategy_name = self.extract_strategy_name(strategy_url)
            except:
                log.error('抽取交易id和策略名失败, 无效的模拟交易url: {}'.format(strategy_url))
                raise
            strategy_worker = Thread(target=self.track_strategy_worker, args=[strategy_id, strategy_name],
                                     kwargs={'interval': track_interval})
            strategy_worker.start()
            workers.append(strategy_worker)
            log.info('开始跟踪策略: {}'.format(strategy_name))
        for worker in workers:
            worker.join()

    @staticmethod
    def extract_strategy_id(strategy_url):
        return re.search(r'(?<=backtestId=)\w+', strategy_url).group()

    def extract_strategy_name(self, strategy_url):
        rep = self.s.get(strategy_url)
        return self.re_find(r'(?<=title="点击修改策略名称"\>).*(?=\</span)', rep.content.decode('utf8'))

    def create_query_transaction_params(self, strategy):
        today_str = datetime.today().strftime('%Y-%m-%d')
        params = {
            'backtestId': strategy,
            'date': today_str,
            'ajax': 1
        }
        return params

    def extract_transactions(self, history):
        transactions = history['data']['transaction']
        return transactions

    @staticmethod
    def stock_shuffle_to_prefix(stock):
        assert len(stock) == 11, 'stock {} must like 123456.XSHG or 123456.XSHE'.format(stock)
        code = stock[:6]
        if stock.find('XSHG') != -1:
            return 'sh' + code
        elif stock.find('XSHE') != -1:
            return 'sz' + code
        raise TypeError('not valid stock code: {}'.format(code))

    def project_transactions(self, transactions):
        for t in transactions:
            t['amount'] = self.re_find('\d+', t['amount'], dtype=int)

            time_str = '{} {}'.format(t['date'], t['time'])
            t['datetime'] = datetime.strptime(time_str, '%Y-%m-%d %H:%M')

            stock = self.re_find(r'\d{6}\.\w{4}', t['stock'])
            t['stock_code'] = self.stock_shuffle_to_prefix(stock)

            t['action'] = 'buy' if t['transaction'] == '买' else 'sell'

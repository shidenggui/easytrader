import os
import pickle
import re
import time
from datetime import datetime
from threading import Thread

import requests
from six.moves.queue import Queue

from .log import log


class JoinQuantFollower(object):
    LOGIN_API = 'https://www.joinquant.com/user/login/doLogin?ajax=1'
    TRANSACTION_API = 'https://www.joinquant.com/algorithm/live/transactionDetail'
    CMD_CACHE_FILE = 'cmd_cache.pk'

    def __init__(self):
        self.trade_queue = Queue()
        self.expired_cmds = set()

        self.s = requests.Session()

    def login(self, user, password):
        # mock headers
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.8',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36',
            'Referer': 'https://www.joinquant.com/user/login/index',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://www.joinquant.com',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }
        self.s.headers.update(headers)

        # init cookie
        self.s.get('https://www.joinquant.com/')

        # post for login
        params = {
            'CyLoginForm[username]': user,
            'CyLoginForm[pwd]': password,
            'ajax': 1
        }
        rep = self.s.post(self.LOGIN_API, data=params)
        self.s.headers.update({
            'cookie': rep.headers['set-cookie']
        })
        log.info('登录成功')

    def follow(self, users, strategies, track_interval=10, trade_cmd_expire_seconds=120, cmd_cache=True):
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
            log.info('开始跟踪策略: {}'.format(strategy_name))

    def load_expired_cmd_cache(self):
        if os.path.exists(self.CMD_CACHE_FILE):
            with open(self.CMD_CACHE_FILE, 'rb') as f:
                self.expired_cmds = pickle.load(f)

    def start_trader_thread(self, users, trade_cmd_expire_seconds):
        trader = Thread(target=self.trade_worker, args=[users], kwargs={'expire_seconds': trade_cmd_expire_seconds})
        trader.setDaemon(True)
        trader.start()

    @staticmethod
    def warp_list(value):
        if not isinstance(value, list):
            value = [value]
        return value

    @staticmethod
    def extract_strategy_id(strategy_url):
        return re.search(r'(?<=backtestId=)\w+', strategy_url).group()

    def extract_strategy_name(self, strategy_url):
        rep = self.s.get(strategy_url)
        return self.re_find(r'(?<=title="点击修改策略名称"\>).*(?=\</span)', rep.content.decode('utf8'))

    def track_strategy_worker(self, strategy, name, interval=10):
        """跟踪下单worker
        :param strategy: 策略id
        :param name: 策略名字
        :param interval: 轮训策略的时间间隔，单位为秒"""
        while True:
            transactions = self.query_strategy_transaction(strategy)
            for t in transactions:
                trade_cmd = {
                    'strategy': strategy,
                    'strategy_name': name,
                    'action': t['action'],
                    'stock_code': t['stock_code'],
                    'amount': t['amount'],
                    'price': t['price'],
                    'datetime': t['datetime']
                }
                if self.is_cmd_expired(trade_cmd):
                    continue
                log.info('策略 [{}] 发送指令到交易队列, 股票: {} 动作: {} 数量: {} 价格: {} 信号产生时间: {}'.format(
                    name, trade_cmd['stock_code'], trade_cmd['action'], trade_cmd['amount'], trade_cmd['price'],
                    trade_cmd['datetime']
                ))
                self.trade_queue.put(trade_cmd)
                self.add_cmd_to_expired_cmds(trade_cmd)
            time.sleep(interval)

    @staticmethod
    def generate_expired_cmd_key(cmd):
        return '{}_{}_{}_{}_{}'.format(
            cmd['strategy_name'], cmd['stock_code'], cmd['action'], cmd['amount'], cmd['price'], cmd['datetime'])

    def is_cmd_expired(self, cmd):
        key = self.generate_expired_cmd_key(cmd)
        return key in self.expired_cmds

    def add_cmd_to_expired_cmds(self, cmd):
        key = self.generate_expired_cmd_key(cmd)
        self.expired_cmds.add(key)

        with open(self.CMD_CACHE_FILE, 'wb') as f:
            pickle.dump(self.expired_cmds, f)

    def trade_worker(self, users, expire_seconds=120):
        while True:
            trade_cmd = self.trade_queue.get()
            for user in users:

                now = datetime.now()
                expire = (now - trade_cmd['datetime']).total_seconds()
                if expire > expire_seconds:
                    log.warning(
                        '策略 [{}] 指令(股票: {} 动作: {} 数量: {} 价格: {})超时，指令产生时间: {} 当前时间: {}, 超过设置的最大过期时间 {} 秒, 被丢弃'.format(
                            trade_cmd['strategy_name'], trade_cmd['stock_code'], trade_cmd['action'],
                            trade_cmd['amount'],
                            trade_cmd['price'], trade_cmd['datetime'], now, expire_seconds))
                    break
                args = {
                    'stock_code': trade_cmd['stock_code'],
                    'price': trade_cmd['price'],
                    'amount': trade_cmd['amount']
                }
                try:
                    response = getattr(user, trade_cmd['action'])(**args)
                except Exception as e:
                    trader_name = type(user).__name__
                    err_msg = '{}: {}'.format(type(e).__name__, e.message)
                    log.error(
                        '{} 执行 策略 [{}] 指令(股票: {} 动作: {} 数量: {} 价格: {} 指令产生时间: {}) 失败, 错误信息: {}'.format(
                            trader_name, trade_cmd['strategy_name'], trade_cmd['stock_code'], trade_cmd['action'],
                            trade_cmd['amount'],
                            trade_cmd['price'], trade_cmd['datetime'], err_msg))
                    continue
                log.info(
                    '策略 [{}] 指令(股票: {} 动作: {} 数量: {} 价格: {} 指令产生时间: {}) 执行成功, 返回: {}'.format(
                        trade_cmd['strategy_name'], trade_cmd['stock_code'], trade_cmd['action'],
                        trade_cmd['amount'],
                        trade_cmd['price'], trade_cmd['datetime'], response))

    def query_strategy_transaction(self, strategy):
        today_str = datetime.today().strftime('%Y-%m-%d')
        params = {
            'backtestId': strategy,
            'data': today_str,
            'ajax': 1
        }

        rep = self.s.get(self.TRANSACTION_API, params=params)
        transactions = rep.json()['data']['transaction']
        self.project_transactions(transactions)
        return transactions

    @staticmethod
    def re_find(pattern, string, dtype=str):
        return dtype(re.search(pattern, string).group())

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

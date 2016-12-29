# coding:utf8
from __future__ import unicode_literals

from datetime import datetime
from threading import Thread

from .follower import BaseFollower
from .log import log


class RiceQuantFollower(BaseFollower):
    def login(self, user, password, **kwargs):
        from rqopen_client import RQOpenClient
        self.client = RQOpenClient(user, password, logger=log)

    def follow(self, users, run_id, track_interval=1,
               trade_cmd_expire_seconds=120, cmd_cache=True, **kwargs):
        """跟踪ricequant对应的模拟交易，支持多用户多策略
        :param users: 支持easytrader的用户对象，支持使用 [] 指定多个用户
        :param run_id: ricequant 的模拟交易ID，支持使用 [] 指定多个模拟交易
        :param track_interval: 轮训模拟交易时间，单位为秒
        :param trade_cmd_expire_seconds: 交易指令过期时间, 单位为秒
        :param cmd_cache: 是否读取存储历史执行过的指令，防止重启时重复执行已经交易过的指令
        """
        users = self.warp_list(users)
        run_id_list = self.warp_list(run_id)

        if cmd_cache:
            self.load_expired_cmd_cache()

        self.start_trader_thread(users, trade_cmd_expire_seconds)

        workers = []
        for run_id in run_id_list:
            strategy_name = self.extract_strategy_name(run_id)
            strategy_worker = Thread(target=self.track_strategy_worker, args=[run_id, strategy_name],
                                     kwargs={'interval': track_interval})
            strategy_worker.start()
            workers.append(strategy_worker)
            log.info('开始跟踪策略: {}'.format(strategy_name))
        for worker in workers:
            worker.join()

    def extract_strategy_name(self, run_id):
        ret_json = self.client.get_positions(run_id)
        if ret_json["code"] != 200:
            log.error("fetch data from run_id {} fail, msg {}".format(run_id, ret_json["msg"]))
            raise RuntimeError(ret_json["msg"])
        return ret_json["resp"]["name"]

    def extract_day_trades(self, run_id):
        ret_json = self.client.get_day_trades(run_id)
        if ret_json["code"] != 200:
            log.error("fetch day trades from run_id {} fail, msg {}".format(run_id, ret_json["msg"]))
            raise RuntimeError(ret_json["msg"])
        return ret_json["resp"]["trades"]

    def query_strategy_transaction(self, strategy, **kwargs):
        transactions = self.extract_day_trades(strategy)
        transactions = self.project_transactions(transactions, **kwargs)
        return self.order_transactions_sell_first(transactions)

    @staticmethod
    def stock_shuffle_to_prefix(stock):
        assert len(stock) == 11, 'stock {} must like 123456.XSHG or 123456.XSHE'.format(stock)
        code = stock[:6]
        if stock.find('XSHG') != -1:
            return 'sh' + code
        elif stock.find('XSHE') != -1:
            return 'sz' + code
        raise TypeError('not valid stock code: {}'.format(code))

    def project_transactions(self, transactions, **kwargs):
        new_transactions = []
        for t in transactions:
            trans = {}
            trans["price"] = t["price"]
            trans["amount"] = abs(t["quantity"])
            trans["datetime"] = datetime.strptime(t["time"], '%Y-%m-%d %H:%M:%S')
            trans["stock_code"] = self.stock_shuffle_to_prefix(t["order_book_id"])
            trans["action"] = 'buy' if t["quantity"] > 0 else 'sell'
            new_transactions.append(trans)

        return new_transactions

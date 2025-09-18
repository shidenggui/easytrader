# -*- coding: utf-8 -*-
import abc
import datetime
import os
import pickle
import queue
import re
import threading
import time
from typing import List
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

import requests

from easytrader import exceptions
from easytrader.log import logger


class TimeoutRequestException(Exception):
    """自定义超时异常"""
    pass


class BaseFollower(metaclass=abc.ABCMeta):
    """
    slippage: 滑点，取值范围为 [0, 1]
    """

    LOGIN_PAGE = ""
    LOGIN_API = ""
    TRANSACTION_API = ""
    CMD_CACHE_FILE = "cmd_cache.pk"
    WEB_REFERER = ""
    WEB_ORIGIN = ""

    def __init__(self):
        self.trade_queue = queue.Queue()
        self.expired_cmds = set()

        self.s = requests.Session()
        self.s.verify = False
        # 设置默认超时时间为1秒
        self.s.timeout = 1
        
        # 创建线程池用于非阻塞网络请求
        self.network_executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="network_req")

        self.slippage: float = 0.0

    def _reliable_request_get(self, url, params=None, timeout=1.0):
        """可靠的GET请求，强制超时控制"""
        import threading
        import time
        
        result = [None]  # 使用列表来存储结果，方便在内部函数中修改
        exception = [None]  # 存储异常
        finished = threading.Event()
        
        def request_worker():
            try:
                start_time = time.time()
                logger.debug("🔗 开始网络请求: %s", url)
                
                response = self.s.get(url, params=params, timeout=timeout)
                
                request_time = time.time() - start_time
                logger.debug("📡 网络请求完成，耗时: %.3f秒", request_time)
                
                result[0] = response
            except Exception as e:
                exception[0] = e
            finally:
                finished.set()
        
        # 启动请求线程
        request_thread = threading.Thread(target=request_worker, daemon=True)
        request_thread.start()
        
        # 等待完成或超时
        if finished.wait(timeout=timeout + 0.5):  # 额外0.5秒容错
            if exception[0]:
                raise exception[0]
            return result[0]
        else:
            # 超时情况
            logger.warning("🚨 强制超时: 请求超过 %.1f秒未完成", timeout + 0.5)
            raise TimeoutRequestException(f"Request timeout after {timeout + 0.5} seconds")

    def login(self, user=None, password=None, **kwargs):
        """
        登陆接口
        :param user: 用户名
        :param password: 密码
        :param kwargs: 其他参数
        :return:
        """
        headers = self._generate_headers()
        self.s.headers.update(headers)

        # init cookie
        self.s.get(self.LOGIN_PAGE)

        # post for login
        params = self.create_login_params(user, password, **kwargs)
        rep = self.s.post(self.LOGIN_API, data=params)

        self.check_login_success(rep)
        logger.info("登录成功")

    def _generate_headers(self):
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Referer": self.WEB_REFERER,
            "X-Requested-With": "XMLHttpRequest",
            "Origin": self.WEB_ORIGIN,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        }
        return headers

    def check_login_success(self, rep):
        """检查登录状态是否成功
        :param rep: post login 接口返回的 response 对象
        :raise 如果登录失败应该抛出 NotLoginError """
        pass

    def create_login_params(self, user, password, **kwargs) -> dict:
        """生成 post 登录接口的参数
        :param user: 用户名
        :param password: 密码
        :return dict 登录参数的字典
        """
        return {}

    def follow(
        self,
        users,
        strategies,
        track_interval=1,
        trade_cmd_expire_seconds=120,
        cmd_cache=True,
        slippage: float = 0.0,
        **kwargs
    ):
        """跟踪平台对应的模拟交易，支持多用户多策略

        :param users: 支持easytrader的用户对象，支持使用 [] 指定多个用户
        :param strategies: 雪球组合名, 类似 ZH123450
        :param total_assets: 雪球组合对应的总资产， 格式 [ 组合1对应资金, 组合2对应资金 ]
            若 strategies=['ZH000001', 'ZH000002'] 设置 total_assets=[10000, 10000], 则表明每个组合对应的资产为 1w 元，
            假设组合 ZH000001 加仓 价格为 p 股票 A 10%, 则对应的交易指令为 买入 股票 A 价格 P 股数 1w * 10% / p 并按 100 取整
        :param initial_assets:雪球组合对应的初始资产, 格式 [ 组合1对应资金, 组合2对应资金 ]
            总资产由 初始资产 × 组合净值 算得， total_assets 会覆盖此参数
        :param track_interval: 轮询模拟交易时间，单位为秒
        :param trade_cmd_expire_seconds: 交易指令过期时间, 单位为秒
        :param cmd_cache: 是否读取存储历史执行过的指令，防止重启时重复执行已经交易过的指令
        :param slippage: 滑点，0.0 表示无滑点, 0.05 表示滑点为 5%
        """
        self.slippage = slippage

    def _calculate_price_by_slippage(self, action: str, price: float) -> float:
        """
        计算考虑滑点之后的价格
        :param action: 交易动作， 支持 ['buy', 'sell']
        :param price: 原始交易价格
        :return: 考虑滑点后的交易价格
        """
        if action == "buy":
            return round(price * (1 + self.slippage), 2)
        if action == "sell":
            return round(price * (1 - self.slippage), 2)
        return price

    def load_expired_cmd_cache(self):
        if os.path.exists(self.CMD_CACHE_FILE):
            with open(self.CMD_CACHE_FILE, "rb") as f:
                self.expired_cmds = pickle.load(f)

    def start_trader_thread(
        self,
        users,
        trade_cmd_expire_seconds,
        entrust_prop="limit",
        send_interval=0,
    ):
        trader = threading.Thread(
            target=self.trade_worker,
            args=[users],
            kwargs={
                "expire_seconds": trade_cmd_expire_seconds,
                "entrust_prop": entrust_prop,
                "send_interval": send_interval,
            },
        )
        trader.setDaemon(True)
        trader.start()

    @staticmethod
    def warp_list(value):
        if not isinstance(value, list):
            value = [value]
        return value

    @staticmethod
    def extract_strategy_id(strategy_url):
        """
        抽取 策略 id，一般用于获取策略相关信息
        :param strategy_url: 策略 url
        :return: str 策略 id
        """
        pass

    def extract_strategy_name(self, strategy_url):
        """
        抽取 策略名，主要用于日志打印，便于识别
        :param strategy_url:
        :return: str 策略名
        """
        pass

    def track_strategy_worker(self, strategy, name, interval=10, **kwargs):
        """跟踪下单worker
        :param strategy: 策略id
        :param name: 策略名字
        :param interval: 轮询策略的时间间隔，单位为秒"""
        logger.info("策略 %s worker线程开始运行，轮询间隔: %s秒", name, interval)
        
        consecutive_errors = 0  # 连续错误计数
        max_consecutive_errors = 5  # 最大连续错误次数
        
        # 检查是否有 stop_event 属性（用于优雅停止）
        stop_event = getattr(self, 'stop_event', None)
        
        while True:
            # 如果有 stop_event 且已设置，则退出
            if stop_event and stop_event.is_set():
                break
                
            try:
                start_time = time.time()
                
                # 使用非阻塞网络请求，设置1秒超时
                future = self.network_executor.submit(self.query_strategy_transaction, strategy, **kwargs)
                try:
                    transactions = future.result(timeout=1.0)  # 1秒超时
                    consecutive_errors = 0  # 重置错误计数
                except FutureTimeoutError:
                    consecutive_errors += 1
                    logger.warning("策略 %s 查询调仓信息超时(1秒)，连续错误次数: %d/%d", 
                                 name, consecutive_errors, max_consecutive_errors)
                    
                    if consecutive_errors >= max_consecutive_errors:
                        logger.error("策略 %s 连续错误次数过多，暂停30秒后重试", name)
                        time.sleep(30)
                        consecutive_errors = 0
                    else:
                        time.sleep(1)
                    continue
            # pylint: disable=broad-except
            except Exception as e:
                consecutive_errors += 1
                logger.exception("策略 %s 获取调仓信息时发生错误: %s，连续错误次数: %d/%d", 
                               name, e, consecutive_errors, max_consecutive_errors)
                
                if consecutive_errors >= max_consecutive_errors:
                    logger.error("策略 %s 连续错误次数过多，暂停60秒后重试", name)
                    time.sleep(60)
                    consecutive_errors = 0
                else:
                    time.sleep(3)
                continue
                
            # 处理交易数据
            if transactions:
                logger.info("策略 %s 发现 %d 条调仓信息", name, len(transactions))
            for transaction in transactions:
                try:
                    trade_cmd = {
                        "strategy": strategy,
                        "strategy_name": name,
                        "action": transaction["action"],
                        "stock_code": transaction["stock_code"],
                        "amount": transaction["amount"],
                        "price": transaction["price"],
                        "datetime": transaction["datetime"],
                    }
                    if self.is_cmd_expired(trade_cmd):
                        continue
                    logger.info(
                        "策略 [%s] 发送指令到交易队列, 股票: %s 动作: %s 数量: %s 价格: %s 信号产生时间: %s",
                        name,
                        trade_cmd["stock_code"],
                        trade_cmd["action"],
                        trade_cmd["amount"],
                        trade_cmd["price"],
                        trade_cmd["datetime"],
                    )
                    self.trade_queue.put(trade_cmd)
                    self.add_cmd_to_expired_cmds(trade_cmd)
                except Exception as e:
                    logger.exception("策略 [%s] 处理调仓记录 %s 失败, 错误: %s", name, transaction, e)
                    continue
            else:
                # 添加心跳日志，证明任务还在运行
                if int(time.time()) % 60 < interval:  # 每分钟只记录一次心跳
                    logger.debug("策略 %s 无调仓信息，任务正常运行中...", name)
            
            # 计算实际睡眠时间，确保准确的轮询间隔
            elapsed = time.time() - start_time
            sleep_time = max(0, interval - elapsed)
            
            if sleep_time > 0:
                try:
                    # 支持中断的睡眠
                    for _ in range(int(sleep_time * 10)):  # 将秒转换为0.1秒的循环
                        if stop_event and stop_event.is_set():
                            break
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    logger.info("程序退出")
                    break
                else:
                    logger.warning("策略 %s 处理时间过长: %.2f秒，超过轮询间隔: %d秒", 
                                 name, elapsed, interval)
        
        logger.info("策略 %s worker线程已停止")
        # 返回成功状态，避免被监控线程误判为异常
        return {"status": "stopped", "strategy": strategy, "name": name}

    @staticmethod
    def generate_expired_cmd_key(cmd):
        return "{}_{}_{}_{}".format(
            cmd["strategy_name"],
            cmd["stock_code"],
            cmd["action"],
            cmd["datetime"],
        )

    def is_cmd_expired(self, cmd):
        key = self.generate_expired_cmd_key(cmd)
        return key in self.expired_cmds

    def add_cmd_to_expired_cmds(self, cmd):
        key = self.generate_expired_cmd_key(cmd)
        self.expired_cmds.add(key)

        with open(self.CMD_CACHE_FILE, "wb") as f:
            pickle.dump(self.expired_cmds, f)

    @staticmethod
    def _is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def _execute_trade_cmd(
        self, trade_cmd, users, expire_seconds, entrust_prop, send_interval
    ):
        """分发交易指令到对应的 user 并执行
        :param trade_cmd:
        :param users:
        :param expire_seconds:
        :param entrust_prop:
        :param send_interval:
        :return:
        """
        for user in users:
            # check expire
            now = datetime.datetime.now()
            expire = (now - trade_cmd["datetime"]).total_seconds()
            if expire > expire_seconds:
                logger.warning(
                    "策略 [%s] 指令(股票: %s 动作: %s 数量: %s 价格: %s)超时，指令产生时间: %s 当前时间: %s, 超过设置的最大过期时间 %s 秒, 被丢弃",
                    trade_cmd["strategy_name"],
                    trade_cmd["stock_code"],
                    trade_cmd["action"],
                    trade_cmd["amount"],
                    trade_cmd["price"],
                    trade_cmd["datetime"],
                    now,
                    expire_seconds,
                )
                break

            # check price
            price = trade_cmd["price"]
            if not self._is_number(price) or price <= 0:
                logger.warning(
                    "策略 [%s] 指令(股票: %s 动作: %s 数量: %s 价格: %s)超时，指令产生时间: %s 当前时间: %s, 价格无效 , 被丢弃",
                    trade_cmd["strategy_name"],
                    trade_cmd["stock_code"],
                    trade_cmd["action"],
                    trade_cmd["amount"],
                    trade_cmd["price"],
                    trade_cmd["datetime"],
                    now,
                )
                break

            # check amount
            if trade_cmd["amount"] <= 0:
                logger.warning(
                    "策略 [%s] 指令(股票: %s 动作: %s 数量: %s 价格: %s)超时，指令产生时间: %s 当前时间: %s, 买入股数无效 , 被丢弃",
                    trade_cmd["strategy_name"],
                    trade_cmd["stock_code"],
                    trade_cmd["action"],
                    trade_cmd["amount"],
                    trade_cmd["price"],
                    trade_cmd["datetime"],
                    now,
                )
                break

            # actual_price = self._calculate_price_by_slippage(
            #     trade_cmd["action"], trade_cmd["price"]
            # )
            actual_price = trade_cmd["price"]
            args = {
                "security": trade_cmd["stock_code"],
                "price": actual_price,
                "amount": trade_cmd["amount"],
                "entrust_prop": entrust_prop,
            }
            try:
                response = getattr(user, trade_cmd["action"])(**args)
            except exceptions.TradeError as e:
                trader_name = type(user).__name__
                err_msg = "{}: {}".format(type(e).__name__, e.args)
                logger.error(
                    "%s 执行 策略 [%s] 指令(股票: %s 动作: %s 数量: %s 价格(考虑滑点): %s 指令产生时间: %s) 失败, 错误信息: %s",
                    trader_name,
                    trade_cmd["strategy_name"],
                    trade_cmd["stock_code"],
                    trade_cmd["action"],
                    trade_cmd["amount"],
                    actual_price,
                    trade_cmd["datetime"],
                    err_msg,
                )
            else:
                logger.info(
                    "策略 [%s] 指令(股票: %s 动作: %s 数量: %s 价格(考虑滑点): %s 指令产生时间: %s) 执行成功, 返回: %s",
                    trade_cmd["strategy_name"],
                    trade_cmd["stock_code"],
                    trade_cmd["action"],
                    trade_cmd["amount"],
                    actual_price,
                    trade_cmd["datetime"],
                    response,
                )

    def trade_worker(
        self, users, expire_seconds=120, entrust_prop="limit", send_interval=0
    ):
        """
        :param send_interval: 交易发送间隔， 默认为0s。调大可防止卖出买入时买出单没有及时成交导致的买入金额不足
        """
        logger.info("💼 交易worker线程开始运行")
        processed_count = 0
        
        while True:
            try:
                # 非阻塞方式获取交易指令，避免无限等待
                queue_start = time.time()
                try:
                    trade_cmd = self.trade_queue.get(timeout=1.0)  # 1秒超时
                    queue_time = time.time() - queue_start
                    processed_count += 1
                    logger.info(f"📤 获取交易指令#{processed_count}，队列等待: {queue_time:.3f}秒")
                except queue.Empty:
                    # 队列为空，继续循环
                    queue_time = time.time() - queue_start
                    if queue_time > 0.5:  # 只有等待时间较长时才记录
                        logger.debug(f"📭 交易队列为空，等待: {queue_time:.3f}秒")
                    time.sleep(0.1)
                    continue
                
                logger.info(f"🚀 开始执行交易指令#{processed_count}: {trade_cmd}")
                
                # 使用线程池执行交易，避免阻塞交易线程
                try:
                    submit_start = time.time()
                    future = self.network_executor.submit(
                        self._execute_trade_cmd,
                        trade_cmd, users, expire_seconds, entrust_prop, send_interval
                    )
                    submit_time = time.time() - submit_start
                    logger.debug(f"🎯 交易指令#{processed_count}已提交到线程池，耗时: {submit_time:.3f}秒")
                    
                    # 设置交易执行超时，避免无限等待
                    execute_start = time.time()
                    future.result(timeout=30.0)  # 30秒超时
                    execute_time = time.time() - execute_start
                    logger.info(f"✅ 交易指令#{processed_count}执行完成，耗时: {execute_time:.3f}秒")
                    
                except Exception as e:
                    execute_time = time.time() - execute_start
                    logger.error(f"❌ 交易指令#{processed_count}执行失败，耗时: {execute_time:.3f}秒，错误: {e}")
                
                # 交易间隔等待
                if send_interval > 0:
                    interval_start = time.time()
                    time.sleep(send_interval)
                    interval_time = time.time() - interval_start
                    logger.debug(f"⏱️ 交易间隔等待完成: {interval_time:.3f}秒")
                
            except Exception as e:
                logger.exception(f"💥 交易worker线程发生错误: {e}")
                time.sleep(1)  # 错误后短暂等待

    def query_strategy_transaction(self, strategy, **kwargs):
        """查询策略调仓信息，带详细监控"""
        query_start = time.time()
        logger.debug("🌐 开始查询策略 %s 调仓信息", strategy)
        
        try:
            # 创建查询参数
            param_start = time.time()
            params = self.create_query_transaction_params(strategy)
            param_time = time.time() - param_start
            logger.debug("📋 策略 %s 参数创建完成，耗时: %.3f秒", strategy, param_time)
            
            # 发起网络请求
            request_start = time.time()
            logger.debug("📡 策略 %s 开始网络请求: %s", strategy, self.TRANSACTION_API)
            
            rep = self._reliable_request_get(self.TRANSACTION_API, params=params, timeout=1.0)
            
            request_time = time.time() - request_start
            logger.debug("📥 策略 %s 网络请求完成，耗时: %.3f秒，状态码: %d", 
                        strategy, request_time, rep.status_code)
            
            # 检查HTTP状态码
            if rep.status_code != 200:
                logger.warning("❌ 查询策略 %s 调仓信息HTTP错误: %d, 响应: %s", 
                             strategy, rep.status_code, rep.text[:200])
                return []
            
            # 解析JSON
            json_start = time.time()
            history = rep.json()
            json_time = time.time() - json_start
            logger.debug("📊 策略 %s JSON解析完成，耗时: %.3f秒", strategy, json_time)
            
        except requests.exceptions.Timeout:
            request_time = time.time() - request_start
            logger.warning("⏰ 查询策略 %s 调仓信息请求超时(1秒)，实际耗时: %.3f秒", strategy, request_time)
            return []
        except TimeoutRequestException as e:
            request_time = time.time() - request_start
            logger.warning("🚨 查询策略 %s 调仓信息强制超时，实际耗时: %.3f秒，错误: %s", strategy, request_time, e)
            return []
        except requests.exceptions.ConnectionError as e:
            request_time = time.time() - request_start
            logger.warning("🔌 查询策略 %s 调仓信息连接错误，耗时: %.3f秒，错误: %s", strategy, request_time, e)
            return []
        except requests.exceptions.RequestException as e:
            request_time = time.time() - request_start
            logger.warning("🚫 查询策略 %s 调仓信息请求失败，耗时: %.3f秒，错误: %s", strategy, request_time, e)
            return []
        except ValueError as e:
            logger.error("📄 查询策略 %s 调仓信息JSON解析失败: %s", strategy, e)
            return []
        except Exception as e:
            request_time = time.time() - request_start
            logger.error("💥 查询策略 %s 调仓信息时发生未知错误，耗时: %.3f秒，错误: %s", strategy, request_time, e)
            return []

        # 处理业务逻辑
        try:
            process_start = time.time()
            transactions = self.extract_transactions(history)
            extract_time = time.time() - process_start
            
            project_start = time.time()
            self.project_transactions(transactions, **kwargs)
            project_time = time.time() - project_start
            
            order_start = time.time()
            result = self.order_transactions_sell_first(transactions)
            order_time = time.time() - order_start
            
            total_time = time.time() - query_start
            logger.debug("⚙️ 策略 %s 业务处理完成，提取: %.3f秒，投影: %.3f秒，排序: %.3f秒，总耗时: %.3f秒", 
                        strategy, extract_time, project_time, order_time, total_time)
            
            return result
            
        except Exception as e:
            total_time = time.time() - query_start
            logger.error("⚙️ 策略 %s 业务处理失败，总耗时: %.3f秒，错误: %s", strategy, total_time, e)
            return []

    def extract_transactions(self, history) -> List[str]:
        """
        抽取接口返回中的调仓记录列表
        :param history: 调仓接口返回信息的字典对象
        :return: [] 调参历史记录的列表
        """
        return []

    def create_query_transaction_params(self, strategy) -> dict:
        """
        生成用于查询调参记录的参数
        :param strategy: 策略 id
        :return: dict 调参记录参数
        """
        return {}

    @staticmethod
    def re_find(pattern, string, dtype=str):
        return dtype(re.search(pattern, string).group())

    @staticmethod
    def re_search(pattern, string, dtype=str):
        return dtype(re.search(pattern,string).group(1))

    def project_transactions(self, transactions, **kwargs):
        """
        修证调仓记录为内部使用的统一格式
        :param transactions: [] 调仓记录的列表
        :return: [] 修整后的调仓记录
        """
        pass

    def order_transactions_sell_first(self, transactions):
        # 调整调仓记录的顺序为先卖再买
        sell_first_transactions = []
        for transaction in transactions:
            if 'action' not in transaction:
                logger.warning("调仓记录 %s 不包含 action 字段，跳过", transaction)
                continue

            if transaction["action"] == "sell":
                sell_first_transactions.insert(0, transaction)
            else:
                sell_first_transactions.append(transaction)
        return sell_first_transactions

    def cleanup(self):
        """清理资源，关闭线程池"""
        try:
            if hasattr(self, 'network_executor'):
                self.network_executor.shutdown(wait=True)
                logger.info("网络请求线程池已关闭")
        except Exception as e:
            logger.error("关闭线程池时发生错误: %s", e)

    def __del__(self):
        """析构函数，确保资源被正确释放"""
        self.cleanup()

# coding: utf-8
import time
from threading import Thread
from . import helpers

class WebTrader:
    def __init__(self):
        self.__read_config()
        self.trade_prefix = self.config['prefix']
        self.heart_active = False
        self.heart_thread = Thread(target=self.send_heartbeat, daemon=True)

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
                self.get_balance()
                time.sleep(10)
            else:
                time.sleep(1)

    def exit(self):
        """结束保持 token 在线的进程"""
        self.heart_active = False

    def __read_config(self):
        """读取 config"""
        self.config = helpers.file2dict(self.config_path)

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
        """发起对 api 的请求并过滤返回结果"""
        pass
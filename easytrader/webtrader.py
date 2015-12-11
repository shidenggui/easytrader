# coding: utf-8
from . import helpers

class WebTrader:
    def __init__(self):
        self.__read_config()
        self.trade_prefix = self.config['prefix']

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
        pass
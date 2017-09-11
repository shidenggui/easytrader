# coding:utf-8

import os
import time
from abc import abstractmethod

from . import helpers
from .config import client


class ClientTrader:
    def __init__(self):
        self._config = client.create(self.broker_type)

    def prepare(self, config_path=None, user=None, password=None, exe_path=None, comm_password=None,
                **kwargs):
        """
        登陆客户端
        :param config_path: 登陆配置文件，跟参数登陆方式二选一
        :param user: 账号
        :param password: 明文密码
        :param exe_path: 客户端路径类似 r'C:\\htzqzyb2\\xiadan.exe', 默认 r'C:\\htzqzyb2\\xiadan.exe'
        :param comm_password: 通讯密码
        :return:
        """
        if config_path is not None:
            account = helpers.file2dict(config_path)
            user = account['user']
            password = account['password']
        self.login(user, password, exe_path or self._config.DEFAULT_EXE_PATH, comm_password, **kwargs)

    @abstractmethod
    def login(self, user, password, exe_path, comm_password=None, **kwargs):
        pass

    @property
    @abstractmethod
    def broker_type(self):
        pass

    @property
    @abstractmethod
    def balance(self):
        pass

    @property
    @abstractmethod
    def position(self):
        pass

    @property
    @abstractmethod
    def cancel_entrusts(self):
        pass

    @property
    @abstractmethod
    def today_entrusts(self):
        pass

    @property
    @abstractmethod
    def today_trades(self):
        pass

    @abstractmethod
    def cancel_entrust(self, entrust_no):
        pass

    @abstractmethod
    def buy(self, security, price, amount, **kwargs):
        pass

    @abstractmethod
    def sell(self, security, price, amount, **kwargs):
        pass

    def auto_ipo(self):
        raise NotImplementedError

    def _run_exe_path(self, exe_path):
        return os.path.join(
            os.path.dirname(exe_path), 'xiadan.exe'
        )

    def _wait(self, seconds):
        time.sleep(seconds)

    def exit(self):
        self._app.kill()

    def _close_prompt_windows(self):
        self._wait(1)
        for w in self._app.windows(class_name='#32770'):
            if w.window_text() != self._config.TITLE:
                w.close()
        self._wait(1)


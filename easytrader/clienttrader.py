# coding:utf-8

import os
import time
from abc import abstractmethod

from . import exceptions
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
        self._switch_left_menus(self._config.AUTO_IPO_MENU_PATH)

        stock_list = self._get_grid_data(self._config.COMMON_GRID_CONTROL_ID)
        valid_list_idx = [i for i, v in enumerate(stock_list) if v['申购数量'] <= 0]
        self._click(self._config.AUTO_IPO_SELECT_ALL_BUTTON_CONTROL_ID)
        self._wait(0.1)

        for row in valid_list_idx:
            self._click_grid_by_row(row)
        self._wait(0.1)

        self._click(self._config.AUTO_IPO_BUTTON_CONTROL_ID)
        self._wait(0.1)

        return self._handle_auto_ipo_pop_dialog()

    def _click_grid_by_row(self, row):
        x = self._config.COMMON_GRID_LEFT_MARGIN
        y = self._config.COMMON_GRID_FIRST_ROW_HEIGHT + self._config.COMMON_GRID_ROW_HEIGHT * row
        self._app.top_window().window(
            control_id=self._config.COMMON_GRID_CONTROL_ID,
            class_name='CVirtualGridCtrl'
        ).click(coords=(x, y))

    def _handle_auto_ipo_pop_dialog(self):
        while self._main.wrapper_object() != self._app.top_window().wrapper_object():
            title = self._get_pop_dialog_title()
            if '提示信息' in title or '委托确认' in title:
                self._app.top_window().type_keys('%Y')
            elif '提示' in title:
                data = self._app.top_window().Static.window_text()
                self._app.top_window()['确定'].click()
                return {'message': data}
            else:
                data = self._app.top_window().Static.window_text()
                self._app.top_window().close()
                return {'message': 'unkown message: {}'.find(data)}
            self._wait(0.1)
        return {'message': 'success'}

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

    def trade(self, security, price, amount):
        self._set_trade_params(security, price, amount)

        self._submit_trade()

        while self._main.wrapper_object() != self._app.top_window().wrapper_object():
            pop_title = self._get_pop_dialog_title()
            if pop_title == '委托确认':
                self._app.top_window().type_keys('%Y')
            elif pop_title == '提示信息':
                if '超出涨跌停' in self._app.top_window().Static.window_text():
                    self._app.top_window().type_keys('%Y')
            elif pop_title == '提示':
                content = self._app.top_window().Static.window_text()
                if '成功' in content:
                    entrust_no = self._extract_entrust_id(content)
                    self._app.top_window()['确定'].click()
                    return {'entrust_no': entrust_no}
                else:
                    self._app.top_window()['确定'].click()
                    self._wait(0.05)
                    raise exceptions.TradeError(content)
            else:
                self._app.top_window().close()
            self._wait(0.3)  # wait next dialog display

# coding:utf8
from __future__ import division

import functools
import io
import os
import re
import time

import easyutils
import pandas as pd
import pywinauto
import pywinauto.clipboard

from . import exceptions
from .clienttrader import ClientTrader
from .log import log


class HTClientTrader(ClientTrader):
    @property
    def broker_type(self):
        return 'ht'

    def login(self, user, password, exe_path, comm_password=None, **kwargs):
        """
        :param user: 用户名
        :param password: 密码
        :param exe_path: 客户端路径, 类似
        :param comm_password:
        :param kwargs:
        :return:
        """
        if comm_password is None:
            raise ValueError('华泰必须设置通讯密码')

        try:
            self._app = pywinauto.Application().connect(path=self._run_exe_path(exe_path), timeout=1)
        except Exception:
            self._app = pywinauto.Application().start(exe_path)

            # wait login window ready
            while True:
                try:
                    self._app.top_window().Edit1.wait('ready')
                    break
                except RuntimeError:
                    pass

            self._app.top_window().Edit1.type_keys(user)
            self._app.top_window().Edit2.type_keys(password)

            self._app.top_window().Edit3.type_keys(comm_password)

            self._app.top_window().type_keys('%Y')

            # detect login is success or not
            self._app.top_window().wait_not('exists', 2)

            self._app = pywinauto.Application().connect(path=self._run_exe_path(exe_path), timeout=10)
        self._close_prompt_windows()
        self._main = self._app.top_window()

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

    @property
    def balance(self):
        self._switch_left_menus(['查询[F4]', '资金股票'])

        return self._get_balance_from_statics()

    def _get_balance_from_statics(self):
        result = {}
        for key, control_id in self._config.BALANCE_CONTROL_ID_GROUP.items():
            result[key] = float(
                self._app.top_window().window(
                    control_id=control_id,
                    class_name='Static',
                ).window_text()
            )
        return result

    @property
    def position(self):
        self._switch_left_menus(['查询[F4]', '资金股票'])

        return self._get_grid_data(self._config.COMMON_GRID_CONTROL_ID)

    @property
    def today_entrusts(self):
        self._switch_left_menus(['查询[F4]', '当日委托'])

        return self._get_grid_data(self._config.COMMON_GRID_CONTROL_ID)

    @property
    def today_trades(self):
        self._switch_left_menus(['查询[F4]', '当日成交'])

        return self._get_grid_data(self._config.COMMON_GRID_CONTROL_ID)

    def buy(self, security, price, amount, **kwargs):
        self._switch_left_menus(['买入[F1]'])

        return self.trade(security, price, amount)

    def sell(self, security, price, amount, **kwargs):
        self._switch_left_menus(['卖出[F2]'])

        return self.trade(security, price, amount)

    @property
    def cancel_entrusts(self):
        self._refresh()
        self._switch_left_menus(['撤单[F3]'])

        return self._get_grid_data(self._config.COMMON_GRID_CONTROL_ID)

    def cancel_entrust(self, entrust_no):
        self._refresh()
        for i, entrust in enumerate(self.cancel_entrusts):
            if entrust[self._config.CANCEL_ENTRUST_ENTRUST_FIELD] == entrust_no:
                self._cancel_entrust_by_double_click(i)
                return self._handle_cancel_entrust_pop_dialog()
        else:
            return {'message': '委托单状态错误不能撤单, 该委托单可能已经成交或者已撤'}

    def auto_ipo(self):
        self._switch_left_menus(['新股申购', '批量新股申购'])

        self._click(self._config.AUTO_IPO_SELECT_ALL_BUTTON_CONTROL_ID)
        self._click(self._config.AUTO_IPO_BUTTON_CONTROL_ID)

        return self._handle_auto_ipo_pop_dialog()

    def _handle_auto_ipo_pop_dialog(self):
        while self._main.wrapper_object() != self._app.top_window().wrapper_object():
            title = self._get_pop_dialog_title()
            if '提示信息' in title:
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

    def _click(self, control_id):
        self._app.top_window().window(
            control_id=control_id,
            class_name='Button'
        ).click()

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
            self._wait(0.2)  # wait next dialog display

    def _extract_entrust_id(self, content):
        return re.search(r'\d+', content).group()

    def _submit_trade(self):
        self._main.window(
            control_id=self._config.TRADE_SUBMIT_CONTROL_ID,
            class_name='Button'
        ).click()

    def _get_pop_dialog_title(self):
        return self._app.top_window().window(
            control_id=self._config.POP_DIALOD_TITLE_CONTROL_ID
        ).window_text()

    def _set_trade_params(self, security, price, amount):
        code = security[-6:]

        self._type_keys(
            self._config.TRADE_SECURITY_CONTROL_ID,
            code
        )
        self._type_keys(
            self._config.TRADE_PRICE_CONTROL_ID,
            easyutils.round_price_by_code(price, code)
        )
        self._type_keys(
            self._config.TRADE_AMOUNT_CONTROL_ID,
            str(int(amount))
        )

    def _get_grid_data(self, control_id):
        grid = self._app.top_window().window(
            control_id=control_id,
            class_name='CVirtualGridCtrl'
        )
        grid.type_keys('^A^C')
        return self._format_grid_data(
            self._get_clipboard_data()
        )

    def _type_keys(self, control_id, text):
        self._app.top_window().window(
            control_id=control_id,
            class_name='Edit'
        ).type_keys(text)

    def _get_clipboard_data(self):
        while True:
            try:
                return pywinauto.clipboard.GetData()
            except Exception as e:
                log.warning('{}, retry ......'.format(e))

    def _switch_left_menus(self, path, sleep=0.2):
        self._get_left_menus_handle().get_item(path).click()
        self._wait(sleep)

    def _switch_left_menus_by_shortcut(self, shortcut, sleep=0.5):
        self._app.top_window().type_keys(shortcut)
        self._wait(sleep)

    @functools.lru_cache()
    def _get_left_menus_handle(self):
        while True:
            try:
                handle = self._app.top_window().window(
                    control_id=129,
                    class_name='SysTreeView32'
                )
                # sometime can't find handle ready, must retry
                handle.wait('ready', 2)
                return handle
            except:
                pass

    def _format_grid_data(self, data):
        df = pd.read_csv(io.StringIO(data),
                         delimiter='\t',
                         dtype=self._config.GRID_DTYPE,
                         na_filter=False,
                         )
        return df.to_dict('records')

    def _handle_cancel_entrust_pop_dialog(self):
        while self._main.wrapper_object() != self._app.top_window().wrapper_object():
            title = self._get_pop_dialog_title()
            if '提示信息' in title:
                self._app.top_window().type_keys('%Y')
            elif '提示' in title:
                data = self._app.top_window().Static.window_text()
                self._app.top_window()['确定'].click()
                return {'message': data}
            else:
                data = self._app.top_window().Static.window_text()
                self._app.top_window().close()
                return {'message': 'unkown message: {}'.find(data)}
            self._wait(0.2)

    def _cancel_entrust_by_double_click(self, row):
        x = self._config.CANCEL_ENTRUST_GRID_LEFT_MARGIN
        y = self._config.CANCEL_ENTRUST_GRID_FIRST_ROW_HEIGHT + self._config.CANCEL_ENTRUST_GRID_ROW_HEIGHT * row
        self._app.top_window().window(
            control_id=self._config.COMMON_GRID_CONTROL_ID,
            class_name='CVirtualGridCtrl'
        ).double_click(coords=(x, y))

    def _refresh(self):
        self._switch_left_menus(['买入[F1]'], sleep=0.05)

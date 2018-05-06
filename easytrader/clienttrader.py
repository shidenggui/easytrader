# coding:utf-8
import functools
import io
import os
import re
import sys
import time
from abc import abstractmethod

import easyutils
import pandas as pd

from . import exceptions
from . import helpers
from .config import client
from .log import log

if not sys.platform.startswith('darwin'):
    import pywinauto
    import pywinauto.clipboard


class PopDialogHandler:
    def __init__(self, app):
        self._app = app

    def handle(self, title):
        if any(s in title for s in {'提示信息', '委托确认', '网上交易用户协议'}):
            self._submit_by_shortcut()

        elif '提示' in title:
            content = self._extract_content()
            self._submit_by_click()
            return {'message': content}

        else:
            content = self._extract_content()
            self._close()
            return {'message': 'unknown message: {}'.format(content)}

    def _extract_content(self):
        return self._app.top_window().Static.window_text()

    def _extract_entrust_id(self, content):
        return re.search(r'\d+', content).group()

    def _submit_by_click(self):
        self._app.top_window()['确定'].click()

    def _submit_by_shortcut(self):
        self._app.top_window().type_keys('%Y')

    def _close(self):
        self._app.top_window().close()


class TradePopDialogHandler(PopDialogHandler):
    def handle(self, title):
        if title == '委托确认':
            self._submit_by_shortcut()

        elif title == '提示信息':
            content = self._extract_content()
            if '超出涨跌停' in content:
                self._submit_by_shortcut()
            elif '委托价格的小数价格应为' in content:
                self._submit_by_shortcut()

        elif title == '提示':
            content = self._extract_content()
            if '成功' in content:
                entrust_no = self._extract_entrust_id(content)
                self._submit_by_click()
                return {'entrust_no': entrust_no}
            else:
                self._submit_by_click()
                time.sleep(0.05)
                raise exceptions.TradeError(content)
        else:
            self._close()


class ClientTrader:
    def __init__(self):
        self._config = client.create(self.broker_type)
        self._app = None
        self._main = None

    def prepare(self,
                config_path=None,
                user=None,
                password=None,
                exe_path=None,
                comm_password=None,
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
            comm_password = account.get('comm_password')
            exe_path = account.get('exe_path')
        self.login(user, password, exe_path or self._config.DEFAULT_EXE_PATH,
                   comm_password, **kwargs)

    @abstractmethod
    def login(self, user, password, exe_path, comm_password=None, **kwargs):
        pass

    def connect(self, exe_path=None, **kwargs):
        """
        直接连接登陆后的客户端
        :param exe_path: 客户端路径类似 r'C:\\htzqzyb2\\xiadan.exe', 默认 r'C:\\htzqzyb2\\xiadan.exe'
        :return:
        """
        connect_path = exe_path or self._config.DEFAULT_EXE_PATH
        if connect_path is None:
            raise ValueError(
                '参数 exe_path 未设置，请设置客户端对应的 exe 地址,类似 C:\\客户端安装目录\\xiadan.exe')

        self._app = pywinauto.Application().connect(
            path=connect_path, timeout=10)
        self._close_prompt_windows()
        self._main = self._app.top_window()

    @property
    def broker_type(self):
        return 'ths'

    @property
    def balance(self):
        self._switch_left_menus(['查询[F4]', '资金股票'])

        return self._get_balance_from_statics()

    def _get_balance_from_statics(self):
        result = {}
        for key, control_id in self._config.BALANCE_CONTROL_ID_GROUP.items():
            result[key] = float(
                self._main.window(
                    control_id=control_id,
                    class_name='Static',
                ).window_text())
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

    @property
    def cancel_entrusts(self):
        self._refresh()
        self._switch_left_menus(['撤单[F3]'])

        return self._get_grid_data(self._config.COMMON_GRID_CONTROL_ID)

    def cancel_entrust(self, entrust_no):
        self._refresh()
        for i, entrust in enumerate(self.cancel_entrusts):
            if entrust[
                    self._config.CANCEL_ENTRUST_ENTRUST_FIELD] == entrust_no:
                self._cancel_entrust_by_double_click(i)
                return self._handle_pop_dialogs()
        else:
            return {'message': '委托单状态错误不能撤单, 该委托单可能已经成交或者已撤'}

    def buy(self, security, price, amount, **kwargs):
        self._switch_left_menus(['买入[F1]'])

        return self.trade(security, price, amount)

    def sell(self, security, price, amount, **kwargs):
        self._switch_left_menus(['卖出[F2]'])

        return self.trade(security, price, amount)

    def market_buy(self, security, amount, ttype=None, **kwargs):
        """
        市价买入
        :param security: 六位证券代码
        :param amount: 交易数量
        :param ttype: 市价委托类型，默认客户端默认选择，
                     深市可选 ['对手方最优价格', '本方最优价格', '即时成交剩余撤销', '最优五档即时成交剩余 '全额成交或撤销']
                     沪市可选 ['最优五档成交剩余撤销', '最优五档成交剩余转限价']

        :return: {'entrust_no': '委托单号'}
        """
        self._switch_left_menus(['市价委托', '买入'])

        return self.market_trade(security, amount, ttype)

    def market_sell(self, security, amount, ttype=None, **kwargs):
        """
        市价卖出
        :param security: 六位证券代码
        :param amount: 交易数量
        :param ttype: 市价委托类型，默认客户端默认选择，
                     深市可选 ['对手方最优价格', '本方最优价格', '即时成交剩余撤销', '最优五档即时成交剩余 '全额成交或撤销']
                     沪市可选 ['最优五档成交剩余撤销', '最优五档成交剩余转限价']

        :return: {'entrust_no': '委托单号'}
        """
        self._switch_left_menus(['市价委托', '卖出'])

        return self.market_trade(security, amount, ttype)

    def market_trade(self, security, amount, ttype=None, **kwargs):
        """
        市价交易
        :param security: 六位证券代码
        :param amount: 交易数量
        :param ttype: 市价委托类型，默认客户端默认选择，
                     深市可选 ['对手方最优价格', '本方最优价格', '即时成交剩余撤销', '最优五档即时成交剩余 '全额成交或撤销']
                     沪市可选 ['最优五档成交剩余撤销', '最优五档成交剩余转限价']

        :return: {'entrust_no': '委托单号'}
        """
        self._set_market_trade_params(security, amount)
        if ttype is not None:
            self._set_market_trade_type(ttype)
        self._submit_trade()

        return self._handle_pop_dialogs(handler_class=TradePopDialogHandler)

    def _set_market_trade_type(self, ttype):
        """根据选择的市价交易类型选择对应的下拉选项"""
        selects = self._main(
            control_id=self._config.TRADE_MARKET_TYPE_CONTROL_ID,
            class_name='ComboBox')
        for i, text in selects.texts():
            # skip 0 index, because 0 index is current select index
            if i == 0:
                continue
            if ttype in text:
                selects.select(i - 1)
                break
        else:
            raise TypeError('不支持对应的市价类型: {}'.format(ttype))

    def auto_ipo(self):
        self._switch_left_menus(self._config.AUTO_IPO_MENU_PATH)

        stock_list = self._get_grid_data(self._config.COMMON_GRID_CONTROL_ID)

        if len(stock_list) == 0:
            return {'message': '今日无新股'}
        invalid_list_idx = [
            i for i, v in enumerate(stock_list) if v['申购数量'] <= 0
        ]

        if len(stock_list) == len(invalid_list_idx):
            return {'message': '没有发现可以申购的新股'}

        self._click(self._config.AUTO_IPO_SELECT_ALL_BUTTON_CONTROL_ID)
        self._wait(0.1)

        for row in invalid_list_idx:
            self._click_grid_by_row(row)
        self._wait(0.1)

        self._click(self._config.AUTO_IPO_BUTTON_CONTROL_ID)
        self._wait(0.1)

        return self._handle_pop_dialogs()

    def _click_grid_by_row(self, row):
        x = self._config.COMMON_GRID_LEFT_MARGIN
        y = self._config.COMMON_GRID_FIRST_ROW_HEIGHT + self._config.COMMON_GRID_ROW_HEIGHT * row
        self._app.top_window().window(
            control_id=self._config.COMMON_GRID_CONTROL_ID,
            class_name='CVirtualGridCtrl').click(coords=(x, y))

    def _is_exist_pop_dialog(self):
        self._wait(0.2)  # wait dialog display
        return self._main.wrapper_object() != self._app.top_window(
        ).wrapper_object()

    def _run_exe_path(self, exe_path):
        return os.path.join(os.path.dirname(exe_path), 'xiadan.exe')

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

        return self._handle_pop_dialogs(handler_class=TradePopDialogHandler)

    def _click(self, control_id):
        self._app.top_window().window(
            control_id=control_id, class_name='Button').click()

    def _submit_trade(self):
        time.sleep(0.05)
        self._main.window(
            control_id=self._config.TRADE_SUBMIT_CONTROL_ID,
            class_name='Button').click()

    def _get_pop_dialog_title(self):
        return self._app.top_window().window(
            control_id=self._config.POP_DIALOD_TITLE_CONTROL_ID).window_text()

    def _set_trade_params(self, security, price, amount):
        code = security[-6:]

        self._type_keys(self._config.TRADE_SECURITY_CONTROL_ID, code)

        # wait security input finish
        self._wait(0.1)

        self._type_keys(self._config.TRADE_PRICE_CONTROL_ID,
                        easyutils.round_price_by_code(price, code))
        self._type_keys(self._config.TRADE_AMOUNT_CONTROL_ID, str(int(amount)))

    def _set_market_trade_params(self, security, amount):
        code = security[-6:]

        self._type_keys(self._config.TRADE_SECURITY_CONTROL_ID, code)

        # wait security input finish
        self._wait(0.1)

        self._type_keys(self._config.TRADE_AMOUNT_CONTROL_ID, str(int(amount)))

    def _get_grid_data(self, control_id):
        grid = self._main.window(
            control_id=control_id, class_name='CVirtualGridCtrl')
        grid.type_keys('^A^C')
        return self._format_grid_data(self._get_clipboard_data())

    def _type_keys(self, control_id, text):
        self._main.window(
            control_id=control_id, class_name='Edit').set_edit_text(text)

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
                handle = self._main.window(
                    control_id=129, class_name='SysTreeView32')
                # sometime can't find handle ready, must retry
                handle.wait('ready', 2)
                return handle
            except:
                pass

    def _format_grid_data(self, data):
        df = pd.read_csv(
            io.StringIO(data),
            delimiter='\t',
            dtype=self._config.GRID_DTYPE,
            na_filter=False,
        )
        return df.to_dict('records')

    def _cancel_entrust_by_double_click(self, row):
        x = self._config.CANCEL_ENTRUST_GRID_LEFT_MARGIN
        y = self._config.CANCEL_ENTRUST_GRID_FIRST_ROW_HEIGHT + self._config.CANCEL_ENTRUST_GRID_ROW_HEIGHT * row
        self._app.top_window().window(
            control_id=self._config.COMMON_GRID_CONTROL_ID,
            class_name='CVirtualGridCtrl').double_click(coords=(x, y))

    def _refresh(self):
        self._switch_left_menus(['买入[F1]'], sleep=0.05)

    def _handle_pop_dialogs(self, handler_class=PopDialogHandler):
        handler = handler_class(self._app)

        while self._is_exist_pop_dialog():
            title = self._get_pop_dialog_title()

            result = handler.handle(title)
            if result:
                return result
        return {'message': 'success'}

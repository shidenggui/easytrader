# -*- coding: utf-8 -*-
import pywinauto
import pywinauto.clipboard
from win32gui import SetForegroundWindow

from . import clienttrader
import logging

class HTClientTrader(clienttrader.BaseLoginClientTrader):

    login_test_host: bool = True

    @property
    def broker_type(self):
        return "ht"

    def login(self, user, password, exe_path, comm_password=None, **kwargs):
        """
        :param user: 用户名
        :param password: 密码
        :param exe_path: 客户端路径, 类似
        :param comm_password:
        :param kwargs:
        :return:
        """
        self._editor_need_type_keys = False
        if comm_password is None:
            raise ValueError("华泰必须设置通讯密码")

        try:
            self._app = pywinauto.Application().connect(
                path=self._run_exe_path(exe_path), timeout=1
            )
        # pylint: disable=broad-except
        except Exception:
            self._app = pywinauto.Application().start(exe_path)

            # wait login window ready
            while True:
                try:
                    self._app.top_window().Edit1.wait("ready")
                    break
                except RuntimeError:
                    pass
            self.login_test_host = False
            if self.login_test_host:
                self._app.top_window().type_keys("%t")
                self.wait(0.5)
                try:
                    self._app.top_window().Button2.wait('enabled',timeout=30, retry_interval=5)
                    self._app.top_window().Button5.check()  # enable 自动选择
                    self.wait(0.5)
                    self._app.top_window().Button3.click()
                    self.wait(0.3)
                except Exception as ex:
                    logging.exception("test speed error", ex)
                    self._app.top_window().wrapper_object().close()
                    self.wait(0.3)

            self._app.top_window().Edit1.set_focus()
            self._app.top_window().Edit1.type_keys(user)
            self._app.top_window().Edit2.type_keys(password)

            self._app.top_window().Edit3.type_keys(comm_password)

            self._app.top_window().button0.click()

            # detect login is success or not
            self._app.top_window().wait_not("exists", 100)

            self._app = pywinauto.Application().connect(
                path=self._run_exe_path(exe_path), timeout=10
            )
        self._close_prompt_windows()
        self._main = self._app.window(title="网上股票交易系统5.0")

    @property
    def balance(self):
        self._switch_left_menus(self._config.BALANCE_MENU_PATH)

        return self._get_balance_from_statics()

    def _get_balance_from_statics(self):
        result = {}
        for key, control_id in self._config.BALANCE_CONTROL_ID_GROUP.items():
            result[key] = float(
                self._main.child_window(
                    control_id=control_id, class_name="Static"
                ).window_text()
            )
        return result


class WKClientTrader(HTClientTrader):

    @property
    def broker_type(self):
        return "wk"

    def login(self, user, password, exe_path, comm_password=None, **kwargs):
        """
                :param user: 用户名
                :param password: 密码
                :param exe_path: 客户端路径, 类似
                :param comm_password:
                :param kwargs:
                :return:
                """
        self._editor_need_type_keys = False
        if comm_password is None:
            raise ValueError("五矿必须设置通讯密码")

        try:
            self._app = pywinauto.Application().connect(
                path=self._run_exe_path(exe_path), timeout=1
            )
        # pylint: disable=broad-except
        except Exception:
            self._app = pywinauto.Application().start(exe_path)

            # wait login window ready
            while True:
                try:
                    self._app.top_window().Edit1.wait("ready")
                    break
                except RuntimeError:
                    pass
            # self.login_test_host = False
            # if self.login_test_host:
            #     self._app.top_window().type_keys("%t")
            #     self.wait(0.5)
            #     try:
            #         self._app.top_window().Button2.wait('enabled', timeout=30, retry_interval=5)
            #         self._app.top_window().Button5.check()  # enable 自动选择
            #         self.wait(0.5)
            #         self._app.top_window().Button3.click()
            #         self.wait(0.3)
            #     except Exception as ex:
            #         logging.exception("test speed error", ex)
            #         self._app.top_window().wrapper_object().close()
            #         self.wait(0.3)

            self._app.top_window().Edit1.set_focus()
            self._app.top_window().Edit1.set_edit_text(user)
            self._app.top_window().Edit2.set_edit_text(password)

            self._app.top_window().Edit3.set_edit_text(comm_password)

            self._app.top_window().Button1.click()

            # detect login is success or not
            self._app.top_window().wait_not("exists", 100)

            self._app = pywinauto.Application().connect(
                path=self._run_exe_path(exe_path), timeout=10
            )
        self._close_prompt_windows()
        self._main = self._app.window(title="网上股票交易系统5.0")
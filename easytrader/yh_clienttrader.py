# coding:utf8
import pywinauto
import pywinauto.clipboard
import re
import tempfile

from . import clienttrader
from . import helpers


class YHClientTrader(clienttrader.ClientTrader):
    @property
    def broker_type(self):
        return 'yh'

    def login(self, user, password, exe_path, comm_password=None, **kwargs):
        """
        登陆客户端
        :param user: 账号
        :param password: 明文密码
        :param exe_path: 客户端路径类似 r'C:\中国银河证券双子星3.2\Binarystar.exe',
            默认 r'C:\中国银河证券双子星3.2\Binarystar.exe'
        :param comm_password: 通讯密码, 华泰需要，可不设
        :return:
        """
        try:
            self._app = pywinauto.Application().connect(
                path=self._run_exe_path(exe_path), timeout=1)
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

            while True:
                self._app.top_window().Edit3.type_keys(
                    self._handle_verify_code())

                self._app.top_window()['登录'].click()

                # detect login is success or not
                try:
                    self._app.top_window().wait_not('exists visible', 10)
                    break
                except:
                    pass

            self._app = pywinauto.Application().connect(
                path=self._run_exe_path(exe_path), timeout=10)
        self._close_prompt_windows()
        self._main = self._app.window(title='网上股票交易系统5.0')
        try:
            self._main.window(
                control_id=129, class_name='SysTreeView32').wait('ready', 2)
        except:
            self._wait(2)
            self._switch_window_to_normal_mode()

    def _switch_window_to_normal_mode(self):
        self._app.top_window().window(
            control_id=32812, class_name='Button').click()

    def _handle_verify_code(self):
        control = self._app.top_window().window(control_id=22202)
        control.click()
        control.draw_outline()

        file_path = tempfile.mktemp()
        control.capture_as_image().save(file_path, 'jpeg')
        vcode = helpers.recognize_verify_code(file_path, 'yh_client')
        return ''.join(re.findall('\d+', vcode))

    @property
    def balance(self):
        self._switch_left_menus(self._config.BALANCE_MENU_PATH)

        return self._get_grid_data(self._config.BALANCE_GRID_CONTROL_ID)

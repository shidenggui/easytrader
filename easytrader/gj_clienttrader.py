# coding:utf8
from __future__ import division

import functools
import io
import os
import re
import tempfile
import time
import sys

import easyutils
# import pandas as pd
import pywinauto
import pywinauto.clipboard
from . import exceptions
from . import helpers
from .yh_clienttrader import YHClientTrader
from .log import log


class GJClientTrader(YHClientTrader):
    @property
    def broker_type(self):
        return 'gj'

    def login(self, user, password, exe_path, comm_password=None, **kwargs):
        """
        登陆客户端
        :param user: 账号
        :param password: 明文密码
        :param exe_path: 客户端路径类似 r'C:\中国银河证券双子星3.2\Binarystar.exe', 默认 r'C:\中国银河证券双子星3.2\Binarystar.exe'
        :param comm_password: 通讯密码, 华泰需要，可不设
        :return:
        """
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
            edit3 = self._app.top_window().window(control_id=0x3eb)
            while True:
                try:
                    code = self._handle_verify_code()
                    print('verify code=',code)
                    edit3.type_keys(
                        code
                    )
                    time.sleep(1)
                    self._app.top_window()['确定(Y)'].click()
                    # detect login is success or not
                    try:
                        self._app.top_window().wait_not('exists', 5)
                        break
                    except:
                        self._app.top_window()['确定'].click()
                        pass
                except Exception as e:
                    print("Exception,",e)
                    pass
            print('connect start')
            self._app = pywinauto.Application().connect(path=self._run_exe_path(exe_path), timeout=10)
            print('connect end')
        self._main = self._app.window(title='网上股票交易系统5.0')

    def _handle_verify_code(self):
        control = self._app.top_window().window(control_id=0x5db)
        control.click()
        time.sleep(0.2)
        file_path = tempfile.mktemp()+'.jpg'
        control.capture_as_image().save(file_path)
        time.sleep(0.2)
        vcode = helpers.recognize_verify_code(file_path, 'gj_client')
        return ''.join(re.findall('[a-zA-Z0-9]+', vcode))

    @property
    def balance(self):
        self._switch_left_menus(['查询[F4]', '资金股票'])
        retv={}
        retv['enable_balance'] = self._app.top_window().window(control_id=0x3f8).window_text()
        retv['total_balance'] = self._app.top_window().window(control_id=0x3f7).window_text()
        return [retv]


    
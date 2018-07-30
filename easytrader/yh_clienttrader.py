# -*- coding: utf-8 -*-
import re
import tempfile
import time
import pywinauto
import pandas as pd
from . import clienttrader
from . import grid_data_get_strategy
from . import helpers


class YHClientTrader(clienttrader.BaseLoginClientTrader):
#     def __init__(self):
#         """
#         Changelog:

#         2018.07.01:
#             银河客户端 2018.5.11 更新后不再支持通过剪切板复制获取 Grid 内容，
#             改为使用保存为 Xls 再读取的方式获取
#         """
#         super().__init__()
#         self.grid_data_get_strategy = grid_data_get_strategy.XlsStrategy

    @property
    def broker_type(self):
        return "yh"

    def login(self, user, password, exe_path, comm_password=None, **kwargs):
        # 至多尝试3次
        for i in range(3):
            try:
                self.login_basic(user, password, exe_path, comm_password, **kwargs)
                re = True
                break
            except Exception:
                print('login again')
                self.close_all()
                time.sleep(0.5)
                re = False
        return re
    
    def close_all(self):
        for i in pywinauto.findwindows.find_windows(title_re = r'用户登录', class_name='#32770'):
            pywinauto.Application().connect(handle=i).kill()  
        for i in pywinauto.findwindows.find_windows(title_re = r'网上股票交易系统'):
            pywinauto.Application().connect(handle=i).kill() 

    def login_basic(self, user, password, exe_path, comm_password=None, **kwargs):
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
                path=self._run_exe_path(exe_path), timeout=1
            )
        except Exception:
            self._app = pywinauto.Application().start(exe_path)

            # logie为用户登录界面
            logie = self._app.window_(title_re='用户登录')
            logie.wait('ready', timeout=30, retry_interval=None)
            
            # wait login window ready
            for c in range(20):
                try:
                    logie.Edit1.wait("ready")
                    break
                except RuntimeError:
                    time.sleep(1)
                    pass
            # 输入用户名
            logie.Edit1.SetEditText('')
            logie.Edit1.SetEditText(user)
            # 输入交易密码
            logie.Edit2.SetEditText('')
            logie.Edit2.SetEditText(password)

            # 输入验证码
            for c in range(30):
                verify_code = self._handle_verify_code(logie)
                logie.Edit3.SetEditText('')
                logie.Edit3.SetEditText(verify_code)
                # 点击确定
                logie['确定(&Y)'].click()
                # 等待登录界面关闭
                try:
                    logie.wait_not('exists visible', timeout=30, retry_interval=None)
                    break
                except:
                    for w in self._app.windows(class_name="#32770"):
                        if w.is_visible() and w.window_text() != '用户登录':
                            w.close()
                    time.sleep(0.1)
            # 重连客户端
            self._app = pywinauto.Application().connect(
                path=self._run_exe_path(exe_path), timeout=10
            )
        for c in range(10):
            self._close_prompt_windows()   
            self._main = self._app.window_(title_re="网上股票交易系统")
            try:
                self._main.wait('exists enabled visible ready', 2)
                self._main_handle = self._main.handle
                break
            except:
                self._switch_window_to_normal_mode()
                time.sleep(3)
        
        self._left_treeview = self._main.window_(control_id=129, class_name="SysTreeView32") 
        self._left_treeview.wait('exists enabled visible ready')

        self._pwindow = self._main.window(control_id=59649, class_name='#32770')
        self._pwindow.wait('exists enabled visible ready')
        
        # 等待一切就绪
        print(self.balance)

        # 关闭其它窗口
        self._check_top_window()
        
        
#         self._close_prompt_windows()
#         self._main = self._app.window(title="网上股票交易系统5.0")
#         try:
#             self._main.window(control_id=129, class_name="SysTreeView32").wait(
#                 "ready", 2
#             )
#         except:
#             self.wait(2)
#             self._switch_window_to_normal_mode()

    def _switch_window_to_normal_mode(self):
        self._app.top_window().window(
            control_id=32812, class_name="Button"
        ).click()

    def _handle_verify_code(self, logie):
        test = logie.wrapper_object()
        for i in test.children():
            if i.control_id()==1499:
                i.click()
                time.sleep(2)
                break
        pos = i.Rectangle()
        pos.right = int(pos.left + (pos.right-pos.left)*4/3)
        file_path = tempfile.mktemp()
        test.capture_as_image(pos).save(file_path, "jpeg")

        verify_code = helpers.recognize_verify_code(file_path, "yh_client")
        res = "".join(re.findall("\d+", verify_code))
        print('识别验证码', res)
        return res

#         control = logie.window(control_id=22202)
#         control.click()
#         control.draw_outline()

#         file_path = tempfile.mktemp()
#         control.capture_as_image().save(file_path, "jpeg")
#         verify_code = helpers.recognize_verify_code(file_path, "yh_client")
#         return "".join(re.findall("\d+", verify_code))

    @property
    def balance(self):
        for c in range(10):
            self._switch_left_menus(["查询[F4]", "资金股份"])
            test = self._get_grid_data(self._config.BALANCE_GRID_CONTROL_ID)
            if isinstance(test, pd.DataFrame):
                break
                
        if isinstance(test, pd.DataFrame):
            if len(test) > 0:
                test = test.to_dict("records")[0]
                bala = {}
                bala['total_value'] = test['总资产']
                bala['stock_value'] = test['总市值']
                bala['ky_cash'] = test['可用金额']
                bala['kq_cash'] = test['资金余额']
            else:
                bala = {}
        else:
            print('读取balance失败...')
            bala = {}
            
        return bala
#         self._switch_left_menus(self._config.BALANCE_MENU_PATH)

#         return self._get_grid_data(self._config.BALANCE_GRID_CONTROL_ID)

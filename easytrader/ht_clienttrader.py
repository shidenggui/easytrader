# -*- coding: utf-8 -*-
import pywinauto
import pywinauto.clipboard
import time
from . import clienttrader


class HTClientTrader(clienttrader.BaseLoginClientTrader):
    @property
    def broker_type(self):
        return "ht"
    
    def login(self, user, password, exe_path, comm_password=None, **kwargs):
        c = 0 
        while c < 3:
            c += 1
            try:
                self.login_basic(user, password, exe_path, comm_password, **kwargs)
                break
            except Exception:
                print('login again')
                for i in pywinauto.findwindows.find_windows(title_re = r'用户登录', class_name='#32770'):
                    pywinauto.Application().connect(handle=i).kill()  
                
            
    def login_basic(self, user, password, exe_path, comm_password=None, **kwargs):
        """
        :param user: 用户名
        :param password: 密码
        :param exe_path: 客户端路径, 类似
        :param comm_password:
        :param kwargs:
        :return:
        """
        if comm_password is None:
            raise ValueError("华泰必须设置通讯密码")

        try:
            self._app = pywinauto.Application().connect(
                path=self._run_exe_path(exe_path), timeout=1
            )
           # 关闭其它窗口
            for w in self._app.windows(class_name="#32770"):
                if w.is_visible() and ('股票交易系统' not in w.window_text()):
                    w.close()
        except Exception:
            self._app = pywinauto.Application().start(exe_path)
            
            # logie为用户登录界面
            logie = self._app.window_(title_re='用户登录')
            logie.wait('ready', timeout=30, retry_interval=None)
            
            # wait login window ready
            while True:
                try:
                    logie.Edit1.wait("ready")
                    break
                except RuntimeError:
                    pass
            # 输入用户名
            logie.Edit1.SetEditText('')
            logie.Edit1.SetEditText(user)
            # 输入交易密码
            logie.Edit2.SetEditText('')
            logie.Edit2.SetEditText(password)
            # 输入通讯密码
            logie.Edit3.SetEditText('')
            logie.Edit3.SetEditText(comm_password)
            # 点击确定
            logie.button0.click()
            
            # 等待登录界面关闭
            logie.wait_not('exists', timeout=30, retry_interval=None)
            time.sleep(0.1)
            
            # 关闭其它窗口
            for w in self._app.windows(class_name="#32770"):
                if w.is_visible() and ('股票交易系统' not in w.window_text()):
                    w.close()
                   
            # 重连客户端
            time.sleep(0.1)
            self._app = pywinauto.Application().connect(
                path=self._run_exe_path(exe_path), timeout=10
            )
            time.sleep(5)
        self._main = self._app.window_(title_re="网上股票交易系统")
        self._main_handle = self._main.handle
        self._left_treeview = self._main.window_(control_id=129, class_name="SysTreeView32").wrapper_object()
        self._left_treeview.wait_for_idle()    
        

    @property
    def balance(self):
        self._switch_left_menus(self._config.BALANCE_MENU_PATH)
        return self._get_balance_from_statics()

    def _get_balance_from_statics(self):
        result = {}
        for key, control_id in self._config.BALANCE_CONTROL_ID_GROUP.items():
            ww = self._main.window(control_id=control_id, class_name="Static")
            @pywinauto.timings.always_wait_until_passes(30, 0.1)
            def f(ww):
                return float(ww.window_text())
            result[key] = f(ww)
        return result
    

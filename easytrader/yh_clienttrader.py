from __future__ import division

import time
import traceback
import win32api
import win32clipboard as cp
import win32gui
from io import StringIO
import subprocess
import tempfile
import pandas as pd
from . import helpers
import win32com.client
from PIL import ImageGrab
import time
import win32con
import os
from .log import log


class YHClientTrader():
    def __init__(self):
        self.Title = '网上股票交易系统5.0'
        

    def login(self, user, password, exe_path='C:\中国银河证券双子星3.2\Binarystar.exe'):
        if self._has_main_window():
            self._get_handles()
            log.info('检测到交易客户端已启动，连接完毕')
            return
        if not self._has_login_window():
            if not os.path.exists(exe_path):
                raise FileNotFoundError('在　{} 未找到应用程序，请用 exe_path 指定应用程序目录'.format(exe_path))
            subprocess.Popen(exe_path)      
        # 检测登陆窗口
        for _ in range(30):
            if self._has_login_window():
                break
            time.sleep(1)
        else:
            raise Exception('启动客户端失败，无法检测到登陆窗口')
        log.info('成功检测到客户端登陆窗口')
        self._set_trade_mode()
        self._set_login_name(user)
        self._set_login_password(password)
        self._set_login_verify_code()
        self._click_login_button()
        
        for _ in range(30):
            if self._has_main_window():
                self._get_handles()
                break
            time.sleep(1)
        else:
            raise Exception('启动交易客户端失败')
        log.info('客户端登陆成功')
    def _set_login_verify_code(self):
        verify_code_image = self._get_verify_code()
        image_path = tempfile.mktemp() + '.jpg'
        verify_code_image.save(image_path)
        result = helpers.recognize_verify_code(image_path, 'yh_client')
        time.sleep(0.2)
        self._input_login_verify_code(result)
        time.sleep(0.4)
        
    def _set_trade_mode(self):
        input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x4f4d)
        win32gui.SendMessage(input_hwnd, win32con.BM_CLICK, None, None)
    def _set_login_name(self, user):
        input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x5523)
        win32gui.SendMessage(input_hwnd, win32con.WM_SETTEXT, None, user)
        
    def _set_login_password(self, password):
        input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x5534)
        win32gui.SendMessage(input_hwnd, win32con.WM_SETTEXT, None, password)
    def _has_login_window(self):       
        self.login_hwnd = win32gui.FindWindow(None, ' - 北京电信')
        log.debug('检测到登陆窗口句柄：{}'.format(self.login_hwnd))
        if self.login_hwnd != 0:
            return True
        return False
        
    def _input_login_verify_code(self, code):
        input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x56b9)
        win32gui.SendMessage(input_hwnd, win32con.WM_SETTEXT, None, code)
    
    def _click_login_button(self):
        input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x1)
        win32gui.SendMessage(input_hwnd, win32con.BM_CLICK, None, None)
    def _has_main_window(self):
        try:
            self._get_handles()
        except:
            return False
        return True
    
       
    def _get_verify_code(self):
        verify_code_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x56ba)
        self.set_foreground_window(self.login_hwnd)
        time.sleep(0.2)
        rect = win32gui.GetWindowRect(verify_code_hwnd)
        return ImageGrab.grab(rect)
    def _get_handles(self):
        Main = win32gui.FindWindow(0, self.Title)  # 交易窗口
        Frame = win32gui.GetDlgItem(Main, 59648)  # 操作窗口框架
        Afxwnd = win32gui.GetDlgItem(Frame, 59648)  # 操作窗口框架
        Hexin = win32gui.GetDlgItem(Afxwnd, 129)
        Scrolwnd = win32gui.GetDlgItem(Hexin, 200)  # 左部折叠菜单控件
        treev = win32gui.GetDlgItem(Scrolwnd, 129)  # 左部折叠菜单控件

        # 获取委托窗口所有控件句柄
        win32api.PostMessage(treev, win32con.WM_KEYDOWN, win32con.VK_F1, 0)
        time.sleep(0.5)
        F_Bentrust = win32gui.GetDlgItem(Frame, 59649)  # 委托窗口框架
        self.E_Bsymbol = win32gui.GetDlgItem(F_Bentrust, 1032)  # 买入代码输入框
        self.E_Bprice = win32gui.GetDlgItem(F_Bentrust, 1033)  # 买入价格输入框
        self.E_Bvol = win32gui.GetDlgItem(F_Bentrust, 1034)  # 买入数量输入框
        self.B_Buy = win32gui.GetDlgItem(F_Bentrust, 1006)  # 买入确认按钮
        self.B_refresh = win32gui.GetDlgItem(F_Bentrust, 32790)  # 刷新持仓按钮
        F_Bhexin = win32gui.GetDlgItem(F_Bentrust, 1047)  # 持仓显示框架
        F_Bhexinsub = win32gui.GetDlgItem(F_Bhexin, 200)  # 持仓显示框架
        self.G_position = win32gui.GetDlgItem(F_Bhexinsub, 1047)  # 持仓列表
        win32api.PostMessage(treev, win32con.WM_KEYDOWN, win32con.VK_F2, 0)
        time.sleep(0.5)
        F_Sentrust = win32gui.GetDlgItem(Frame, 59649)  # 委托窗口框架
        self.E_Ssymbol = win32gui.GetDlgItem(F_Sentrust, 1032)  # 卖出代码输入框
        self.E_Sprice = win32gui.GetDlgItem(F_Sentrust, 1033)  # 卖出价格输入框
        self.E_Svol = win32gui.GetDlgItem(F_Sentrust, 1034)  # 卖出数量输入框
        self.B_Sell = win32gui.GetDlgItem(F_Sentrust, 1006)  # 卖出确认按钮

        # 撤单窗口
        win32api.PostMessage(treev, win32con.WM_KEYDOWN, win32con.VK_F3, 0)
        time.sleep(0.5)
        F_Centrust = win32gui.GetDlgItem(Frame, 59649)  # 撤单窗口框架
        self.E_Csymbol = win32gui.GetDlgItem(F_Centrust, 3348)  # 卖出代码输入框
        self.B_Csort = win32gui.GetDlgItem(F_Centrust, 3349)  # 查询代码按钮
        self.B_Cbuy = win32gui.GetDlgItem(F_Centrust, 30002)  # 撤买
        self.B_Csell = win32gui.GetDlgItem(F_Centrust, 30003)  # 撤卖
        F_Chexin = win32gui.GetDlgItem(F_Centrust, 1047)
        F_Chexinsub = win32gui.GetDlgItem(F_Chexin, 200)
        self.G_entrust = win32gui.GetDlgItem(F_Chexinsub, 1047)  # 委托列表

    def buy(self, stock_code, price, amount):
        """
        买入股票
        :param stock_code: 股票代码
        :param price: 买入价格
        :param amount: 买入股数
        :return: bool: 买入信号是否成功发出
        """
        amount = str(amount // 100 * 100)
        price = str(price)

        try:
            win32gui.SendMessage(self.E_Bsymbol, win32con.WM_SETTEXT, None, stock_code)  # 输入买入代码
            win32gui.SendMessage(self.E_Bprice, win32con.WM_SETTEXT, None, price)  # 输入买入价格
            time.sleep(0.2)
            win32gui.SendMessage(self.E_Bvol, win32con.WM_SETTEXT, None, amount)  # 输入买入数量
            time.sleep(0.2)
            win32gui.SendMessage(self.B_Buy, win32con.BM_CLICK, None, None)  # 买入确定
            time.sleep(0.3)
        except:
            traceback.print_exc()
            return False
        return True

    def sell(self, stock_code, price, amount):
        """
        买出股票
        :param stock_code: 股票代码
        :param price: 卖出价格
        :param amount: 卖出股数
        :return: bool 卖出操作是否成功
        """
        amount = str(amount // 100 * 100)
        price = str(price)

        try:
            win32gui.SendMessage(self.E_Ssymbol, win32con.WM_SETTEXT, None, stock_code)  # 输入卖出代码
            win32gui.SendMessage(self.E_Sprice, win32con.WM_SETTEXT, None, price)  # 输入卖出价格
            win32gui.SendMessage(self.E_Sprice, win32con.BM_CLICK, None, None)  # 输入卖出价格
            print('add click')
            time.sleep(0.2)
            win32gui.SendMessage(self.E_Svol, win32con.WM_SETTEXT, None, amount)  # 输入卖出数量
            time.sleep(0.2)
            win32gui.SendMessage(self.B_Sell, win32con.BM_CLICK, None, None)  # 卖出确定
            time.sleep(0.3)
        except:
            traceback.print_exc()
            return False
        return True

    def cancel_entrust(self, stock_code, direction):
        """
        撤单
        :param stock_code: str 股票代码
        :param direction: str 'buy' 撤买， 'sell' 撤卖
        :return: bool 撤单信号是否发出
        """
        direction = 0 if direction == 'buy' else 1

        try:
            win32gui.SendMessage(self.B_refresh, win32con.BM_CLICK, None, None)  # 刷新持仓
            time.sleep(0.2)
            win32gui.SendMessage(self.E_Csymbol, win32con.WM_SETTEXT, None, stock_code)  # 输入撤单
            win32gui.SendMessage(self.B_Csort, win32con.BM_CLICK, None, None)  # 查询代码
            time.sleep(0.2)
            if direction == 0:
                win32gui.SendMessage(self.B_Cbuy, win32con.BM_CLICK, None, None)  # 撤买
            elif direction == 1:
                win32gui.SendMessage(self.B_Csell, win32con.BM_CLICK, None, None)  # 撤卖
        except:
            traceback.print_exc()
            return False
        time.sleep(0.3)
        return True

    @property
    def position(self):
        return self.get_position()

    def get_position(self):
        win32gui.SendMessage(self.B_refresh, win32con.BM_CLICK, None, None)  # 刷新持仓
        time.sleep(0.1)
        self.set_foreground_window(self.G_position)
        time.sleep(0.1)
        data = self.read_clipboard()
        return self.project_copy_data(data)

    @staticmethod
    def project_copy_data(copy_data):
        reader = StringIO(copy_data)
        df = pd.read_csv(reader, delim_whitespace=True)
        return df.to_dict('records')

    @staticmethod
    def read_clipboard():
        win32api.keybd_event(17, 0, 0, 0)
        win32api.keybd_event(67, 0, 0, 0)
        win32api.keybd_event(67, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        cp.OpenClipboard()
        raw_text = cp.GetClipboardData(win32con.CF_UNICODETEXT)
        cp.CloseClipboard()
        return raw_text

    @staticmethod
    def project_position_str(raw):
        reader = StringIO(raw)
        df = pd.read_csv(reader, delim_whitespace=True)
        return df

    @staticmethod
    def set_foreground_window(hwnd):
        shell = win32com.client.Dispatch('WScript.Shell')
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(hwnd)

    @property
    def entrust(self):
        return self.get_entrust()

    def get_entrust(self):
        win32gui.SendMessage(self.B_refresh, win32con.BM_CLICK, None, None)  # 刷新持仓
        time.sleep(0.2)
        self.set_foreground_window(self.G_entrust)
        time.sleep(0.2)
        data = self.read_clipboard()
        return self.project_copy_data(data)

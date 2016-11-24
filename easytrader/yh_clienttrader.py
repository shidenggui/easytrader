from __future__ import division

import os
import subprocess
import tempfile
import time
import traceback
import win32api
import win32gui
from io import StringIO

import pandas as pd
import pyperclip
import win32com.client
import win32con
from PIL import ImageGrab

from . import helpers
from .log import log


class YHClientTrader():
    def __init__(self):
        self.Title = '网上股票交易系统5.0'

    def prepare(self, config_path=None, user=None, password=None, exe_path='C:\中国银河证券双子星3.2\Binarystar.exe'):
        """
        登陆银河客户端
        :param config_path: 银河登陆配置文件，跟参数登陆方式二选一
        :param user: 银河账号
        :param password: 银河明文密码
        :param exe_path: 银河客户端路径
        :return:
        """
        if config_path is not None:
            account = helpers.file2dict(config_path)
            user = account['user']
            password = account['password']
        self.login(user, password, exe_path)

    def login(self, user, password, exe_path):
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

        # 登陆
        self._set_trade_mode()
        self._set_login_name(user)
        self._set_login_password(password)
        for _ in range(10):
            self._set_login_verify_code()
            self._click_login_button()
            time.sleep(3)
            if not self._has_login_window():
                break
            self._click_login_verify_code()

        for _ in range(60):
            if self._has_main_window():
                self._get_handles()
                break
            time.sleep(1)
        else:
            raise Exception('启动交易客户端失败')
        log.info('客户端登陆成功')

    def _set_login_verify_code(self):
        verify_code_image = self._grab_verify_code()
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
        time.sleep(0.5)
        input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x5523)
        win32gui.SendMessage(input_hwnd, win32con.WM_SETTEXT, None, user)

    def _set_login_password(self, password):
        time.sleep(0.5)
        input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x5534)
        win32gui.SendMessage(input_hwnd, win32con.WM_SETTEXT, None, password)

    def _has_login_window(self):
        for title in [' - 北京电信', ' - 北京电信 - 北京电信']:
            self.login_hwnd = win32gui.FindWindow(None, title)
            if self.login_hwnd != 0:
                return True
        return False

    def _input_login_verify_code(self, code):
        input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x56b9)
        win32gui.SendMessage(input_hwnd, win32con.WM_SETTEXT, None, code)

    def _click_login_verify_code(self):
        input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x56ba)
        rect = win32gui.GetWindowRect(input_hwnd)
        self._mouse_click(rect[0] + 5, rect[1] + 5)

    @staticmethod
    def _mouse_click(x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    def _click_login_button(self):
        time.sleep(1)
        input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x1)
        win32gui.SendMessage(input_hwnd, win32con.BM_CLICK, None, None)

    def _has_main_window(self):
        try:
            self._get_handles()
        except:
            return False
        return True

    def _grab_verify_code(self):
        verify_code_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x56ba)
        self._set_foreground_window(self.login_hwnd)
        time.sleep(1)
        rect = win32gui.GetWindowRect(verify_code_hwnd)
        return ImageGrab.grab(rect)

    def _get_handles(self):
        trade_main_hwnd = win32gui.FindWindow(0, self.Title)  # 交易窗口
        operate_frame_hwnd = win32gui.GetDlgItem(trade_main_hwnd, 59648)  # 操作窗口框架
        operate_frame_afx_hwnd = win32gui.GetDlgItem(operate_frame_hwnd, 59648)  # 操作窗口框架
        hexin_hwnd = win32gui.GetDlgItem(operate_frame_afx_hwnd, 129)
        scroll_hwnd = win32gui.GetDlgItem(hexin_hwnd, 200)  # 左部折叠菜单控件
        tree_view_hwnd = win32gui.GetDlgItem(scroll_hwnd, 129)  # 左部折叠菜单控件

        # 获取委托窗口所有控件句柄
        win32api.PostMessage(tree_view_hwnd, win32con.WM_KEYDOWN, win32con.VK_F1, 0)
        time.sleep(0.5)

        # 买入相关
        entrust_window_hwnd = win32gui.GetDlgItem(operate_frame_hwnd, 59649)  # 委托窗口框架
        self.buy_stock_code_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 1032)  # 买入代码输入框
        self.buy_price_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 1033)  # 买入价格输入框
        self.buy_amount_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 1034)  # 买入数量输入框
        self.buy_btn_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 1006)  # 买入确认按钮
        self.refresh_entrust_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 32790)  # 刷新持仓按钮
        entrust_frame_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 1047)  # 持仓显示框架
        entrust_sub_frame_hwnd = win32gui.GetDlgItem(entrust_frame_hwnd, 200)  # 持仓显示框架
        self.position_list_hwnd = win32gui.GetDlgItem(entrust_sub_frame_hwnd, 1047)  # 持仓列表
        win32api.PostMessage(tree_view_hwnd, win32con.WM_KEYDOWN, win32con.VK_F2, 0)
        time.sleep(0.5)

        # 卖出相关
        sell_entrust_frame_hwnd = win32gui.GetDlgItem(operate_frame_hwnd, 59649)  # 委托窗口框架
        self.sell_stock_code_hwnd = win32gui.GetDlgItem(sell_entrust_frame_hwnd, 1032)  # 卖出代码输入框
        self.sell_price_hwnd = win32gui.GetDlgItem(sell_entrust_frame_hwnd, 1033)  # 卖出价格输入框
        self.sell_amount_hwnd = win32gui.GetDlgItem(sell_entrust_frame_hwnd, 1034)  # 卖出数量输入框
        self.sell_btn_hwnd = win32gui.GetDlgItem(sell_entrust_frame_hwnd, 1006)  # 卖出确认按钮

        # 撤单窗口
        win32api.PostMessage(tree_view_hwnd, win32con.WM_KEYDOWN, win32con.VK_F3, 0)
        time.sleep(0.5)
        cancel_entrust_window_hwnd = win32gui.GetDlgItem(operate_frame_hwnd, 59649)  # 撤单窗口框架
        self.cancel_stock_code_hwnd = win32gui.GetDlgItem(cancel_entrust_window_hwnd, 3348)  # 卖出代码输入框
        self.cancel_query_hwnd = win32gui.GetDlgItem(cancel_entrust_window_hwnd, 3349)  # 查询代码按钮
        self.cancel_buy_hwnd = win32gui.GetDlgItem(cancel_entrust_window_hwnd, 30002)  # 撤买
        self.cancel_sell_hwnd = win32gui.GetDlgItem(cancel_entrust_window_hwnd, 30003)  # 撤卖

        chexin_hwnd = win32gui.GetDlgItem(cancel_entrust_window_hwnd, 1047)
        chexin_sub_hwnd = win32gui.GetDlgItem(chexin_hwnd, 200)
        self.entrust_list_hwnd = win32gui.GetDlgItem(chexin_sub_hwnd, 1047)  # 委托列表

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
            win32gui.SendMessage(self.buy_stock_code_hwnd, win32con.WM_SETTEXT, None, stock_code)  # 输入买入代码
            win32gui.SendMessage(self.buy_price_hwnd, win32con.WM_SETTEXT, None, price)  # 输入买入价格
            time.sleep(0.2)
            win32gui.SendMessage(self.buy_amount_hwnd, win32con.WM_SETTEXT, None, amount)  # 输入买入数量
            time.sleep(0.2)
            win32gui.SendMessage(self.buy_btn_hwnd, win32con.BM_CLICK, None, None)  # 买入确定
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
            win32gui.SendMessage(self.sell_stock_code_hwnd, win32con.WM_SETTEXT, None, stock_code)  # 输入卖出代码
            win32gui.SendMessage(self.sell_price_hwnd, win32con.WM_SETTEXT, None, price)  # 输入卖出价格
            win32gui.SendMessage(self.sell_price_hwnd, win32con.BM_CLICK, None, None)  # 输入卖出价格
            time.sleep(0.2)
            win32gui.SendMessage(self.sell_amount_hwnd, win32con.WM_SETTEXT, None, amount)  # 输入卖出数量
            time.sleep(0.2)
            win32gui.SendMessage(self.sell_btn_hwnd, win32con.BM_CLICK, None, None)  # 卖出确定
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
            win32gui.SendMessage(self.refresh_entrust_hwnd, win32con.BM_CLICK, None, None)  # 刷新持仓
            time.sleep(0.2)
            win32gui.SendMessage(self.cancel_stock_code_hwnd, win32con.WM_SETTEXT, None, stock_code)  # 输入撤单
            win32gui.SendMessage(self.cancel_query_hwnd, win32con.BM_CLICK, None, None)  # 查询代码
            time.sleep(0.2)
            if direction == 0:
                win32gui.SendMessage(self.cancel_buy_hwnd, win32con.BM_CLICK, None, None)  # 撤买
            elif direction == 1:
                win32gui.SendMessage(self.cancel_sell_hwnd, win32con.BM_CLICK, None, None)  # 撤卖
        except:
            traceback.print_exc()
            return False
        time.sleep(0.3)
        return True

    @property
    def position(self):
        return self.get_position()

    def get_position(self):
        win32gui.SendMessage(self.refresh_entrust_hwnd, win32con.BM_CLICK, None, None)  # 刷新持仓
        time.sleep(0.1)
        self._set_foreground_window(self.position_list_hwnd)
        time.sleep(0.1)
        data = self._read_clipboard()
        return self.project_copy_data(data)

    @staticmethod
    def project_copy_data(copy_data):
        reader = StringIO(copy_data)
        df = pd.read_csv(reader, delim_whitespace=True)
        return df.to_dict('records')

    def _read_clipboard(self):
        for _ in range(15):
            try:
                win32api.keybd_event(17, 0, 0, 0)
                win32api.keybd_event(67, 0, 0, 0)
                win32api.keybd_event(67, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.2)
                return pyperclip.paste()
            except Exception as e:
                log.error('open clipboard failed: {}, retry...'.format(e))
                time.sleep(1)
        else:
            raise Exception('read clipbord failed')

    @staticmethod
    def _project_position_str(raw):
        reader = StringIO(raw)
        df = pd.read_csv(reader, delim_whitespace=True)
        return df

    @staticmethod
    def _set_foreground_window(hwnd):
        shell = win32com.client.Dispatch('WScript.Shell')
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(hwnd)

    @property
    def entrust(self):
        return self.get_entrust()

    def get_entrust(self):
        win32gui.SendMessage(self.refresh_entrust_hwnd, win32con.BM_CLICK, None, None)  # 刷新持仓
        time.sleep(0.2)
        self._set_foreground_window(self.entrust_list_hwnd)
        time.sleep(0.2)
        data = self._read_clipboard()
        return self.project_copy_data(data)

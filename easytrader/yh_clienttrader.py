import win32api, win32gui, win32con, win32com
from io import StringIO
import pandas as pd
import win32clipboard as cp
import pandas as pd
import time


# ----------------------------utils------------------------------------

def find_idxSubHandle(pHandle, winClass, index=0):
    assert type(index) == int and index >= 0
    handle = win32gui.FindWindowEx(pHandle, 0, winClass, None)
    while index > 0:
        handle = win32gui.FindWindowEx(pHandle, handle, winClass, None)
        index -= 1
    return handle


def get_clipboard():
    win32api.keybd_event(17, 0, 0, 0)
    win32api.keybd_event(67, 0, 0, 0)
    win32api.keybd_event(67, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.1)
    cp.OpenClipboard()
    # raw_text = CP.GetClipboardData(win32con.CF_TEXT)
    raw_text = cp.GetClipboardData(win32con.CF_UNICODETEXT)
    cp.CloseClipboard()
    # decode = raw_text.decode('gb2312').split()
    # decode = raw_text.split()
    # decode.pop()
    # return decode
    return raw_text


# -----------------------------Class_HT------------------------------------

class YHClientTrader():
    def __init__(self):
        self.Title = '网上股票交易系统5.0'
        self._get_handles()

    def _get_handles(self):
        Main = win32gui.FindWindow(0, self.Title)  # HT交易窗口
        Frame = win32gui.GetDlgItem(Main, 59648)  # 操作窗口框架
        Afxwnd = win32gui.GetDlgItem(Frame, 59648)  # 操作窗口框架
        Hexin = win32gui.GetDlgItem(Afxwnd, 129)
        Scrolwnd = win32gui.GetDlgItem(Hexin, 200)  # 左部折叠菜单控件
        treev = win32gui.GetDlgItem(Scrolwnd, 129)  # 左部折叠菜单控件
        # 获取委托窗口所有控件句柄
        win32api.PostMessage(treev, win32con.WM_KEYDOWN, win32con.VK_F1, 0)
        time.sleep(0.1)
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
        time.sleep(0.1)
        F_Sentrust = win32gui.GetDlgItem(Frame, 59649)  # 委托窗口框架
        self.E_Ssymbol = win32gui.GetDlgItem(F_Sentrust, 1032)  # 卖出代码输入框
        self.E_Sprice = win32gui.GetDlgItem(F_Sentrust, 1033)  # 卖出价格输入框
        self.E_Svol = win32gui.GetDlgItem(F_Sentrust, 1034)  # 卖出数量输入框
        self.B_Sell = win32gui.GetDlgItem(F_Sentrust, 1006)  # 卖出确认按钮
        # 撤单窗口
        win32api.PostMessage(treev, win32con.WM_KEYDOWN, win32con.VK_F3, 0)
        time.sleep(0.1)
        F_Centrust = win32gui.GetDlgItem(Frame, 59649)  # 撤单窗口框架
        self.E_Csymbol = win32gui.GetDlgItem(F_Centrust, 3348)  # 卖出代码输入框
        self.B_Csort = win32gui.GetDlgItem(F_Centrust, 3349)  # 查询代码按钮
        self.B_Cbuy = win32gui.GetDlgItem(F_Centrust, 30002)  # 撤买
        self.B_Csell = win32gui.GetDlgItem(F_Centrust, 30003)  # 撤卖
        F_Chexin = win32gui.GetDlgItem(F_Centrust, 1047)
        F_Chexinsub = win32gui.GetDlgItem(F_Chexin, 200)
        self.G_entrust = win32gui.GetDlgItem(F_Chexinsub, 1047)  # 委托列表

    def buy(self, stock_code, price, amount):
        win32gui.SendMessage(self.E_Bsymbol, win32con.WM_SETTEXT, None, stock_code)  # 输入买入代码
        win32gui.SendMessage(self.E_Bprice, win32con.WM_SETTEXT, None, price)  # 输入买入价格
        time.sleep(0.1)
        win32gui.SendMessage(self.E_Bvol, win32con.WM_SETTEXT, None, amount)  # 输入买入数量
        time.sleep(0.1)
        win32gui.SendMessage(self.B_Buy, win32con.BM_CLICK, None, None)  # 买入确定
        time.sleep(0.2)
        return 0

    def sell(self, stock_code, price, amount):
        win32gui.SendMessage(self.E_Ssymbol, win32con.WM_SETTEXT, None, stock_code)  # 输入卖出代码
        win32gui.SendMessage(self.E_Sprice, win32con.WM_SETTEXT, None, price)  # 输入卖出价格
        time.sleep(0.1)
        win32gui.SendMessage(self.E_Svol, win32con.WM_SETTEXT, None, amount)  # 输入卖出数量
        time.sleep(0.1)
        win32gui.SendMessage(self.B_Sell, win32con.BM_CLICK, None, None)  # 卖出确定
        time.sleep(0.2)
        return 0

    def cancle(self, symbol, direction):
        win32gui.SendMessage(self.B_refresh, win32con.BM_CLICK, None, None)  # 刷新持仓
        time.sleep(0.2)
        win32gui.SendMessage(self.E_Csymbol, win32con.WM_SETTEXT, None, symbol)  # 输入撤单
        win32gui.SendMessage(self.B_Csort, win32con.BM_CLICK, None, None)  # 查询代码
        time.sleep(0.1)
        if direction == 0:
            win32gui.SendMessage(self.B_Cbuy, win32con.BM_CLICK, None, None)  # 撤买
        elif direction == 1:
            win32gui.SendMessage(self.B_Csell, win32con.BM_CLICK, None, None)  # 撤卖
        time.sleep(0.3)
        return 0

    @property
    def position(self):
        win32gui.SendMessage(self.B_refresh, win32con.BM_CLICK, None, None)  # 刷新持仓
        #time.sleep(0.05)
        win32gui.SetForegroundWindow(self.G_position)
        #time.sleep(0.05)
        data = self.get_clipboard()
        return self.project_copy_str(data)

    @staticmethod
    def project_copy_str(copy_data):
        reader = StringIO(copy_data)
        df = pd.read_csv(reader, delim_whitespace=True)
        return df.to_dict('records')

    @staticmethod
    def get_clipboard():
        win32api.keybd_event(17, 0, 0, 0)
        win32api.keybd_event(67, 0, 0, 0)
        win32api.keybd_event(67, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        cp.OpenClipboard()
        raw_text = cp.GetClipboardData(win32con.CF_UNICODETEXT)
        cp.CloseClipboard()
        return raw_text
    def project_position_str(self, raw):
        reader = StringIO(raw)
        df = pd.read_csv(reader, delim_whitespace=True)
        return df

    @property
    def entrust(self):
        win32gui.SendMessage(self.B_refresh, win32con.BM_CLICK, None, None)  # 刷新持仓
        time.sleep(0.5)
        win32gui.SetForegroundWindow(self.G_entrust)
        time.sleep(0.5)
        data = get_clipboard()
        print(data)
        return self.project_copy_str(data)


# ------------------------------Test-------------------------------------------
if __name__ == '__main__':
    trader = YHClientTrader()
    time.sleep(1)
    print(trader.position())
    # trader.buy('000002', '24.76', '100')
    # trader.cancle('000002', 0)
    # df = trader.position()
    # print(trader.entrusts())

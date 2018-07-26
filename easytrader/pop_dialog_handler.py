# coding:utf-8
import re
import time
from . import exceptions

class PopDialogHandler:
    def __init__(self, app, top_window=None):
        self._app = app
        if top_window is None:
            self._top_window = self._app.top_window()
        else:
            self._top_window = top_window

    def handle(self, title):
        if any(s in title for s in {"提示信息", "委托确认", "网上交易用户协议"}):
            self._submit_by_shortcut()

        elif "提示" in title:
            content = self._extract_content()
            self._submit_by_click()
            return {"message": content}

        else:
            content = self._extract_content()
            self._close()
            return {"message": "unknown message: {}".format(content)}

    def _extract_content(self):
        for c in range(20):
            sss = time.time()
            try:
                test = self._top_window.window(control_id=1004, class_name='Static')
                res = test.window_text()
                return res
            except Exception as e:
                print('_extract_content', e)
                self._top_window = self._app.top_window()
            zzz = time.time()
            if (zzz-sss) < 0.1:
                time.sleep(0.1-(zzz-sss))

    def _extract_entrust_id(self, content):
        return re.search(r"\d+", content).group()

    def _submit_by_click(self):
        """用快捷键ENTER"""
        for c in range(10):
            sss = time.time()
            try:
                # test = self._top_window.window(title='确定', class_name='Button')
                # test.click()
                self._top_window.TypeKeys("{ENTER}")
                break
            except Exception as e:
                print('PopDialog _submit_by_click', e)
                self._top_window = self._app.top_window()
            zzz = time.time()
            if((zzz-sss)<0.1):
                time.sleep(0.1-(zzz-sss))

    def _submit_by_shortcut(self):
        for c in range(10):
            sss = time.time()
            try:
                self._top_window.type_keys("%Y")
                break
            except Exception as e:
                print('PopDialog _submit_by_shortcut', e)
                self._top_window = self._app.top_window()
            zzz = time.time()
            if((zzz-sss)<0.1):
                time.sleep(0.1-(zzz-sss))

    def _submit_by_shortcut_yes(self):  # 点击 是
        for c in range(10):
            sss = time.time()
            try:
                self._top_window.type_keys("%Y")
                break
            except Exception as e:
                print('PopDialog _submit_by_shortcut_yes', e)
                self._top_window = self._app.top_window()
            zzz = time.time()
            if((zzz-sss)<0.1):
                time.sleep(0.1-(zzz-sss))

    def _submit_by_shortcut_no(self):   # 点击 否
        for c in range(10):
            sss = time.time()
            try:
                self._top_window.type_keys("%N")
                break
            except Exception as e:
                print('PopDialog _submit_by_shortcut_no', e)
                self._top_window = self._app.top_window()
            zzz = time.time()
            if((zzz-sss)<0.1):
                time.sleep(0.1-(zzz-sss))
        
    def _close(self):
        for c in range(10):
            sss = time.time()
            try:
                self._top_window.close()
                break
            except Exception as e:
                print('PopDialog _close', e)
                self._top_window = self._app.top_window()
            zzz = time.time()
            if((zzz-sss)<0.1):
                time.sleep(0.1-(zzz-sss))     


class TradePopDialogHandler(PopDialogHandler):
    def handle(self, title):
        if title == "委托确认":
            self._submit_by_shortcut_yes()

        elif title == "提示信息":
            content = self._extract_content()
            if "超出涨跌停" in content:
                self._submit_by_shortcut_no()
                return {"failure": content}
            elif "委托价格的小数部分应为" in content:
                self._submit_by_shortcut_no()
                return {"failure": content}
            else:
                self._submit_by_shortcut_yes()

        elif title == "提示":
            content = self._extract_content()
            if "成功" in content:
                entrust_no = self._extract_entrust_id(content)
                self._submit_by_click()
                return {"success": entrust_no}
            else:
                self._submit_by_click()
                return {"failure": content}
        else:
            self._close()

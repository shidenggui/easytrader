# coding:utf-8
import re
import time
from typing import Optional

from easytrader import exceptions
from easytrader.log import logger
from easytrader.utils.perf import perf_clock
from easytrader.utils.win_gui import SetForegroundWindow, ShowWindow, win32defines


class PopDialogHandler:
    def __init__(self, app):
        self._app = app

    @staticmethod
    def _set_foreground(window):
        if window.has_style(win32defines.WS_MINIMIZE):  # if minimized
            ShowWindow(window.wrapper_object(), 9)  # restore window state
        else:
            SetForegroundWindow(window.wrapper_object())  # bring to front

    @perf_clock
    def handle(self, title):
        if any(s in title for s in {"提示信息", "委托确认", "网上交易用户协议", "撤单确认"}):
            self._submit_by_shortcut()
            return None

        if "提示" in title:
            content = self._extract_content()
            self._submit_by_click()
            return {"message": content}

        content = self._extract_content()
        self._close()
        return {"message": "unknown message: {}".format(content)}

    def _extract_content(self):
        # self.log_control_identifiers()

        edit_control = self._app.top_window().child_window(class_name="Edit",  found_index=0)
        if edit_control.exists():
            return edit_control.window_text()
        
        static_control = self._app.top_window().child_window(class_name="Static", found_index=0)
        if static_control.exists():
            return static_control.window_text()
    
    def log_control_identifiers(self):
        top_window = self._app.top_window()
        
        # 遍历并记录所有子控件
        children = top_window.children()
        for child in children:
            logger.debug(f"Control: {child.control_type}, Name: {child.window_text()}")

    @staticmethod
    def _extract_entrust_id(content):
        return re.search(r"[\da-zA-Z]+", content).group()

    def _submit_by_click(self):
        try:
            self._app.top_window()["确定"].click()
        except Exception as ex:
            self._app.Window_(best_match="Dialog", top_level_only=True).ChildWindow(
                best_match="确定"
            ).click()

    def _submit_by_shortcut(self):
        self._set_foreground(self._app.top_window())
        self._app.top_window().type_keys("%Y", set_foreground=False)

    def _close(self):
        self._app.top_window().close()


class TradePopDialogHandler(PopDialogHandler):
    @perf_clock
    def handle(self, title) -> Optional[dict]:
        if title == "委托确认":
            self._submit_by_shortcut()
            return None

        if title == "提示信息":
            content = self._extract_content()
            if "超出涨跌停" in content:
                self._submit_by_shortcut()
                return None

            if "委托价格的小数价格应为" in content:
                self._submit_by_shortcut()
                return None

            if "逆回购" in content:
                self._submit_by_shortcut()
                return None

            if "正回购" in content:
                self._submit_by_shortcut()
                return None

            return None

        if title == "提示":
            content = self._extract_content()
            if "成功" in content:
                entrust_no = self._extract_entrust_id(content)
                self._submit_by_click()
                return {"entrust_no": entrust_no}

            self._submit_by_click()
            time.sleep(0.05)
            raise exceptions.TradeError(content)
        self._close()
        return None

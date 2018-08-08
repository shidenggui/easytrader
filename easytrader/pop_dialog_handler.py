# coding:utf-8
import re
import time
from typing import Optional

from . import exceptions


class PopDialogHandler:
    def __init__(self, app):
        self._app = app

    def handle(self, title):
        if any(s in title for s in {"提示信息", "委托确认", "网上交易用户协议"}):
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
        return self._app.top_window().Static.window_text()

    def _extract_entrust_id(self, content):
        return re.search(r"\d+", content).group()

    def _submit_by_click(self):
        self._app.top_window()["确定"].click()

    def _submit_by_shortcut(self):
        self._app.top_window().type_keys("%Y")

    def _close(self):
        self._app.top_window().close()


class TradePopDialogHandler(PopDialogHandler):
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

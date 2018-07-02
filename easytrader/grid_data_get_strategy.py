# -*- coding: utf-8 -*-
import abc
import io
import tempfile

import pandas as pd
import pywinauto.clipboard

from .log import log


class IGridDataGetStrategy(abc.ABC):
    @abc.abstractmethod
    def get(self, control_id: int):
        """
        :param control_id: grid 的 control id
        :return: grid 数据
        :rtype: List[Dict]
        """
        pass


class BaseStrategy(IGridDataGetStrategy):
    def __init__(self, trader):
        self._trader = trader

    @abc.abstractmethod
    def get(self, control_id: int):
        """
        :param control_id: grid 的 control id
        :return: grid 数据
        :rtype: list[dict]
        """
        pass

    def _get_grid(self, control_id):
        grid = self._trader.main.window(
            control_id=control_id, class_name="CVirtualGridCtrl"
        )
        return grid


class CopyStrategy(BaseStrategy):
    """
    通过复制 grid 内容到剪切板z再读取来获取 grid 内容
    """

    def get(self, control_id: int):
        grid = self._get_grid(control_id)
        grid.type_keys("^A^C")
        content = self._get_clipboard_data()
        return self._format_grid_data(content)

    def _format_grid_data(self, data):
        df = pd.read_csv(
            io.StringIO(data),
            delimiter="\t",
            dtype=self._trader.config.GRID_DTYPE,
            na_filter=False,
        )
        return df.to_dict("records")

    def _get_clipboard_data(self):
        while True:
            try:
                return pywinauto.clipboard.GetData()
            except Exception as e:
                log.warning("{}, retry ......".format(e))


class XlsStrategy(BaseStrategy):
    """
    通过将 Grid 另存为 xls 文件再读取的方式获取 grid 内容，
    用于绕过一些客户端不允许复制的限制
    """

    def get(self, control_id: int):
        grid = self._get_grid(control_id)

        # ctrl+s 保存 grid 内容为 xls 文件
        grid.type_keys("^s")
        self._trader.wait(1)

        temp_path = tempfile.mktemp(suffix=".csv")
        self._trader.app.top_window().type_keys(temp_path)

        # alt+s保存，alt+y替换已存在的文件
        self._trader.app.top_window().type_keys("%{s}%{y}")
        return self._format_grid_data(temp_path)

    def _format_grid_data(self, data):
        df = pd.read_csv(
            data,
            encoding="gbk",
            delimiter="\t",
            dtype=self._trader.config.GRID_DTYPE,
            na_filter=False,
        )
        return df.to_dict("records")

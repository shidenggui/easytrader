# coding:utf-8
import unittest
from unittest import mock

from easytrader import XueQiuFollower


class TestXueQiuTrader(unittest.TestCase):
    def test_adjust_sell_amount_without_enable(self):
        follower = XueQiuFollower()

        mock_user = mock.MagicMock()
        follower._users = [mock_user]

        follower._adjust_sell = False
        amount = follower._adjust_sell_amount('169101', 1000)
        self.assertEqual(amount, amount)

    def test_adjust_sell_amount(self):
        follower = XueQiuFollower()

        mock_user = mock.MagicMock()
        follower._users = [mock_user]
        mock_user.position = TEST_POSITION

        follower._adjust_sell = True
        test_cases = [
            ('169101', 600, 600),
            ('169101', 700, 600),
            ('000000', 100, 100),
            ('sh169101', 700, 600),
        ]
        for stock_code, sell_amount, excepted_amount in test_cases:
            amount = follower._adjust_sell_amount(stock_code, sell_amount)
            self.assertEqual(amount, excepted_amount)


TEST_POSITION = [{
    'Unnamed: 14': '',
    '买入冻结': 0,
    '交易市场': '深Ａ',
    '卖出冻结': 0,
    '参考市价': 1.464,
    '参考市值': 919.39,
    '参考成本价': 1.534,
    '参考盈亏': -43.77,
    '可用余额': 628,
    '当前持仓': 628,
    '盈亏比例(%)': -4.544,
    '股东代码': '0000000000',
    '股份余额': 628,
    '证券代码': '169101'
}]

# coding: utf-8

import os
import sys
import time
import unittest

sys.path.append('.')

import easytrader


class TestYhClientTrader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # input your test account and password
        cls._ACCOUNT = os.environ.get('EZ_TEST_YH_ACCOUNT') or 'your account'
        cls._PASSWORD = os.environ.get('EZ_TEST_YH_password') or 'your password'

        cls._user = easytrader.use('yh_client')
        cls._user.prepare(user=cls._ACCOUNT, password=cls._PASSWORD)

    def test_balance(self):
        time.sleep(3)
        result = self._user.balance

    def test_today_entrusts(self):
        result = self._user.today_entrusts

    def test_today_trades(self):
        result = self._user.today_trades

    def test_cancel_entrusts(self):
        result = self._user.cancel_entrusts

    def test_cancel_entrust(self):
        result = self._user.cancel_entrust('123456789')

    def test_invalid_buy(self):
        with self.assertRaises(easytrader.exceptions.TradeError):
            result = self._user.buy('511990', 1, 1e10)

    def test_invalid_sell(self):
        with self.assertRaises(easytrader.exceptions.TradeError):
            result = self._user.buy('162411', 200, 1e10)

    def test_auto_ipo(self):
        self._user.auto_ipo()

if __name__ == '__main__':
    unittest.main()

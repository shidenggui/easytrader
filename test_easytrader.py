# coding: utf-8

import os
import sys
import time
import unittest
from unittest import mock

sys.path.append('.')

TEST_CLIENTS = os.environ.get('EZ_TEST_CLIENTS', 'yh')


@unittest.skipUnless('yh' in TEST_CLIENTS, 'skip yh test')
class TestYhClientTrader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import easytrader
        if 'yh' not in TEST_CLIENTS:
            return

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
        import easytrader
        with self.assertRaises(easytrader.exceptions.TradeError):
            result = self._user.buy('511990', 1, 1e10)

    def test_invalid_sell(self):
        import easytrader
        with self.assertRaises(easytrader.exceptions.TradeError):
            result = self._user.sell('162411', 200, 1e10)

    def test_auto_ipo(self):
        self._user.auto_ipo()


@unittest.skipUnless('ht' in TEST_CLIENTS, 'skip ht test')
class TestHTClientTrader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import easytrader
        if 'ht' not in TEST_CLIENTS:
            return

        # input your test account and password
        cls._ACCOUNT = os.environ.get('EZ_TEST_HT_ACCOUNT') or 'your account'
        cls._PASSWORD = os.environ.get('EZ_TEST_HT_password') or 'your password'
        cls._COMM_PASSWORD = os.environ.get('EZ_TEST_HT_comm_password') or 'your comm password'

        cls._user = easytrader.use('ht_client')
        cls._user.prepare(user=cls._ACCOUNT, password=cls._PASSWORD, comm_password=cls._COMM_PASSWORD)

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
        import easytrader
        with self.assertRaises(easytrader.exceptions.TradeError):
            result = self._user.buy('511990', 1, 1e10)

    def test_invalid_sell(self):
        import easytrader
        with self.assertRaises(easytrader.exceptions.TradeError):
            result = self._user.sell('162411', 200, 1e10)

    def test_auto_ipo(self):
        self._user.auto_ipo()


class TestClientTrader(unittest.TestCase):
    def test_connect(self):
        from easytrader.clienttrader import ClientTrader
        c = ClientTrader()

        with self.assertRaises(ValueError):
            c.connect()

    def test_auto_ipo_with_failed_situation(self):
        from easytrader.clienttrader import ClientTrader
        c = ClientTrader()
        with mock.patch.object(c, '_switch_left_menus'):
            for case, res in [
                ([], {'message': '今日无新股'}),
                ([{'申购数量': 0}], {'message': '没有发现可以申购的新股'})
            ]:
                with mock.patch.object(c, '_get_grid_data') as ipo_list_mock:
                    ipo_list_mock.return_value = case
                    self.assertDictEqual(c.auto_ipo(), res)


if __name__ == '__main__':
    unittest.main()

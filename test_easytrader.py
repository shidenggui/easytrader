# coding: utf-8

import unittest
from unittest import mock
from datetime import datetime
import time

import easytrader
from easytrader import JoinQuantFollower, RiceQuantFollower
from easytrader import helpers
from easytrader.follower import BaseFollower


class TestEasytrader(unittest.TestCase):

    def test_helpers(self):
        result = helpers.get_stock_type('162411')
        self.assertEqual(result, 'sz')

        result = helpers.get_stock_type('691777')
        self.assertEqual(result, 'sh')

        result = helpers.get_stock_type('sz162411')
        self.assertEqual(result, 'sz')

    def test_format_response_data_type(self):
        user = easytrader.use('ht')

        test_data = [{
            'current_amount': '187.00',
            'current_balance': '200.03',
            'stock_code': '000001'
        }]
        result = user.format_response_data_type(test_data)

        self.assertIs(type(result[0]['current_amount']), int)
        self.assertIs(type(result[0]['current_balance']), float)
        self.assertIs(type(result[0]['stock_code']), str)

        test_data = [{'position_str': '',
                      'date': '',
                      'fund_account': '',
                      'stock_account': '',
                      'stock_code': '',
                      'entrust_bs': '',
                      'business_price': '',
                      'business_amount': '',
                      'business_time': '',
                      'stock_name': '',
                      'business_status': '',
                      'business_type': ''}]
        result = user.format_response_data_type(test_data)

    def test_ht_fix_error_data(self):
        user = easytrader.use('ht')
        test_data = {
            'cssweb_code': 'error',
            'cssweb_type': 'GET_STOCK_POSITON'
        }

        return_data = user.fix_error_data(test_data)
        self.assertEqual(test_data, return_data)

        test_data = [{
            'stock_code': '162411',
            'entrust_bs': '2'},
            {'no_use_index': 'hello'}]

        normal_return_data = [{
            'stock_code': '162411',
            'entrust_bs': '2'}]

        return_data = user.fix_error_data(test_data)
        self.assertEqual(return_data, normal_return_data)

    def test_helpers_grep_comma(self):
        test_data = '123'
        normal_data = '123'
        result = helpers.grep_comma(test_data)
        self.assertEqual(result, normal_data)

        test_data = '4,000'
        normal_data = '4000'
        result = helpers.grep_comma(test_data)
        self.assertEqual(result, normal_data)

    def test_helpers_str2num(self):
        test_data = '123'
        normal_data = 123
        result = helpers.str2num(test_data, 'int')
        self.assertEqual(result, normal_data)

        test_data = '1,000'
        normal_data = 1000
        result = helpers.str2num(test_data, 'int')
        self.assertEqual(result, normal_data)

        test_data = '123.05'
        normal_data = 123.05
        result = helpers.str2num(test_data, 'float')
        self.assertAlmostEqual(result, normal_data)

        test_data = '1,023.05'
        normal_data = 1023.05
        result = helpers.str2num(test_data, 'float')
        self.assertAlmostEqual(result, normal_data)

    def test_gf_check_account_live(self):
        user = easytrader.use('gf')

        test_data = None
        with self.assertRaises(easytrader.webtrader.NotLoginError):
            user.check_account_live(test_data)
        self.assertFalse(user.heart_active)

        test_data = {'success': False, 'data': [{}], 'total': 1}
        with self.assertRaises(easytrader.webtrader.NotLoginError):
            user.check_account_live(test_data)
        self.assertFalse(user.heart_active)


class TestXueQiuTrader(unittest.TestCase):

    def test_set_initial_assets(self):
        # default set to 1e6
        xq_user = easytrader.use('xq')
        self.assertEqual(xq_user.multiple, 1e6)

        xq_user = easytrader.use('xq', initial_assets=1000)
        self.assertEqual(xq_user.multiple, 1000)

        # cant low than 1000
        with self.assertRaises(ValueError):
            xq_user = easytrader.use('xq', initial_assets=999)

        # initial_assets must be number
        cases = [None, '', b'', bool]
        for v in cases:
            with self.assertRaises(TypeError):
                xq_user = easytrader.use('xq', initial_assets=v)


class TestJoinQuantFollower(unittest.TestCase):

    def test_extract_strategy_id(self):
        cases = [('https://www.joinquant.com/algorithm/live/index?backtestId=aaaabbbbcccc',
                  'aaaabbbbcccc')]
        for test, result in cases:
            extracted_id = JoinQuantFollower.extract_strategy_id(test)
            self.assertEqual(extracted_id, result)

    def test_stock_shuffle_to_prefix(self):
        cases = [('123456.XSHG', 'sh123456'),
                 ('000001.XSHE', 'sz000001')]
        for test, result in cases:
            self.assertEqual(
                JoinQuantFollower.stock_shuffle_to_prefix(test),
                result
            )

        with self.assertRaises(AssertionError):
            JoinQuantFollower.stock_shuffle_to_prefix('1234')

    def test_project_transactions(self):
        cases = [([{'type': '市价单', 'price': 8.11, 'commission': 9.98, 'gains': 0, 'time': '14:50', 'date': '2016-11-18',
                    'security': '股票', 'stock': '华纺股份(600448.XSHG)', 'transaction': '买', 'total': 33251,
                    'status': '全部成交',
                    'amount': "<span class='buy'>4100股</span>"}],
                  [{'type': '市价单', 'price': 8.11, 'commission': 9.98, 'gains': 0, 'time': '14:50', 'date': '2016-11-18',
                    'security': '股票', 'stock': '华纺股份(600448.XSHG)', 'transaction': '买', 'total': 33251,
                    'status': '全部成交',
                    'amount': 4100,
                    'action': 'buy',
                    'stock_code': 'sh600448',
                    'datetime':
                        datetime.strptime('2016-11-18 14:50', '%Y-%m-%d %H:%M')
                    }])]
        for test, result in cases:
            JoinQuantFollower().project_transactions(test),
            self.assertListEqual(
                test,
                result
            )


class TestFollower(unittest.TestCase):

    def test_is_number(self):
        cases = [('1', True),
                 ('--', False)]
        for string, result in cases:
            test = BaseFollower._is_number(string)
            self.assertEqual(test, result)

    @mock.patch.object(BaseFollower, 'trade_worker', autospec=True)
    def test_send_interval(self, mock_trade_worker):
        cases = [(1, 1), (2, 2)]
        for follower_cls in [JoinQuantFollower, RiceQuantFollower]:
            for test_data, truth in cases:
                follower = follower_cls()
                try:
                    follower.follow(None, None, send_interval=test_data)
                except:
                    pass
                print(test_data, truth)
                self.assertEqual(mock_trade_worker.call_args[1]['send_interval'], truth)


if __name__ == '__main__':
    unittest.main()

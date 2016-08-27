import unittest

import easytrader
from easytrader import helpers


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

    def test_ht_format_exchagnebill_request_data(self):
        user = easytrader.use('ht')
        import datetime
        # print(datetime.datetime.now().strftime("%Y%m%d"))
        # user.exchangebill

if __name__ == '__main__':
    unittest.main()

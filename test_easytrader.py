import unittest
import easytrader
from easytrader import helpers

class TestEasytrader(unittest.TestCase):
    def test_helpers(self):
        result = helpers.get_stock_type('162411')
        self.assertEqual(result, 'sz')

        result = helpers.get_stock_type('691777')
        self.assertEqual(result, 'sh')

        result = helpers.get_stock_type(162411)
        self.assertEqual(result, 'sz')

    def test_format_response_data_type(self):
        user = easytrader.use('ht')

        test_data = [{
            'current_amount': '187.00',
            'current_balance': '200.03',
            'stock_code' : '000001'
        }]
        result = user.format_response_data_type(test_data)

        self.assertIs(type(result[0]['current_amount']), int)
        self.assertIs(type(result[0]['current_balance']), float)
        self.assertIs(type(result[0]['stock_code']), str)

        test_data = [{'position_str': '',
                      'date':'',
                      'fund_account': '',
                      'stock_account': '',
                      'stock_code': '',
                      'entrust_bs': '',
                      'business_price':'',
                      'business_amount':'',
                      'business_time':'',
                      'stock_name': '',
                      'business_status': '',
                      'business_type':''}]
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
            {'nouse_index': 'hello'}]

        normal_return_data = [{
        'stock_code': '162411',
        'entrust_bs': '2'}]

        return_data = user.fix_error_data(test_data)
        self.assertEqual(return_data, normal_return_data)


if __name__ == '__main__':
    unittest.main()

# -*- coding: utf-8 -*-
#
# Author: heheqiao(614400597@qq.com)
#
'''Test for ``trader.FixedTrader``
'''
import mock
from nose.tools import assert_equal
from easytrader import gftrader


@mock.patch.object(gftrader.GFTrader, 'get_value')
def test_get_entrust(mock_get_value):
    '''UnitTest of ``gftrader.GFTrader.get_entrust``
    '''
    mock_get_value.return_value = (
        [u'test', u'test'], 100
    )

    assert_equal(
        gftrader.GFTrader().get_entrust(0),
        {u'data': [u'test', u'test'], u'total': 100, u'success': True}
    )


@mock.patch.object(gftrader.GFTrader, 'do')
def test_get_entrust_with_pos(mock_do):
    '''UnitTest of ``gftrader.GFTrader.get_entrust_with_pos``
    '''
    gftrader.GFTrader().get_entrust_with_pos(u'test')

    mock_do.assert_called_with({
        u'classname': u'com.gf.etrade.control.StockUF2Control',
        u'query_mode': 0, u'query_direction': 0,
        u'postion_str': u'test',
        u'request_num': 100,
        u'method': u'queryDRWT'
    })


@mock.patch.object(gftrader.GFTrader, 'get_entrust_without_pos')
@mock.patch.object(gftrader.GFTrader, 'get_entrust_with_pos')
def test_get_value(mock_get_pos, mock_get):
    '''UnitTest of ``gftrader.GFTrader.get_value``
    '''
    # Case1:result[u'total'] < 100
    mock_get.return_value = {
        u'data': [u'test'], u'total': 1
    }

    assert_equal(
        gftrader.GFTrader().get_value(0),
        ([u'test'], 1)
    )
    mock_get_pos.assert_not_called()

    # Case2:result[u'total'] >= 100
    mock_get.return_value = {
        u'data': [{u'position_str': u'test'}], u'total': 100
    }
    mock_get_pos.return_value = {
        u'data': [u'test'], u'total': 50
    }

    assert_equal(
        gftrader.GFTrader().get_value(0),
        ([{u'position_str': u'test'}, u'test'], 150)
    )
    mock_get_pos.assert_called_with(0, u'test')

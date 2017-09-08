# coding:utf8

def create(broker):
    if broker == 'yh':
        return YH
    raise NotImplemented


class YH:
    TITLE = '网上股票交易系统5.0'

    TRADE_SECURITY_CONTROL_ID = 1032
    TRADE_PRICE_CONTROL_ID = 1033
    TRADE_AMOUNT_CONTROL_ID = 1034

    TRADE_SUBMIT_CONTROL_ID = 1006

    COMMON_GRID_CONTROL_ID = 1047
    BALANCE_GRID_CONTROL_ID = 1047

    POP_DIALOD_TITLE_CONTROL_ID = 1365

    GRID_DTYPE = {
        '操作日期': str,
        '委托编号': str,
        '申请编号': str,
        '合同编号': str,
        '证券代码': str,
        '股东代码': str,
        '资金帐号': str,
        '资金帐户': str,
        '发生日期': str
    }

    CANCEL_ENTRUST_ENTRUST_FIELD = '合同编号'
    CANCEL_ENTRUST_GRID_LEFT_MARGIN = 50
    CANCEL_ENTRUST_GRID_FIRST_ROW_HEIGHT = 30
    CANCEL_ENTRUST_GRID_ROW_HEIGHT = 16

    AUTO_IPO_SELECT_ALL_BUTTON_CONTROL_ID = 1098
    AUTO_IPO_BUTTON_CONTROL_ID = 1006

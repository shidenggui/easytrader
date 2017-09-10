# coding:utf8

def create(broker):
    if broker == 'yh':
        return YH
    elif broker == 'ht':
        return HT
    elif broker == 'gj':
        return GJ    
    raise NotImplemented


class YH:
    DEFAULT_EXE_PATH = r'C:\中国银河证券双子星3.2\Binarystar.exe'
    TITLE = '网上股票交易系统5.0'

    TRADE_SECURITY_CONTROL_ID = 1032
    TRADE_PRICE_CONTROL_ID = 1033
    TRADE_AMOUNT_CONTROL_ID = 1034

    TRADE_SUBMIT_CONTROL_ID = 1006

    COMMON_GRID_CONTROL_ID = 1047
    BALANCE_GRID_CONTROL_ID = 1308

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


class HT:
    DEFAULT_EXE_PATH = r'C:\htzqzyb2\xiadan.exe'
    TITLE = '网上股票交易系统5.0'

    TRADE_SECURITY_CONTROL_ID = 1032
    TRADE_PRICE_CONTROL_ID = 1033
    TRADE_AMOUNT_CONTROL_ID = 1034

    TRADE_SUBMIT_CONTROL_ID = 1006

    COMMON_GRID_CONTROL_ID = 1047

    BALANCE_CONTROL_ID_GROUP = {
        '资金余额': 1012,
        '冻结资金': 1013,
        '可用金额': 1016,
        '可取金额': 1017,
        '股票市值': 1014,
        '总资产': 1015
    }

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

class GJ:
    DEFAULT_EXE_PATH = 'C:\\全能行证券交易终端\\xiadan.exe'
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

    ENABLE_BALANCE_TEXT_ID = 0x3f8
    TOTAL_BALANCE_TEXT_ID = 0x3f7
    
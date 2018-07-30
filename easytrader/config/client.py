# -*- coding: utf-8 -*-
def create(broker):
    if broker == "yh":
        return YH
    elif broker == "ht":
        return HT
    elif broker == "gj":
        return GJ
    elif broker == "ths":
        return CommonConfig
    raise NotImplemented


class CommonConfig:
    DEFAULT_EXE_PATH = None
    TITLE = "网上股票交易系统5.0"
    
    TOP_TOOLBAR_CONTROL_ID = 59392
    
    TRADE_ACCOUNT_CONTROL_ID = 1004
    TRADE_SECURITY_CONTROL_ID = 1032
    TRADE_PRICE_CONTROL_ID = 1033
    TRADE_AMOUNT_CONTROL_ID = 1034
    TRADE_SECURITY_HIGH_LIMIT = 1028
    TRADE_SECURITY_NAME_ID = 1036

    TRADE_SUBMIT_CONTROL_ID = 1006

    TRADE_MARKET_TYPE_CONTROL_ID = 1541
    
    TISHI_CONTENT_CONTROL_ID = 1004

    COMMON_GRID_CONTROL_ID = 1047

    COMMON_GRID_LEFT_MARGIN = 10
    COMMON_GRID_FIRST_ROW_HEIGHT = 30
    COMMON_GRID_ROW_HEIGHT = 16

    BALANCE_MENU_PATH = ["查询[F4]", "资金股票"]
    POSITION_MENU_PATH = ["查询[F4]", "资金股票"]
    TODAY_ENTRUSTS_MENU_PATH = ["查询[F4]", "当日委托"]
    TODAY_TRADES_MENU_PATH = ["查询[F4]", "当日成交"]

    BALANCE_CONTROL_ID_GROUP = {
        "资金余额": 1012,
        "可用金额": 1016,
        "可取金额": 1017,
        "股票市值": 1014,
        "总资产": 1015,
    }

    POP_DIALOD_TITLE_CONTROL_ID = 1365

    GRID_DTYPE = {
        "操作日期": str,
        "委托编号": str,
        "申请编号": str,
        "合同编号": str,
        "证券代码": str,
        "股东代码": str,
        "资金帐号": str,
        "资金帐户": str,
        "发生日期": str,
    }

    CANCEL_ENTRUST_ENTRUST_FIELD = "合同编号"
    CANCEL_ENTRUST_GRID_LEFT_MARGIN = 50
    CANCEL_ENTRUST_GRID_FIRST_ROW_HEIGHT = 30
    CANCEL_ENTRUST_GRID_ROW_HEIGHT = 16

    AUTO_IPO_SELECT_ALL_BUTTON_CONTROL_ID = 1098
    AUTO_IPO_BUTTON_CONTROL_ID = 1006
    AUTO_IPO_MENU_PATH = ["新股申购", "批量新股申购"]


class YH(CommonConfig):
    DEFAULT_EXE_PATH = r"C:\双子星-中国银河证券\Binarystar.exe"

    BALANCE_GRID_CONTROL_ID = 1308

    GRID_DTYPE = {
        "操作日期": str,
        "委托编号": str,
        "申请编号": str,
        "合同编号": str,
        "证券代码": str,
        "股东代码": str,
        "资金帐号": str,
        "资金帐户": str,
        "发生日期": str,
    }

    AUTO_IPO_MENU_PATH = ["新股申购", "一键打新"]


class HT(CommonConfig):
    DEFAULT_EXE_PATH = r"C:\htzqzyb2\xiadan.exe"

    BALANCE_CONTROL_ID_GROUP = {
        "资金余额": 1012,
        "冻结资金": 1013,
        "可用金额": 1016,
        "可取金额": 1017,
        "股票市值": 1014,
        "总资产": 1015,
    }

    GRID_DTYPE = {
        "操作日期": str,
        "委托编号": str,
        "申请编号": str,
        "合同编号": str,
        "证券代码": str,
        "股东代码": str,
        "资金帐号": str,
        "资金帐户": str,
        "发生日期": str,
    }

    AUTO_IPO_MENU_PATH = ["新股申购", "批量新股申购"]


class GJ(CommonConfig):
    DEFAULT_EXE_PATH = "C:\\全能行证券交易终端\\xiadan.exe"

    GRID_DTYPE = {
        "操作日期": str,
        "委托编号": str,
        "申请编号": str,
        "合同编号": str,
        "证券代码": str,
        "股东代码": str,
        "资金帐号": str,
        "资金帐户": str,
        "发生日期": str,
    }

    AUTO_IPO_MENU_PATH = ["新股申购", "新股批量申购"]

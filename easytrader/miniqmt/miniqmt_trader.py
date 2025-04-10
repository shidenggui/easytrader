from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
from xtquant import xtconstant
import random
from easytrader.log import logger
from easytrader.utils.perf import perf_clock
from easytrader.utils.stock import get_stock_type

# 市价委托类型映射
MARKET_ORDER_TYPE_NAME_MAP = {
    "sh": {
        "对手方最优价格委托": xtconstant.MARKET_PEER_PRICE_FIRST,
        "本方最优价格委托": xtconstant.MARKET_MINE_PRICE_FIRST,
        "最优五档即时成交剩余撤销": xtconstant.MARKET_SH_CONVERT_5_CANCEL,
        "最优五档即时成交剩转限价": xtconstant.MARKET_SH_CONVERT_5_LIMIT,
    },
    "sz": {
        "对手方最优价格委托": xtconstant.MARKET_PEER_PRICE_FIRST,
        "本方最优价格委托": xtconstant.MARKET_MINE_PRICE_FIRST,
        "即时成交剩余撤销委托": xtconstant.MARKET_SZ_INSTBUSI_RESTCANCEL,
        "最优五档即时成交剩余撤销": xtconstant.MARKET_SZ_CONVERT_5_CANCEL,
        "全额成交或撤销委托": xtconstant.MARKET_SZ_FULL_OR_CANCEL,
    },
}

# 市价委托类型反向映射（不区分交易所）
MARKET_ORDER_TYPE_MAP = {
    xtconstant.STOCK_BUY: "买入",
    xtconstant.STOCK_SELL: "卖出",
    xtconstant.MARKET_PEER_PRICE_FIRST: "对手方最优价格委托",
    xtconstant.MARKET_MINE_PRICE_FIRST: "本方最优价格委托",
    xtconstant.MARKET_SH_CONVERT_5_CANCEL: "最优五档即时成交剩余撤销",
    xtconstant.MARKET_SH_CONVERT_5_LIMIT: "最优五档即时成交剩转限价",
    xtconstant.MARKET_SZ_INSTBUSI_RESTCANCEL: "即时成交剩余撤销委托",
    xtconstant.MARKET_SZ_CONVERT_5_CANCEL: "最优五档即时成交剩余撤销",
    xtconstant.MARKET_SZ_FULL_OR_CANCEL: "全额成交或撤销委托",
}

# 交易操作(offset_flag)映射
OFFSET_FLAG_MAP = {
    xtconstant.OFFSET_FLAG_OPEN: "买入",
    xtconstant.OFFSET_FLAG_CLOSE: "卖出",
    xtconstant.OFFSET_FLAG_FORCECLOSE: "强平",
    xtconstant.OFFSET_FLAG_CLOSETODAY: "平今",
    xtconstant.OFFSET_FLAG_ClOSEYESTERDAY: "平昨",
    xtconstant.OFFSET_FLAG_FORCEOFF: "强减",
    xtconstant.OFFSET_FLAG_LOCALFORCECLOSE: "本地强平",
}
# 委托状态(order_status)映射
ORDER_STATUS_MAP = {
    xtconstant.ORDER_UNREPORTED: "未报",
    xtconstant.ORDER_WAIT_REPORTING: "待报",
    xtconstant.ORDER_REPORTED: "已报",
    xtconstant.ORDER_REPORTED_CANCEL: "已报待撤",
    xtconstant.ORDER_PARTSUCC_CANCEL: "部成待撤",
    xtconstant.ORDER_PART_CANCEL: "部撤",
    xtconstant.ORDER_CANCELED: "已撤",
    xtconstant.ORDER_PART_SUCC: "部成",
    xtconstant.ORDER_SUCCEEDED: "已成",
    xtconstant.ORDER_JUNK: "废单",
    xtconstant.ORDER_UNKNOWN: "未知"
}

# 多空方向(direction)映射
DIRECTION_MAP = {
    xtconstant.DIRECTION_FLAG_LONG: "多",
    xtconstant.DIRECTION_FLAG_SHORT: "空",
}

# 券商价格类型(price_type)映射
# 官网文档见 https://dict.thinktrader.net/innerApi/enum_constants.html?id=7zqjlm#enum-ebrokerpricetype-%E4%BB%B7%E6%A0%BC%E7%B1%BB%E5%9E%8B
BROKER_PRICE_TYPE_MAP = {
    49: "市价",  # enum_EBrokerPriceType.BROKER_PRICE_ANY
    50: "限价",  # enum_EBrokerPriceType.BROKER_PRICE_LIMIT
    51: "最优价",  # enum_EBrokerPriceType.BROKER_PRICE_BEST
    52: "配股",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_ALLOTMENT
    53: "转托",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_REFER
    54: "申购",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_SUBSCRIBE
    55: "回购",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_BUYBACK
    56: "配售",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_PLACING
    57: "指定",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_DECIDE
    58: "转股",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_EQUITY
    59: "回售",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_SELLBACK
    60: "股息",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_DIVIDEND
    68: "深圳配售确认",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_SHENZHEN_PLACING
    69: "配售放弃",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_CANCEL_PLACING
    70: "无冻质押",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_WDZY
    71: "冻结质押",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_DJZY
    72: "无冻解押",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_WDJY
    73: "解冻解押",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_JDJY
    75: "投票",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_VOTE
    77: "预售要约解除",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_YSYYJC
    78: "基金设红",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_FUND_DEVIDEND
    79: "基金申赎",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_FUND_ENTRUST
    80: "跨市转托",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_CROSS_MARKET
    81: "ETF申购",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_ETF
    83: "权证行权",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_EXERCIS
    84: "对手方最优价格",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_PEER_PRICE_FIRST
    85: "最优五档即时成交剩余转限价",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_L5_FIRST_LIMITPX
    86: "本方最优价格",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_MIME_PRICE_FIRST
    87: "即时成交剩余撤销",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_INSTBUSI_RESTCANCEL
    88: "最优五档即时成交剩余撤销",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_L5_FIRST_CANCEL
    89: "全额成交并撤单",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_FULL_REAL_CANCEL
    90: "基金拆合",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_FUND_CHAIHE
    91: "债转股",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_DEBT_CONVERSION
    92: "港股通竞价限价",  # BROKER_PRICE_BID_LIMIT
    93: "港股通增强限价",  # enum_EBrokerPriceType.BROKER_PRICE_ENHANCED_LIMIT
    94: "港股通零股限价",  # enum_EBrokerPriceType.BROKER_PRICE_RETAIL_LIMIT
    101: "直接还券",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_DIRECT_SECU_REPAY
    107: "担保品划转",  # enum_EBrokerPriceType.BROKER_PRICE_PROP_COLLATERAL_TRANSFER
    'j': "增发",
    'w': "定价",  # 全国股转 - 挂牌公司交易 - 协议转让
    'x': "成交确认",  # 全国股转 - 挂牌公司交易 - 协议转让
    'y': "互报成交确认",  # 全国股转 - 挂牌公司交易 - 协议转让
    'z': "限价",  # 用于挂牌公司交易 - 做市转让 - 限价买卖和两网及退市交易-限价买卖
}


class DefaultXtQuantTraderCallback(XtQuantTraderCallback):
    """
    XtQuantTrader回调类的默认实现
    """

    def on_disconnected(self):
        """
        连接状态回调
        :return:
        """
        logger.info("连接断开")

    def on_account_status(self, status):
        """
        账号状态信息推送
        :param response: XtAccountStatus 对象
        :return:
        """
        logger.info(
            f"账户状态信息: account_id={status.account_id}, account_type={status.account_type}, status={status.status}"
        )

    def on_stock_order(self, order):
        """
        委托信息推送
        :param order: XtOrder对象
        :return:
        """
        logger.info(
            f"委托回调: stock_code={order.stock_code}, order_status={order.order_status}, order_sysid={order.order_sysid}"
        )

    def on_stock_trade(self, trade):
        """
        成交信息推送
        :param trade: XtTrade对象
        :return:
        """
        logger.info(
            f"成交回调: account_id={trade.account_id}, stock_code={trade.stock_code}, order_id={trade.order_id}"
        )

    def on_order_error(self, order_error):
        """
        下单失败信息推送
        :param order_error:XtOrderError 对象
        :return:
        """
        logger.info(
            f"下单失败回调: order_id={order_error.order_id}, error_id={order_error.error_id}, error_msg={order_error.error_msg}"
        )

    def on_cancel_error(self, cancel_error):
        """
        撤单失败信息推送
        :param cancel_error: XtCancelError 对象
        :return:
        """
        logger.info(
            f"撤单失败回调: order_id={cancel_error.order_id}, error_id={cancel_error.error_id}, error_msg={cancel_error.error_msg}"
        )

    def on_order_stock_async_response(self, response):
        """
        异步下单回报推送
        :param response: XtOrderResponse 对象
        :return:
        """
        logger.info(f"异步下单回报: account_id={response.account_id}, order_id={response.order_id}, seq={response.seq}")

    def on_smt_appointment_async_response(self, response):
        """
        :param response: XtAppointmentResponse 对象
        :return:
        """
        logger.info(
            f"预约委托异步回报: account_id={response.account_id}, order_sysid={response.order_sysid}, error_id={response.error_id}, error_msg={response.error_msg}, seq={response.seq}"
        )


class MiniqmtTrader:
    broker_type = "miniqmt"

    def __init__(self):
        self._account: StockAccount = None
        self._trader: XtQuantTrader = None

    def connect(
        self,
        miniqmt_path: str = r"D:\国金证券QMT交易端\userdata_mini",
        stock_account: str = None,
        trader_callback: XtQuantTraderCallback = DefaultXtQuantTraderCallback(),
    ):
        """
        连接到 miniqmt 交易端
        注意：登录qmt客户端时必须勾选极简模式/独立交易模式，否则无法连接
        :param miniqmt_path: miniqmt 安装路径，类似 r"D:\\国金证券QMT交易端\\userdata_mini"
            注意：不建议安装在C盘。安装在C盘的话，每次都需要用管理员权限运行策略，才能正常连接，否则有权限问题
        :param stock_account: 资金账号
        :param trader_callback: 交易回调对象，默认使用 DefaultXtQuantTraderCallback
        :return: None
        """
        session_id = int(random.randint(100000, 999999))
        self._trader = XtQuantTrader(miniqmt_path, session_id, callback=trader_callback)
        self._trader.start()

        if self._trader.connect() == 0:
            logger.info(f'成功连接到 miniqmt, 账号 {stock_account}')
            self._account = StockAccount(stock_account)
            self._trader.subscribe(self._account)
        else:
            logger.error('连接失败，请检查路径或其他情况')

    @property
    def trader(self) -> XtQuantTrader:
        """
        获取交易对象
        :return: XtQuantTrader 对象
        """
        return self._trader

    @property
    def account(self) -> StockAccount:
        """
        获取账户对象
        :return: StockAccount 对象
        """
        return self._account

    @property
    def balance(self):
        """
        获取账户资产信息。
        qmt 官方文档：https://dict.thinktrader.net/nativeApi/xttrader.html?id=7zqjlm#%E8%B5%84%E4%BA%A7%E6%9F%A5%E8%AF%A2

        :return:
            list of dict: 包含账户资产信息的字典，包括:
            - total_asset: 总资产
            - market_value: 持仓市值
            - cash: 可用资金
            - frozen_cash: 冻结资金
            - account_type: 账户类型
            - account_id: 账户ID
        """
        asset = self._trader.query_stock_asset(self._account)
        return [
            {
                'total_asset': asset.total_asset,
                'market_value': asset.market_value,
                'cash': asset.cash,
                'frozen_cash': asset.frozen_cash,
                'account_type': asset.account_type,
                'account_id': asset.account_id,
            }
        ]

    @property
    def position(self):
        """
        获取账户持仓信息。
        qmt 官方文档： https://dict.thinktrader.net/nativeApi/xttrader.html?id=7zqjlm#%E6%8C%81%E4%BB%93%E6%9F%A5%E8%AF%A2

        :return:
            list of dict: 包含账户持仓信息的字典列表，每个字典包括:
            - stock_code: 证券代码
            - security: 六位证券代码
            - volume: 持仓数量
            - can_use_volume: 可用数量
            - open_price: 开仓价
            - market_value: 市值
            - frozen_volume: 冻结数量
            - on_road_volume: 在途股份
            - yesterday_volume: 昨夜拥股
            - avg_price: 成本价
            - direction: 多空方向
            - account_type: 账号类型
            - account_id: 资金账号
        """
        xt_positions = self._trader.query_stock_positions(self._account)
        positions = []
        for pos in xt_positions:
            positions.append(
                {
                    'stock_code': pos.stock_code,
                    'security': pos.stock_code[:6],
                    'volume': pos.volume,
                    'can_use_volume': pos.can_use_volume,
                    'open_price': pos.open_price,
                    'market_value': pos.market_value,
                    'frozen_volume': pos.frozen_volume,
                    'on_road_volume': pos.on_road_volume,
                    'yesterday_volume': pos.yesterday_volume,
                    'avg_price': pos.avg_price,
                    'direction': pos.direction,
                    'account_type': pos.account_type,
                    'account_id': pos.account_id,
                }
            )
        return positions

    @property
    def today_entrusts(self):
        """
        获取今日委托列表。
        qmt 官方文档： https://dict.thinktrader.net/nativeApi/xttrader.html?id=7zqjlm#%E5%A7%94%E6%89%98%E6%9F%A5%E8%AF%A2

        :return:
            list of dict: 包含委托信息的字典列表，每个字典包括:
            - stock_code: 证券代码
            - security: 六位证券代码
            - order_id: 订单编号
            - order_sysid: 柜台合同编号
            - order_time: 报单时间
            - order_type: 委托类型
            - order_type_name: 委托类型名称
            - order_volume: 委托数量
            - price_type: 报价类型
            - price_type_name: 报价类型名称
            - price: 委托价格
            - traded_volume: 成交数量
            - traded_price: 成交均价
            - order_status: 委托状态
            - order_status_name: 委托状态名称
            - status_msg: 委托状态描述
            - offset_flag: 交易操作
            - offset_flag_name: 交易操作名称
            - strategy_name: 策略名称
            - order_remark: 委托备注
            - direction: 多空方向
            - direction_name: 多空方向名称
            - account_type: 账号类型
            - account_id: 资金账号
        """
        xt_orders = self._trader.query_stock_orders(self._account, False)
        if xt_orders is None:
            return []

        orders = []
        for order in xt_orders:
            orders.append(
                {
                    'security': order.stock_code[:6],
                    'stock_code': order.stock_code,
                    'order_id': order.order_id,
                    'order_sysid': order.order_sysid,
                    'order_time': order.order_time,
                    'order_type': order.order_type,
                    'order_type_name': MARKET_ORDER_TYPE_MAP.get(order.order_type, order.order_type),
                    'order_volume': order.order_volume,
                    'price_type': order.price_type,
                    'price_type_name': BROKER_PRICE_TYPE_MAP.get(order.price_type, order.price_type),
                    'price': order.price,
                    'traded_volume': order.traded_volume,
                    'traded_price': order.traded_price,
                    'order_status': order.order_status,
                    'order_status_name': ORDER_STATUS_MAP.get(order.order_status, order.order_status),
                    'status_msg': order.status_msg,
                    'offset_flag': order.offset_flag,
                    'offset_flag_name': OFFSET_FLAG_MAP.get(order.offset_flag, order.offset_flag),
                    'strategy_name': order.strategy_name,
                    'order_remark': order.order_remark,
                    'direction': order.direction,
                    'direction_name': DIRECTION_MAP.get(order.direction, order.direction),
                    'account_type': order.account_type,
                    'account_id': order.account_id,
                }
            )
        return orders

    @property
    def today_trades(self):
        """
        获取今日成交列表。
        qmt 官方文档： https://dict.thinktrader.net/nativeApi/xttrader.html?id=7zqjlm#%E6%88%90%E4%BA%A4%E6%9F%A5%E8%AF%A2

        :return:
            list of dict: 包含成交信息的字典列表，每个字典包括:
            - stock_code: 证券代码
            - security: 六位证券代码
            - traded_id: 成交编号
            - traded_time: 成交时间
            - traded_price: 成交均价
            - traded_volume: 成交数量
            - traded_amount: 成交金额
            - order_id: 订单编号
            - order_type: 委托类型
            - order_type_name: 委托类型名称
            - offset_flag: 交易操作（买入/卖出）
            - offset_flag_name: 交易操作名称
            - account_id: 资金账号
            - account_type: 账号类型
            - order_sysid: 柜台合同编号
            - strategy_name: 策略名称
            - order_remark: 委托备注
        """
        xt_trades = self._trader.query_stock_trades(self._account)
        if xt_trades is None:
            return []

        trades = []
        for trade in xt_trades:
            trades.append(
                {
                    'security': trade.stock_code[:6],
                    'stock_code': trade.stock_code,
                    'traded_id': trade.traded_id,
                    'traded_time': trade.traded_time,
                    'traded_price': trade.traded_price,
                    'traded_volume': trade.traded_volume,
                    'traded_amount': trade.traded_amount,
                    'order_id': trade.order_id,
                    'order_type': trade.order_type,
                    'order_type_name': MARKET_ORDER_TYPE_MAP.get(trade.order_type, trade.order_type),
                    'offset_flag': trade.offset_flag,
                    'offset_flag_name': OFFSET_FLAG_MAP.get(trade.offset_flag, trade.offset_flag),
                    'account_id': trade.account_id,
                    'account_type': trade.account_type,
                    'order_sysid': trade.order_sysid,
                    'strategy_name': trade.strategy_name,
                    'order_remark': trade.order_remark,
                }
            )
        return trades

    @perf_clock
    def buy(self, security: str, price: float, amount: int):
        """
        限价买入
        qmt 官方文档： https://dict.thinktrader.net/nativeApi/xttrader.html?id=7zqjlm#%E8%82%A1%E7%A5%A8%E5%90%8C%E6%AD%A5%E6%8A%A5%E5%8D%95

        :param security: 六位证券代码
        :param price: 交易价格
        :param amount: 交易数量
        :return: {'entrust_no': '订单编号'}
            系统生成的订单编号，成功发送委托后的订单编号为大于0的正整数，如果为-1表示委托失败
            注：有订单编号不一定表示成功，具体成功与否需要查看下单回调 on_order_error。
            例如非交易时间下单可以拿到订单编号，但 on_order_error 回调会报错：
            下单失败回调: order_id=10231, error_id=-61, error_msg=限价买入 [SZ162411] [COUNTER] [12313][当前时间不允许此类证券交易]
        """
        return self.trade(security, price, amount, is_buy=True)

    @perf_clock
    def sell(self, security, price, amount, **kwargs):
        """
        限价卖出
        qmt 官方文档： https://dict.thinktrader.net/nativeApi/xttrader.html?id=7zqjlm#%E8%82%A1%E7%A5%A8%E5%90%8C%E6%AD%A5%E6%8A%A5%E5%8D%95

        :param security: 六位证券代码
        :param price: 交易价格
        :param amount: 交易数量
        :return: {'entrust_no': '订单编号'}
            系统生成的订单编号，成功发送委托后的订单编号为大于0的正整数，如果为-1表示委托失败
            注：有订单编号不一定表示成功，具体成功与否需要查看下单回调 on_order_error。
            例如非交易时间下单可以拿到订单编号，但 on_order_error 回调会报错：
            下单失败回调: order_id=10231, error_id=-61, error_msg=限价买入 [SZ162411] [COUNTER] [12313][当前时间不允许此类证券交易]
        """

        return self.trade(security, price, amount, is_buy=False)

    def trade(self, security: str, price: float, amount: int, *, is_buy: bool) -> int:
        """
        限价交易
        qmt 官方文档： https://dict.thinktrader.net/nativeApi/xttrader.html?id=7zqjlm#%E8%82%A1%E7%A5%A8%E5%90%8C%E6%AD%A5%E6%8A%A5%E5%8D%95

        :param security: 六位证券代码
        :param price: 交易价格
        :param amount: 交易数量
        :param is_buy: 是否为买入
        :return: {'entrust_no': '订单编号'}
            系统生成的订单编号，成功发送委托后的订单编号为大于0的正整数，如果为-1表示委托失败
            注：有订单编号不一定表示成功，具体成功与否需要查看下单回调 on_order_error。
            例如非交易时间下单可以拿到订单编号，但 on_order_error 回调会报错：
            下单失败回调: order_id=10231, error_id=-61, error_msg=限价买入 [SZ162411] [COUNTER] [12313][当前时间不允许此类证券交易]
        """
        action = "买入" if is_buy else "卖出"
        logger.info(f"限价{action}请求: 股票代码={security}, 价格={price}, 数量={amount}")
        
        order_id = self._trader.order_stock(
            account=self._account,
            stock_code=self._get_stock_code(security),
            order_type=xtconstant.STOCK_BUY if is_buy else xtconstant.STOCK_SELL,
            order_volume=amount,
            price_type=xtconstant.FIX_PRICE,
            price=price,
        )
        
        if order_id > 0:
            logger.info(f"限价{action}委托成功: 股票代码={security}, 委托单号={order_id}")
        else:
            logger.error(f"限价{action}委托失败: 股票代码={security}, 错误码={order_id}")
            
        return {'entrust_no': order_id}

    @perf_clock
    def market_buy(self, security, amount, ttype=None):
        """
        市价买入
        qmt 官方文档： https://dict.thinktrader.net/nativeApi/xttrader.html?id=7zqjlm#%E8%82%A1%E7%A5%A8%E5%90%8C%E6%AD%A5%E6%8A%A5%E5%8D%95

        :param security: 六位证券代码
        :param amount: 交易数量
        :param ttype: 市价委托类型，默认'对手方最优价格委托'
                 深市可选:
                - 对手方最优价格委托
                - 本方最优价格委托
                - 即时成交剩余撤销委托
                - 最优五档即时成交剩余撤销
                - 全额成交或撤销委托
                 沪市可选:
                - 对手方最优价格委托
                - 最优五档即时成交剩余撤销
                - 最优五档即时成交剩转限价
                - 本方最优价格委托
        :return: {'entrust_no': '订单编号'}
            系统生成的订单编号，成功发送委托后的订单编号为大于0的正整数，如果为-1表示委托失败
            注：有订单编号不一定表示成功，具体成功与否需要查看下单回调 on_order_error。
            例如非交易时间下单可以拿到订单编号，但 on_order_error 回调会报错：
            下单失败回调: order_id=10231, error_id=-61, error_msg=限价买入 [SZ162411] [COUNTER] [12313][当前时间不允许此类证券交易]
        """

        return self.market_trade(security, amount, ttype, is_buy=True)

    @perf_clock
    def market_sell(self, security, amount, ttype=None):
        """
        市价卖出
        qmt 官方文档： https://dict.thinktrader.net/nativeApi/xttrader.html?id=7zqjlm#%E8%82%A1%E7%A5%A8%E5%90%8C%E6%AD%A5%E6%8A%A5%E5%8D%95

        :param security: 六位证券代码
        :param amount: 交易数量
        :param ttype: 市价委托类型，默认'对手方最优价格委托'
                 深市可选:
                - 对手方最优价格委托
                - 本方最优价格委托
                - 即时成交剩余撤销委托
                - 最优五档即时成交剩余撤销
                - 全额成交或撤销委托
                 沪市可选:
                - 对手方最优价格委托
                - 最优五档即时成交剩余撤销
                - 最优五档即时成交剩转限价
                - 本方最优价格委托
        :return: {'entrust_no': '订单编号'}
            系统生成的订单编号，成功发送委托后的订单编号为大于0的正整数，如果为-1表示委托失败
            注：有订单编号不一定表示成功，具体成功与否需要查看下单回调 on_order_error。
            例如非交易时间下单可以拿到订单编号，但 on_order_error 回调会报错：
            下单失败回调: order_id=10231, error_id=-61, error_msg=限价买入 [SZ162411] [COUNTER] [12313][当前时间不允许此类证券交易]
        """

        return self.market_trade(security, amount, ttype, is_buy=False)

    def market_trade(self, security: str, amount: int, ttype: str = None, *, is_buy: bool):
        """
        市价交易
        qmt 官方文档： https://dict.thinktrader.net/nativeApi/xttrader.html?id=7zqjlm#%E8%82%A1%E7%A5%A8%E5%90%8C%E6%AD%A5%E6%8A%A5%E5%8D%95

        :param security: 六位证券代码
        :param amount: 交易数量
        :param ttype: 市价委托类型，默认'对手方最优价格委托'
                 深市可选:
                - 对手方最优价格委托
                - 本方最优价格委托
                - 即时成交剩余撤销委托
                - 最优五档即时成交剩余撤销
                - 全额成交或撤销委托
                 沪市可选:
                - 对手方最优价格委托
                - 最优五档即时成交剩余撤销
                - 最优五档即时成交剩转限价
                - 本方最优价格委托
        :return: {'entrust_no': '订单编号'}
            系统生成的订单编号，成功发送委托后的订单编号为大于0的正整数，如果为-1表示委托失败
            注：有订单编号不一定表示成功，具体成功与否需要查看下单回调 on_order_error。
            例如非交易时间下单可以拿到订单编号，但 on_order_error 回调会报错：
            下单失败回调: order_id=10231, error_id=-61, error_msg=限价买入 [SZ162411] [COUNTER] [12313][当前时间不允许此类证券交易]
        """
        if ttype is None:
            ttype = '对手方最优价格委托'

        action = "市价买入" if is_buy else "市价卖出"
        logger.info(f"{action}请求: 股票代码={security}, 委托类型={ttype}, 数量={amount}")

        def _get_price_type(security: str, ttype: str) -> int:
            """报价类型"""
            exchange = get_stock_type(security)
            if ttype not in MARKET_ORDER_TYPE_NAME_MAP[exchange]:
                raise ValueError(f"{exchange}市场不支持的市价委托类型: {ttype}")
            return MARKET_ORDER_TYPE_NAME_MAP[exchange][ttype]

        order_id = self._trader.order_stock(
            account=self._account,
            stock_code=self._get_stock_code(security),
            order_type=xtconstant.STOCK_BUY if is_buy else xtconstant.STOCK_SELL,
            order_volume=amount,
            price_type=_get_price_type(security, ttype),
            price=0,
        )
        
        if order_id > 0:
            logger.info(f"{action}委托成功: 股票代码={security}, 委托单号={order_id}")
        else:
            logger.error(f"{action}委托失败: 股票代码={security}, 错误码={order_id}")
            
        return {'entrust_no': order_id}

    @perf_clock
    def cancel_entrust(self, entrust_no: int):
        """
        撤销委托单
        qmt 官方文档： https://dict.thinktrader.net/nativeApi/xttrader.html?id=7zqjlm#%E8%82%A1%E7%A5%A8%E5%90%8C%E6%AD%A5%E6%92%A4%E5%8D%95

        :param entrust_no: 委托单号，由买入或卖出函数返回
        :return: {'success': True/False, 'message': '撤单结果'}
                 True: 成功发出撤单指令，False: 撤单失败
        """
        result = self._trader.cancel_order_stock(self._account, entrust_no)
        # 根据官方文档，0表示成功，-1表示失败
        if result == 0:
            return {'success': True, 'message': 'success'}
        else:
            return {'success': False, 'message': 'failed'}

    def _get_stock_code(self, security: str) -> str:
        """
        获取股票代码
        :param security: 六位证券代码
        :return: 格式化的股票代码
        """
        return f'{security}.{get_stock_type(security).upper()}'

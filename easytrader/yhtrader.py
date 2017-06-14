# coding: utf-8
from __future__ import division, unicode_literals

import math
import logging
import os
import random
import re
import time

import requests

from . import helpers
from .log import log
from .webtrader import WebTrader, NotLoginError

VERIFY_CODE_POS = 0
TRADE_MARKET = 1
HOLDER_NAME = 0


# 用于将一个list按一定步长切片，返回这个list切分后的list
def slice_list(step=None, num=None, data_list=None):
    if not ((step is None) & (num is None)):
        if num is not None:
            step = math.ceil(len(data_list) / num)
        return [data_list[i: i + step] for i in range(0, len(data_list), step)]
    else:
        print("step和num不能同时为空")
        return False


class YHTrader(WebTrader):
    config_path = os.path.dirname(__file__) + '/config/yh.json'

    def __init__(self, debug=True):
        super(YHTrader, self).__init__(debug=debug)
        self.cookie = None
        self.account_config = None
        self.s = None
        self.exchange_stock_account = dict()

    def login(self, throw=False):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Referer': 'https://www.chinastock.com.cn/trade/webtrade/login.jsp'
        }
        if self.s is not None:
            self.s.get(self.config['logout_api'])
        self.s = requests.Session()
        self.s.headers.update(headers)
        data = self.s.get(self.config['login_page'])

        # 查找验证码
        verify_code = self.handle_recognize_code()

        if not verify_code:
            return False

        login_status, result = self.post_login_data(verify_code)
        if login_status is False and throw:
            raise NotLoginError(result)

        accounts = self.do(self.config['account4stock'])
        if accounts is False:
            return False
        if len(accounts) < 2:
            raise Exception('无法获取沪深 A 股账户: %s' % accounts)
        for account in accounts:
            if account['交易市场'] == '深A' and account['股东代码'].startswith('0'):
                self.exchange_stock_account['0'] = account['股东代码'][0:10]
            elif account['交易市场'] == '沪A' and account['股东代码'].startswith('A'):
                self.exchange_stock_account['1'] = account['股东代码'][0:10]
        return login_status

    def handle_recognize_code(self):
        """获取并识别返回的验证码
        :return:失败返回 False 成功返回 验证码"""
        # 获取验证码
        verify_code_response = self.s.get(self.config['verify_code_api'], params=dict(updateverify=random.random()))
        # 保存验证码
        image_path = os.path.join(os.getcwd(), 'vcode')
        with open(image_path, 'wb') as f:
            f.write(verify_code_response.content)

        verify_code = helpers.recognize_verify_code(image_path, 'yh')
        log.debug('verify code detect result: %s' % verify_code)

        ht_verify_code_length = 4
        if len(verify_code) != ht_verify_code_length:
            return False
        return verify_code

    def post_login_data(self, verify_code):
        login_params = dict(
            self.config['login'],
            mac=helpers.get_mac(),
            clientip='',
            inputaccount=self.account_config['inputaccount'],
            trdpwd=self.account_config['trdpwd'],
            checkword=verify_code
        )

        if self.account_config.get('orgid'):
            login_params['orgid'] = self.account_config.get('orgid')
        if self.account_config.get('inputtype'):
            login_params['inputtype'] = self.account_config.get('inputtype')

        log.debug('login params: %s' % login_params)
        login_response = self.s.post(self.config['login_api'], params=login_params)
        log.debug('login response: %s' % login_response.text)

        if login_response.text.find('success') != -1:
            return True, None
        return False, login_response.text

    def _prepare_account(self, user, password, **kwargs):
        self.account_config = {
            'inputaccount': user,
            'trdpwd': password
        }
        self.account_config.update(**kwargs)

    def check_available_cancels(self, parsed=True):
        """
        @Contact: Emptyset <21324784@qq.com>
        检查撤单列表
        """
        try:
            response = self.s.get("https://www.chinastock.com.cn/trade/webtrade/stock/StockEntrustCancel.jsp",
                                  cookies=self.cookie)
            if response.status_code != 200:
                return False
            html = response.text.replace("\t", "").replace("\n", "").replace("\r", "")
            if html.find("请重新登录") != -1:
                return False
            pattern = r'<tr\s(?:[a-zA-Z0-9\:\=\'\"\(\)\s]*)>(.+)</tr></TBODY>'
            result1 = re.findall(pattern, html)[0]
            pattern = r'<td\s(?:[a-zA-Z0-9=_\"\:]*)>([\S]+)</td>'
            parsed_data = re.findall(pattern, result1)
            cancel_list = slice_list(step=12, data_list=parsed_data)
        except Exception as e:
            return []
        result = list()
        if parsed:
            for item in cancel_list:
                if len(item) == 12:
                    item_dict = {
                        "time": item[0],
                        "code": item[1],
                        "name": item[2],
                        "status": item[3],
                        "iotype": item[4],
                        "price": float(item[5]),
                        "volume": int(item[6]),
                        "entrust_num": item[7],
                        "trans_vol": int(item[8]),
                        "canceled_vol": int(item[9]),
                        "investor_code": item[10],
                        "account": item[11]
                    }
                elif len(item) == 11:
                    item_dict = {
                        "time": item[0],
                        "code": item[1],
                        "name": item[2],
                        "status": item[3],
                        "iotype": "",
                        "price": float(item[4]),
                        "volume": int(item[5]),
                        "entrust_num": item[6],
                        "trans_vol": int(item[7]),
                        "canceled_vol": int(item[8]),
                        "investor_code": item[9],
                        "account": item[10]
                    }
                else:
                    continue
                result.append(item_dict)
        return result

    def cancel_entrust(self, entrust_no, stock_code):
        """撤单
        :param entrust_no: 委托单号
        :param stock_code: 股票代码"""
        need_info = self.__get_trade_need_info(stock_code)
        cancel_params = dict(
            self.config['cancel_entrust'],
            orderSno=entrust_no,
            secuid=need_info['stock_account']
        )
        cancel_response = self.s.post(self.config['trade_api'], params=cancel_params)
        log.debug('cancel trust: %s' % cancel_response.text)
        return cancel_response.json()

    def cancel_entrusts(self, entrust_no):
        """
        @Contact: Emptyset <21324784@qq.com>
        批量撤单
        @param
            entrust_no: string类型
                        委托单号，用逗号隔开
                        e.g:"8000,8001,8002"
        @return
            返回格式是list，比如一个22个单子的批量撤单
            e.g.:
            [{"success":15, "failed":0},{"success":7, "failed":0}]
        """
        import time
        list_entrust_no = entrust_no.split(",")
        # 一次批量撤单不能超过15个
        list_entrust_no = slice_list(step=15, data_list=list_entrust_no)
        result = list()
        for item in list_entrust_no:
            if item[-1] == "":
                num = len(item) - 1
            else:
                num = len(item)
            cancel_data = {
                "ajaxFlag": "stock_batch_cancel",
                "num": num,
                "orderSno": ",".join(item)
            }
            while True:
                try:
                    cancel_response = self.s.post(
                        "https://www.chinastock.com.cn/trade/AjaxServlet",
                        data=cancel_data,
                        timeout=1,
                    )
                    if cancel_response.status_code == 200:
                        cancel_response_json = cancel_response.json()
                        # 如果出现“系统超时请重新登录”之类的错误信息，直接返回False
                        if "result_type" in cancel_response_json and "result_type" == 'error':
                            return False
                        result.append(cancel_response_json)
                        break
                    else:
                        log.debug('{}'.format(cancel_response))
                except Exception as e:
                    log.debug('{}'.format(e))
            time.sleep(0.2)
        return result

    @property
    def current_deal(self):
        return self.get_current_deal()

    def get_current_deal(self, date=None):
        """
        获取当日成交列表.
        """
        return self.do(self.config['current_deal'])

    def get_his_deal(self, bgd, edd):
        """
         <905266420@qq.com>
        获取历史时间段内的全部成交列表
            e.g.: get_deal( bgd="2016-07-14", edd="2016-08-14" )
            遇到提示“系统超时请重新登录”或者https返回状态码非200或者其他异常情况会返回False
        """
        data = {
            "sdate": bgd,
            "edate": edd
        }

        try:
            response = self.s.post("https://www.chinastock.com.cn/trade/webtrade/stock/stock_cj_query.jsp", data=data,
                                   cookies=self.cookie)
            if response.status_code != 200:
                return False
            if response.text.find("重新登录") != -1:
                return False
            res = self.format_response_data(response.text)
            return res
        except Exception as e:
            log.warning("撤单出错".format(e))
            return False

    def get_deal(self, date=None):
        """
        @Contact: Emptyset <21324784@qq.com>
        获取历史日成交列表
            e.g.: get_deal( "2016-07-14" )
            如果不传递日期则取的是当天成交列表
            返回值格式与get_current_deal相同
            遇到提示“系统超时请重新登录”或者https返回状态码非200或者其他异常情况会返回False
        """
        if date is None:
            data = {}
        else:
            data = {
                "sdate": date,
                "edate": date
            }
        try:
            response = self.s.post("https://www.chinastock.com.cn/trade/webtrade/stock/stock_cj_query.jsp", data=data,
                                   cookies=self.cookie)
            if response.status_code != 200:
                return False
            if response.text.find("重新登录") != -1:
                return False
            res = self.format_response_data(response.text)
            return res
        except Exception as e:
            log.warning("撤单出错".format(e))
            return False

    def buy(self, stock_code, price, amount=0, volume=0, entrust_prop='limit'):
        """买入股票
        :param stock_code: 股票代码
        :param price: 买入价格
        :param amount: 买入股数
        :param volume: 买入总金额 由 volume / price 取整， 若指定 price 则此参数无效
        :param entrust_prop: 委托类型 'limit' 限价单 , 'market'　市价单, 'market_cancel' 五档即时成交剩余转限制
        """
        market_type = helpers.get_stock_type(stock_code)
        bsflag = None
        if entrust_prop == 'limit':
            bsflag = '0B'
        elif entrust_prop == 'market_cancel':
            bsflag = '0d'
        elif market_type == 'sh':
            bsflag = '0q'
        elif market_type == 'sz':
            bsflag = '0a'
        assert bsflag is not None

        params = dict(
            self.config['buy'],
            bsflag=bsflag,
            qty=int(amount) if amount else volume // price // 100 * 100
        )
        return self.__trade(stock_code, price, entrust_prop=entrust_prop, other=params)

    def sell(self, stock_code, price, amount=0, volume=0, entrust_prop='limit'):
        """卖出股票
        :param stock_code: 股票代码
        :param price: 卖出价格
        :param amount: 卖出股数
        :param volume: 卖出总金额 由 volume / price 取整， 若指定 amount 则此参数无效
        :param entrust_prop: str 委托类型 'limit' 限价单 , 'market'　市价单, 'market_cancel' 五档即时成交剩余转限制
        """
        market_type = helpers.get_stock_type(stock_code)
        bsflag = None
        if entrust_prop == 'limit':
            bsflag = '0S'
        elif entrust_prop == 'market_cancel':
            bsflag = '0i'
        elif market_type == 'sh':
            bsflag = '0r'
        elif market_type == 'sz':
            bsflag = '0f'
        assert bsflag is not None

        params = dict(
            self.config['sell'],
            bsflag=bsflag,
            qty=amount if amount else volume // price
        )
        return self.__trade(stock_code, price, entrust_prop=entrust_prop, other=params)

    def fundpurchase(self, stock_code, amount=0):
        """基金申购
        :param stock_code: 基金代码
        :param amount: 申购份额
        """
        params = dict(
            self.config['fundpurchase'],
            price=1,  # 价格默认为1
            qty=amount
        )
        return self.__tradefund(stock_code, other=params)

    def fundredemption(self, stock_code, amount=0):
        """基金赎回
        :param stock_code: 基金代码
        :param amount: 赎回份额
        """
        params = dict(
            self.config['fundredemption'],
            price=1,  # 价格默认为1
            qty=amount
        )
        return self.__tradefund(stock_code, other=params)

    def fundsubscribe(self, stock_code, amount=0):
        """基金认购
        :param stock_code: 基金代码
        :param amount: 认购份额
        """
        params = dict(
            self.config['fundsubscribe'],
            price=1,  # 价格默认为1
            qty=amount
        )
        return self.__tradefund(stock_code, other=params)

    def fundsplit(self, stock_code, amount=0):
        """基金分拆
        :param stock_code: 母份额基金代码
        :param amount: 分拆份额
        """
        params = dict(
            self.config['fundsplit'],
            qty=amount
        )
        return self.__tradefund(stock_code, other=params)

    def fundmerge(self, stock_code, amount=0):
        """基金合并
        :param stock_code: 母份额基金代码
        :param amount: 合并份额
        """
        params = dict(
            self.config['fundmerge'],
            qty=amount
        )
        return self.__tradefund(stock_code, other=params)

    def __tradefund(self, stock_code, other):
        # 检查是否已经掉线
        if not self.heart_thread.is_alive():
            check_data = self.get_balance()
            if type(check_data) == dict:
                return check_data
        need_info = self.__get_trade_need_info(stock_code)
        trade_params = dict(
            other,
            stockCode=stock_code,
            market=need_info['exchange_type'],
            secuid=need_info['stock_account']
        )

        trade_response = self.s.post(self.config['trade_api'], params=trade_params)
        log.debug('trade response: %s' % trade_response.text)
        return trade_response.json()

    def __trade(self, stock_code, price, entrust_prop, other):
        # 检查是否已经掉线
        if not self.heart_thread.is_alive():
            check_data = self.get_balance()
            if type(check_data) == dict:
                return check_data
        need_info = self.__get_trade_need_info(stock_code)
        trade_params = dict(
            other,
            stockCode=stock_code[-6:],
            price=price,
            market=need_info['exchange_type'],
            secuid=need_info['stock_account']
        )
        trade_response = self.s.post(self.config['trade_api'], params=trade_params)
        log.debug("{}".format(self.config['trade_api']))
        log.debug("{}".format(trade_params))
        log.debug('trade response: %s' % trade_response.text)
        time.sleep(0.5)  # 避免银河 '请求频繁，请稍后再试' 的错误
        return trade_response.json()

    def __get_trade_need_info(self, stock_code):
        """获取股票对应的证券市场和帐号"""
        sh_exchange_type = '1'
        sz_exchange_type = '0'
        exchange_type = sh_exchange_type if helpers.get_stock_type(stock_code) == 'sh' else sz_exchange_type
        return dict(
            exchange_type=exchange_type,
            stock_account=self.exchange_stock_account[exchange_type]
        )

    def create_basic_params(self):
        basic_params = dict(
            CSRF_Token='undefined',
            timestamp=random.random(),
        )
        return basic_params

    def request(self, params):
        url = self.trade_prefix + params['service_jsp']
        r = self.s.get(url, cookies=self.cookie)
        if r.status_code != 200:
            return False
        if r.text.find('系统超时请重新登录') != -1:
            return False
        if params['service_jsp'] == '/trade/webtrade/stock/stock_zjgf_query.jsp':
            if params['service_type'] == 2:
                rptext = r.text[0:r.text.find('操作')]
                return rptext
            else:
                rbtext = r.text[r.text.find('操作'):]
                rbtext += 'yhposition'
                return rbtext
        else:
            return r.text

    def format_response_data(self, data):
        if not data:
            return False
        # 需要对于银河持仓情况特殊处理
        if data.find('yhposition') != -1:
            search_result_name = re.findall(r'<td nowrap=\"nowrap\" class=\"head(?:\w{0,5})\">(.*)</td>', data)
            search_result_content = []
            search_result_content_tmp = re.findall(r'<td nowrap=\"nowrap\" ( |style.*)>(.*)</td>', data)
            for item in search_result_content_tmp:
                s = item[-1] if type(item) is not str else item
                k = re.findall(">(.*)<", s)
                if len(k) > 0:
                    s = k[-1]
                search_result_content.append(s)
        else:
            # 获取原始data的html源码并且解析得到一个可读json格式
            search_result_name = re.findall(r'<td nowrap=\"nowrap\" class=\"head(?:\w{0,5})\">(.*)</td>', data)
            search_result_content = re.findall(r'<td nowrap=\"nowrap\">([^～]*?)</td>', data)
            search_result_content = list(map(lambda x: x.replace('&nbsp', '').replace(';', ''), search_result_content))

        col_len = len(search_result_name)
        if col_len == 0 or len(search_result_content) % col_len != 0:
            if len(search_result_content) == 0:
                return list()
            raise Exception("Get Data Error: col_num: {}, Data: {}".format(col_len, search_result_content))
        else:
            row_len = len(search_result_content) // col_len
            res = list()
            for row in range(row_len):
                item = dict()
                for col in range(col_len):
                    col_name = search_result_name[col]
                    item[col_name] = search_result_content[row * col_len + col]
                res.append(item)

        return self.format_response_data_type(res)

    def check_account_live(self, response):
        if hasattr(response, 'get'):
            if response.get('error_no') == '-1' or response.get('result_type') == 'error':
                self.heart_active = False
                raise NotLoginError(response.get('result_msg'))

    def heartbeat(self):
        heartbeat_params = dict(
            ftype='bsn'
        )
        res = self.s.post(self.config['heart_beat'], params=heartbeat_params)

    def unlockscreen(self):
        unlock_params = dict(
            password=self.account_config['trdpwd'],
            mainAccount=self.account_config['inputaccount'],
            ftype='bsn'
        )
        log.debug('unlock params: %s' % unlock_params)
        unlock_resp = self.s.post(self.config['unlock'], params=unlock_params)
        log.debug('unlock resp: %s' % unlock_resp.text)

    def get_ipo_info(self):
        """
        查询新股申购信息
        :return: (df_taoday_ipo, df_ipo_limit), 分别是当日新股申购列表信息， 申购额度。
        df_today_ipo
            代码	名称	价格	账户额度	申购下限	申购上限	证券账号	交易所	发行日期
        0	2830	名雕股份	16.53	17500	500	xxxxx	xxxxxxxx	深A	20161201
        1	732098	森特申购	9.18	27000	1000	xxxxx	xxxxxxx	沪A	20161201

        df_ipo_limit:
            市场	证券账号	账户额度
        0	深圳	xxxxxxx	xxxxx
        1	上海	xxxxxxx	xxxxx

        """
        import pandas as pd
        from bs4 import BeautifulSoup

        ipo_response = self.s.get(
            self.config['ipo_api'],
            params=dict(),
            headers={
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN",
                "Connection": "Keep-Alive",
                "Host": "www.chinastock.com.cn",
                "Referer": "https://www.chinastock.com.cn/trade/webtrade/login.jsp",
                "User-Agent": "Mozilla/4.0(compatible;MSIE,7.0;Windows NT 10.0; WOW64;Trident / 7.0;.NET4.0C;.NET4.0E;.NET CLR2.0.50727;.NET CLR 3.0.30729;.NET CLR 3.5.30729;InfoPath.3)"
            })
        if ipo_response.status_code != 200:
            return None, None
        html = ipo_response.content
        soup = BeautifulSoup(html, 'lxml')
        tables = soup.findAll('table', attrs={'class': 'fee'})
        df_ipo_limit = pd.read_html(str(tables[0]), flavor='lxml', header=0, encoding='utf-8')[0]
        df_today_ipo = pd.read_html(str(tables[1]), flavor='lxml', header=0, encoding='utf-8')[0]
        df_today_ipo[['代码']] = df_today_ipo[['代码']].applymap(lambda x: '{:0>6}'.format(x))
        return df_today_ipo, df_ipo_limit

    def get_ipo_limit(self, stock_code):
        """
        查询当日某只新股申购额度、申购上限、价格。
        仅为了兼容佣金宝同名方法。 不需要兼容，最好使用get_ipo_info()[0]
        :param stock_code: 申购代码!!!
        :return: high_amount(最高申购股数) enable_amount(申购额度) last_price(发行价)

        """
        (df1, df2) = self.get_ipo_info()
        if df1 is None:
            log.debug('查询错误: %s')
            return None
        df = df1[df1['代码'] == stock_code]
        if len(df) == 0:
            return dict()
        ser = df.iloc[0]
        return dict(high_amount=int(ser['申购上限']), enable_amount=int(ser['账户额度']),
                    last_price=float(ser['价格']))

    def auto_ipo(self):
        """
        自动打新
        :return: list(dict) dict 格式为 {'申购股票': 申购返回结果}
        """
        ipo_info, _ = self.get_ipo_info()
        ipo_info.fillna(0, inplace=True)

        res = []
        for _, row in ipo_info.iterrows():
            if row['账户额度'] <= 0:
                continue

            ipo_amount = min(row['账户额度'], row['申购上限'])
            response = self.buy(row['代码'], row['价格'], ipo_amount)
            res.append({
                row['名称']: response
            })
        return res

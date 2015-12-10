'''
# 华泰交易接口
# 测试环境: ubuntu14.04  python3.4
# 注意事项:
#   调用try_auto_login() 自动OCR 需要安装 tesseract-ocr
#   调用show_verify_code() 自动显示验证码,需要安装imagemagick
#
# 使用方法:
# 初始化
# htsc = HTSocket('xx','xx','xxx')
#
# 自动登录:
# while(not htsc.try_auto_login()):
#     time.sleep(3)
#
# 手动登录:
# htsc.prepare_login()
# htsc.show_verify_code()
# vericode = input("input verify code: ")
# htsc.enter_verify_code(vericode)
# htsc.login()
# htsc.prepare_trade()
#
# 连接站点并获取信息,成功返回True,失败返回False
# htsc._get_balance()       获取账目
# htsc._get_position()      获取仓位
# htsc._get_cancel_list()   获取可撤单列表
# htsc._get_today_entrust() 获取今日委托列表
# htsc._get_today_trade()   获取今日成交列表
#
# htsc可读取参数
# htsc.balance              账目信息,字典
        # {
        #     'money_type': '0',
        #     'money_name': '人民币',
        #     'market_value': 100000.0,     股票市值
        #     'fetch_balance': '0',         可取
        #     'enable_balance': 100000.0,   可用资金
        #     'asset_balance': 10000.0,     总资产
        #     'current_balance': '0'
        # }
# htsc.stock_position       仓位信息,列表,列表元素为字典
        # {
        #     'enable_amount': '0',         可用数量
        #     'stock_name': '银华日利',         股票缩写
        #     'last_price': 102.534,        最近查询价格
        #     'income_balance': '0',
        #     'market_value': 10253.4,      市值
        #     'keep_cost_price': 102.534,   保本价格
        #     'av_buy_price': '0',
        #     'hand_flag': '0',
        #     'current_amount': 100.0,      股票数量
        #     'stock_code': '511880',       股票代码
        #     'cost_price': 102.534,        成本价
        #     'exchange_type': '1',
        #     'av_income_balance': '0',
        #     'exchange_name': '上海Ａ',
        #     'stock_account': 'A111111111'
        # }
# htsc.cancel_list          可撤单清单,列表,列表元素为字典
        # {
        #     'entrust_amount': 1000.0,     委托数量
        #     'exchange_type': '1',
        #     'entrust_prop': '0',
        #     'entrust_status': '2',        2为已报;
        #     'business_amount': '0',
        #     'business_price': '0',
        #     'entrust_no': '24555',        委托号
        #     'entrust_time': '110952',
        #     'entrust_price': 102.5,       委托价格
        #     'stock_name': '银华日利',
        #     'exchange_name': '上海Ａ',
        #     'bs_name': '买入',
        #     'stock_account': 'A11111111', 股东账户
        #     'stock_code': '511880',       股票代码
        #     'entrust_bs': '1',            1为买入;2为卖出
        #     'status_name': '已报',
        #     'prop_name': '买卖'
        # }
# htsc.entrust_list         委托清单,列表,列表元素为字典
        # {
        #     'entrust_price': 102.533,     委托价格
        #     'stock_account': 'A1111111',  股东账户
        #     'entrust_time': '110849',     委托时间
        #     'entrust_amount': 100.0,      委托数量
        #     'stock_name': '银华日利',
        #     'status_name': '已成',
        #     'exchange_type': '1',
        #     'prop_name': '买卖',
        #     'bs_name': '买入',
        #     'entrust_status': '8',        8为已成,9为废单,6为已撤,2为已报
        #     'entrust_no': '24410',        委托号
        #     'business_price': 102.533,
        #     'business_amount': 100.0,
        #     'entrust_prop': '0',
        #     'stock_code': '511880',       股票代码
        #     'entrust_bs': '1',            1为买入,2为卖出
        #     'exchange_name': '上海Ａ'
        # }
# htsc.trade_list           成交清单,列表,列表元素为字典
        # {
        #     'business_amount': 200.0,     成交数量
        #     'stock_code': '511990',       股票代码
        #     'date': '20150828',           成交日期
        #     'bs_name': '卖出',
        #     'remark': '成交',
        #     'business_balance': 20001.6,  成交金额
        #     'stock_name': '华宝添益',
        #     'exchange_type': '上海Ａ',
        #     'stock_account': 'A11111111', 股东账户
        #     'entrust_no': '26717',        委托号
        #     'business_price': 100.008,    成交均价
        #     'serial_no': '35486'          流水号
        # }
'''

import socket
import uuid
import re
import requests
from random import random as rand
from base64 import b64decode, b64encode
import json
from PIL import Image

import logging
logging.basicConfig(level=logging.INFO, filename='.htsckt.log', filemode='w')
logging.captureWarnings(True)

class HTSocket(object):
    def __init__(self, account, encrypted_password, service_password, hd_model='ST9320325AS'):#"WD-WX31C32M1910"):

        # 用户账号
        self.__account = account

        # 用户加密后的交易密码
        self.__encrypted_password = encrypted_password

        # 用户通信密码
        self.__service_password = service_password

        # 用户硬盘型号
        self.__harddisk_model = hd_model

        # 用户类型
        self.__user_type = "jy"

        # 获取mac地址
        self.__mac_addr = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        logging.info(self.__mac_addr)

        # 获取ip地址
        #self.__ip_addr = '192.168.1.123'
        #import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("baidu.com", 80))
            self.__ip_addr = s.getsockname()[0]
        finally:
            if s:
                s.close()
        logging.info(self.__ip_addr)

        # 验证码
        self.__verify_code = ""
        self.__vericodefn = './.vericode{account}.jsp'.format(account=account)
        # 欢迎页面,可在该页面获得验证码
        self.__welcome_page = "https://service.htsc.com.cn/service/login.jsp"

        # 验证码地址
        self.__verify_page = "https://service.htsc.com.cn/service/pic/verifyCodeImage.jsp?ran="

        # 登录页面
        self.__login_page = "https://service.htsc.com.cn/service/loginAction.do?method=login"

        # 交易页面
        self.__jy_page = "https://service.htsc.com.cn/service/jy.jsp?sub_top=jy"

        # 交易key获取页面
        self.__jy_key_page = "https://service.htsc.com.cn/service/flashbusiness_new3.jsp?etfCode="

        # 交易接口
        self.__trade_page = "https://tradegw.htsc.com.cn/?"

        # 初始化浏览器
        self.__session = requests.session()
        # 设置user-agent
        self.__session.headers['User-Agent'] = 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)'

        # 交易传输key
        self.__trade_keys = {}

        # 股东账号
        # 上海
        self.__market_account_sh = None
        # 深圳
        self.__market_account_sz = None

        # 交易参数
        self.__trade_version = 1
        self.__op_entrust_way = 7

        # 账目信息
        # 账目信息为一个字典,其内容示例为:
        # {
        #     'money_type': '0',
        #     'money_name': '人民币',
        #     'market_value': 100000.0,     股票市值
        #     'fetch_balance': '0',         可取
        #     'enable_balance': 100000.0,   可用资金
        #     'asset_balance': 10000.0,     总资产
        #     'current_balance': '0'
        # }
        self.__balance = None
        self.__capital = {}

        # 持仓信息
        # 持仓为一个数组,即list()
        # 数组中的元素为字典,其内容示例为:
        # {
        #     'enable_amount': '0',         可用数量
        #     'stock_name': '银华日利',         股票缩写
        #     'last_price': 102.534,        最近查询价格
        #     'income_balance': '0',
        #     'market_value': 10253.4,      市值
        #     'keep_cost_price': 102.534,   保本价格
        #     'av_buy_price': '0',
        #     'hand_flag': '0',
        #     'current_amount': 100.0,      股票数量
        #     'stock_code': '511880',       股票代码
        #     'cost_price': 102.534,        成本价
        #     'exchange_type': '1',
        #     'av_income_balance': '0',
        #     'exchange_name': '上海Ａ',
        #     'stock_account': 'A111111111'
        # }
        self.__stock_position = None

        # 可撤单交易列表
        # 可撤单交易列表为一个数组,即list()
        # 数组中的元素为字典,其内容示例为:
        # {
        #     'entrust_amount': 1000.0,     委托数量
        #     'exchange_type': '1',
        #     'entrust_prop': '0',
        #     'entrust_status': '2',        2为已报;
        #     'business_amount': '0',
        #     'business_price': '0',
        #     'entrust_no': '24555',        委托号
        #     'entrust_time': '110952',
        #     'entrust_price': 102.5,       委托价格
        #     'stock_name': '银华日利',
        #     'exchange_name': '上海Ａ',
        #     'bs_name': '买入',
        #     'stock_account': 'A11111111', 股东账户
        #     'stock_code': '511880',       股票代码
        #     'entrust_bs': '1',            1为买入;2为卖出
        #     'status_name': '已报',
        #     'prop_name': '买卖'
        # }
        self.__cancel_list = None

        # 当日委托列表
        # 当日委托列表为一个数组,即list()
        # 数组中的元素为字典,其内容示例为:
        # {
        #     'entrust_price': 102.533,     委托价格
        #     'stock_account': 'A1111111',  股东账户
        #     'entrust_time': '110849',     委托时间
        #     'entrust_amount': 100.0,      委托数量
        #     'stock_name': '银华日利',
        #     'status_name': '已成',
        #     'exchange_type': '1',
        #     'prop_name': '买卖',
        #     'bs_name': '买入',
        #     'entrust_status': '8',        8为已成,9为废单,6为已撤,2为已报
        #     'entrust_no': '24410',        委托号
        #     'business_price': 102.533,
        #     'business_amount': 100.0,
        #     'entrust_prop': '0',
        #     'stock_code': '511880',       股票代码
        #     'entrust_bs': '1',            1为买入,2为卖出
        #     'exchange_name': '上海Ａ'
        # }
        self.__entrust_list = None

        # 当日成交列表
        # 当日成交列表为一个数组,即list()
        # 数组中的元素为字典,其内容示例为:
        # {
        #     'business_amount': 200.0,     成交数量
        #     'stock_code': '511990',       股票代码
        #     'date': '20150828',           成交日期
        #     'bs_name': '卖出',
        #     'remark': '成交',
        #     'business_balance': 20001.6,  成交金额
        #     'stock_name': '华宝添益',
        #     'exchange_type': '上海Ａ',
        #     'stock_account': 'A11111111', 股东账户
        #     'entrust_no': '26717',        委托号
        #     'business_price': 100.008,    成交均价
        #     'serial_no': '35486'          流水号
        # }
        self.__trade_list = None

    @property
    def balance(self):
        return self.__balance

    @property
    def capital(self):
        return self.__capital

    @property
    def stock_position(self):
        return self.__stock_position

    @property
    def cancel_list(self):
        return self.__cancel_list

    @property
    def entrust_list(self):
        return self.__entrust_list

    @property
    def trade_list(self):
        return self.__trade_list

    # 获取验证码
    def get_verify_code(self):
        vericode_url = self.__verify_page + str(rand())
        # logging.info(vericode_url);
        resp = self.__session.get(vericode_url)
        with open(self.__vericodefn, 'wb') as file:
            file.write(resp.content)
        # logging.warning("verify code is stored in self.__vericodefn. "
        #                 "use enter_verify_code() to input the code and then login()!")

    # 显示验证码,需要安装imagemagick
    def show_verify_code(self):
        image = Image.open(self.__vericodefn)
        image.show()

    # 识别验证码
    def recognize_verify_code(self):
        import tempfile   # 在win下有兼容性问题
        import subprocess
        # import os

        path = self.__vericodefn

        # temp = tempfile.NamedTemporaryFile(delete=False)
        # process = subprocess.Popen(['tesseract', path, temp.name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        temp = '.vericode{account}'.format(account=self.__account)
        process = subprocess.Popen(['tesseract', path, temp], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        process.communicate()

        # with open(temp.name + '.txt', 'r') as handle:
        with open(temp + '.txt', 'r+') as handle:
            contents = handle.read()
            handle.truncate(0)  # 将文件内容置为空
        # os.remove(temp.name + '.txt')
        # os.remove(temp.name)

        return contents.replace(" ", "").replace("\n", "").replace("\r", "").replace("><", "x")

    # 输入验证码
    def enter_verify_code(self, text):
        self.__verify_code = text
        logging.warning("verify code is entered: " + text)

    # 登录准备,获取验证码
    def prepare_login(self):
        # 建立初始连接
        self.__session.get(self.__welcome_page, verify=False)
        # 获取验证码
        self.get_verify_code()

    # 登录
    def login(self):
        payload = {
            'userType': self.__user_type,
            'loginEvent': 1,
            'trdpwdEns': self.__encrypted_password,
            'macaddr': self.__mac_addr,
            'hddInfo': self.__harddisk_model,
            'lipInfo': self.__ip_addr,
            'topath': 'null',
            'accountType': 1,
            'userName': self.__account,
            'servicePwd': self.__service_password,
            'trdpwd': self.__encrypted_password,
            'vcode': self.__verify_code
        }

        resp = self.__session.post(self.__login_page, data=payload)
        content = resp.text.replace('\r','').replace('\n','')
        # logging.warning('lonin info: '+content)
        # with open('log', 'w') as f:
        #     f.write(content)

        if re.match('.*欢迎您登录.*', content):
            logging.warning("login successfully!")
            return True  # , content
        else:
            return False  # , content

    # base64译码
    @staticmethod
    def __encode_base64(text):
        return b64encode(text.encode('utf8')).decode('utf8')

    # base64解码
    @staticmethod
    def __decode_base64_utf8(text):
        return b64decode(text).decode('utf8')#('2312')

    # base64解码
    @staticmethod
    def __decode_base64_gb2312(text):
        return b64decode(text).decode('gb2312')

    # base64解码
    @staticmethod
    def __decode_base64_gbk(text):
        return b64decode(text).decode('gbk')

    # base64解码
    @staticmethod
    def __decode_base64(text):
        try:
            return b64decode(text).decode('gbk')
        except Exception as e:
            return b64decode(text).decode('utf8')
            #return b64decode(text).decode('gbk')  # ('gb2312')

    # 将字典数据打包成字符串
    @staticmethod
    def __join_keys(keys):
        jnkys = '&'.join([k + "=" + str(keys[k]) for k in keys])
        # logging.info('bug here? ==> ' + jnkys)
        return jnkys

    # 将dict中的value转换为float,如果可能的话.
    # 因为部分股票代码,如000002是以0开头的,所以转化为int会造成股票代码的错误
    # 因此,即使可以转换为整数,也保持其字符串属性不变
    @staticmethod
    def __convert_value_in_dict_to_float(input_dict):
        result = dict()
        for (k, v) in input_dict.items():
            # add: _[Ii]d ?
            if re.match(r'.*_([Cc]ode|[Ff]lag|[Tt]ype|[Aa]ccount)$', k) or (len(v) >1 and re.match(r'^0\d+$',v)):
                result[k] = v
            elif re.fullmatch(r'[-+]?\d+\.\d+$', v):
                result[k] = float(v)
            elif re.fullmatch(r'[-+]?\d+$', v):
                result[k] = int(v)
            else:
                result[k] = v
        return result

    # 获取交易传输key
    def prepare_trade(self):
        # 进入交易页面
        self.__session.get(self.__jy_page)
        # 获取交易key
        resp = self.__session.get(self.__jy_key_page)
        content = resp.text.replace('\r','').replace('\n','')
        # with open('log', 'w') as f:
        #     f.write(content)

        m = re.match(r'.*var\s+data\s+=\s+"(.*?)";.*', content)
        if not m:
            return False
        else:
            self.__trade_keys = json.loads(self.__decode_base64(m.group(1)))
            # logging.info("trade keys: " + str(self.__trade_keys))
        # 如果key中的account与用户输入的相同,说明已经正确的登录
        if self.__trade_keys['fund_account'] == self.__account:
            #获取股票账户
            for market_account in self.__trade_keys['item']:
                if 'exchange_type' in market_account:
                    if market_account['exchange_type'] == 1:
                        self.__market_account_sh = market_account['stock_account']
                    if market_account['exchange_type'] == 2:
                        self.__market_account_sz = market_account['stock_account']
            return True
        else:
            return False

    '''
    def auto_login(self):
        from time import sleep
        while(not self.try_auto_login()):
            sleep(3)
    '''
    # 自动登录,并进入交易页面, 系统需要安装tesseract-ocr
    def try_auto_login(self):
        # 连接欢迎页面,获取验证码
        self.prepare_login()
        # 识别验证码
        verify_code = self.recognize_verify_code()
        # 输入验证码
        self.enter_verify_code(verify_code)
        # 登录
        # recontent = self.login()
        # logging.info('login info: '+ recontent[1]) # 臨時用來查看有哪些失敗情形
        if not self.login():  # recontent[0]:
            return False  # , recontent[1]
        # 获取交易传输key
        return self.prepare_trade()

    # 连接交易服务器,将payload译码为base64,并将返回结果从base64译码返回
    def __connect_trade_server(self, payload):
        # 将payload转换成字符串
        payload_string = self.__join_keys(payload)
        # 将字符串转换成base64格式
        payload_in_base64 = self.__encode_base64(payload_string)
        #logging.info('payload raw is: ' + payload_string)
        #logging.info('payload base64 is: ' + payload_in_base64)

        # 连接交易服务器
        url = self.__trade_page + payload_in_base64
        resp = self.__session.get(url)
        # 获取返回数据(base64格式)
        content_in_base64 = resp.text
        #logging.info('return in base64 is: ' + content_in_base64)
        # 译码为字符串
        content = self.__decode_base64(content_in_base64).replace('\n', '').replace('\r','') # replace(r'\n', '')
        # logging.info('return raw is: ' + content)
        # 将字符串转为json
        return_in_json = json.loads(content)
        return return_in_json

    def succeed(self, return_in_json):
        '''
        # 判断返回数据是否成功

        if 'cssweb_code' in return_in_json and return_in_json['cssweb_code'] == 'success':
            return return_in_json
        else:
            return None
        '''
        return 'cssweb_code' in return_in_json and return_in_json['cssweb_code'] == 'success'

    # 连接, 获取账户信息
    def _get_balance(self):
        payload = {
            'uid': self.__trade_keys['uid'],
            'cssweb_type': 'GET_FUNDS',
            'version': self.__trade_version,
            'custid': self.__trade_keys['account_content'],
            'op_branch_no': self.__trade_keys['branch_no'],
            'branch_no': self.__trade_keys['branch_no'],
            'op_entrust_way': self.__op_entrust_way,
            'op_station': self.__trade_keys['op_station'],
            'function_id': 405,
            'fund_account': self.__trade_keys['account_content'],
            'password': self.__trade_keys['trdpwd'],
            'identity_type': '',
            'money_type': '',
            'ram': str(rand())
        }
        result = self.__connect_trade_server(payload)
        if self.succeed(result):
            #self.__capital = result['item']
            for balance in result['item']:
                '''
                    多幣種:
                '''
                if 'money_type' in balance:
                    try:
                        self.__capital[balance['money_type']] = \
                            self.__convert_value_in_dict_to_float(balance)
                    except Exception as e:
                        raise
                    if balance['money_type'] == '0':
                        self.__balance = self.__convert_value_in_dict_to_float(balance)
            # logging.info('balance is : ' + str(self.__balance))
            return True
        else:
            print(result['cssweb_code'])
            return False

    # 连接服务器,获取仓位信息
    def _get_position(self):
        payload = {
            'uid': self.__trade_keys['uid'],
            'cssweb_type': 'GET_STOCK_POSITION',
            'version': self.__trade_version,
            'custid': self.__trade_keys['account_content'],
            'op_branch_no': self.__trade_keys['branch_no'],
            'branch_no': self.__trade_keys['branch_no'],
            'op_entrust_way': self.__op_entrust_way,
            'op_station': self.__trade_keys['op_station'],
            'function_id': 403,
            'fund_account': self.__trade_keys['account_content'],
            'password': self.__trade_keys['trdpwd'],
            'identity_type': '',
            'exchange_type': '',
            'stock_account': '',
            'stock_code': '',
            'query_direction': '',
            'query_mode': 0,
            'request_num': 100,
            'position_str': '',
            'ram': str(rand())
        }
        result = self.__connect_trade_server(payload)
        if self.succeed(result):
            self.__stock_position = list()
            for stock in result['item']:
                if 'exchange_type' in stock:
                    self.__stock_position.append(self.__convert_value_in_dict_to_float(stock))
            # logging.info('stock position is: ' + str(self.__stock_position))
            return True
        else:
            return False

    # 连接服务器, 执行买入操作
    def _buy(self, exchange_type, account, code, amount=0, price=0):
        payload = {
            'uid': self.__trade_keys['uid'],
            'cssweb_type': 'STOCK_BUY',
            'version': self.__trade_version,
            'custid': self.__trade_keys['account_content'],
            'op_branch_no': self.__trade_keys['branch_no'],
            'branch_no': self.__trade_keys['branch_no'],
            'op_entrust_way': self.__op_entrust_way,
            'op_station': self.__trade_keys['op_station'],
            'function_id': 302,
            'fund_account': self.__trade_keys['account_content'],
            'password': self.__trade_keys['trdpwd'],
            'identity_type': '',
            'exchange_type': exchange_type,
            'stock_account': account,
            'stock_code': code,
            'entrust_amount': amount,
            'entrust_price': price,
            'entrust_prop': 0,
            'entrust_bs': 1,
            'ram': str(rand())
        }
        result = self.__connect_trade_server(payload)
        return result

    # 连接服务器, 执行卖出操作
    def _sell(self, exchange_type, account, code, amount=0, price=0):
        payload = {
            'uid': self.__trade_keys['uid'],
            'cssweb_type': 'STOCK_SALE',
            'version': self.__trade_version,
            'custid': self.__trade_keys['account_content'],
            'op_branch_no': self.__trade_keys['branch_no'],
            'branch_no': self.__trade_keys['branch_no'],
            'op_entrust_way': self.__op_entrust_way,
            'op_station': self.__trade_keys['op_station'],
            'function_id': 302,
            'fund_account': self.__trade_keys['account_content'],
            'password': self.__trade_keys['trdpwd'],
            'identity_type': '',
            'exchange_type': exchange_type,
            'stock_account': account,
            'stock_code': code,
            'entrust_amount': amount,
            'entrust_price': price,
            'entrust_prop': 0,
            'entrust_bs': 2,
            'ram': str(rand())
        }
        result = self.__connect_trade_server(payload)
        return result

    # 连接服务器, 执行撤单操作
    #def _cancel(self, account, code,  entrust_no):
    def _cancel(self, entrust_no):
        payload = {
            'uid': self.__trade_keys['uid'],
            'cssweb_type': 'STOCK_CANCEL',
            'version': self.__trade_version,
            'custid': self.__trade_keys['account_content'],
            'op_branch_no': self.__trade_keys['branch_no'],
            'branch_no': self.__trade_keys['branch_no'],
            'op_entrust_way': self.__op_entrust_way,
            'op_station': self.__trade_keys['op_station'],
            'function_id': 304,
            'fund_account': self.__trade_keys['account_content'],
            'password': self.__trade_keys['trdpwd'],
            'identity_type': '',
            'batch_flag': 0,
            'exchange_type': '',
            'entrust_no': entrust_no,
            'entrust_bs': 2,
            'ram': str(rand())
        }
        result = self.__connect_trade_server(payload)
        return result

    # 连接服务器, 获取当日委托
    def _get_today_entrust(self):
        payload = {
            'uid': self.__trade_keys['uid'],
            'cssweb_type': 'GET_TODAY_ENTRUST',
            'version': self.__trade_version,
            'custid': self.__trade_keys['account_content'],
            'op_branch_no': self.__trade_keys['branch_no'],
            'branch_no': self.__trade_keys['branch_no'],
            'op_entrust_way': self.__op_entrust_way,
            'op_station': self.__trade_keys['op_station'],
            'function_id': 401,
            'fund_account': self.__trade_keys['account_content'],
            'password': self.__trade_keys['trdpwd'],
            'identity_type': '',
            'exchange_type': '',
            'stock_account': '',
            'stock_code': '',
            'locate_entrust_no': '',
            'query_direction': '',
            'sort_direction': 0,
            'request_num': 300,
            'position_str': '',
            'ram': str(rand())
        }
        result = self.__connect_trade_server(payload)
        if self.succeed(result):
            self.__entrust_list = list()
            for order in result['item']:
                if 'entrust_no' in order:
                    self.__entrust_list.append(self.__convert_value_in_dict_to_float(order))
            # logging.info('entrust list is: ' + str(self.__entrust_list))
            return True
        else:
            return False

    # 连接服务器, 查询当日成交
    def _get_today_trade(self):
        payload = {
            'uid': self.__trade_keys['uid'],
            'cssweb_type': 'GET_TODAY_TRADE',
            'version': self.__trade_version,
            'custid': self.__trade_keys['account_content'],
            'op_branch_no': self.__trade_keys['branch_no'],
            'branch_no': self.__trade_keys['branch_no'],
            'op_entrust_way': self.__op_entrust_way,
            'op_station': self.__trade_keys['op_station'],
            'function_id': 402,
            'fund_account': self.__trade_keys['account_content'],
            'password': self.__trade_keys['trdpwd'],
            'identity_type': '',
            'serial_no': '',
            'exchange_type': '',
            'stock_account': '',
            'stock_code': '',
            'query_direction': 1,
            'request_num': 300,
            'query_mode': 0,
            'position_str': '',
            'ram': str(rand())
        }
        result = self.__connect_trade_server(payload)
        if self.succeed(result):
            self.__trade_list = list()
            for order in result['item']:
                if 'entrust_no' in order:
                    self.__trade_list.append(self.__convert_value_in_dict_to_float(order))
            # logging.info('trade list is: ' + str(self.__trade_list))
            return True
        else:
            return False

    # 连接服务器, 获取可撤单交易
    def _get_cancel_list(self):
        payload = {
            'uid': self.__trade_keys['uid'],
            'cssweb_type': 'GET_CANCEL_LIST',
            'version': self.__trade_version,
            'custid': self.__trade_keys['account_content'],
            'op_branch_no': self.__trade_keys['branch_no'],
            'branch_no': self.__trade_keys['branch_no'],
            'op_entrust_way': self.__op_entrust_way,
            'op_station': self.__trade_keys['op_station'],
            'function_id': 401,
            'fund_account': self.__trade_keys['account_content'],
            'password': self.__trade_keys['trdpwd'],
            'identity_type': '',
            'exchange_type': '',
            'stock_account': '',
            'stock_code': '',
            'locate_entrust_no': '',
            'query_direction': '',
            'sort_direction': 0,
            'request_num': 300,
            'position_str': '',
            'ram': str(rand())
        }
        result = self.__connect_trade_server(payload)
        if self.succeed(result):
            self.__cancel_list = list()
            for order in result['item']:
                if 'entrust_no' in order:
                    self.__cancel_list.append(self.__convert_value_in_dict_to_float(order))
            # logging.info('cancel list is: ' + str(self.__cancel_list))
            return True
        else:
            return False


if __name__ == '__main__':
    pass
    # logging.info("This is a test......\n")
    """

    with open('.config', 'r') as f:
        config = json.loads(f.read().replace('\r','').replace('\n',''))  # replace(r\n', ''))

    htsc = HTSocket(config['account'], config['password'], config['service_password'])
    lgn = htsc.try_auto_login()
    if lgn:
        # print(lgn)
        '''
        htsc.prepare_login()
        htsc.show_verify_code()
        vericode = input("input verify code: ")
        htsc.enter_verify_code(vericode)
        htsc.login()
        htsc.prepare_trade()
        '''
        htsc._get_balance()
        htsc._get_position()
        htsc._get_cancel_list()
        htsc._get_today_entrust()
        htsc._get_today_trade()

        htsc.balance
        htsc.stock_position
        htsc.cancel_list
        htsc.entrust_list
        htsc.trade_list

    """

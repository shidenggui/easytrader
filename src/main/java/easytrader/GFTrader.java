package easytrader;
http://blog.csdn.net/lllkey/article/details/17526323
	http://blog.sina.com.cn/s/blog_4829b9400101pxs6.html
		https://my.oschina.net/u/1251149/blog/299010
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.imageio.ImageIO;

import org.apache.http.HttpResponse;
import org.apache.http.NameValuePair;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.protocol.HTTP;
import org.apache.http.util.EntityUtils;

import com.alibaba.fastjson.JSONObject;

//# coding: utf-8
//from __future__ import division
//
//import json
//import os
//import re
//import tempfile
//import urllib
//
//import requests
//import six
//
//from . import helpers
//from .webtrader import WebTrader
//from .log import log
//
//VERIFY_CODE_POS = 0
//TRADE_MARKET = 1
//SESSIONIDPOS = 32
//HOLDER_POS = 11
//SH = 0
//SZ = 1
//
//
class GFTrader extends WebTrader {
	

   private CloseableHttpClient httpClient;
   
   protected String config_path() {
return GFTrader.class.getClassLoader().getResource("easytrader/config/gf.json").getPath();	   
   }
	public GFTrader() {
//        super(GFTrader, self).__init__()
//        self.cookie = None
//        self.account_config = None
//        self.s = None
//        self.exchange_stock_account = dict()
//        self.sessionid = ''
//        self.holdername = list()
		httpClient = HttpClientBuilder.create().build();
	}
	
	/**
	 * 获取并识别返回的验证码
	 *  
	 * @return 失败返回 False 成功返回 验证码
	 * @author Darkness
	 * @date 2016年9月21日 下午2:43:20
	 * @version V1.0
	 */
	public String  __handle_recognize_code() {
		String verifyCodeApi = this.config.getString("verify_code_api");
		return __handle_recognize_code(verifyCodeApi);
	}
	
	public String  __handle_recognize_code(String verifyCodeApi) {
//        # 获取验证码
		
		HttpGet httpGet = new HttpGet(verifyCodeApi);
        try {
			HttpResponse response = httpClient.execute(httpGet);

			BufferedImage verifyCodeImage = ImageIO.read(response.getEntity().getContent());

			EntityUtils.consume(response.getEntity());
			
			GFVerifyCode gfVerifyCode = new GFVerifyCode(verifyCodeImage);
			String code = gfVerifyCode.getValue();
			if(code.length() !=5) {
				return __handle_recognize_code();
			}
//			if(code.length() !)
			return code;
		} catch (IOException e) {
			e.printStackTrace();
		}
        return "";
//        # 保存验证码
//        image_path = tempfile.mktemp()
//        with open(image_path, 'wb') as f:
//            f.write(bytes(verify_code_response.content))
//
//        verify_code = helpers.recognize_verify_code(image_path, broker='gf')
//        log.debug('verify code detect result: %s' % verify_code)
//        os.remove(image_path)
//
//        ht_verify_code_length = 5
//        if len(verify_code) != ht_verify_code_length:
//            return False
//        return verify_code
	}
	
	/**
	 * 访问登录页面获取 cookie
	 *  
	 * @author Darkness
	 * @date 2016年9月21日 下午2:38:56
	 * @version V1.0
	 */
    public void __go_login_page() {
		try {
			HttpGet httpGet = new HttpGet(this.config.getString("logout_api"));
			HttpResponse response = httpClient.execute(httpGet);
			httpGet = new HttpGet(this.config.getString("login_page"));
			response = httpClient.execute(httpGet);
		} catch (IOException e) {
			e.printStackTrace();
		}
    }
	/**
	 * 实现广发证券的自动登录
	 */
    public boolean login() {
        this.__go_login_page();
        String verify_code = this.__handle_recognize_code();
//
//        if not verify_code:
//            return False
//
        this.post_login_data(verify_code);
//        login_status, result = self.post_login_data(verify_code)
//        if login_status is False:
//            return False
//        return True
//
        return true;
    }
    public void post_login_data(String verify_code) {
//        login_params = dict(
//            self.config['login'],
//            mac=helpers.get_mac(),
//            username=self.account_config['username'],
//            password=self.account_config['password'],
//            tmp_yzm=verify_code
//        )
    	HashMap<String, String> login_params = this.config.getObject("login", HashMap.class);
    	HttpPost post = new HttpPost(this.config.getString("login_api"));
		List<NameValuePair> nvps = new ArrayList<>();
	    nvps.add(new BasicNameValuePair("authtype", login_params.get("authtype")));
		nvps.add(new BasicNameValuePair("disknum", login_params.get("disknum")));
		nvps.add(new BasicNameValuePair("loginType", login_params.get("loginType")));
		nvps.add(new BasicNameValuePair("origin", login_params.get("origin")));
		nvps.add(new BasicNameValuePair("mac", "BC:5F:F4:F9:7A:9D"));
		
		nvps.add(new BasicNameValuePair("username", this.account_config.getString("username")));
		nvps.add(new BasicNameValuePair("password", this.account_config.getString("password")));
		
		nvps.add(new BasicNameValuePair("tmp_yzm", verify_code));
		// 把控制台输入的验证码填入
		try {
			post.setEntity(new UrlEncodedFormEntity(nvps, HTTP.UTF_8));
		} catch (UnsupportedEncodingException e) {
			e.printStackTrace();
		}

		try {
			CloseableHttpResponse response = httpClient.execute(post);
			
			String responseText = EntityUtils.toString(response.getEntity());
			System.out.println(responseText);
			EntityUtils.consume(response.getEntity());
			
		} catch (ClientProtocolException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
//        login_response = self.s.post(self.config['login_api'], params=login_params)
//        log.info('login response: {}'.format(login_response.text))
//        if login_response.json()['success'] == True:
//            v = login_response.headers
//            self.sessionid = v['Set-Cookie'][-SESSIONIDPOS:]
//            self.__set_trade_need_info()
//            return True, None
//        return False, login_response.text
//
    }
//    def create_basic_params(self):
//        basic_params = dict(
//            dse_sessionId=self.sessionid
//        )
//        return basic_params
//
//    def request(self, params):
//        if six.PY2:
//            params_str = urllib.urlencode(params)
//            unquote_str = urllib.unquote(params_str)
//        else:
//            params_str = urllib.parse.urlencode(params)
//            unquote_str = urllib.parse.unquote(params_str)
//        url = self.trade_prefix + '?' + unquote_str
//        r = self.s.post(url)
//        log.debug('raw response: {}'.format(r.text))
//        return r.content
//
//    def format_response_data(self, data):
//        if six.PY2:
//            return_data = json.loads(data.encode('utf-8'))
//        else:
//            return_data = json.loads(str(data, 'utf-8'))
//        return return_data
//
//    def check_account_live(self, response):
//        if hasattr(response, 'data') and response.get('error_no') == '-1':
//            self.heart_active = False
//
//    def __set_trade_need_info(self):
//        """设置交易所需的一些基本参数
//        """
//        account_params = dict(
//            self.config['accountinfo']
//        )
//        if six.PY2:
//            params_str = urllib.urlencode(account_params)
//            unquote_str = urllib.unquote(params_str)
//        else:
//            params_str = urllib.parse.urlencode(account_params)
//            unquote_str = urllib.parse.unquote(params_str)
//        url = self.trade_prefix + '?' + unquote_str
//        r = self.s.get(url)
//        log.debug('get account info: {}'.format(r.text))
//        jslist = r.text.split(';')
//        jsholder = jslist[HOLDER_POS]
//        jsholder = re.findall(r'\[(.*)\]', jsholder)
//        jsholder = eval(jsholder[0])
//
//        if len(jsholder) < 3:
//            self.holdername.append(jsholder[0])
//            self.holdername.append(jsholder[1])
//            return
//        self.holdername.append(jsholder[1])
//        self.holdername.append(jsholder[2])
//
//    def __get_trade_need_info(self, stock_code):
//        """获取股票对应的证券市场和帐号"""
//        # 获取股票对应的证券市场
//        exchange_type = self.holdername[SH]['exchange_type'] if helpers.get_stock_type(stock_code) == 'sh' \
//            else self.holdername[SZ]['exchange_type']
//        # 获取股票对应的证券帐号
//        stock_account = self.holdername[SH]['stock_account'] if exchange_type == '1' \
//            else self.holdername[SZ]['stock_account']
//        return dict(
//            exchange_type=exchange_type,
//            stock_account=stock_account
//        )
//
//    def buy(self, stock_code, price, amount=0, volume=0, entrust_prop=0):
//        """买入
//        :param stock_code: 股票代码
//        :param price: 买入价格
//        :param amount: 买入股数
//        :param volume: 买入总金额 由 volume / price 取 100 的整数， 若指定 amount 则此参数无效
//        :param entrust_prop: 委托类型，暂未实现，默认为限价委托
//        """
//        params = dict(
//            self.config['buy'],
//            entrust_amount=amount if amount else volume // price // 100 * 100,
//            entrust_prop=entrust_prop
//        )
//        return self.__trade(stock_code, price, other=params)
//
//    def sell(self, stock_code, price, amount=0, volume=0, entrust_prop=0):
//        """卖出
//        :param stock_code: 股票代码
//        :param price: 卖出价格
//        :param amount: 卖出股数
//        :param volume: 卖出总金额 由 volume / price 取整， 若指定 amount 则此参数无效
//        :param entrust_prop: 委托类型，暂未实现，默认为限价委托
//        """
//        params = dict(
//            self.config['sell'],
//            entrust_amount=amount if amount else volume // price,
//            entrust_prop=entrust_prop
//        )
//        return self.__trade(stock_code, price, other=params)
//
//    def cnjj_apply(self, stock_code, amount):
//        """场内基金申购
//        :param stock_code: 基金代码
//        :param amount: 申购金额
//        """
//        params = dict(
//            self.config['cnjj_apply'],
//            entrust_amount=amount
//        )
//        return self.__trade(stock_code, 0, other=params)
//
//    def cnjj_redemption(self, stock_code, amount=0):
//        """场内基金赎回
//        :param stock_code: 基金代码
//        :param amount: 赎回份额
//        """
//        params = dict(
//            self.config['cnjj_redeem'],
//            entrust_amount=amount
//        )
//        return self.__trade(stock_code, 1, other=params)
//
//    def fund_subscribe(self, stock_code, price=0, entrust_prop='LFS'):
//        """基金认购
//        :param stock_code: 基金代码
//        :param price: 认购金额
//        """
//        params = dict(
//            self.config['fundsubscribe'],
//            entrust_amount=1,
//            entrust_prop=entrust_prop
//        )
//        return self.__trade(stock_code, price, other=params)
//
//    def fund_purchase(self, stock_code, price=0, entrust_prop='LFC'):
//        """基金申购
//        :param stock_code: 基金代码
//        :param amount: 申购金额
//        """
//        params = dict(
//            self.config['fundpurchase'],
//            entrust_amount=1,
//            entrust_prop=entrust_prop
//        )
//        return self.__trade(stock_code, price, other=params)
//
//    def fund_redemption(self, stock_code, amount=0, entrust_prop='LFR'):
//        """基金赎回
//        :param stock_code: 基金代码
//        :param amount: 赎回份额
//        """
//        params = dict(
//            self.config['fundredemption'],
//            entrust_amount=amount,
//            entrust_prop=entrust_prop
//        )
//        return self.__trade(stock_code, 1, other=params)
//
//    def fund_merge(self, stock_code, amount=0, entrust_prop='LFM'):
//        """基金合并
//        :param stock_code: 母份额基金代码
//        :param amount: 合并份额
//        """
//        params = dict(
//            self.config['fundmerge'],
//            entrust_amount=amount,
//            entrust_prop=entrust_prop
//        )
//        return self.__trade(stock_code, 1, other=params)
//
//    def fund_split(self, stock_code, amount=0, entrust_prop='LFP'):
//        """基金分拆
//        :param stock_code: 母份额基金代码
//        :param amount: 分拆份额
//        """
//        params = dict(
//            self.config['fundsplit'],
//            entrust_amount=amount,
//            entrust_prop=entrust_prop
//        )
//        return self.__trade(stock_code, 1, other=params)
//
//    def nxbQueryPrice(self, fund_code):
//        """牛熊宝查询
//        """
//        params = dict(
//            self.config['nxbQueryPrice'],
//            fund_code=fund_code
//        )
//        return self.do(params)
//
//    def nxbentrust(self, fund_code, amount, price, bs, auto_deal="true"):
//        """牛熊宝单项申报
//        :param fund_code: 转换代码
//        :param amount: 转入数量, like n*1000, min 1000
//        :param price: 转换比例 like 0.8
//        :param bs: 转换方向，1为母转子，2为子转母
//        """
//        # TODO: What's auto_deal
//        params = dict(
//            self.config['nxbentrust'],
//            fund_code=fund_code,
//            entrust_amount=amount,
//            entrust_price=price,
//            entrust_bs=bs,
//            auto_deal=auto_deal
//        )
//        return self.do(params)
//
//    def nxbentrustcancel(self, entrust_no):
//        """牛熊宝撤单,撤单后再次调用nxbQueryEntrust确认撤单成功
//        param: entrust_no: 单号，通过调用nxbQueryEntrust查询
//        """
//        params = dict(
//            self.config['nxbentrustcancel'],
//            entrust_no=entrust_no
//        )
//        return self.do(params)
//
//    def nxbQueryEntrust(self, start_date="0", end_date="0", query_type="1"):
//        """当日委托
//        :param start_date: 开始日期20160515,0为当天
//        :param end_date: 结束日期20160522,0为当天
//        :param query_type: 委托查询类型,0为历史查询，1为当日查询
//        """
//        params = dict(
//            self.config['nxbQueryEntrust'],
//            query_type=query_type,
//            prodta_no="98",
//            entrust_no="0",
//            fund_code="",
//            start_date=start_date,
//            end_date=end_date,
//            position_str="0",
//            limit="10",
//            start="0"
//        )
//        if query_type == "1":
//            params['query_mode'] = "1"
//        return self.do(params)
//
//    def nxbQueryDeliverOfToday(self):
//        """当日转换
//        """
//        params = dict(
//            self.config['nxbQueryDeliver'],
//            query_type="2",
//            prodta_no="98",
//            fund_code="",
//            position_str="0",
//            limit="10",
//            start="0"
//        )
//        return self.do(params)
//
//    def nxbQueryHisDeliver(self, start_date, end_date):
//        """历史转换
//        """
//        params = dict(
//            self.config['nxbQueryHisDeliver'],
//            query_type="2",
//            prodta_no="98",
//            fund_code="",
//            position_str="0",
//            limit="50",
//            start="0",
//            start_date=start_date,
//            end_date=end_date
//        )
//        return self.do(params)
//
//    def queryOfStkCodes(self):
//        """牛熊宝代码查询？
//        """
//        params = dict(
//            self.config['queryOfStkCodes'],
//            prodta_no="98",
//            business_type="2"
//        )
//        return self.do(params)
//
//    def queryNXBOfStock(self):
//        """牛熊宝持仓查询
//        """
//        params = dict(
//            self.config['queryNXBOfStock'],
//            fund_company="98",
//            query_mode="0",
//            start="0",
//            limit="10"
//        )
//        return self.do(params)
//
//    def __trade(self, stock_code, price, other):
//        need_info = self.__get_trade_need_info(stock_code)
//        trade_param = dict(
//            other,
//            stock_account=need_info['stock_account'],
//            exchange_type=need_info['exchange_type'],
//            stock_code=stock_code,
//            entrust_price=price,
//            dse_sessionId=self.sessionid
//        )
//        return self.do(trade_param)
//
//    def cancel_entrust(self, entrust_no):
//        """撤单
//        :param entrust_no: 委单号"""
//        cancel_params = dict(
//            self.config['cancel_entrust'],
//            entrust_no=entrust_no,
//            dse_sessionId=self.sessionid
//        )
//        return self.do(cancel_params)
//
//    @property
//    def exchangebill(self):
//        start_date, end_date = helpers.get_30_date()
//        return self.get_exchangebill(start_date, end_date)
//
//    def getStockQuotation(self, stockcode):
//        exchange_info = self.__get_trade_need_info(stockcode)
//        params = dict(
//            self.config['queryStockInfo'],
//            exchange_type=exchange_info['exchange_type'],
//            stock_code=stockcode
//        )
//        request_params = self.create_basic_params()
//        request_params.update(params)
//        response_data = self.request(request_params)
//        response_data = str(response_data)
//        response_data = response_data[response_data.find('hq') + 3:response_data.find('hqtype') - 1]
//        response_data = response_data.replace('\\x', '\\u00')
//        return json.loads(response_data)
//
//    def get_exchangebill(self, start_date, end_date):
//        """
//        查询指定日期内的交割单
//        :param start_date: 20160211
//        :param end_date: 20160211
//        :return:
//        """
//        params = self.config['exchangebill'].copy()
//        params.update({
//            "start_date": start_date,
//            "end_date": end_date,
//        })
//        return self.do(params)
//        
//    @property
//    def today_ipo_list(self):
//        '''
//
//        查询今日ipo的股票列表
//        :return:
//        '''
//        params = self.config['today_ipo_list'].copy()
//        return self.do(params)
//
//   
//    def today_ipo_limit(self):
//        '''
//
//        查询今日账户新股申购额度
//        :return:
//        '''
//        params = self.config['today_ipo_limit'].copy()
//        return self.do(params)
	
	public static void main(String[] args) {
		GFTrader trader = new GFTrader();
		trader.prepare(userDir() + "gf.json"); // 或者 yjb.json 或者 yh.json 等配置文件路径
		trader.balance();
//		trader.__handle_recognize_code("https://trade.gf.com.cn/yzm.jpgx");
	}

	private static String userDir() {
		return System.getProperty("user.dir") + File.separator;
	}
	@Override
	protected void check_account_live(JSONObject response) {
		// TODO Auto-generated method stub
		
	}

	@Override
	protected Map<String, String> create_basic_params() {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	protected String request(Map<String, String> params) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	protected JSONObject format_response_data(String data) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public JSONObject check_login_status(JSONObject return_data) {
		// TODO Auto-generated method stub
		return return_data;
	}
}
package easytrader;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import com.alibaba.fastjson.JSONObject;

//# coding: utf-8
//import logging
//import os
//import re
//import time
//from threading import Thread
//
//import six
//
//from . import helpers
//from .log import log
//
//if six.PY2:
//    import sys
//
//    stdi, stdo, stde = sys.stdin, sys.stdout, sys.stderr  # 获取标准输入、标准输出和标准错误输出
//    reload(sys)
//    sys.stdin, sys.stdout, sys.stderr = stdi, stdo, stde  # 保持标准输入、标准输出和标准错误输出
//    sys.setdefaultencoding('utf8')

abstract class WebTrader {
	
    private String global_config_path = WebTrader.class.getClassLoader().getResource("easytrader/config/global.json").getPath();
//    private String config_path = "";
//
    protected JSONObject account_config;
	protected JSONObject config;
	protected JSONObject global_config;
	
	public WebTrader() {
        this.__read_config();
//        self.trade_prefix = self.config['prefix']
//        self.account_config = ''
//        self.heart_active = True
//        self.heart_thread = Thread(target=self.send_heartbeat)
//        self.heart_thread.setDaemon(True)
	}
	
	public void read_config(String path) {
            try {
				this.account_config = Helpers.file2dict(path);
			} catch (IOException e) {
				e.printStackTrace();
//				log.error('配置文件格式有误，请勿使用记事本编辑，推荐使用 notepad++ 或者 sublime text');
			}
	}
	
	/**
	 * 登录的统一接口
	 * @param need_data 登录所需数据
	 */
	public void prepare(String need_data) {
        this.read_config(need_data);
        this.autologin();
	}
	
	/**
	 * 实现自动登录
	 */
	public void autologin() {
		//登录次数限制
		int limit=10;
		boolean success = false;
		for (int i = 0; i < limit; i++) {
			if(this.login()) {
				success = true;
				break;
			}
		}
		if(!success) {
			throw new NotLoginError("登录失败次数过多, 请检查密码是否正确 / 券商服务器是否处于维护中 / 网络连接是否正常");
		}
        this.keepalive();
	}
	
	protected abstract boolean login();
	
	ScheduledExecutorService heartThread;
	
	/**
	 * 启动保持在线的进程
	 */
    private void keepalive() {
    	heartThread = Executors.newScheduledThreadPool(1);
    	//每隔10秒查询指定接口保持 token 的有效性
    	heartThread.scheduleAtFixedRate(new Runnable() {
    		@Override
    		public void run() {
    			send_heartbeat();
    		}
    	}, 1, 10, TimeUnit.SECONDS);
    	
    	
    }
//        """ """
//        if self.heart_thread.is_alive():
//            self.heart_active = True
//        else:
//            self.heart_thread.start()
//
    private void send_heartbeat() {
//        """"""
//        while True:
//            if self.heart_active:
//                try:
//                    log_level = log.level
//
//                    log.setLevel(logging.ERROR)
    	JSONObject   response = this.heartbeat();
                    this.check_account_live(response);
//
//                    log.setLevel(log_level)
//                except:
//                    self.autologin()
//                time.sleep(10)
//            else:
//                time.sleep(1)
//
    }
    private JSONObject heartbeat() {
    	return this.balance();
    }
//
    protected abstract void check_account_live(JSONObject response) ;

    public void exit() {
//        """结束保持 token 在线的进程"""
//        self.heart_active = False
    	if(heartThread !=null && !heartThread.isShutdown()) {
    		heartThread.shutdown();
    	}
    }
    public void __read_config() {
//        """读取 config"""
        try {
			this.config = Helpers.file2dict(this.config_path());
			this.global_config = Helpers.file2dict(this.global_config_path);
		} catch (IOException e) {
			e.printStackTrace();
		}
//        self.config.update(self.global_config)
    }
    
    protected abstract String config_path();
//    @property
    public JSONObject balance() {
        return this.get_balance();
    }
    public JSONObject get_balance() {
//        """获取账户资金状况"""
        return this._do(this.config.getObject("balance", HashMap.class));
    }
//    @property
//    def position(self):
//        return self.get_position()
//
//    def get_position(self):
//        """获取持仓"""
//        return self.do(self.config['position'])
//
//    @property
//    def entrust(self):
//        return self.get_entrust()
//
//    def get_entrust(self):
//        """获取当日委托列表"""
//        return self.do(self.config['entrust'])
//
//    @property
//    def current_deal(self):
//        return self.get_current_deal()
//
//    def get_current_deal(self):
//        """获取当日委托列表"""
//        # return self.do(self.config['current_deal'])
//        log.warning('目前仅在 佣金宝/银河子类 中实现, 其余券商需要补充')
//
//    @property
//    def exchangebill(self):
//        """
//        默认提供最近30天的交割单, 通常只能返回查询日期内最新的 90 天数据。
//        :return:
//        """
//        # TODO 目前仅在 华泰子类 中实现
//        start_date, end_date = helpers.get_30_date()
//        return self.get_exchangebill(start_date, end_date)
//
//    def get_exchangebill(self, start_date, end_date):
//        """
//        查询指定日期内的交割单
//        :param start_date: 20160211
//        :param end_date: 20160211
//        :return:
//        """
//        log.warning('目前仅在 华泰子类 中实现, 其余券商需要补充')
//
//    def get_ipo_limit(self, stock_code):
//        """
//        查询新股申购额度申购上限
//        :param stock_code: 申购代码 ID
//        :return:
//        """
//        log.warning('目前仅在 佣金宝子类 中实现, 其余券商需要补充')
//
    /**
     * 发起对 api 的请求并过滤返回结果
     * @param params 交易所需的动态参数
     */
    public JSONObject _do(Map<String, String> params) {
    	Map<String, String> request_params = this.create_basic_params();
    	request_params.putAll(params);
        String response_data = this.request(request_params);
//        try:
           JSONObject format_json_data = this.format_response_data(response_data);
//        except:
//            # Caused by server force logged out
//            return None
        JSONObject return_data = this.fix_error_data(format_json_data);
//        try:
            this.check_login_status(return_data);
//        except NotLoginError:
//            self.autologin()
        return return_data;
//
    }
        /**
         * 生成基本的参数
         * @return
         */
        protected abstract Map<String, String> create_basic_params();
//
        /**
         * 请求并获取 JSON 数据
         * @param params Get 参数
         * @return
         */
        protected abstract String request(Map<String, String> params);
        
        /**
         * 格式化返回的 json 数据
         * @param data 请求返回的数据
         * @return
         */
        protected abstract JSONObject format_response_data(String data);
        
        /**
         * 若是返回错误移除外层的列表
         * @param data 需要判断是否包含错误信息的数据
         * @return
         */
        protected JSONObject fix_error_data(JSONObject data) {
        	return data;
        }
//
//    def format_response_data_type(self, response_data):
//        """格式化返回的值为正确的类型
//        :param response_data: 返回的数据
//        """
//        if type(response_data) is not list:
//            return response_data
//
//        int_match_str = '|'.join(self.config['response_format']['int'])
//        float_match_str = '|'.join(self.config['response_format']['float'])
//        for item in response_data:
//            for key in item:
//                try:
//                    if re.search(int_match_str, key) is not None:
//                        item[key] = helpers.str2num(item[key], 'int')
//                    elif re.search(float_match_str, key) is not None:
//                        item[key] = helpers.str2num(item[key], 'float')
//                except ValueError:
//                    continue
//        return response_data
//
    public abstract JSONObject check_login_status(JSONObject return_data) ;
}
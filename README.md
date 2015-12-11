# easytrader

* 进行简单的 web 股票交易
* **目前还很不完善,仅供测试**

### TODO

* 支持更多券商
* 实现自动登录
* 优化速度

### 支持券商

* 佣金宝
* 华泰（支持自动登录，还在测试阶段）

### requirements
> Python 3.4+
 
> pip install -r requirements.txt

> 华泰的自动登录需要安装 tesseract，并保证在命令行下 tesseract 可用

### 用法

#### 引入:

```python
from easytrader import YJBTrader, HTTrader
```

#### 设置账户:

##### 佣金宝
```python
user = YJBTrader()
user.token = 'ABC...CBA'
```
[如何获取 token](http://www.jisilu.cn/question/42707)

##### 华泰

```python
user = HTTrader()
user.read_config('me.json')
```

**注**: 华泰需要配置 `me.json` 填入相关信息, trdpwd 加密后的密码首次需要登录后查看登录 post的trdpwd 值确定

#### 自动登录 

##### 华泰

```python
user.autologin()
```
### 交易相关
以下用法以佣金宝为例，华泰类似

#### 获取资金状况:

```python
user.balance
```

**return**
```python
[{ 'asset_balance': '资产总值',
   'current_balance': '当前余额',
   'enable_balance': '可用金额',
   'market_value': '证券市值',
   'money_type': '币种',
   'pre_interest': '预计利息' ]}

```

#### 获取持仓:

```python
user.position
```

**return**
```python
[{'cost_price': '摊薄成本价',
   'current_amount': '当前数量',
   'enable_amount': '可卖数量',
   'income_balance': '摊薄浮动盈亏',
   'keep_cost_price': '保本价',
   'last_price': '最新价',
   'market_value': '证券市值',
   'position_str': '定位串',
   'stock_code': '证券代码',
   'stock_name': '证券名称'}]

```

#### 获取今日委托单
```python
user.entrust
```

**return** 

```python
[{'business_amount': '成交数量',
  'business_price': '成交价格',
  'entrust_amount': '委托数量',
  'entrust_bs': '买卖方向',
  'entrust_no': '委托编号',
  'entrust_price': '委托价格',
  'entrust_status': '委托状态',  # 废单 / 已报
  'report_time': '申报时间',
  'stock_code': '证券代码',
  'stock_name': '证券名称'}]

```


#### 买入:

```python
user.buy('162411', price=0.55, amount=100)
```

**return** 

```python
[{'entrust_no': '委托编号',
  'init_date': '发生日期',
  'batch_no': '委托批号',
  'report_no': '申报号',
  'seat_no': '席位编号',
  'entrust_time': '委托时间',
  'entrust_price': '委托价格',
  'entrust_amount': '委托数量',
  'stock_code': '证券代码',
  'entrust_bs': '买卖方向',
  'entrust_type': '委托类别',
  'entrust_status': '委托状态',
  'fund_account': '资金帐号',
  'error_no': '错误号',
  'error_info': '错误原因'}]
```

#### 卖出:

```python
user.sell('162411', price=0.55, amount=100)
```
#### 撤单（华泰特有）

```python
user.cancel_entrust('委托单号')
```

#### 掉线(佣金宝特有)

后台开了一个进程30秒请求一次维持 token 的有效性，理论上是不会掉线的。
如果掉线了,请求会返回

```python
{'error_info': '登陆已经超时，请重新登陆！', 'error_no': '-1'}
```

这时只需要重新设置token就可以了

```python
user.token='valid token'
```

#### 其他
其他可参考下面链接

[佣金宝](http://www.jisilu.cn/question/42707)

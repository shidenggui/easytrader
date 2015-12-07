# easytrader

* 进行简单的 web 股票交易
* **目前还很不完善,仅供测试**

### 支持券商

* 佣金宝

### requirements
* Python 3.4

> pip install -r requirements.txt

### 用法

#### 引入:

```python
from easytrader import YJBTrader
```

#### 设置账户:

```python
user = YJBTrader()
user.token = 'ABC...CBA'
```

[如何获取 token](http://www.jisilu.cn/question/42707)

#### 获取资金状况:

```python
user.balance
```

**return**
```python
{
  'asset_balance': '2.180',  # '资产总值'
  'current_balance': '2.180',  # '当前余额'
  'enable_balance': '2.180',  # '可用余额'
  'market_value': '0.000',  # '证券市值'
  'money_type': '人民币',
  'pre_interest': '0.000'  # '预计利息'
} 
```

#### 获取持仓:

```python
user.position
```

**return**
```python
[{
  'cost_price': '0.000',
  'current_amount': '0', # 当前数量
  'enable_amount': '0', # 可用数量
  'income_balance': '-11.100',
  'keep_cost_price': '0.000',
  'last_price': '0.571',
  'market_value': '0.000', # 证券市值
  'position_str': '定位字符串，无意义',
  'stock_code': '162411',
  'stock_name': '华宝油气'
}]
```

#### 获取今日委托单
```python
user.entrust
```

```python
[{
  'entrust_no': '委托编号',
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
  'error_info': '错误原因'
}]
```

#### 买入:

```python
user.buy('162411', price=0.55, amount=100)
```

#### 卖出:

```python
user.sell('162411', price=0.55, amount=100)
```

#### 返回信息
返回的都是 `JSON` 格式的信息,具体参考下面链接

[佣金宝](http://www.jisilu.cn/question/42707)

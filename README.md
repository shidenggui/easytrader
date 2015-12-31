# easytrader

* 进行简单的 web 股票交易
* 实现自动登录
* 有兴趣的可以加群 `429011814` 一起讨论

**开发环境** : `Ubuntu 15.10` / `Python 3.4`

### 相关
[获取新浪免费实时行情的类库: easyquotation](https://github.com/shidenggui/easyquotation)

[简单的股票量化交易框架 使用 easytrader 和 easyquotation](https://github.com/shidenggui/easyquant)

### 支持券商

* 佣金宝（支持自动登录）
* 华泰（支持自动登录）

### requirements

> Python 3.4+
 
> pip install -r requirements.txt

> 华泰 / 佣金宝 的自动登录需要安装以下二者之一： 

* `JAVA` : 推荐, 识别率高，安装简单, 需要命令行下 `java -version` 可用 (感谢空中园的贡献)
* `tesseract` : 保证在命令行下 `tesseract` 可用


### 用法

#### 引入:

```python
import easytrader
```

#### 设置账户:

##### 佣金宝
```python
user = easytrader.use('yjb') # 佣金宝支持 ['yjb', 'YJB', '佣金宝']
```

##### 华泰

```python
user = easytrader.use('ht') # 华泰支持 ['ht', 'HT', '华泰']
```

##### 自动登录

```python
user.prepare('ht.json') // 或者 yjb.json 
```

**注**: 

* 华泰需要配置 `ht.json` 填入相关信息, `trdpwd` 加密后的密码首次需要登录后查看登录 `POST` 的 `trdpwd` 值确定
* 佣金宝需要配置 `yjb.json` 并填入相关信息, 其中的 `password` 为加密后的 `password`

[如何获取配置所需信息, 可参考此文章](http://www.jisilu.cn/question/42707)

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

### 其他
[交易接口分析以及其他开源量化相关论坛](http://www.celuetan.com) 

[软件实现原理](http://www.jisilu.cn/question/42707)

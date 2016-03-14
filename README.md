# easytrader

* 进行自动的程序化股票交易
* 实现自动登录
* 支持命令行调用，方便其他语言适配
* 支持 Python3 / Python2, Linux / Win
* 有兴趣的可以加群 `429011814` 一起讨论

**开发环境** : `Ubuntu 15.10` / `Python 3.5`

### 相关
[获取新浪免费实时行情的类库: easyquotation](https://github.com/shidenggui/easyquotation)

[简单的股票量化交易框架 使用 easytrader 和 easyquotation](https://github.com/shidenggui/easyquant)

捐助: [支付宝](http://7xqo8v.com1.z0.glb.clouddn.com/zhifubao2.png)  [微信](http://7xqo8v.com1.z0.glb.clouddn.com/wx.png)
### 支持券商

* 佣金宝
* 华泰
* 银河 (感谢 [ruyiqf](https://github.com/ruyiqf) 的贡献)

### 模拟交易

* 雪球组合（[说明](doc/xueqiu.md)）

### requirements

> pip install -r requirements.txt

> 华泰 / 佣金宝 的自动登录需要安装以下二者之一： 

* `JAVA` : 推荐, 识别率高，安装简单, 需要命令行下 `java -version` 可用 (感谢空中园的贡献)
* `tesseract` : 保证在命令行下 `tesseract` 可用

### 安装

```python
pip install easytrader
```

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
##### 银河 

```python
user = easytrader.use('yh') # 银河支持 ['yh', 'YH', '银河']
```

##### 自动登录

```python
user.prepare('ht.json') // 或者 yjb.json 或者 yh.json 等配置文件路径
```

**注**:

配置文件需要自己用编辑器编辑生成, 请勿使用记事本, 推荐使用 [notepad++](https://notepad-plus-plus.org/zh/) 或者 [sublime text](http://www.sublimetext.com/)


格式可以参照 `Github` 目录下对应的 `json` 文件


* 华泰需要配置 `ht.json` 填入相关信息, `trdpwd` 加密后的密码首次需要登录后查看登录 `POST` 的 `trdpwd` 值确定
* 佣金宝需要配置 `yjb.json` 并填入相关信息, 其中的 `password` 为加密后的 `password`
* 银河需要配置 `yh.json` 填入相关信息, `trdpwd` 加密后的密码首次需要登录后查看登录 `POST` 的 `trdpwd` 值确定, 以及登录`POST`请求里面的`hardinfo`字段 


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
  'entrust_status': '委托状态',  # 废单 / 已报
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
#### 撤单

##### 华泰

```python
user.cancel_entrust('委托单号')
```
##### 佣金宝

```python
user.cancel_entrust('委托单号', '股票代码')
```
##### 银河证券

```python
user.cancel_entrust('委托单号', '股票代码')
```

#### 银河证券场内基金功能

##### 基金认购

```python
user.fundsubscribe('基金代码', '基金份额')
```
##### 基金申购

```python
user.fundpurchase('基金代码', '基金份额')
```
##### 基金赎回
```python
user.fundredemption('基金代码', '基金份额')
```
##### 基金合并

```python
user.fundmerge('基金代码', '基金份额')
```
##### 基金拆分

```python
user.fundsplit('基金代码', '基金份额')
```

#### 查询交割单

##### 华泰

需要注意通常券商只会返回有限天数最新的交割单，如查询2015年整年数据, 华泰只会返回年末的90天的交割单

```python
user.exchangebill   # 查询最近30天的交割单

user.get_exchangebill('开始日期', '截止日期')   # 指定查询时间段, 日期格式为 "20160214"
```

**return**
```python
{["entrust_bs": "操作", # "1":"买入", "2":"卖出", " ":"其他"
  "business_balance": "成交金额",
  "stock_name": "证券名称",
  "fare1": "印花税",
  "occur_balance": "发生金额",
  "stock_account": "股东帐户",
  "business_name": "摘要", # "证券买入", "证券卖出", "基金拆分", "基金合并", "交收证券冻结", "交收证券冻结取消", "开放基金赎回", "开放基金赎回返款", "基金资金拨入", "基金资金拨出", "交收资金冻结取消", "开放基金申购"
  "farex": "",
  "fare0": "手续费",
  "stock_code": "证券代码",
  "occur_amount": "成交数量",
  "date": "成交日期",
  "post_balance": "本次余额",
  "fare2": "其他杂费",
  "fare3": "",
  "entrust_no": "合同编号",
  "business_price": "成交均价",
]}

# 未确认的key有, farex, fare3
# 未确认的表头有 结算汇率, 备注
```

### 命令行模式

#### 登录

```
 python cli.py --use ht --prepare ht.json 
```

注: 此时会生成 `account.session` 文件保存生成的 `user` 对象

#### 获取余额 / 持仓 / 以及其他变量

```
 python cli.py --get balance
```

#### 买卖 / 撤单

```
 python cli.py --do buy 162411 0.450 100
```
#### 查看帮助 

```
 python cli.py --help
```

#### Q&A

##### Question

如何关闭 debug 日志的输出

##### Answer

```python
user = easytrader.use('ht', debug=False)

```

##### Question

编辑完配置文件，运行后出现 `json` 解码报错的信息。类似于下面

```python
raise JSONDecodeError("Expecting value", s, err.value) from None

JSONDecodeError: Expecting value
```

##### Answer
请勿使用 `记事本` 编辑账户的 `json` 配置文件，推荐使用 [notepad++](https://notepad-plus-plus.org/zh/) 或者 [sublime text](http://www.sublimetext.com/)

### 其他
[交易接口分析以及其他开源量化相关论坛](http://www.celuetan.com) 

[软件实现原理](http://www.jisilu.cn/question/42707)

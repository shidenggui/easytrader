# easytrader

* 进行自动的程序化股票交易
* 实现自动登录
* 支持跟踪 `joinquant`, `ricequant` 的模拟交易
* 支持跟踪 雪球组合 调仓
* 支持命令行调用，方便其他语言适配
* 支持 Python3 / Python2, Linux / Win, 推荐使用 `Python3`
* 有兴趣的可以加群 `556050652` 、`549879767`(已满) 、`429011814`(已满) 一起讨论
* 捐助: [支付宝](http://7xqo8v.com1.z0.glb.clouddn.com/zhifubao2.png)  [微信](http://7xqo8v.com1.z0.glb.clouddn.com/wx.png) 或者 银河开户可以加群找我


**开发环境** : `Ubuntu 16.04` / `Python 3.5`

### 相关

[量化交流论坛](http://www.celuetan.com)

[获取新浪免费实时行情的类库: easyquotation](https://github.com/shidenggui/easyquotation)

[简单的股票量化交易框架 使用 easytrader 和 easyquotation](https://github.com/shidenggui/easyquant)


### 支持券商

* 银河
* 广发
* 银河客户端(支持自动登陆), 须在 `windows` 平台下载 `银河双子星` 客户端
* 佣金宝(web已经关闭)

### 模拟交易

* 雪球组合 by @[haogefeifei](https://github.com/haogefeifei)（[说明](doc/xueqiu.md)）

### requirements

> pip install -r requirements.txt

> 银河可以直接自动登录

> 广发的自动登录需要安装下列的 tesseract：

* `tesseract` : 非 `pytesseract`, 需要单独安装, [地址](https://github.com/tesseract-ocr/tesseract/wiki),保证在命令行下 `tesseract` 可用

##### 银河客户端设置

* 系统设置 > 快速交易: 关闭所有的买卖，撤单等确认选项
* 系统设置 > 界面设置: 界面不操作超时时间设为 0
* 系统设置 > 交易设置: 默认买入价格/买入数量/卖出价格/卖出数量 都设置为 空


### 安装

```shell
pip install easytrader
```

注： `Windows` 用户 `pip` 安装时会提示 `No module named xxx`, 请使用 `pip install xxx` 安装对应缺失的 `module`, 然后再重新 `pip install easytrader`, 可以参考此文档 [INSTALL4Windows.md](INSTALL4Windows.md)

### 升级

```shell
pip install easytrader --upgrade
```

### 用法

#### 引入:

```python
import easytrader
```

#### 设置账户:

##### 银河

```python
user = easytrader.use('yh') # 银河支持 ['yh', 'YH', '银河']
```

##### 银河客户端

```python
user = easytrader.use('yh_client') # 银河客户端支持 ['yh_client', 'YH_CLIENT', '银河客户端']
```

##### 广发

```python
user = easytrader.use('gf') # 广发支持 ['gf', 'GF', '广发']
```


#### 登录帐号

##### 使用配置文件

```python
user.prepare('/path/to/your/ht.json') // 或者 yh.json 或者 yh_client.json 等配置文件路径
```

##### 参数登录
```
user.prepare(user='用户名', password='券商加密后的密码, 雪球、银河客户端为明文密码')
```

**注**:

使用配置文件模式, 配置文件需要自己用编辑器编辑生成, 请勿使用记事本, 推荐使用 [notepad++](https://notepad-plus-plus.org/zh/) 或者 [sublime text](http://www.sublimetext.com/)


格式可以参照 `Github` 目录下对应的 `json` 文件

* 银河类似下面文章中所说的方法。 通过在 `web` 手动登陆后等待一段时间出现锁屏, 然后需要输入密码解锁，银河的加密密码可以通过这个解锁锁屏的请求抓取到
* 雪球配置中 `username` 为邮箱, `account` 为手机, 填两者之一即可，另一项改为 `""`, 密码直接填写登录的明文密码即可，不需要抓取 `POST` 的密码
* 银河客户端直接使用明文的账号和密码即可

[如何获取配置所需信息, 可参考此文章](https://www.jisilu.cn/question/42707)

### 交易相关
以下用法以佣金宝为例

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

##### 银河

```python
user.cancel_entrust('委托单号', '股票代码')
```

##### 银河客户端


```python
user.cancel_entrust('股票6位代码,不带前缀', "撤单方向，可使用 ['buy', 'sell']"
```


####  ipo 打新

#### 银河

```python
user.get_ipo_info()
```

**return**


```python
(df_taoday_ipo, df_ipo_limit), 分别是当日新股申购列表信息， 申购额度。
        df_today_ipo
            代码	名称	价格	账户额度	申购下限	申购上限	证券账号	交易所	发行日期
        0	2830	名雕股份	16.53	17500	500	xxxxx	xxxxxxxx	深A	20161201
        1	732098	森特申购	9.18	27000	1000	xxxxx	xxxxxxx	沪A	20161201

        df_ipo_limit:
            市场	证券账号	账户额度
        0	深圳	xxxxxxx	xxxxx
        1	上海	xxxxxxx	xxxxx
``

#### 查询交割单

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

```

#### 基金申购

##### 银河

```
user.fundpurchase(stock_code, amount):
```

#### 基金赎回

##### 银河

```
user.fundredemption(stock_code, amount):
```

#### 基金认购

##### 银河

```
user.fundsubscribe(stock_code, amount):
```


#### 基金分拆

##### 银河

```
user.fundsplit(stock_code, amount):
```

#### 基金合并

##### 银河

```
user.fundmerge(stock_code, amount):
```



#### 查询当日成交

##### 佣金宝

```python
user.current_deal
```

**return**

```python
[{'business_amount': '成交数量',
'business_price': '成交价格',
'entrust_amount': '委托数量',
'entrust_bs': '买卖方向',
'stock_account': '证券帐号',
'fund_account': '资金帐号',
'position_str': '定位串',
'business_status': '成交状态',
'date': '发生日期',
'business_type': '成交类别',
'business_time': '成交时间',
'stock_code': '证券代码',
'stock_name': '证券名称'}]
```

##### 佣金宝

```python
user.get_ipo_limit('申购代码')
```

**return**

```python
{'high_amount': '最高申购股数',
'enable_amount': '申购额度',
'last_price': '发行价',}
```

#### 查询今天可以申购的新股信息

```python
from easytrader import helpers
ipo_data = helpers.get_today_ipo_data()
print(ipo_data)
```

**return**

```python
[{'stock_code': '股票代码',
  'stock_name': '股票名称',
  'price': 发行价,
  'apply_code': '申购代码'}]
```

#### 雪球组合调仓

```python
user.adjust_weight('000001', 10)
```


### 跟踪 joinquant / ricequant  的模拟交易

#### 初始化跟踪的 trader

这里以雪球为例, 也可以使用银河之类 easytrader 支持的券商

```
xq_user = easytrader.use('xq')
xq_user.prepare('xq.json')
```

#### 初始化跟踪 joinquant / ricequant 的 follower

```
target = 'jq'  # joinquant
target = 'rq'  # ricequant
follower = easytrader.follower(target)
follower.login(user='rq/jq用户名', password='rq/jq密码')
```

#### 连接 follower 和 trader

##### joinquant
```
follower.follow(xq_user, 'jq的模拟交易url')
```

注: jq的模拟交易url指的是对应模拟交易对应的可以查看持仓, 交易记录的页面, 类似 `https://www.joinquant.com/algorithm/live/index?backtestId=xxx`

##### ricequant

```
follower.follow(xq_user, run_id)
```
注：ricequant的run_id即PT列表中的ID。

正常会输出

![](https://raw.githubusercontent.com/shidenggui/assets/master/easytrader/joinquant.jpg)

enjoy it

### 跟踪 雪球的组合

#### 初始化跟踪的 trader

同上

#### 初始化跟踪 雪球组合 的 follower

```
xq_follower = easytrader.follower('xq')
xq_follower.login(user='xq用户名', password='xq密码')
```

#### 连接 follower 和 trader

```
xq_follower.follow(xq_user, 'xq组合ID，类似ZH123456', total_assets=100000)
```


注: 雪球组合是以百分比调仓的， 所以需要额外设置组合对应的资金额度

* 这里可以设置 total_assets, 为当前组合的净值对应的总资金额度, 具体可以参考参数说明
* 或者设置 initial_assets, 这时候总资金额度为 initial_assets * 组合净值


#### 多用户跟踪多策略

```
follower.follow(users=[xq_user, yh_user], strategies=['组合1', '组合2'], total_assets=[10000, 10000])
```

#### 目录下产生的 cmd_cache.pk

这是用来存储历史执行过的交易指令，防止在重启程序时重复执行交易过的指令，可以通过 `follower.follow(xxx, cmd_cache=False)` 来关闭

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

哪里可以找到对应的 `ht.json` , `xq.json` 的说明

##### Answer

这个文件需要自己新建，对应的格式在 `github` 项目的根目录下有对应的模板

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

[软件实现原理](http://www.jisilu.cn/question/42707)

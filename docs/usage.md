# 引入

```python
import easytrader
```

**设置账户**:

**银河**

```python
user = easytrader.use('yh') # 银河支持 ['yh', 'YH', '银河']
```

** 银河客户端**

```python
user = easytrader.use('yh_client') # 银河客户端支持 ['yh_client', 'YH_CLIENT', '银河客户端']
```

** 广发**

```python
user = easytrader.use('gf') # 广发支持 ['gf', 'GF', '广发']
```

**湘财证券**

```python
user = easytrader.use('xczq') # 湘财证券支持 ['xczq', '湘财证券']
```


# 抓取登陆所需的密码

使用 `easytrader` 的广发，银河 `web` 版本时，需要抓取对应券商的加密密码

** 银河 web 版本**

**推荐获取方法:**

在 IE 浏览器中打开下面这个网页， [一键获取银河加密密码](http://htmlpreview.github.io/?https://github.com/shidenggui/assets/blob/master/easytrader/get_yh_password.html), 若有弹框的话选择允许控件运行，按步骤操作就可以获得密码

**其他方式**

* [银河web获取加密密码的图文教程, 其他类似](https://shimo.im/doc/kvazIHNTRvYr7iqe)(需要安装 fildder 软件)
* [如何获取配置所需信息, 也可参考此文章](https://www.jisilu.cn/question/42707)

**广发**

参考此文档 [INSTALL4Windows.md](other/INSTALL4Windows.md)

参考银河的获取密码的其他方式


**雪球**

 雪球配置中 `username` 为邮箱, `account` 为手机, 填两者之一即可，另一项改为 `""`, 密码直接填写登录的明文密码即可，不需要抓取 `POST` 的密码

**银河客户端**

银河客户端直接使用明文的账号和密码即可


# 登录帐号

登陆账号有两种方式，`使用参数` 和 `使用配置文件`

** 参数登录(推荐)**

```
user.prepare(user='用户名', password='银河，广发web端需要券商加密后的密码, 雪球、银河客户端为明文密码')
```

**注:**雪球额外有个 account 参数，见上文介绍

** 使用配置文件**

```python
user.prepare('/path/to/your/yh.json') // 或者 zq.json 或者 yh_client.json 等配置文件路径
```

**注**: 使用配置文件模式, 配置文件需要自己用编辑器编辑生成, 请勿使用记事本, 推荐使用 [notepad++](https://notepad-plus-plus.org/zh/) 或者 [sublime text](http://www.sublimetext.com/)

*格式如下*

银河 

```
{
    "inputaccount": "客户号",
    "trdpwd": "加密后的密码"
}
```

银河客户端

```
{
  "user": "银河用户名",
  "password": "银河明文密码"
}

```

广发

```
{
  "username": "加密的客户号",
  "password": "加密的密码"
}
```

湘菜证券

```
{
  "account": "客户号",
  "password": "密码"
}
```

### 交易相关

以下用法以银河为例

#### 获取资金状况:

```python
user.balance
```

**return**
```python
[{'参考市值': 21642.0,
  '可用资金': 28494.21,
  '币种': '0',
  '总资产': 50136.21,
  '股份参考盈亏': -90.21,
  '资金余额': 28494.21,
  '资金帐号': 'xxx'}]
```

#### 获取持仓:

```python
user.position
```

**return**
```python
[{'买入冻结': 0,
  '交易市场': '沪A',
  '卖出冻结': '0',
  '参考市价': 4.71,
  '参考市值': 10362.0,
  '参考成本价': 4.672,
  '参考盈亏': 82.79,
  '当前持仓': 2200,
  '盈亏比例(%)': '0.81%',
  '股东代码': 'xxx',
  '股份余额': 2200,
  '股份可用': 2200,
  '证券代码': '601398',
  '证券名称': '工商银行'}]
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
{'orderid': 'xxxxxxxx', 'ordersno': '1111'}
```

#### 卖出:

```python
user.sell('162411', price=0.55, amount=100)
```

**return**

```python
{'orderid': 'xxxxxxxx', 'ordersno': '1111'}
```

#### 一键打新

##### 银河

```python
user.auto_ipo()
```

#### 撤单

##### 银河

```python
user.cancel_entrust('委托单号', '股票代码')
```

**return**

```
{'msgok': '撤单申报成功'}
```

##### 银河客户端


```python
user.cancel_entrust('股票6位代码,不带前缀', "撤单方向，可使用 ['buy', 'sell']"
```

#### 查询当日成交

```python
user.current_deal
```

**return**

```
[{'买卖标志': '买入',
  '交易市场': '深A',
  '委托序号': '12345',
  '成交价格': 0.626,
  '成交数量': 100,
  '成交日期': '20170313',
  '成交时间': '09:50:30',
  '成交金额': 62.60,
  '股东代码': 'xxx',
  '证券代码': '162411',
  '证券名称': '华宝油气'}]
```

#### 今日委托

```python
user.entrust
```

**return**

```
[{'买卖标志': '买入',
  '交易市场': '深A',
  '委托价格': 0.627,
  '委托序号': '111111',
  '委托数量': 100,
  '委托日期': '20170313',
  '委托时间': '09:50:30',
  '成交数量': 100,
  '撤单数量': 0,
  '状态说明': '已成',
  '股东代码': 'xxxxx',
  '证券代码': '162411',
  '证券名称': '华宝油气'},
 {'买卖标志': '买入',
  '交易市场': '深A',
  '委托价格': 0.6,
  '委托序号': '1111',
  '委托数量': 100,
  '委托日期': '20170313',
  '委托时间': '09:40:30',
  '成交数量': 0,
  '撤单数量': 100,
  '状态说明': '已撤',
  '股东代码': 'xxx',
  '证券代码': '162411',
  '证券名称': '华宝油气'}]
```

####  ipo 打新

*银河*

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
```

然后使用 `user.buy` 接口按返回的价格数量买入对应新股就可以了

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

#### 使用市价单跟踪模式，目前仅支持银河

```
follower.follow(***, entrust_prop='market')
```

#### 调整下单间隔, 默认为0s。调大可防止卖出买入时卖出单没有及时成交导致的买入金额不足

```
follower.follow(***, send_interval=30) # 设置下单间隔为 30 s
```


### 命令行模式

#### 登录

```
 python cli.py --use yh --prepare yh.json
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



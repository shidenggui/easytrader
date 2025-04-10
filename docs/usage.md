# 使用

## 引入

```python
import easytrader
```

## 设置同花顺客户端类型

**通用同花顺客户端**

```python
user = easytrader.use('universal_client') 
```

注: 通用同花顺客户端是指同花顺官网提供的客户端软件内的下单程序，内含对多个券商的交易支持，适用于券商不直接提供同花顺客户端时的后备方案。

**其他券商专用同花顺客户端**

```python
user = easytrader.use('ths')
```

注: 其他券商专用同花顺客户端是指对应券商官网提供的基于同花顺修改的软件版本，类似银河的双子星(同花顺版本)，国金证券网上交易独立下单程序（核新PC版）等。


**雪球组合**

```python
user = easytrader.use('xq')
```

**国金客户端**

```python
user = easytrader.use('gj_client') 
```

**海通客户端**

```python
user = easytrader.use('htzq_client')
```

**华泰客户端**

```python
user = easytrader.use('ht_client')
```


## 启动并连接客户端

### （一）其他券商专用同花顺客户端

其他券商专用同花顺客户端不支持自动登录，需要先手动登录。

请手动打开并登录客户端后，运用connect函数连接客户端。

```python
user.connect(r'客户端xiadan.exe路径') # 类似 r'C:\htzqzyb2\xiadan.exe'
```

### （二）通用同花顺客户端

需要先手动登录一次：添加券商，填入账户号、密码、验证码，勾选“保存密码”

第一次登录后，上述信息被缓存，可以调用prepare函数自动登录（仅需账户号、客户端路径，密码随意输入）。

### （三）其它

非同花顺的客户端，可以调用prepare函数自动登录。

调用prepare时所需的参数，可以通过`函数参数` 或 `配置文件` 赋予。

**1. 函数参数(推荐)**

```
user.prepare(user='用户名', password='雪球、银河客户端为明文密码', comm_password='华泰通讯密码，其他券商不用')
```

注: 雪球比较特殊，见下列配置文件格式

**2. 配置文件**

```python
user.prepare('/path/to/your/yh_client.json')  # 配置文件路径
```

注: 配置文件需自己用编辑器编辑生成, **请勿使用记事本**, 推荐使用 [notepad++](https://notepad-plus-plus.org/zh/) 或者 [sublime text](http://www.sublimetext.com/) 。

**配置文件格式如下：**

银河/国金客户端

```
{
  "user": "用户名",
  "password": "明文密码"
}

```

华泰客户端

```
{
   "user": "华泰用户名",
   "password": "华泰明文密码",
   "comm_password": "华泰通讯密码"
}

```

雪球

```
{
  "cookies": "雪球 cookies，登陆后获取，获取方式见 https://smalltool.github.io/2016/08/02/cookie/",
  "portfolio_code": "组合代码(例:ZH818559)",
  "portfolio_market": "交易市场(例:us 或者 cn 或者 hk)"
}
```

## 交易相关

有些客户端无法通过默认方法输入文本，可以通过开启 type_keys 的方法绕过，开启方式

```python
user.enable_type_keys_for_editor()
```

###  获取资金状况

```python
user.balance

# return
[{'参考市值': 21642.0,
  '可用资金': 28494.21,
  '币种': '0',
  '总资产': 50136.21,
  '股份参考盈亏': -90.21,
  '资金余额': 28494.21,
  '资金帐号': 'xxx'}]
```

### 获取持仓

```python
user.position

# return
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

### 买入

```python
user.buy('162411', price=0.55, amount=100)

# return
{'entrust_no': 'xxxxxxxx'}
```

注: 系统可以配置是否返回成交回报。如果没配的话默认返回 `{"message": "success"}`

### 卖出

```python
user.sell('162411', price=0.55, amount=100)

# return
{'entrust_no': 'xxxxxxxx'}
```


### 撤单

```python
user.cancel_entrust('buy/sell 获取的 entrust_no')

# return
{'message': 'success'}
```

### 查询当日成交

```python
user.today_trades

# return
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

### 查询当日委托

```python
user.today_entrusts

# return
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


### 查询今日可申购新股

```python
from easytrader.utils.stock import get_today_ipo_data
get_today_ipo_data()

# return
[{'stock_code': '股票代码',
  'stock_name': '股票名称',
  'price': 发行价,
  'apply_code': '申购代码'}]
```

### 一键打新

```python
user.auto_ipo()
```

### 刷新数据

```python
user.refresh()
```

### 雪球组合比例调仓 

```python
user.adjust_weight('股票代码', 目标比例)
```

例如 `user.adjust_weight('000001', 10)`是将平安银行在组合中的持仓比例调整到10%。

## 退出客户端软件

```python
user.exit()
```

## 常见问题

### 某些同花顺客户端不允许拷贝 `Grid` 数据

现在默认获取 `Grid` 数据的策略是通过剪切板拷贝，有些券商不允许这种方式，导致无法获取持仓等数据。为解决此问题，额外实现了一种通过将 `Grid` 数据存为文件再读取的策略，
使用方式如下:

```python
from easytrader import grid_strategies

user.grid_strategy = grid_strategies.Xls
```

### 通过工具栏刷新按钮刷新数据

当前的刷新数据方式是通过切换菜单栏实现，通用但是比较缓慢，可以选择通过点击工具栏的刷新按钮来刷新

```python
from easytrader import refresh_strategies

# refresh_btn_index 指的是刷新按钮在工具栏的排序，默认为第四个，根据客户端实际情况调整
user.refresh_strategy = refresh_strategies.Toolbar(refresh_btn_index=4)
```

### 无法保存对应的 xls 文件

有些系统默认的临时文件目录过长，使用 xls 策略时无法正常保存，可通过如下方式修改为自定义目录

```
user.grid_strategy_instance.tmp_folder = 'C:\\custom_folder'
```

### 如何关闭 debug 日志的输出

```python
user = easytrader.use('yh', debug=False)

```


# 编辑配置文件，运行后出现 `json` 解码报错


出现如下错误

```python
raise JSONDecodeError("Expecting value", s, err.value) from None

JSONDecodeError: Expecting value
```

请勿使用 `记事本` 编辑账户的 `json` 配置文件，推荐使用 [notepad++](https://notepad-plus-plus.org/zh/) 或者 [sublime text](http://www.sublimetext.com/)


# 引入

```python
import easytrader
```

# 设置券商类型

**银河客户端**

```python
user = easytrader.use('yh_client')
```
**华泰客户端**

```python
user = easytrader.use('ht_client')
```

**国金客户端**

```python
user = easytrader.use('gj_client') 
```

**通用同花顺客户端**


```python
user = easytrader.use('ths')
```

注: 通用同花顺客户端是指对应券商官网提供的基于同花顺修改的软件版本，类似银河的双子星(同花顺版本), 海王星(通达信版本)


# 设置账户信息

登陆账号有两种方式，`使用参数` 和 `使用配置文件`

使用通用同花顺客户端不支持自动登陆，所以无需设置，参看下文`直接连接通用同花顺客户端`

**参数登录(推荐)**

```
user.prepare(user='用户名', password='雪球、银河客户端为明文密码', comm_password='华泰通讯密码，其他券商不用')
```

**使用配置文件**

```python
user.prepare('/path/to/your/yh_client.json') // 配置文件路径
```

**注**: 使用配置文件模式, 配置文件需要自己用编辑器编辑生成, 请勿使用记事本, 推荐使用 [notepad++](https://notepad-plus-plus.org/zh/) 或者 [sublime text](http://www.sublimetext.com/)

**格式如下**

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
  "password": "华泰明文密码"
  "comm_password": "华泰通讯密码"
}

```

# 直接连接通用同花顺客户端

需要先手动登陆客户端到交易窗口，然后运用下面的代码连接交易窗口

```python
user.connect(r'客户端xiadan.exe路径') # 类似 r'C:\htzqzyb2\xiadan.exe' 
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

#### 买入:

```python
user.buy('162411', price=0.55, amount=100)
```

**return**

```python
{'entrust_no': 'xxxxxxxx'}
```

#### 卖出:

```python
user.sell('162411', price=0.55, amount=100)
```

**return**

```python
{'entrust_no': 'xxxxxxxx'}
```

#### 一键打新

```python
user.auto_ipo()
```

#### 撤单

```python
user.cancel_entrust('buy/sell 获取的 entrust_no')
```

**return**

```
{'message': '撤单申报成功'}
```


#### 当日成交

```python
user.today_trades
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

#### 当日委托

```python
user.today_entrusts
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

#### 退出客户端软件

```
user.exit()
```

### 远端服务器模式

#### 在服务器上启动服务

```python
from easytrader import server

server.run(port=1430) # 默认端口为 1430
```

#### 远程客户端调用

```python
from easytrader import remoteclient

user = remoteclient.use('使用客户端类型，可选 yh_client, ht_client 等', host='服务器ip', port='服务器端口，默认为1430')

其他用法同上
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
 python cli.py --use yh --prepare gf.json
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



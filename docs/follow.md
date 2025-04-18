# 策略跟踪 

## 跟踪 `joinquant` / `ricequant`  的模拟交易

##### 1) 初始化跟踪的 trader

这里以雪球为例, 也可以使用银河之类 `easytrader` 支持的券商

```
xq_user = easytrader.use('xq')
xq_user.prepare('xq.json')
```

##### 2) 初始化跟踪 `joinquant` / `ricequant` 的 follower

```
target = 'jq'  # joinquant
target = 'rq'  # ricequant
follower = easytrader.follower(target)
follower.login(user='rq/jq用户名', password='rq/jq密码')
```

##### 3) 连接 follower 和 trader

##### joinquant
```
follower.follow(xq_user, 'jq的模拟交易url')
```

注: jq的模拟交易url指的是对应模拟交易对应的可以查看持仓, 交易记录的页面, 类似 `https://www.joinquant.com/algorithm/live/index?backtestId=xxx`

正常会输出

![enjoy it](https://raw.githubusercontent.com/shidenggui/assets/master/easytrader/joinquant.jpg)

注: 启动后发现跟踪策略无输出，那是因为今天模拟交易没有调仓或者接收到的调仓信号过期了，默认只处理120s内的信号，想要测试的可以用下面的命令：

```python
jq_follower.follow(user, '模拟交易url',
          trade_cmd_expire_seconds=100000000000, cmd_cache=False)
```

- trade_cmd_expire_seconds 默认处理多少秒内的信号

- cmd_cache 是否读取已经执行过的命令缓存，以防止重复执行

目录下产生的 cmd_cache.pk，是用来存储历史执行过的交易指令，防止在重启程序时重复执行交易过的指令，可以通过 `follower.follow(xxx, cmd_cache=False)` 来关闭。

##### ricequant

```
follower.follow(xq_user, run_id)
```
注：ricequant的run_id即PT列表中的ID。


## 跟踪雪球的组合

##### 1) 初始化跟踪的 trader

同上

##### 2) 初始化跟踪 雪球组合 的 follower

```
xq_follower = easytrader.follower('xq')
xq_follower.login(cookies='雪球 cookies，登陆后获取，获取方式见 https://smalltool.github.io/2016/08/02/cookie/')
```

##### 3) 连接 follower 和 trader

```
xq_follower.follow(xq_user, 'xq组合ID，类似ZH123456', total_assets=100000)
```


注: 雪球组合是以百分比调仓的， 所以需要额外设置组合对应的资金额度

* 这里可以设置 total_assets, 为当前组合的净值对应的总资金额度, 具体可以参考参数说明
* 或者设置 initial_assets, 这时候总资金额度为 initial_assets * 组合净值

* 雪球额外支持 adjust_sell 参数，决定是否根据用户的实际持仓数调整卖出股票数量，解决雪球根据百分比调仓时计算出的股数有偏差的问题。当卖出股票数大于实际持仓数时，调整为实际持仓数。目前仅在银河客户端测试通过。 当 users 为多个时，根据第一个 user 的持仓数决定


#### 3. 多用户跟踪多策略

```
follower.follow(users=[xq_user, yh_user], strategies=['组合1', '组合2'], total_assets=[10000, 10000])
```

#### 4. 其它与跟踪有关的问题

使用市价单跟踪模式，目前仅支持银河

```
follower.follow(***, entrust_prop='market')
```

调整下单间隔, 默认为0s。调大可防止卖出买入时卖出单没有及时成交导致的买入金额不足

```
follower.follow(***, send_interval=30) # 设置下单间隔为 30 s
```
设置买卖时的滑点

```
follower.follow(***, slippage=0.05) # 设置滑点为 5%
```

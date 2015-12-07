# easytrader

* 进行简单的 web 股票交易
* **目前还很不完善,仅供测试**

### 支持券商

* 佣金宝

### requirements

> pip install -r requirements.txt

### 用法

#### 引入:

```python
from esaytrader import YJBTrader
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

#### 获取持仓:

```python
user.position
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

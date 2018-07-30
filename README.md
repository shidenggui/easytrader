# easytrader

[![Package](https://img.shields.io/pypi/v/easytrader.svg)](https://pypi.python.org/pypi/easytrader)
[![Travis](https://img.shields.io/travis/shidenggui/easytrader.svg)](https://travis-ci.org/shidenggui/easytrader)
[![License](https://img.shields.io/github/license/shidenggui/easytrader.svg)](https://github.com/shidenggui/easytrader/blob/master/LICENSE)

基于easytrader的二次开发，目标：可用于实战的无人值守全自动交易
取消 委托前弹窗和撤单前弹窗，可加快速度!
* 进行自动的程序化股票交易
* 支持跟踪 `joinquant`, `ricequant` 的模拟交易
* 支持跟踪 雪球组合 调仓
* 支持通用的同花顺客户端模拟操作
* 实现自动登录
* 支持通过 webserver 远程操作客户端
* 支持命令行调用，方便其他语言适配
* 支持 Python3, Linux / Win, 推荐使用 `Python3`
* 有兴趣的可以加群 `556050652` 一起讨论
* 捐助:

![微信](http://7xqo8v.com1.z0.glb.clouddn.com/wx.png?imageView2/1/w/300/h/300)             ![支付宝](http://7xqo8v.com1.z0.glb.clouddn.com/zhifubao2.png?imageView2/1/w/300/h/300)


## 公众号

扫码关注“易量化”的微信公众号，不定时更新一些个人文章及与大家交流

![](http://7xqo8v.com1.z0.glb.clouddn.com/easy_quant_qrcode.jpg?imageView2/1/w/300/h/300)


**开发环境** : `Ubuntu 16.04` / `Python 3.5`

### 相关

[获取新浪免费实时行情的类库: easyquotation](https://github.com/shidenggui/easyquotation)

[简单的股票量化交易框架 使用 easytrader 和 easyquotation](https://github.com/shidenggui/easyquant)

### 支持券商

* 银河客户端, 须在 `windows` 平台下载 `银河双子星` 客户端
* 华泰客户端(网上交易系统（专业版Ⅱ）)
* 国金客户端(全能行证券交易终端PC版)
* 其他券商通用同花顺客户端(需要手动登陆)

注: 现在有些新的同花顺客户端对拷贝剪贴板数据做了限制，我在 [issue](https://github.com/shidenggui/easytrader/issues/272) 里提供了几个券商老版本的下载地址。


### 实盘易

如果有对其他券商或者通达信版本的需求，可以查看 [实盘易](http://www.iguuu.com/e?x=19828)

### 模拟交易

* 雪球组合 by @[haogefeifei](https://github.com/haogefeifei)（[说明](doc/xueqiu.md)）

### 使用文档

[中文文档](http://easytrader.readthedocs.io/zh/master/)

### 其他

[软件实现原理](http://www.jisilu.cn/question/42707)

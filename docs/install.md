### requirements

银河可以直接自动登录, 广发的自动登录需要安装 tesseract：

* `tesseract` : 非 `pytesseract`, 需要单独安装, [地址](https://github.com/tesseract-ocr/tesseract/wiki),保证在命令行下 `tesseract` 可用

##### 银河客户端设置

* 系统设置 > 快速交易: 关闭所有的买卖，撤单等确认选项
* 系统设置 > 界面设置: 界面不操作超时时间设为 0
* 系统设置 > 交易设置: 默认买入价格/买入数量/卖出价格/卖出数量 都设置为 空


### 安装

```shell
pip install easytrader
```

注： `Windows` 用户 `pip` 安装时会提示 `No module named xxx`, 请使用 `pip install xxx` 安装对应缺失的 `module`, 然后再重新 `pip install easytrader`, 可以参考此文档 [INSTALL4Windows.md](other/INSTALL4Windows.md)

### 升级

```shell
pip install easytrader -U
```



# 如何关闭 debug 日志的输出

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

### 其他

[软件实现原理](http://www.jisilu.cn/question/42707)

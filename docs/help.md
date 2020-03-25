# 无法保存对应的 xls 文件

有些系统默认的临时文件目录过长，使用 xls 策略时无法正常保存，可通过如下方式修改为自定义目录

```
user.grid_strategy_instance.tmp_folder = 'C:\\custom_folder'
```

# 某些券商客户端无法输入文本

有些客户端无法通过 set_edit_text 方法输入内容，可以通过使用 type_keys 方法绕过，开启方式

```
user.enable_type_keys_for_editor()
```

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

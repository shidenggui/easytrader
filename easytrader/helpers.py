# coding: utf-8
import os
import json


def file2dict(path):
    with open(path) as f:
        return json.load(f)


def get_stock_type(stock_code):
    """判断股票ID对应的证券市场
    :param stock_code:股票ID
    :return 'sh' or 'sz'"""
    if str(stock_code).startswith(('5', '6', '9')):
        return 'sh'
    return 'sz'


def recognize_verify_code(image_path):
    """识别验证码，返回识别后的字符串，使用 tesseract 实现
    :param image_path
    :return recognized verify code string"""
    # 调用 tesseract 识别
    # ubuntu 15.10 无法识别的手动 export TESSDATA_PREFIX
    system_result = os.system('tesseract {} result -psm 7'.format(image_path))
    system_success = 0
    if system_result != system_success:
        os.system('export TESSDATA_PREFIX="/usr/share/tesseract-ocr/tessdata/"; tesseract {} result -psm 7'.format(image_path))

    # 获取识别的验证码
    verify_code_result = 'result.txt'
    try:
        with open(verify_code_result) as f:
            recognized_code = f.readline()
    except UnicodeDecodeError:
        with open(verify_code_result, encoding='gbk') as f:
            recognized_code = f.readline()
    # 移除空格和换行符
    return_index = -1
    recognized_code = recognized_code.replace(' ', '')[:return_index]

    os.remove(verify_code_result)

    return recognized_code

# coding: utf-8
import os
import json
import subprocess
import sys
import uuid
from logbook import Logger, StreamHandler

StreamHandler(sys.stdout).push_application()
log = Logger(os.path.basename(__file__))


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


def recognize_verify_code(image_path, broker='ht'):
    """识别验证码，返回识别后的字符串，使用 tesseract 实现
    :param image_path
    :return recognized verify code string"""
    verify_code_tool = 'getcode_jdk1.5.jar' if broker == 'ht' else 'yjb_verify_code.jar guojin'
    # 检查 java 环境，若有则调用 jar 包处理 (感谢空中园的贡献)
    out_put = subprocess.getoutput('java -version')
    log.debug('java detect result: %s' % out_put)
    if out_put.find('java version') is not -1:
        out_put = subprocess.getoutput(
            'java -jar %s %s' % (os.path.join(os.path.dirname(__file__), 'thirdlibrary', verify_code_tool), image_path))
        log.debug('recognize output: %s' % out_put)
        verify_code_start = -4
        return out_put[verify_code_start:]
    # 调用 tesseract 识别
    # ubuntu 15.10 无法识别的手动 export TESSDATA_PREFIX
    system_result = os.system('tesseract {} result -psm 7'.format(image_path))
    system_success = 0
    if system_result != system_success:
        os.system(
            'export TESSDATA_PREFIX="/usr/share/tesseract-ocr/tessdata/"; tesseract {} result -psm 7'.format(image_path))

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


def get_mac():
    # 获取mac地址 link: http://stackoverflow.com/questions/28927958/python-get-mac-address
    return ("".join(c + "-" if i % 2 else c for i, c in enumerate(hex(
            uuid.getnode())[2:].zfill(12)))[:-1]).upper()

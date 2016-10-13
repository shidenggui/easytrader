# coding: utf-8
from __future__ import division

import datetime
import json
import os
import re
import ssl
import sys
import uuid

import six
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

from .log import log

if six.PY2:
    from io import open


class EntrustProp(object):
    Limit = 'limit'
    Market = 'market'


class Ssl3HttpAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)


def file2dict(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def get_stock_type(stock_code):
    """判断股票ID对应的证券市场
    匹配规则
    ['50', '51', '60', '90', '110'] 为 sh
    ['00', '13', '18', '15', '16', '18', '20', '30', '39', '115'] 为 sz
    ['5', '6', '9'] 开头的为 sh， 其余为 sz
    :param stock_code:股票ID, 若以 'sz', 'sh' 开头直接返回对应类型，否则使用内置规则判断
    :return 'sh' or 'sz'"""
    assert type(stock_code) is str, 'stock code need str type'
    if stock_code.startswith(('sh', 'sz')):
        return stock_code[:2]
    if stock_code.startswith(('50', '51', '60', '73', '90', '110', '113', '132', '204', '78')):
        return 'sh'
    if stock_code.startswith(('00', '13', '18', '15', '16', '18', '20', '30', '39', '115', '1318')):
        return 'sz'
    if stock_code.startswith(('5', '6', '9')):
        return 'sh'
    return 'sz'


def ht_verify_code_new(image_path):
    """显示图片，人肉读取，手工输入"""

    from PIL import Image

    img = Image.open(image_path)
    img.show()

    # 关闭图片后输入答案
    s = input('input the pics answer :')

    return s


def recognize_verify_code(image_path, broker='ht'):
    """识别验证码，返回识别后的字符串，使用 tesseract 实现
    :param image_path: 图片路径
    :param broker: 券商 ['ht', 'yjb', 'gf', 'yh']
    :return recognized: verify code string"""

    if broker == 'ht':
        return ht_verify_code_new(image_path)
    elif broker == 'yjb':
        return detect_yjb_result(image_path)
    elif broker == 'gf':
        return detect_gf_result(image_path)
    elif broker == 'yh':
        return detect_yh_result(image_path)
    # 调用 tesseract 识别
    return default_verify_code_detect(image_path)


def detect_ht_result(image_path):
    code = detect_verify_code_by_java(image_path, 'ht')
    if not code:
        return default_verify_code_detect(image_path)
    return code


def detect_yjb_result(image_path):
    code = detect_verify_code_by_java(image_path, 'yjb')
    if not code:
        return default_verify_code_detect(image_path)
    return code


def detect_verify_code_by_java(image_path, broker):
    jars = {
        'ht': ('getcode_jdk1.5.jar', ''),
        'yjb': ('yjb_verify_code.jar', 'guojin')
    }
    verify_code_tool, param = jars[broker]
    # 检查 java 环境，若有则调用 jar 包处理 (感谢空中园的贡献)
    # noinspection PyGlobalUndefined
    if six.PY2:
        if sys.platform == 'win32':
            from subprocess import PIPE, Popen, STDOUT

            def getoutput(cmd, input=None, cwd=None, env=None):
                pipe = Popen(cmd, shell=True, cwd=cwd, env=env, stdout=PIPE, stderr=STDOUT)
                (output, err_out) = pipe.communicate(input=input)
                return output.decode().rstrip('\r\n')
        else:
            import commands
            getoutput = commands.getoutput
    else:
        from subprocess import getoutput
    out_put = getoutput('java -version')
    log.debug('java detect result: %s' % out_put)
    if out_put.find('java version') != -1 or out_put.find('openjdk') != -1:
        tool_path = os.path.join(os.path.dirname(__file__), 'thirdlibrary', verify_code_tool)
        out_put = getoutput('java -jar "{}" {} {}'.format(tool_path, param, image_path))
        log.debug('recognize output: %s' % out_put)
        verify_code_start = -4
        return out_put[verify_code_start:]


def default_verify_code_detect(image_path):
    from PIL import Image
    img = Image.open(image_path)
    return invoke_tesseract_to_recognize(img)


def detect_gf_result(image_path):
    from PIL import ImageFilter, Image
    img = Image.open(image_path)
    if hasattr(img, "width"):
        width, height = img.width, img.height
    else:
        width, height = img.size
    for x in range(width):
        for y in range(height):
            if img.getpixel((x, y)) < (100, 100, 100):
                img.putpixel((x, y), (256, 256, 256))
    gray = img.convert('L')
    two = gray.point(lambda p: 0 if 68 < p < 90 else 256)
    min_res = two.filter(ImageFilter.MinFilter)
    med_res = min_res.filter(ImageFilter.MedianFilter)
    for _ in range(2):
        med_res = med_res.filter(ImageFilter.MedianFilter)
    return invoke_tesseract_to_recognize(med_res)


def detect_yh_result(image_path):
    from PIL import Image

    img = Image.open(image_path)

    brightness = list()
    for x in range(img.width):
        for y in range(img.height):
            (r, g, b) = img.getpixel((x, y))
            brightness.append(r + g + b)
    avg_brightness = sum(brightness) // len(brightness)

    for x in range(img.width):
        for y in range(img.height):
            (r, g, b) = img.getpixel((x, y))
            if ((r + g + b) > avg_brightness / 1.5) or (y < 3) or (y > 17) or (x < 5) or (x > (img.width - 5)):
                img.putpixel((x, y), (256, 256, 256))

    return invoke_tesseract_to_recognize(img)


def invoke_tesseract_to_recognize(img):
    import pytesseract
    try:
        res = pytesseract.image_to_string(img)
    except FileNotFoundError:
        raise Exception('tesseract 未安装，请至 https://github.com/tesseract-ocr/tesseract/wiki 查看安装教程')
    valid_chars = re.findall('[0-9a-z]', res, re.IGNORECASE)
    return ''.join(valid_chars)


def get_mac():
    # 获取mac地址 link: http://stackoverflow.com/questions/28927958/python-get-mac-address
    return ("".join(c + "-" if i % 2 else c for i, c in enumerate(hex(
        uuid.getnode())[2:].zfill(12)))[:-1]).upper()


def grep_comma(num_str):
    return num_str.replace(',', '')


def str2num(num_str, convert_type='float'):
    num = float(grep_comma(num_str))
    return num if convert_type == 'float' else int(num)


def get_30_date():
    """
    获得用于查询的默认日期, 今天的日期, 以及30天前的日期
    用于查询的日期格式通常为 20160211
    :return:
    """
    now = datetime.datetime.now()
    end_date = now.date()
    start_date = end_date - datetime.timedelta(days=30)
    return start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d")


def get_today_ipo_data():
    """
    查询今天可以申购的新股信息
    :return: 今日可申购新股列表 apply_code申购代码 price发行价格
    """

    import random
    import json
    import datetime
    import requests

    agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0'
    send_headers = {
        'Host': 'xueqiu.com',
        'User-Agent': agent,
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'deflate',
        'Cache-Control': 'no-cache',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://xueqiu.com/hq',
        'Connection': 'keep-alive'
    }

    sj = random.randint(1000000000000, 9999999999999)
    home_page_url = 'https://xueqiu.com'
    ipo_data_url = "https://xueqiu.com/proipo/query.json?column=symbol,name,onl_subcode,onl_subbegdate,actissqty,onl" \
                   "_actissqty,onl_submaxqty,iss_price,onl_lotwiner_stpub_date,onl_lotwinrt,onl_lotwin_amount,stock_" \
                   "income&orderBy=onl_subbegdate&order=desc&stockType=&page=1&size=30&_=%s" % (str(sj))

    session = requests.session()
    session.get(home_page_url, headers=send_headers)  # 产生cookies
    ipo_response = session.post(ipo_data_url, headers=send_headers)

    json_data = json.loads(ipo_response.text)
    today_ipo = []

    for line in json_data['data']:
        # if datetime.datetime(2016, 9, 14).ctime()[:10] == line[3][:10]:
        if datetime.datetime.now().ctime()[:10] == line[3][:10]:
            today_ipo.append({
                'stock_code': line[0],
                'stock_name': line[1],
                'apply_code': line[2],
                'price': line[7]
            })

    return today_ipo

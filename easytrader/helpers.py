# -*- coding: utf-8 -*-
import datetime
import json
import random
import re

import requests

from . import exceptions


def parse_cookies_str(cookies):
    """
    parse cookies str to dict
    :param cookies: cookies str
    :type cookies: str
    :return: cookie dict
    :rtype: dict
    """
    cookie_dict = {}
    for record in cookies.split(";"):
        key, value = record.strip().split("=", 1)
        cookie_dict[key] = value
    return cookie_dict


def file2dict(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_stock_type(stock_code):
    """判断股票ID对应的证券市场
    匹配规则
    ['50', '51', '60', '90', '110'] 为 sh
    ['00', '13', '18', '15', '16', '18', '20', '30', '39', '115'] 为 sz
    ['5', '6', '9'] 开头的为 sh， 其余为 sz
    :param stock_code:股票ID, 若以 'sz', 'sh' 开头直接返回对应类型，否则使用内置规则判断
    :return 'sh' or 'sz'"""
    stock_code = str(stock_code)
    if stock_code.startswith(("sh", "sz")):
        return stock_code[:2]
    if stock_code.startswith(
        ("50", "51", "60", "73", "90", "110", "113", "132", "204", "78")
    ):
        return "sh"
    if stock_code.startswith(
        ("00", "13", "18", "15", "16", "18", "20", "30", "39", "115", "1318")
    ):
        return "sz"
    if stock_code.startswith(("5", "6", "9")):
        return "sh"
    return "sz"


def recognize_verify_code(image_path, broker="ht"):
    """识别验证码，返回识别后的字符串，使用 tesseract 实现
    :param image_path: 图片路径
    :param broker: 券商 ['ht', 'yjb', 'gf', 'yh']
    :return recognized: verify code string"""

    if broker == "gf":
        return detect_gf_result(image_path)
    if broker in ["yh_client", "gj_client"]:
        return detect_yh_client_result(image_path)
    # 调用 tesseract 识别
    return default_verify_code_detect(image_path)


def detect_yh_client_result(image_path):
    """封装了tesseract的识别，部署在阿里云上，服务端源码地址为： https://github.com/shidenggui/yh_verify_code_docker"""
    api = "http://yh.ez.shidenggui.com:5000/yh_client"
    with open(image_path, "rb") as f:
        rep = requests.post(api, files={"image": f})
    if rep.status_code != 201:
        error = rep.json()["message"]
        raise exceptions.TradeError("request {} error: {}".format(api, error))
    return rep.json()["result"]


def input_verify_code_manual(image_path):
    from PIL import Image

    image = Image.open(image_path)
    image.show()
    code = input(
        "image path: {}, input verify code answer:".format(image_path)
    )
    return code


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
    gray = img.convert("L")
    two = gray.point(lambda p: 0 if 68 < p < 90 else 256)
    min_res = two.filter(ImageFilter.MinFilter)
    med_res = min_res.filter(ImageFilter.MedianFilter)
    for _ in range(2):
        med_res = med_res.filter(ImageFilter.MedianFilter)
    return invoke_tesseract_to_recognize(med_res)


def invoke_tesseract_to_recognize(img):
    import pytesseract

    try:
        res = pytesseract.image_to_string(img)
    except FileNotFoundError:
        raise Exception(
            "tesseract 未安装，请至 https://github.com/tesseract-ocr/tesseract/wiki 查看安装教程"
        )
    valid_chars = re.findall("[0-9a-z]", res, re.IGNORECASE)
    return "".join(valid_chars)


def grep_comma(num_str):
    return num_str.replace(",", "")


def str2num(num_str, convert_type="float"):
    num = float(grep_comma(num_str))
    return num if convert_type == "float" else int(num)


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

    agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0"
    send_headers = {
        "Host": "xueqiu.com",
        "User-Agent": agent,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "deflate",
        "Cache-Control": "no-cache",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://xueqiu.com/hq",
        "Connection": "keep-alive",
    }

    timestamp = random.randint(1000000000000, 9999999999999)
    home_page_url = "https://xueqiu.com"
    ipo_data_url = (
        "https://xueqiu.com/proipo/query.json?column=symbol,name,onl_subcode,onl_subbegdate,actissqty,onl"
        "_actissqty,onl_submaxqty,iss_price,onl_lotwiner_stpub_date,onl_lotwinrt,onl_lotwin_amount,stock_"
        "income&orderBy=onl_subbegdate&order=desc&stockType=&page=1&size=30&_=%s"
        % (str(timestamp))
    )

    session = requests.session()
    session.get(home_page_url, headers=send_headers)  # 产生cookies
    ipo_response = session.post(ipo_data_url, headers=send_headers)

    json_data = json.loads(ipo_response.text)
    today_ipo = []

    for line in json_data["data"]:
        if datetime.datetime.now().strftime("%a %b %d") == line[3][:10]:
            today_ipo.append(
                {
                    "stock_code": line[0],
                    "stock_name": line[1],
                    "apply_code": line[2],
                    "price": line[7],
                }
            )

    return today_ipo

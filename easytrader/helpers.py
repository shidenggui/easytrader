# coding: utf-8
import json

def file2dict(path):
    with open(path) as f:
        return json.load(f)

def get_stock_type(stock_code):
    if str(stock_code).startswith('5', '6', '9'):
        return 'SH'
    return 'SZ'


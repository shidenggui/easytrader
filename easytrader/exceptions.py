# -*- coding: utf-8 -*-
"""
Exceptions
"""


class TradeError(IOError):
    pass


class NotLoginError(Exception):
    def __init__(self, result=None):
        super(NotLoginError, self).__init__()
        self.result = result

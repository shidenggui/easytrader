# -*- coding: utf-8-*-
import easytrader
import os
import sys
import time
import datetime
import logbook
from logbook import Logger, StreamHandler, FileHandler

class AutoTrade(object):
    def __init__(self):
        self.user = easytrader.use('yh')
        self.user.prepare('yh.json')
        self.user.balance

def main():
    autotrade = AutoTrade()

if __name__ == "__main__":
    main()

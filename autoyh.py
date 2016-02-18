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
        print(self.user.balance)
        self.user.fundpurchase('161812', 100)
        #self.user.fundredemption('161812', 1000)

def main():
    autotrade = AutoTrade()

if __name__ == "__main__":
    main()

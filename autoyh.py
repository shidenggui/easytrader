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
        #self.user.fundpurchase('161812', 100)
        #self.user.fundredemption('161812', 1000)
        #self.user.fundmerge('161812', 100)
        #self.user.fundsubscribe('161812', 100)
        #print(self.user.entrust)
        #print(self.user.position)

def main():
    autotrade = AutoTrade()

if __name__ == "__main__":
    main()

# -*- coding: utf-8-*-
import easytrader
import os
import sys
import time
import datetime
import logbook
from logbook import Logger, StreamHandler, FileHandler

class AutoGf(object):
    def __init__(self):
        self.user = easytrader.use('gf')
        self.user.prepare('gf.json')

    def work(self):
        print(self.user.balance)
        print(self.user.position)
        print(self.user.nxbQueryPrice('878002'))
        data = self.user.getStockQuotation('000001')
        print(data)
        #data = self.user.fund_purchase('502010', price=700)
        #print(data)
        #data = self.user.fund_merge('502010', amount=100)
        #data = self.user.fund_split('502010', amount=100)
        #self.user.sell('601398', 4.25, amount=100) 
        #print(self.user.entrust)
        #print(self.user.cancel_entrust('2859'))

def main():
    autoq = AutoGf()
    autoq.work()

if __name__ == "__main__":
    main()

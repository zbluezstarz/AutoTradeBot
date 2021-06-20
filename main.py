import sys
import os
import time
import pyupbit

from library import coin_api
from library.crypto_currency import *
#from config import config
#from db import db
from log import logging_api


#from PyQt5.QtWidgets import *
#from PyQt5 import uic
#from PyQt5.QtCore import *

#form_class = uic.loadUiType("MainWindow.ui")[0]




'''

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.btn_clicked)
        self.isRunning = False

        
        self.val_search_day = 3
        self.now = datetime.datetime.today()
        self.today_string = str(self.now.year) + (str(self.now.month)).zfill(2) + (str(self.now.day)).zfill(2)


        self.coin_values = dict()
        self.now = datetime.datetime.today()
        self.coin_values_filename = "coin_values_filename.txt"
        #self.coin_values_filename = self.today_string + ".txt"
        self.trade_value_top_coin_name = []

        if os.path.isfile(self.coin_values_filename) == False:
            self.update_flag = True
        else:
            with open(self.coin_values_filename) as file:
                line = file.readline().strip()
                if line != self.today_string:
                    self.update_flag = True
                else:
                    self.update_flag = False

        if self.update_flag == True:
            self.count = 1
            for coin_name in self.coin_names:
                print(self.count)
                self.count += 1
                df = pyupbit.get_ohlcv(ticker=coin_name['market'])  # count=val_search_day)
                # print(df.iloc[-2]['value'])
                self.coin_values[coin_name['market']] = df.iloc[-2]['value']

            # print(coin_values)
            self.coin_values_reverse = sorted(self.coin_values.items(), reverse=True, key=lambda item: item[1])
            # print(coin_values_reverse)

            self.trade_value_top = self.coin_values_reverse[:self.max_num]
            # print(len(trade_value_top), trade_value_top)

            for i in range(self.max_num):
                self.trade_value_top_coin_name.append(self.trade_value_top[i][0])
            # print(trade_value_top)
            print(self.trade_value_top_coin_name)
            file = open(self.coin_values_filename, 'a')
            file.write(self.today_string + "\n")
            file.write(' '.join(self.trade_value_top_coin_name))
            file.close()
        else:
            with open(self.coin_values_filename) as file:
                lines = file.readlines()
                self.trade_value_top_coin_name = lines[1].split(" ")
                print(self.trade_value_top_coin_name)

        self.now = datetime.datetime.now()
        self.mid = datetime.datetime(self.now.year, self.now.month, self.now.day) + datetime.timedelta(1)


        self.log = ""
        self.count = 0

        self.timer = QTimer(self)
        self.timer.start(10000)
        self.timer.timeout.connect(self.timeout)

    def btn_clicked(self):
        if self.isRunning == True:
            self.isRunning = False
        else:
            self.isRunning = True

        print(self.isRunning)

    def timeout(self):
        #while True:

        try:
            if self.isRunning == True:
                self.file = open("LOG_" + self.today_string + ".txt", 'a')
                for ticker in self.trade_value_top_coin_name:
                    # print(upbit.get_balance(ticker))
                    self.target_price = coin_api.get_target_price(ticker)
                    self.now = datetime.datetime.now()
                    if self.mid < self.now < self.mid + datetime.timedelta(seconds=60):
                        print("Enter Midnight~~")
                        self.targetPrice = coin_api.get_target_price(ticker)
                        self.mid = datetime.datetime(self.now.year, self.now.month, self.now.day) + datetime.timedelta(1)
                        self.ma5 = coin_api.get_yesterday_ma5(ticker)
                        coin_api.sell_crypto_currency(self.upbit, ticker)

                    self.current_price = pyupbit.get_current_price(ticker)
                    self.ma5 = coin_api.get_yesterday_ma5(ticker)
                    self.log = "{0:<12}".format(ticker) + '\t' + "{0:>15}".format(self.target_price) + "{0:>15}".format(
                        self.current_price)
                    if (self.current_price > self.target_price) and (self.current_price > self.ma5):
                        coin_api.buy_crypto_currency(self.upbit, ticker)
                        self.log += ("Buy" + ticker)

                    self.file.write(self.log + "\n")
                    # print(log)
                    time.sleep(0.2)
                self.file.close()
            else:
                pass

        except:
            print("Error")
            self.file.close()

        print("========================================")
        #time.sleep(10)
        # count += 1
        # print(count)
'''

#app = QApplication(sys.argv)
#window = MyWindow()
#window.show()
crypto = CryptoCurrency()
#app.exec_()
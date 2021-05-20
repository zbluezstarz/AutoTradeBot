import sys
import os
import pyupbit
import datetime

with open("../key.txt") as f:
    lines = f.readlines()
    acc_key = lines[0].strip()
    sec_key = lines[1].strip()

max_num = 20
val_search_day = 3

upbit = pyupbit.Upbit(acc_key, sec_key)

#print(pyupbit.get_ohlcv("KRW-BTC"))

coin_names = pyupbit.fetch_market()
#print(coin_names)

coin_values = dict()
now = datetime.datetime.today()
coin_values_filename = str(now.year) + (str(now.month)).zfill(2) + (str(now.day)).zfill(2) + ".txt"

trade_value_top_coin_name = []

if os.path.isfile(coin_values_filename) == False:
    count = 1
    for coin_name in coin_names:
        print(count)
        count += 1
        df = pyupbit.get_ohlcv(ticker=coin_name['market'])#count=val_search_day)
        #print(df.iloc[-2]['value'])
        coin_values[coin_name['market']] = df.iloc[-2]['value']

    #print(coin_values)
    coin_values_reverse = sorted(coin_values.items(), reverse=True, key=lambda item: item[1])
    #print(coin_values_reverse)

    trade_value_top = coin_values_reverse[:max_num]
    #print(len(trade_value_top), trade_value_top)

    for i in range(max_num):
        trade_value_top_coin_name.append(trade_value_top[i][0])
    #print(trade_value_top)
    print(trade_value_top_coin_name)
    file = open(coin_values_filename, 'a')
    file.write(' '.join(trade_value_top_coin_name))
    file.close()
else:
    with open(coin_values_filename) as file:
        lines = file.readlines()
        trade_value_top_coin_name = lines[0].split(" ")
        print(trade_value_top_coin_name)
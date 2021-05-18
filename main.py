import sys
import pyupbit

with open("../key.txt") as f:
    lines = f.readlines()
    acc_key = lines[0].strip()
    sec_key = lines[1].strip()

max_num = 20
val_search_day = 3

upbit = pyupbit.Upbit(acc_key, sec_key)

print(pyupbit.get_ohlcv("KRW-BTC"))

coin_names = pyupbit.fetch_market()
print(coin_names)

coin_values = dict()
count = 1
print(coin_values)
for coin_name in coin_names:
    print(count)
    count += 1
    df = pyupbit.get_ohlcv(ticker=coin_name['market'])#count=val_search_day)
    #print(df.iloc[-2]['value'])
    coin_values[coin_name['market']] = df.iloc[-2]['value']


#print(coin_values)
sorted(coin_values.items(), key=lambda x: x[1], reverse=True)
coin_values_reverse = sorted(coin_values.items(), reverse=True, key=lambda item: item[1])
#print(coin_values_reverse)

trade_value_top = coin_values_reverse[:max_num]
#print(len(trade_value_top), trade_value_top)
trade_value_top_coin_name = []
for i in range(max_num):
    trade_value_top_coin_name.append(trade_value_top[i][0])
#print(trade_value_top)
print(trade_value_top_coin_name)
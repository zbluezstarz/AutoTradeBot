import time

import pyupbit
import datetime
import pandas


def get_exchange_api():
    return pyupbit


def create_exchange_instance(acc_key, sec_key):
    return get_exchange_api().Upbit(acc_key, sec_key)


def connect_exchange(key_name):
    with open(key_name) as f:
        lines = f.readlines()
        acc_key = lines[0].strip()
        sec_key = lines[1].strip()
        exchange = create_exchange_instance(acc_key, sec_key)
        return exchange


def get_exchane_price_update_time(exchange_api):
    df = exchange_api.get_ohlcv("KRW-BTC", interval="day", count=1)
    start_time = df.index[0]
    return start_time


def get_moving_average(exchange_api, ticker, day_num):
    df = exchange_api.get_ohlcv(ticker, interval="day", count=day_num)
    ma = df['close'].rolling(day_num).mean().iloc[-1]
    return ma


def get_current_price(exchange_api, ticker):
    return exchange_api.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]


def get_balance(exchange, currency):
    balances = exchange.get_balances()
    for b in balances:
        if b['currency'] == currency:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0.0
    return 0.0


def write_target_tickers_in_file(file_name, target_tickers):
    file_now = datetime.datetime.now()
    file = open(file_name, 'w')
    file.write(str(file_now) + "\n")
    file.write(' '.join(target_tickers))
    file.close()


def get_custom_1days_ohlcv(exchange_api, ticker, end_day_str, end_hours_int, day_num):
    to_str = datetime.datetime.strptime(end_day_str, '%Y%m%d') + datetime.timedelta(hours=end_hours_int + 1)
    hours_unit = 24
    remain_day_num = day_num
    df = exchange_api.get_ohlcv(ticker, interval="minute60", count=1 * hours_unit, to=to_str)
    remain_day_num -= 1
    to_str -= datetime.timedelta(days=1)

    while remain_day_num > 0:
        print(remain_day_num)
        new_1day_df = exchange_api.get_ohlcv(ticker, interval="minute60", count=1 * hours_unit, to=to_str)
        if new_1day_df is None:
            continue
        if new_1day_df.shape[0] % 24 != 0:
            print("== sample is shortage")
            return None, None
        df = pandas.concat([new_1day_df, df])
        remain_day_num -= 1
        to_str -= datetime.timedelta(days=1)
        time.sleep(0.1)

    index = []
    data = []

    if ((day_num * hours_unit) > df.shape[0]) or df.shape[0] % 24 != 0:
        print("** sample is shortage")
        return None, None

    for i in range(day_num):
        idx_start = i * hours_unit
        idx_end = (i+1) * hours_unit

        data.append({
            'open': df['open'][idx_start],
            'high': max(list((df['high'][idx_start:idx_end]).values)),
            'low': min(list((df['low'][idx_start:idx_end]).values)),
            'close': df['close'][idx_end-1],
            'volume': sum(list((df['volume'][idx_start:idx_end]).values)),
            'value': sum(list((df['value'][idx_start:idx_end]).values)),
            'vol_half1': sum(list((df['volume'][idx_start:idx_start+int(hours_unit/2)]).values)),
            'vol_half2': sum(list((df['volume'][idx_start + int(hours_unit/2):idx_end]).values)),
            'val_half1': sum(list((df['value'][idx_start:idx_start + int(hours_unit / 2)]).values)),
            'val_half2': sum(list((df['value'][idx_start + int(hours_unit / 2):idx_end]).values)),
            'profit': (df['close'][idx_end-1] - df['open'][idx_start]) / df['open'][idx_start] * 100.0,
            'pro_half1': (df['close'][idx_end-int(hours_unit / 2) - 1] - df['open'][idx_start]) /
             df['open'][idx_start] * 100.0,
            'pro_half2': (df['close'][idx_end-1] - df['close'][idx_end-int(hours_unit / 2) - 1]) /
             df['open'][idx_start] * 100.0

            }
        )
        index.append(df.index[idx_end-1])
    new_df = pandas.DataFrame(data, index=index)
    return df, new_df


if __name__ == "__main__":
    pass

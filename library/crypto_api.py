import pyupbit
import datetime


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


if __name__ == "__main__":
    pass

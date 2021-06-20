import pyupbit

target_ratio = 0.5
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

def buy_crypto_currency(market, ticker):
    krw = market.get_balance() / 5
    orderbook = pyupbit.get_orderbook(ticker)

    bids_asks = orderbook[0]['orderbook_units']
    print(type(bids_asks))

    sell_price = bids_asks[0]['ask_price']
    unit = krw / float(sell_price)
    #market.buy_market_order(ticker, unit)
    print(market.buy_market_order(ticker, krw))
    print("Buy", ticker, krw)

def get_target_price(ticker):
    df = pyupbit.get_ohlcv(ticker)
    yesterday = df.iloc[-2]

    today_open = yesterday['close']
    yesterday_high = yesterday['high']
    yesterday_low = yesterday['low']
    target = today_open + (yesterday_high - yesterday_low) * target_ratio
    return target

def sell_crypto_currency(market, ticker):
    unit = market.get_balance(ticker)
    if unit > 0.0:
        market.sell_market_order(ticker, unit)

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
                return 0
    return 0

if __name__ == "__main__":
    pass
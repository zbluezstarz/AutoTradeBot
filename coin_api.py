import pyupbit

target_ratio = 0.5
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

def get_yesterday_ma5(ticker):
    df = pyupbit.get_ohlcv(ticker)
    close = df['close']
    ma = close.rolling(window=5).mean()
    return ma[-2]

if __name__ == "__main__":
    pass
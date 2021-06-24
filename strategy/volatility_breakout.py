from log.logging_api import *
from library.coin_api import *
import datetime
import time
import os


class VolatilityBreakout:
    def __init__(self, exchange, api):
        self.name = "VolatilityBreakout"
        self.is_running = False
        self.exchange_api = api
        self.exchange = exchange
        self.k = 0.5
        self.moving_average_day = 5
        self.max_ticker_num = 20
        self.each_ticker_value = 10000.0
        self.loss_cut = -60.0
        self.profit_cut = 50.0
        self.target_tickers = []
        self.target_tickers_file = "target_tickers.txt"

        logger.info("Create VolatilityBreakout Strategy Object")

    def set_parameters(self):
        logger.debug("Get " + self.name + " Parameters from file")
        self.k = 0.5
        self.moving_average_day = 5
        self.max_ticker_num = 20
        self.each_ticker_value = 10000.0
        self.loss_cut = -70.0
        self.profit_cut = 50.0
        logger.info("Set " + self.name + " Parameters")

    def get_start_end_time(self):
        start_time = get_exchane_price_update_time(self.exchange_api)
        end_time = start_time + datetime.timedelta(days=1)
        logger.info("Start " + self.name + " Trading : " + str(start_time) + " ~ " + str(end_time))
        return start_time, end_time

    def is_change_target_ticker(self):
        pass

    def execute_buy_strategy(self, target_ticker, remain_buy_list):
        target_price = self.get_target_price(target_ticker, self.k)
        ma = get_moving_average(self.exchange_api, target_ticker, self.moving_average_day)
        # logger.debug("MA: " + str(ma))
        current_price = get_current_price(self.exchange_api, target_ticker)
        krw = get_balance(self.exchange, "KRW")
        logger.debug("{0:<9}".format(target_ticker) + " | " +
                     "{0:<9}".format(str(int(target_price))) + ":" +
                     "{0:<9}".format(str(int(current_price))) + ", " +
                     "{0:<9}".format(str(int(krw)))
                     )
        if target_price < current_price and ma < current_price:
            if krw > 5000:
                result = self.exchange.buy_market_order(target_price, self.each_ticker_value * 0.9995)
                if 'error' not in result.keys():
                    remain_buy_list.remove(target_ticker)
                logger.debug(target_ticker + "," + target_price + ", Buy " + str(result))



    def execute_sell_strategy(self, remain_buy_list):
        balances = self.exchange.get_balances()
        for balance in balances:
            logger.debug(balance)
            currency = balance['currency']
            if currency == 'KRW':
                continue
            else:
                ticker = balance['unit_currency'] + '-' + currency
                current_price = float(self.exchange_api.get_current_price(ticker))
                logger.debug(currency + " = " + str(current_price))
                avg_buy_price = float(balance['avg_buy_price'])
                profit_rate = ((current_price - avg_buy_price) / avg_buy_price) * 100.0
                logger.debug(ticker + " >>> " + str(profit_rate))
                if (profit_rate < self.loss_cut) or (profit_rate > self.profit_cut):
                    result = self.exchange.sell_market_order(ticker, balance['balance'])
                    if 'error' not in result.keys():
                        remain_buy_list.append(ticker)
                    logger.debug("Sell " + ticker + ", " + balance['balance'] + " " + str(result))

    def execute_turn_end_process(self):
        logger.debug("Sell All Tickers")
        balances = self.exchange.get_balances()
        # print(balances)
        for balance in balances:
            logger.debug(balance)
            currency = balance['currency']
            # print(currency)
            if currency == 'KRW':
                continue
            else:
                ticker = balance['unit_currency'] + '-' + currency
                # print(currency + " = " + str(self.exchange_api.get_current_price(ticker)))
                result = self.exchange.sell_market_order(ticker, balance['balance'])
                logger.debug("Sell " + ticker + ", " + balance['balance'] + " " + str(result))

    def update_target_tickers(self, start_time, end_time):
        if os.path.isfile(self.target_tickers_file) is False:
            self.target_tickers = self.get_target_ticker(self.exchange_api, self.max_ticker_num)
            write_target_tickers_in_file(self.target_tickers_file, self.target_tickers)
        else:
            logger.info(self.target_tickers_file + " is already Exist")
            with open(self.target_tickers_file) as file:
                line = file.readline().strip()
                logger.debug(line)
                file_time = datetime.datetime.strptime(line, '%Y-%m-%d %H:%M:%S.%f')
                logger.debug(file_time)

                if start_time < file_time < end_time:
                    with open(self.target_tickers_file) as target_ticker_file:
                        lines = target_ticker_file.readlines()
                        self.target_tickers = lines[1].split(" ")
                        logger.debug(self.target_tickers)
                else:
                    self.target_tickers = self.get_target_ticker(self.exchange_api, self.max_ticker_num)
                    write_target_tickers_in_file(self.target_tickers_file, self.target_tickers)
                    logger.debug(self.target_tickers)

        return self.target_tickers

    def get_target_price(self, ticker, k):
        df = self.exchange_api.get_ohlcv(ticker, interval="day", count=2)
        target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
        return target_price

    def get_target_ticker(self, exchange_api, max_ticker_num):
        coin_values = dict()
        trade_value_top_coin_name = []
        coin_names = exchange_api.fetch_market()
        count = 1
        for coin_name in coin_names:
            print(count)
            count += 1
            df = exchange_api.get_ohlcv(ticker=coin_name['market'])  # count=val_search_day)
            coin_values[coin_name['market']] = df.iloc[-2]['value']
        # print(coin_values)
        coin_values_reverse = sorted(coin_values.items(), reverse=True, key=lambda item: item[1])
        # print(coin_values_reverse)
        trade_value_top = coin_values_reverse[:max_ticker_num]
        # print(len(trade_value_top), trade_value_top)
        for i in range(max_ticker_num):
            trade_value_top_coin_name.append(trade_value_top[i][0])
        # print(trade_value_top)
        # print(trade_value_top_coin_name)
        return trade_value_top_coin_name

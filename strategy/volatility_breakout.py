from log.logging_api import *
from library.crypto_api import *
import datetime
import time
import os

from strategy.strategy_abstract import CryptoStrategy


class VolatilityBreakout(CryptoStrategy):
    def __init__(self, exchange, api):
        self.name = "VolatilityBreakout"
        self.is_running = False
        self.exchange_api = api
        self.exchange = exchange
        self.target_tickers = []
        self.target_tickers_file = "target_tickers.txt"
        self.count = 0
        # Parameters
        self.k = 0.4
        self.moving_average_day = 3
        self.max_ticker_num = 20
        self.each_ticker_value = 10000.0
        self.loss_cut = -5.0
        self.profit_cut = 10.0
        self.threshold_rate = 0.2
        logger.info("Create VolatilityBreakout Strategy Object")

    def set_parameters(self):
        logger.debug("Get " + self.name + " Parameters from file")
        self.k = 0.4
        self.moving_average_day = 3
        self.max_ticker_num = 20
        self.each_ticker_value = 10000.0
        self.loss_cut = -10.0
        self.profit_cut = 200.0
        self.threshold_rate = 0.2
        logger.info("Set " + self.name + " Parameters")

    def get_turn_start_end_time(self):
        start_time = get_exchane_price_update_time(self.exchange_api)
        end_time = start_time + datetime.timedelta(days=1)
        logger.info("Start " + self.name + " Trading : " + str(start_time) + " ~ " + str(end_time))
        return start_time, end_time

    def isTurnRestartTiming(self, end_time, running_now):
        if running_now > (end_time + datetime.timedelta(seconds=60)):
            return True
        else:
            return False

    def isRunningTiming(self, start_time, end_time, running_now):
        if start_time < running_now < end_time - datetime.timedelta(seconds=30):
            return True
        else:
            return False

    def execute_buy_strategy(self, target_tickers, remain_buy_list):
        logger.debug("{0:^9}".format("ticker") + " | " +
                     "{0:^9}".format("target") + " | " +
                     "{0:^9}".format("current") + " | " +
                     "{0:^9}".format("KRW") + " | "
                     )
        for target_ticker in target_tickers:
            if target_ticker not in remain_buy_list:
                logger.info(target_ticker + " already buy")
                continue

            balance = self.exchange.get_balance(ticker=target_ticker)
            target_price = self.get_target_price(target_ticker, self.k)
            target_price_threshold = target_price + target_price * self.threshold_rate
            current_price = get_current_price(self.exchange_api, target_ticker)
            krw = get_balance(self.exchange, "KRW")
            logger.debug("{0:>9}".format(target_ticker) + " | " +
                         "{0:>9}".format(str(int(target_price))) + " | " +
                         "{0:>9}".format(str(int(current_price))) + " | " +
                         "{0:>9}".format(str(int(krw))) + " | "
                         )

            if float(balance) > 0.0:
                ret_msg = target_ticker + ' already has (' + str(balance) + ')'
                logger.debug(ret_msg)
                # send_message_to_chat(ret_msg)

            else:
                ma = get_moving_average(self.exchange_api, target_ticker, self.moving_average_day)
                # logger.debug("MA: " + str(ma))
                if (target_price < current_price < target_price_threshold) and ma < current_price:
                    if krw > 5000.0:
                        if krw < self.each_ticker_value:
                            result = self.exchange.buy_market_order(target_ticker, krw * 0.9995)
                        else:
                            result = self.exchange.buy_market_order(target_ticker, self.each_ticker_value * 0.9995)
                        if 'error' not in result.keys():
                            remain_buy_list.remove(target_ticker)
                        buy_msg = "Buy " + target_ticker + " (" + str(target_price) + "), " + str(result)
                        logger.debug(buy_msg)
                        send_message_to_chat(buy_msg)
            time.sleep(0.1)

    def execute_sell_strategy(self, remain_buy_list):
        balances = self.exchange.get_balances()
        for balance in balances:
            avg_buy_price = balance['avg_buy_price']
            currency = balance['currency']
            # if currency == 'KRW':
            if avg_buy_price is '0':
                continue
            else:
                logger.debug(balance)
                target_ticker = balance['unit_currency'] + '-' + currency
                current_price = float(self.exchange_api.get_current_price(target_ticker))
                balance_ticker_price = float(balance['balance']) * current_price
                if balance_ticker_price >= 5000.0:
                    logger.debug(currency + " = " + str(current_price))
                    avg_buy_price = float(balance['avg_buy_price'])
                    profit_rate = ((current_price - avg_buy_price) / avg_buy_price) * 100.0
                    logger.debug(target_ticker + " >>> " + str(profit_rate))
                    if (profit_rate < self.loss_cut) or (profit_rate > self.profit_cut):
                        result = self.exchange.sell_market_order(target_ticker, balance['balance'])
                        # if 'error' not in result.keys():
                        #    remain_buy_list.append(target_ticker)
                        logger.debug("Sell " + target_ticker + ", " + balance['balance'] + " " + str(result))
                        send_message_to_chat("Sell " + target_ticker + ", " + balance['balance'] + " " + str(result))
                else:
                    err_msg = target_ticker + "balance_ticker price under 5000 " + str(balance_ticker_price)
                    logger.debug(err_msg)
                    send_message_to_chat(err_msg)

            time.sleep(0.1)

    def execute_turn_end_process(self):
        logger.debug("Sell All Tickers")
        balances = self.exchange.get_balances()
        # print(balances)
        for balance in balances:
            currency = balance['currency']
            # print(currency)
            if currency == 'KRW':
                continue
            else:
                logger.debug(balance)
                ticker = balance['unit_currency'] + '-' + currency
                # print(currency + " = " + str(self.exchange_api.get_current_price(ticker)))
                result = self.exchange.sell_market_order(ticker, balance['balance'])
                sell_msg = "Sell " + ticker + ", " + str(balance['balance']) + " " + str(result)
                logger.debug(sell_msg)
                send_message_to_chat(sell_msg)

    def update_target_tickers(self, start_time, end_time):
        if os.path.isfile(self.target_tickers_file) is False:
            self.target_tickers = self.get_target_ticker(self.exchange_api, self.max_ticker_num)
            write_target_tickers_in_file(self.target_tickers_file, self.target_tickers)
        else:
            logger.info(self.target_tickers_file + " is already Exist")
            with open(self.target_tickers_file) as file:
                line = file.readline().strip()
                # logger.debug(line)
                file_time = datetime.datetime.strptime(line, '%Y-%m-%d %H:%M:%S.%f')
                # logger.debug(file_time)

                if start_time < file_time < end_time:
                    with open(self.target_tickers_file) as target_ticker_file:
                        local_lines = target_ticker_file.readlines()
                        self.target_tickers = local_lines[1].split(" ")
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
        self.count = 1
        coin_values = dict()
        trade_value_top_coin_name = []
        coin_names = exchange_api.fetch_market()
        logger.debug("Get Ticker Values Start!")
        for coin_name in coin_names:
            logger.debug(str(self.count))
            self.count += 1
            df = exchange_api.get_ohlcv(ticker=coin_name['market'])  # count=val_search_day)
            coin_values[coin_name['market']] = df.iloc[-2]['value']
            time.sleep(0.1)
        logger.debug("Get Ticker Values End!")
        # logger.debug(coin_values)
        coin_values_reverse = sorted(coin_values.items(), reverse=True, key=lambda item: item[1])
        # logger.debug(coin_values_reverse)
        trade_value_top = coin_values_reverse[:max_ticker_num]
        # logger.debug(len(trade_value_top), trade_value_top)
        for i in range(max_ticker_num):
            trade_value_top_coin_name.append(trade_value_top[i][0])
        # logger.debug(trade_value_top)
        # logger.debug(trade_value_top_coin_name)
        return trade_value_top_coin_name

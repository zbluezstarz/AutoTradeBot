#import os.path
from log.logging_api import *
from config import crypto_param
from library import coin_api
from strategy.volatility_breakout import *

class CryptoCurrency():
    def __init__(self):
        self.is_running = False
        self.target_tickers = []
        self.remain_buy_list = []
        self.is_no_action_time = False

        logger.info("Get Crypto Class Parameter")
        crypto_param.get_crypto_parameter()

        logger.info("Connect Exchange")
        self.exchange_obj = coin_api.connect_exchange("../key.txt")
        self.exchange_api = coin_api.get_exchange_api()

        logger.info("Create Strategy Object")
        self.current_strategy = \
            VolatilityBreakout(self.exchange_obj, self.exchange_api)

        logger.info("Set Strategy Parameters")
        self.current_strategy.set_parameters()

    def init_trade(self):
        start_time, end_time = self.current_strategy.get_start_end_time()
        logger.info("Init Target Tickers")
        str(start_time) + " ~ " + str(end_time)
        self.target_tickers = self.current_strategy.update_target_tickers(start_time, end_time)
        self.remain_buy_list = self.target_tickers

        return start_time, end_time

    def start_trade(self):
        start_time, end_time = self.init_trade()
        logger.info("Start Trading")
        self.is_running = True

        self.is_no_action_time = False

        while self.is_running:
            try:
                for target_ticker in self.target_tickers:
                    if target_ticker not in self.remain_buy_list:
                        logger.info(target_ticker + " already buy")
                        continue

                    running_now = datetime.datetime.now()

                    if start_time < running_now < end_time - datetime.timedelta(seconds=30):
                        self.current_strategy.execute_buy_strategy(target_ticker, self.remain_buy_list)

                    elif running_now > (end_time + datetime.timedelta(seconds=30)):
                        self.current_strategy.execute_turn_end_process()

                        start_time, end_time = self.init_trade()
                        self.is_no_action_time = False
                        break

                    else:
                        self.is_no_action_time = True
                        logger.debug("No Action Time~")
                        time.sleep(10)

                    time.sleep(1)
                if not self.is_no_action_time:
                    self.current_strategy.execute_sell_strategy(self.remain_buy_list)

            except Exception as e:
                logger.critical(e)

            time.sleep(1)

        logger.info("Stop " + self.name + " Trading")


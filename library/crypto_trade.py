from log.logging_api import *
from config import crypto_param
from library import crypto_api
from strategy.volatility_breakout import *


class CryptoTrade:
    def __init__(self):
        self.is_running = False
        self.target_tickers = []
        self.remain_buy_list = []
        self.is_no_action_time = False

        logger.info("Get Crypto Class Parameter")
        crypto_param.get_crypto_parameter()
        self.transaction_time = 10.0

        logger.info("Connect Exchange")
        self.exchange_obj = crypto_api.connect_exchange("../key.txt")
        self.exchange_api = crypto_api.get_exchange_api()

        logger.info("Create Strategy Object")
        self.current_strategy = \
            VolatilityBreakout(self.exchange_obj, self.exchange_api)

        logger.info("Set Strategy Parameters")
        self.current_strategy.set_parameters()

    def init_trade(self):
        start_time, end_time = self.current_strategy.get_turn_start_end_time()
        init_msg = "Init Target Tickers"
        logger.info(init_msg)
        sendMessageToChat(init_msg)
        str(start_time) + " ~ " + str(end_time)
        self.target_tickers = self.current_strategy.update_target_tickers(start_time, end_time)
        self.remain_buy_list = self.target_tickers
        init_msg = "Init Trade Completed"
        logger.info(init_msg)
        sendMessageToChat(init_msg)

        return start_time, end_time

    def start_trade(self):
        start_time, end_time = self.init_trade()
        logger.info("Start Trading")
        self.is_running = True

        self.is_no_action_time = False

        while self.is_running:
            try:
                running_now = datetime.datetime.now()
                if self.current_strategy.isRunningTiming(start_time, end_time, running_now):
                    self.current_strategy.execute_buy_strategy(self.target_tickers, self.remain_buy_list)

                elif self.current_strategy.isTurnRestartTiming(end_time, running_now):
                    self.current_strategy.execute_turn_end_process()

                    start_time, end_time = self.init_trade()
                    self.is_no_action_time = False
                    break

                else:
                    self.is_no_action_time = True
                    logger.debug("No Action Time~")
                    time.sleep(10)

                if not self.is_no_action_time:
                    self.current_strategy.execute_sell_strategy(self.remain_buy_list)

            except Exception as e:
                logger.critical(e)
                sendMessageToChat(e)

            time.sleep(self.transaction_time)

        logger.info("Stop " + self.current_strategy.name + " Trading")

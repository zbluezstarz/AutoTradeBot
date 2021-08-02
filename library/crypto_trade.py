from config import crypto_param
from config.crypto_param import *
from library import crypto_api
from strategy.volatility_breakout import *


class CryptoTrade:
    def __init__(self):
        self.is_running = False
        self.target_tickers = []
        self.remain_buy_list = []
        self.is_no_action_time = False
        self.running_timing = False
        self.restart_timing = False
        self.count = 0
        self.sim_day_num = 0  # Backtest Only

        logger.info("Get Crypto Class Parameter")
        crypto_param.print_crypto_parameter()
        self.transaction_time = float(crypto_param.transaction_sec)
        self.chat_sleep_time = float(crypto_param.chat_sleep_time)

        logger.info("Connect Exchange")
        self.exchange_api = crypto_api.connect_exchange(crypto_param.exchange, "../key.txt")
        self.quotation_api = crypto_api.get_quotation_api(crypto_param.exchange)

        logger.info("Create Strategy Object")
        self.current_strategy = \
            VolatilityBreakout(self.exchange_api, self.quotation_api)

        if crypto_param.exchange == "backtest":
            self.current_strategy.set_start_time(self.quotation_api.get_sim_start_time())
            self.running_timing = True
            self.init_back_index = self.quotation_api.get_sim_index_update()
            self.sim_day_num = self.quotation_api.get_sim_day_num()
            logger.debug("backtest simulation num " + str(self.sim_day_num))

        logger.info("Set Strategy Parameters")
        self.current_strategy.set_parameters(crypto_param)

    def init_trade(self):
        start_time, end_time = self.current_strategy.get_turn_start_end_time()
        init_msg = "Init Target Tickers"
        logger.info(init_msg)
        send_message_to_chat(init_msg, self.chat_sleep_time)
        str(start_time) + " ~ " + str(end_time)
        self.target_tickers = self.current_strategy.update_target_tickers(start_time, end_time)
        self.remain_buy_list = self.target_tickers
        init_msg = "Init Trade Completed"
        logger.info(init_msg)
        send_message_to_chat(init_msg, self.chat_sleep_time)

        return start_time, end_time

    def start_trade(self):
        start_time, end_time = self.init_trade()
        logger.info("Start Trading")
        self.is_running = True

        self.is_no_action_time = False

        while self.is_running:
            try:
                running_now = datetime.datetime.now()

                if crypto_param.exchange == "backtest":
                    self.count += 1
                    if self.count > 24:  # TODO : Set 1day simulation sample count(1~24)
                        self.count = 0
                        self.running_timing = False
                        self.restart_timing = True
                else:
                    self.running_timing = self.current_strategy.isRunningTiming(start_time, end_time, running_now)
                    self.restart_timing = self.current_strategy.isTurnRestartTiming(end_time, running_now)

                if self.running_timing is True:
                    self.current_strategy.execute_buy_strategy(self.target_tickers, self.remain_buy_list)

                    if not self.is_no_action_time:
                        self.current_strategy.execute_sell_strategy(self.remain_buy_list)

                    if crypto_param.exchange == "backtest":
                        self.quotation_api.set_sim_sub_index_update()
                        index = self.quotation_api.get_sim_index_update() - self.init_back_index
                        sub_index = self.quotation_api.get_sim_sub_index_update() - \
                                    (self.quotation_api.get_sim_index_update() * 24)
                        logger.debug("Simulation(" + str(index) + "-" + str(sub_index) + ")")

                elif self.restart_timing is True:
                    self.current_strategy.execute_turn_end_process()

                    start_time, end_time = self.init_trade()
                    self.is_no_action_time = False

                    if crypto_param.exchange == "backtest":
                        self.running_timing = True
                        self.restart_timing = False
                        self.quotation_api.set_sim_index_update()
                        if (index - 1) >= self.sim_day_num:
                            self.is_running = False
                        else:
                            logger.info("Simulation Turn Restart")

                    krw = crypto_api.get_balance(self.exchange_api, "KRW")

                    logger.info("****** " + str(krw) + " ******")
                    # TODO : MDD logging

                else:
                    self.is_no_action_time = True
                    logger.debug("No Action Time~")
                    time.sleep(3600)

            except Exception as e:
                logger.critical(e)
                send_message_to_chat(e)

            time.sleep(self.transaction_time)

        logger.info("Stop " + self.current_strategy.name + " Trading")

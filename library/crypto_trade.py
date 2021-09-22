from config import crypto_param
from config.crypto_param import *
from library import crypto_api
# from strategy.volatility_breakout import *
from strategy.volatility_modi1 import *


class CryptoTrade:
    def __init__(self):
        logger.info("Get Crypto Class Parameter")
        crypto_param.print_crypto_parameter()
        self.transaction_time = float(crypto_param.transaction_sec)
        self.chat_sleep_time = float(crypto_param.chat_sleep_time)

        logger.info("Connect Exchange")
        self.exchange_api = crypto_api.connect_exchange(crypto_param.exchange, "../key.txt")
        self.quotation_api = crypto_api.get_quotation_api(crypto_param.exchange)

        logger.info("Create Strategy Object")
        self.current_strategy = VolatilityModi1(self.exchange_api, self.quotation_api)
        # VolatilityBreakout(self.exchange_api, self.quotation_api)

        self.is_running = False
        self.target_tickers = []
        self.remain_buy_list = []
        self.is_no_action_time = False
        self.running_timing = False
        self.restart_timing = False
        self.count = 0
        self.no_action_sleep_time = 300
        self.sim_day_num = 0  # Backtest Only
        self.backtest_index = 0
        self.running_now = datetime.datetime.now()

        if self.is_backtest():
            self.current_strategy.set_start_time(self.quotation_api.get_sim_start_time())
            self.running_timing = True
            self.init_back_index = self.quotation_api.get_sim_index_update()
            self.sim_day_num = self.quotation_api.get_sim_day_num()
            self.current_strategy.set_backtest_flag(True)
            logger.debug("backtest simulation num " + str(self.sim_day_num))

        self.current_strategy.execute_turn_end_process()

        self.cash = crypto_api.get_balance(self.exchange_api, "KRW")
        self.previous_cash = self.cash
        self.start_cash = self.cash
        self.highest_cash = self.cash
        self.lowest_cash = self.cash
        self.last_highest_cash = self.cash
        self.last_lowest_cash = self.cash
        self.ror = 1
        self.mdd = 0
        self.accumulate_ror = 1
        self.trade_count = 0
        self.win_count = 0
        self.trade_logs = dict()
        self.mdd_logs = dict()

        logger.info("Set Strategy Parameters")
        self.current_strategy.set_parameters(crypto_param)

    def is_backtest(self):
        if crypto_param.exchange == "backtest":
            return True
        else:
            return False

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
        start_time, end_time = self.current_strategy.get_turn_start_end_time()
        logger.info("Start Trading")
        self.is_running = True

        self.is_no_action_time = True
        self.previous_cash = self.cash

        self.backtest_index = 0

        while self.is_running:
            try:
                running_now = datetime.datetime.now()

                if self.is_backtest():
                    self.backtest_set_trade_flag()
                else:
                    self.running_timing = self.current_strategy.isRunningTiming(start_time, end_time, running_now)
                    self.restart_timing = self.current_strategy.isTurnRestartTiming(end_time, running_now)

                if self.running_timing is True:

                    if self.is_no_action_time:
                        self.is_no_action_time = False
                        start_time, end_time = self.init_trade()

                    self.current_strategy.execute_buy_strategy(self.target_tickers, self.remain_buy_list)

                    # if not self.is_no_action_time:
                    self.current_strategy.execute_sell_strategy(self.remain_buy_list)

                    if self.is_backtest():
                        self.backtest_update_index()

                elif self.restart_timing is True:
                    self.current_strategy.execute_turn_end_process()

                    # Update Next Turn Start/End Time
                    start_time, end_time = self.current_strategy.get_turn_start_end_time()
                    self.is_no_action_time = False

                    if self.is_backtest():
                        self.backtest_reset_parameter()

                    self.update_trade_result()

                    self.is_no_action_time = True
                else:
                    self.process_no_action_time()

            except Exception as e:
                logger.critical(e)
                send_message_to_chat(e)

            time.sleep(self.transaction_time)

        logger.info("Stop " + self.current_strategy.name + " Trading")
        self.print_trade_final_result()

    def update_trade_result(self):
        self.cash = crypto_api.get_balance(self.exchange_api, "KRW")
        self.highest_cash = max(self.highest_cash, self.cash)
        self.lowest_cash = min(self.lowest_cash, self.cash)
        self.last_highest_cash = max(self.last_highest_cash, self.cash)
        self.last_lowest_cash = min(self.last_lowest_cash, self.cash)

        dd = -1

        if self.last_highest_cash == self.cash:
            self.last_lowest_cash = self.cash

        if self.last_lowest_cash == self.cash:
            dd = (self.last_highest_cash - self.last_lowest_cash) / self.last_highest_cash * 100.0
            self.mdd = max(self.mdd, dd)

        if self.mdd == dd:
            self.mdd_logs[str(self.running_now)] = {'mdd': self.mdd, 'last_highest': self.last_highest_cash,
                                               'last_lowest': self.last_lowest_cash}
        self.trade_logs[str(self.running_now)] = {'profit_ratio': (self.ror - 1) * 100.0 if self.ror > 1 else 0,
                                             'loss_ratio': (self.ror - 1) * 100.0 if self.ror < 1 else 0}

        self.trade_count += 1
        if self.previous_cash < self.cash:
            self.win_count += 1
        self.ror = self.cash / self.previous_cash
        self.accumulate_ror *= self.ror

        logger.info("****** " + str(self.cash) + " ******")

        self.previous_cash = self.cash

    def process_no_action_time(self):
        logger.debug("No Action Time ~ " + str(self.no_action_sleep_time) + "s")
        time.sleep(self.no_action_sleep_time)

    def print_trade_final_result(self):
        logger.info("Trade Count : " + str(self.trade_count))
        logger.info("Win Count : " + str(self.win_count) + ", " + str(self.win_count / self.trade_count * 100.0) + "%")
        logger.info("ROR : " + str(self.ror))
        logger.info("Accumulate ROR : " + str(self.accumulate_ror))
        logger.info("Highest Cash : " + str(self.highest_cash))
        logger.info("Lowest Cash : " + str(self.lowest_cash))
        logger.info("MDD : " + str(self.mdd))

        df = pandas.DataFrame.from_dict(self.trade_logs)
        df = df.T
        avg_profit = df[df['profit_ratio'] > 0]['profit_ratio'].mean()
        avg_loss = df[df['loss_ratio'] < 0]['loss_ratio'].mean()

        logger.info("HPR : " + str((self.cash - self.start_cash) / self.start_cash * 100.0))
        logger.info("Avg Profit Ratio : " + str(avg_profit))
        logger.info("Avg Loss Ratio : " + str(avg_loss))
        logger.info("Profit Loss Ratio : " + str(abs(avg_profit / avg_loss)))

        logger.debug(self.mdd_logs)
        logger.debug(self.trade_logs)

    def backtest_update_index(self):
        self.quotation_api.set_sim_sub_index_update()
        self.backtest_index = self.quotation_api.get_sim_index_update() - self.init_back_index
        sub_index = self.quotation_api.get_sim_sub_index_update() - (self.quotation_api.get_sim_index_update() * 24)
        logger.debug("Simulation(" + str(self.backtest_index) + "-" + str(sub_index) + ")")

    def backtest_set_trade_flag(self):
        self.count += 1
        if self.count > 12:  # TODO : Set 1day simulation sample count(1~24)
            self.count = 0
            self.running_timing = False
            self.restart_timing = True

    def backtest_reset_parameter(self):
        self.running_now = self.trade_count + 1
        self.running_timing = True
        self.restart_timing = False
        self.quotation_api.set_sim_index_update()
        if (self.backtest_index - 1) >= self.sim_day_num:
            self.is_running = False
        else:
            logger.info("Simulation Turn Restart")

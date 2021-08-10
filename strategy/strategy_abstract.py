import sys
from log.logging_api import *
from abc import *

class CryptoStrategy(metaclass=ABCMeta):

    @abstractmethod
    def set_parameters(self, crypto_param):
        logger.critical(sys._getframe(0).f_code.co_name + " MUST implement!!")

    @abstractmethod
    def get_turn_start_end_time(self):
        logger.critical(sys._getframe(0).f_code.co_name + " MUST implement!!")

    @abstractmethod
    def update_target_tickers(self, start_time, end_time):
        logger.critical(sys._getframe(0).f_code.co_name + " MUST implement!!")

    @abstractmethod
    def execute_buy_strategy(self, target_tickers, remain_buy_list):
        logger.critical(sys._getframe(0).f_code.co_name + " MUST implement!!")

    @abstractmethod
    def execute_sell_strategy(self, remain_buy_list):
        logger.critical(sys._getframe(0).f_code.co_name + " MUST implement!!")

    @abstractmethod
    def execute_turn_end_process(self):
        logger.critical(sys._getframe(0).f_code.co_name + " MUST implement!!")

    @abstractmethod
    def isTurnRestartTiming(self, end_time, running_now):
        logger.critical(sys._getframe(0).f_code.co_name + " MUST implement!!")
        return True

    @abstractmethod
    def isRunningTiming(self, start_time, end_time, running_now):
        logger.critical(sys._getframe(0).f_code.co_name + " MUST implement!!")
        return True
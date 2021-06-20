#import os.path
from log.logging_api import *
from config import crypto_param
from library import coin_api
from strategy import volatility_breakout

class CryptoCurrency():
    def __init__(self):

        logger.info("Get Crypto Class Parameter")
        crypto_param.get_crypto_parameter()

        logger.info("Connect Exchange")
        self.exchange_inst = coin_api.connect_exchange("../key.txt")
        self.exchange_api = coin_api.get_exchange_api()
        #self.coin_names = coin_api.get_exchange_api().fetch_market()
        #logger.debug(os.getcwd())

        logger.info("Create Strategy Object")
        self.current_strategy = \
            volatility_breakout.VolatilityBreakout(self.exchange_inst, self.exchange_api)

        logger.info("Set Strategy Parameters")
        self.current_strategy.set_parameters()

        logger.info("Start Trading")
        self.current_strategy.start_trade()


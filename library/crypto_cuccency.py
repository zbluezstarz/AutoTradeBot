#import os.path
from log.logging_api import *
from config import crypto_param
from library import coin_api

class CryptoCurrency():
    def __init__(self):

        logger.info("Get Crypto Class Parameter:")
        crypto_param.get_crypto_parameter(logger)

        logger.info("Connect Exchange")
        self.exchange = coin_api.connect_exchange("../key.txt")
        #self.coin_names = coin_api.get_exchange_api().fetch_market()
        #logger.debug(os.getcwd())
        logger.info("Get Strategy Parameter")
        logger.info("Create Strategy Object")
        logger.info("Start Trading")
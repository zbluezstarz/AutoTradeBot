from log.logging_api import *

class CryptoParameter:
    def __init__(self):
        with open("config/config.txt") as f:
            config_file = f.readlines()
            self.exchange = config_file[0].split(":")[1].strip()
            self.strategy = config_file[1].split(":")[1].strip()
            self.transaction_sec = config_file[2].split(":")[1].strip()
            self.chat_sleep_time = config_file[3].split(":")[1].strip()

    def print_crypto_parameter(self):
        logger.info("Exchange : " + self.exchange)
        logger.info("Strategy : " + self.strategy)
        logger.info("Transaction : " + self.transaction_sec)


crypto_param = CryptoParameter()


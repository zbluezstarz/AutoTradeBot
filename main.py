from library.crypto_trade import *
from log.logging_api import *


logger.info("Auto Trade Bot Start!")
crypto = CryptoTrade()
crypto.start_trade()

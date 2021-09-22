from library.crypto_trade import *
from library.logging_api import *


logger.info("Auto Trade Bot Start!")
crypto = CryptoTrade()
crypto.start_trade()

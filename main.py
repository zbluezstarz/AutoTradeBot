from library.crypto_currency import *
from log.logging_api import *


logger.info("Auto Trade Bot Start!")
crypto = CryptoCurrency()
crypto.start_trade()

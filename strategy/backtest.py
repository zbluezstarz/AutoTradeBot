import os
import time
import pyupbit
from library.crypto_api import *


def create_backtest_data():
    tickers = pyupbit.get_tickers()
    print(tickers)

    now = datetime.datetime.today()
    today_str = str(now.year) + (str(now.month)).zfill(2) + (str(now.day)).zfill(2)
    # Create Backtest Data
    count = 0
    for ticker in tickers:
        if "KRW" in ticker:
            target_tickers_file1 = "../db/" + ticker + "_org.xlsx"
            target_tickers_file2 = "../db/" + ticker + "_mod.xlsx"
            if os.path.isfile(target_tickers_file1) is False:
                print(ticker)
                org_df, mod_df = get_custom_1days_ohlcv(pyupbit, ticker, today_str, 0, 1000)

                if org_df is not None and mod_df is not None:
                    org_df.to_excel(target_tickers_file1)
                    mod_df.to_excel(target_tickers_file2)
                    count += 1
                    print(count)
                    time.sleep(1)
            else:
                print("target_tickers_file is exist!!" + " (" + ticker + ")")

create_backtest_data()


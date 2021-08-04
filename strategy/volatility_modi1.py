from library.crypto_api import *
import datetime
import time
import os

from strategy.strategy_abstract import CryptoStrategy


class VolatilityModi1(CryptoStrategy):
    def __init__(self, exchange_api, quotation_api):
        self.name = "VolatilityModi1"
        self.is_running = False
        self.quotation_api = quotation_api
        self.exchange_api = exchange_api
        self.target_tickers = []
        self.target_tickers_file = "target_tickers.txt"
        self.count = 0
        self.chat_sleep_time = 0.0
        # Parameters
        self.reference_time = 0
        self.delta_time = datetime.timedelta(days=1)
        init_now = datetime.datetime.now()
        self.start_time = datetime.datetime(init_now.year, init_now.month, init_now.day, self.reference_time, 0, 0)
        self.max_ticker_num = 20
        self.krw = get_balance(self.exchange_api, "KRW")
        self.krw_per_ticker = self.krw / float(self.max_ticker_num)
        self.noise_ratio_average_day = 20
        self.filtered_tickers_info = []

        self.loss_cut = -10.0
        self.profit_cut = 300.0

        logger.info("Create VolatilityBreakout Strategy Object")

    def set_parameters(self, crypto_param):
        logger.debug("Get " + self.name + " Parameters from file")

        self.chat_sleep_time = float(crypto_param.chat_sleep_time)
        logger.info("Set " + self.name + " Parameters")

    def set_start_time(self, start_time):
        self.start_time = start_time

    def get_start_time(self):
        return self.start_time

    def get_turn_start_end_time(self):
        start_time = self.get_start_time()
        end_time = start_time + datetime.timedelta(hours=12)
        self.set_start_time(start_time + self.delta_time)
        logger.info("Start " + self.name + " Trading : " + str(start_time) + " ~ " + str(end_time))
        return start_time, end_time

    def isTurnRestartTiming(self, end_time, running_now):
        if running_now > (end_time + datetime.timedelta(seconds=10)):
            return True
        else:
            return False

    def isRunningTiming(self, start_time, end_time, running_now):
        if start_time < running_now < end_time - datetime.timedelta(seconds=30):
            return True
        else:
            return False

    def execute_buy_strategy(self, target_tickers, remain_buy_list):
        '''
        logger.debug("{0:^9}".format("ticker") + " | " +
                     "{0:^9}".format("target") + " | " +
                     "{0:^9}".format("current") + " | " +
                     "{0:^9}".format("KRW") + " | "
                     )
        '''

        index = 0
        for target_ticker in target_tickers:
            index += 1
            if target_ticker not in remain_buy_list:
                logger.info(target_ticker + " already buy")
                continue

            balance = self.exchange_api.get_balance(ticker=target_ticker)
            target_price = self.filtered_tickers_info[index - 1]['target_price']
            # target_price_threshold = target_price + target_price * self.threshold_rate
            current_price = get_current_price(self.quotation_api, target_ticker)
            krw = get_balance(self.exchange_api, "KRW")

            '''
            logger.debug("{0:>9}".format(target_ticker) + " | " +
                         "{0:>9}".format(str(int(target_price))) + " | " +
                         "{0:>9}".format(str(int(current_price))) + " | " +
                         "{0:>9}".format(str(int(krw))) + " | "
                         )
            '''

            if float(balance) > 0.0:
                ret_msg = target_ticker + ' already has (' + str(balance) + ')'
                logger.debug(ret_msg)
                # send_message_to_chat(ret_msg, self.chat_sleep_time)

            else:
                if target_price < current_price:
                    market_timing_ratio = self.filtered_tickers_info[index - 1]['market_timing_ratio']
                    buy_price = self.krw_per_ticker * market_timing_ratio
                    logger.debug(str(buy_price) + ", " + str(self.krw_per_ticker))
                    if krw > 5000.0:
                        result = self.exchange_api.buy_market_order(target_ticker, buy_price)

                        if 'error' not in result.keys():
                            remain_buy_list.remove(target_ticker)
                        buy_msg = "Buy " + target_ticker + " (" + str(current_price) + "), " + str(result)
                        logger.debug(buy_msg)
                        send_message_to_chat(buy_msg, self.chat_sleep_time)
            # time.sleep(0.1)

    def execute_sell_strategy(self, remain_buy_list):
        balances = self.exchange_api.get_balances()
        for balance in balances:
            avg_buy_price = balance['avg_buy_price']
            currency = balance['currency']
            # if currency == 'KRW':
            if avg_buy_price == '0':
                continue
            else:
                # logger.debug(balance)
                target_ticker = balance['unit_currency'] + '-' + currency
                current_price = float(self.quotation_api.get_current_price(target_ticker))
                balance_ticker_price = float(balance['balance']) * current_price
                if balance_ticker_price >= 5000.0:
                    # logger.debug(currency + " = " + str(current_price))
                    avg_buy_price = float(balance['avg_buy_price'])
                    profit_rate = ((current_price - avg_buy_price) / avg_buy_price) * 100.0
                    # logger.debug(target_ticker + " >>> " + str(profit_rate))
                    if (profit_rate < self.loss_cut) or (profit_rate > self.profit_cut):
                        result = self.exchange_api.sell_market_order(target_ticker, balance['balance'])
                        # if 'error' not in result.keys():
                        #    remain_buy_list.append(target_ticker)
                        sell_msg = "Sell " + target_ticker + " (" + str(current_price) + "," + str(profit_rate)\
                                   + "%), " + str(result)
                        logger.debug(sell_msg)
                        send_message_to_chat(sell_msg, self.chat_sleep_time)
                else:
                    err_msg = target_ticker + " balance_ticker price under 5000 " + str(balance_ticker_price)
                    logger.debug(err_msg)
                    send_message_to_chat(err_msg, self.chat_sleep_time)

            time.sleep(0.1)

    def execute_turn_end_process(self):
        logger.debug("Sell All Tickers")
        balances = self.exchange_api.get_balances()
        # logger.debug(balances)

        for balance in balances[:]:
            currency = balance['currency']
            # logger.debug(balance)
            if currency == 'KRW':
                continue
            else:
                # logger.debug(balance)
                ticker = balance['unit_currency'] + '-' + currency
                # print(currency + " = " + str(self.quotation_api.get_current_price(ticker)))
                result = self.exchange_api.sell_market_order(ticker, balance['balance'])
                # sell_msg = "Sell " + ticker + ", " + str(balance['balance']) + " " + str(result)
                avg_buy_price = float(balance['avg_buy_price'])
                current_price = float(self.quotation_api.get_current_price(ticker))
                profit_rate = ((current_price - avg_buy_price) / avg_buy_price) * 100.0
                sell_msg = "Sell " + ticker + " (" + str(current_price) + "," + str(profit_rate) + "%), " + str(result)
                logger.debug(sell_msg)
                send_message_to_chat(sell_msg, self.chat_sleep_time)
            # logger.debug(balances)

        self.krw = get_balance(self.exchange_api, "KRW")
        self.filtered_tickers_info = []
        self.target_tickers = []

    def get_target_price(self, ticker, k):
        df = self.quotation_api.get_ohlcv(ticker, interval="day", count=1)
        target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
        return target_price

    def update_target_tickers(self, start_time, end_time):
        self.filtered_tickers_info = []
        self.target_tickers = []
        now = datetime.datetime.today()
        today_str = str(now.year) + (str(now.month)).zfill(2) + (str(now.day)).zfill(2)
        tickers = self.get_target_ticker(self.quotation_api, self.max_ticker_num)
        count = 0
        for ticker in tickers:
            count += 1
            # logger.debug(str(count) + " : " + ticker)
            org_df, mod_df = get_custom_1days_ohlcv(self.quotation_api, ticker, today_str, 0, 30)
            if float(mod_df['pro_half2'][-1]) > 0.0 and float(mod_df['vol_half2'][-1]) > float(mod_df['vol_half1'][-1]):
                self.target_tickers.append(ticker)
                market_timing_ratio = 0.0

                # logger.debug(mod_df)

                MAs = [mod_df['close'].rolling(3).mean().iloc[-1],
                       mod_df['close'].rolling(5).mean().iloc[-1],
                       mod_df['close'].rolling(10).mean().iloc[-1],
                       mod_df['close'].rolling(20).mean().iloc[-1]]

                close_price = mod_df['close'].iloc[-1]

                # logger.debug(MAs)
                # logger.debug(close_price)

                for MA in MAs:
                    if MA > close_price:
                        market_timing_ratio += 1.0

                market_timing_ratio = market_timing_ratio / float(len(MAs))
                # noise_ratio_average = mod_df['noise_ratio'].rolling(self.noise_ratio_average_day).mean().iloc[-1]
                noise_ratio_average = mod_df['nr_half1'].rolling(self.noise_ratio_average_day).mean().iloc[-1]
                # logger.debug(mod_df['noise_ratio'].rolling(self.noise_ratio_average_day).mean())

                target_price = \
                    mod_df.iloc[-1]['close'] + (mod_df.iloc[-1]['high'] - mod_df.iloc[-1]['low']) * noise_ratio_average

                ticker_info = {'ticker': ticker,
                               'market_timing_ratio': market_timing_ratio,
                               'target_price': target_price,
                               'noise_ratio': noise_ratio_average}
                self.filtered_tickers_info.append(ticker_info)
            # logger.debug(org_df)
            # logger.debug(mod_df)
        logger.debug(len(self.filtered_tickers_info))
        logger.debug(self.filtered_tickers_info)

        if len(self.target_tickers) != 0:
            self.krw_per_ticker = self.krw / float(len(self.target_tickers))
        else:
            self.krw_per_ticker = self.krw

        return self.target_tickers

    def get_target_ticker(self, quotation_api, max_ticker_num):

        market_lists = [{'market': 'KRW-BTC', 'korean_name': '비트코인', 'english_name': 'Bitcoin'},
                        {'market': 'KRW-ARDR', 'korean_name': '아더', 'english_name': 'Ardor'},
                        {'market': 'KRW-ADA', 'korean_name': '에이다', 'english_name': 'Ada'},
                        {'market': 'KRW-ARK', 'korean_name': '아크', 'english_name': 'Ark'},
                        {'market': 'KRW-BAT', 'korean_name': '베이직어텐션토큰', 'english_name': 'Basic Attention Token'},
                        {'market': 'KRW-BCH', 'korean_name': '비트코인캐시', 'english_name': 'Bitcoin Cash'},
                        {'market': 'KRW-BTG', 'korean_name': '비트코인골드', 'english_name': 'Bitcoin Gold'},
                        {'market': 'KRW-CVC', 'korean_name': '시빅', 'english_name': 'Civic'},
                        {'market': 'KRW-ELF', 'korean_name': '엘프', 'english_name': 'aelf'},
                        {'market': 'KRW-EOS', 'korean_name': '이오스', 'english_name': 'EOS'},
                        {'market': 'KRW-ETH', 'korean_name': '이더리움', 'english_name': 'Ethereum'},
                        {'market': 'KRW-ETC', 'korean_name': '이더리움클래식', 'english_name': 'Ethereum Classic'},
                        {'market': 'KRW-GAS', 'korean_name': '가스', 'english_name': 'GAS'},
                        {'market': 'KRW-GRS', 'korean_name': '그로스톨코인', 'english_name': 'Groestlcoin'},
                        {'market': 'KRW-ICX', 'korean_name': '아이콘', 'english_name': 'Icon'},
                        {'market': 'KRW-IOST', 'korean_name': '아이오에스티', 'english_name': 'IOST'},
                        {'market': 'KRW-IOTA', 'korean_name': '아이오타', 'english_name': 'IOTA'},
                        {'market': 'KRW-IQ', 'korean_name': '에브리피디아', 'english_name': 'Everipedia'},
                        {'market': 'KRW-KNC', 'korean_name': '카이버네트워크', 'english_name': 'Kyber Network'},
                        {'market': 'KRW-LOOM', 'korean_name': '룸네트워크', 'english_name': 'Loom Network'},
                        {'market': 'KRW-LSK', 'korean_name': '리스크', 'english_name': 'Lisk'},
                        {'market': 'KRW-LTC', 'korean_name': '라이트코인', 'english_name': 'Litecoin'},
                        {'market': 'KRW-MED', 'korean_name': '메디블록', 'english_name': 'MediBloc'},
                        {'market': 'KRW-MFT', 'korean_name': '메인프레임', 'english_name': 'Mainframe'},
                        {'market': 'KRW-MTL', 'korean_name': '메탈', 'english_name': 'Metal'},
                        {'market': 'KRW-NEO', 'korean_name': '네오', 'english_name': 'NEO'},
                        {'market': 'KRW-OMG', 'korean_name': '오미세고', 'english_name': 'OmiseGo'},
                        {'market': 'KRW-ONG', 'korean_name': '온톨로지가스', 'english_name': 'ONG'},
                        {'market': 'KRW-ONT', 'korean_name': '온톨로지', 'english_name': 'Ontology'},
                        {'market': 'KRW-POLY', 'korean_name': '폴리매쓰', 'english_name': 'Polymath'},
                        {'market': 'KRW-POWR', 'korean_name': '파워렛저', 'english_name': 'Power ledger'},
                        {'market': 'KRW-QTUM', 'korean_name': '퀀텀', 'english_name': 'Qtum'},
                        {'market': 'KRW-REP', 'korean_name': '어거', 'english_name': 'Augur'},
                        {'market': 'KRW-RFR', 'korean_name': '리퍼리움', 'english_name': 'Refereum'},
                        {'market': 'KRW-SBD', 'korean_name': '스팀달러', 'english_name': 'SteemDollars'},
                        {'market': 'KRW-SC', 'korean_name': '시아코인', 'english_name': 'Siacoin'},
                        {'market': 'KRW-SNT', 'korean_name': '스테이터스네트워크토큰', 'english_name': 'Status Network Token'},
                        {'market': 'KRW-STEEM', 'korean_name': '스팀', 'english_name': 'Steem'},
                        {'market': 'KRW-STORJ', 'korean_name': '스토리지', 'english_name': 'Storj'},
                        {'market': 'KRW-TRX', 'korean_name': '트론', 'english_name': 'TRON'},
                        {'market': 'KRW-UPP', 'korean_name': '센티넬프로토콜', 'english_name': 'Sentinel Protocol'},
                        {'market': 'KRW-WAVES', 'korean_name': '웨이브', 'english_name': 'Waves'},
                        {'market': 'KRW-XEM', 'korean_name': '넴', 'english_name': 'NEM'},
                        {'market': 'KRW-XLM', 'korean_name': '스텔라루멘', 'english_name': 'Lumen'},
                        {'market': 'KRW-XRP', 'korean_name': '리플', 'english_name': 'Ripple'},
                        {'market': 'KRW-ZIL', 'korean_name': '질리카', 'english_name': 'Zilliqa'},
                        {'market': 'KRW-ZRX', 'korean_name': '제로엑스', 'english_name': '0x Protocol'}]

        tickers = []
        for market in market_lists:
            tickers.append(market['market'])
        # print(tickers)
        return tickers


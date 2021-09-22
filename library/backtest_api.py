import pandas

from library.logging_api import *

# TODO : Reduce Simulation Running Time


class BackExchange:
    def __init__(self):
        self.index = 30  # for searching Max 30days Profit
        self.sub_index = self.index * 24
        self.start_money = 1000000.0
        self.sim_day_num = 730
        self.sim_balance = [{'currency': 'KRW',
                             'balance': str(float(self.start_money)),
                             'locked': '0.0',
                             'avg_buy_price': '0',
                             'avg_buy_price_modified': True,
                             'unit_currency': 'KRW'}]
        self.fee_ratio = 0.0005

        logger.debug("=== DataFrame Load Start ===")
        self.df_dict_org = {}
        self.df_dict_mod = {}

        tickers = self.get_tickers()
        count = 0
        for ticker in tickers:
            file_name = "db/" + ticker + "_org.xlsx"
            df = pandas.read_excel(file_name, engine='openpyxl')
            df.set_index('Unnamed: 0', inplace=True)
            self.df_dict_org[ticker] = df
            file_name = "db/" + ticker + "_mod.xlsx"
            df = pandas.read_excel(file_name, engine='openpyxl')
            df.set_index('Unnamed: 0', inplace=True)
            self.df_dict_mod[ticker] = df
            logger.debug(ticker + " DataFrame is Loaded " + str(count))
            count += 1

    def calculate_price(self, df):
        # price = (float(df['high']) + float(df['low'])) / 2.0
        price = float(df['open'])
        return price

    def set_back_exchange(self, acc_key, sec_key):
        pass

    def get_tickers(self, fiat="ALL", limit_info=False):
        market_lists = self.fetch_market()
        tickers = []
        for market in market_lists:
            tickers.append(market['market'])
        # print(tickers)
        return tickers

    def get_ohlcv(self, ticker="KRW-BTC", interval="day", count=30, to=None, period=0.1):
        slicing_df = None
        if interval == "minutes60" or interval == "minute60":
            df = self.df_dict_org[ticker]
            slicing_df = df.iloc[self.sub_index - count: self.sub_index]
        else:  # if interval == "day":
            df = self.df_dict_mod[ticker]
            slicing_df = df.iloc[self.index - count: self.index]

        # logger.debug(slicing_df)
        return slicing_df

    def get_balances(self, contain_req=False):
        return self.sim_balance

    def get_balance(self, ticker="KRW", contain_req=False):
        try:
            balances = self.get_balances()

            # search the current currency
            balance = 0
            for x in balances:
                if x['currency'] == ticker:
                    balance = float(x['balance'])
                    break

                return balance
        except Exception as x:
            logger.critical(x.__class__.__name__)
            return None

    def get_orderbook(self, tickers="KRW-BTC"):
        try:
            # file_name = "db/" + tickers + "_org.xlsx"
            # df = pandas.read_excel(file_name, engine='openpyxl')
            # df.set_index('Unnamed: 0', inplace=True)
            df = self.df_dict_org[tickers]
            slicing_df = df.iloc[self.sub_index: self.sub_index + 1]
            # print(slicing_df)

            # price = (float(slicing_df['high']) + float(slicing_df['low'])) / 2.0
            price = self.calculate_price(slicing_df)
            contents = [{'market': tickers,
                         'timestamp': slicing_df.index[0],
                         'total_ask_size': float(slicing_df['volume']),
                         'total_bid_size': float(slicing_df['volume']),
                         'orderbook_units': [{'ask_price': price,
                                              'bid_price': price,
                                              'ask_size': float(slicing_df['volume']),
                                              'bid_size': float(slicing_df['volume'])}]}]

            return contents
        except Exception as x:
            logger.critical(x.__class__.__name__)
            return None

    def buy_market_order(self, ticker, price, contain_req=False):
        try:
            if price > 5000.0:
                df = self.df_dict_org[ticker]
                slicing_df = df.iloc[self.sub_index: self.sub_index + 1]

                ticker_name = str(ticker).split("-")[1].strip()
                real_price = price * (1.0 + self.fee_ratio)

                is_already_has_ticker = False
                i = 0
                for sim_balance in self.sim_balance:
                    if sim_balance['currency'] == ticker_name:
                        is_already_has_ticker = True
                        break
                    else:
                        i += 1
                # logger.debug(self.sim_balance)
                if is_already_has_ticker is True:
                    # target_price = float(slicing_df['high'])
                    # target_price = (float(slicing_df['high']) + float(slicing_df['low'])) / 2.0
                    target_price = self.calculate_price(slicing_df)
                    total_price = (float(self.sim_balance[i]['avg_buy_price']) * float(self.sim_balance[i]['balance']))\
                                     + float(price)
                    balance = float(price) / target_price + float(self.sim_balance[i]['balance'])
                    avg_buy_price = float(total_price) / float(balance)
                    self.sim_balance[i]['balance'] = str(balance)
                    self.sim_balance[i]['avg_buy_price'] = str(avg_buy_price)
                else:
                    # avg_buy_price = float(slicing_df['high'])
                    # avg_buy_price = (float(slicing_df['high']) + float(slicing_df['low'])) / 2.0
                    avg_buy_price = self.calculate_price(slicing_df)
                    balance = float(price) / avg_buy_price
                    logger.critical(str(avg_buy_price))
                    logger.critical(str(price))
                    logger.critical(str(balance))

                    self.sim_balance.append({'currency': ticker_name,
                                             'balance': str(balance),
                                             'locked': '0.0',
                                             'avg_buy_price': str(avg_buy_price),
                                             'avg_buy_price_modified': True,
                                             'unit_currency': 'KRW'})

                self.start_money = float(self.start_money) - float(real_price)

                self.sim_balance[0] = {'currency': 'KRW',
                                       'balance': str(self.start_money),
                                       'locked': '0.0',
                                       'avg_buy_price': '0',
                                       'avg_buy_price_modified': True,
                                       'unit_currency': 'KRW'}
                # logger.debug(self.sim_balance)
                result = {'uuid': 'c20f1a3c-3890-4b9b-b99b-f952bf698f7b',
                          'side': 'bid',
                          'ord_type': 'price',
                          'price': float(price),
                          'state': 'wait',
                          'market': ticker,
                          'created_at': str(datetime.datetime.now()),
                          'volume': None,
                          'remaining_volume': None,
                          'reserved_fee': str((float(price) * self.fee_ratio)),
                          'remaining_fee': str((float(price) * self.fee_ratio)),
                          'paid_fee': '0.0',
                          'locked': str((float(price) * (1.0 + self.fee_ratio))),
                          'executed_volume': '0.0',
                          'trades_count': 0}
                # print(self.sim_balance)
                # print(result)
                return result
            else:
                result = {'uuid': 'c20f1a3c-3890-4b9b-b99b-f952bf698f7b',
                          'side': 'bid',
                          'ord_type': 'price',
                          'price': 0.0,
                          'state': 'wait',
                          'market': ticker,
                          'created_at': str(datetime.datetime.now()),
                          'volume': None,
                          'remaining_volume': None,
                          'reserved_fee': '0.0',
                          'remaining_fee': '0.0',
                          'paid_fee': '0.0',
                          'locked': '0.0',
                          'executed_volume': '0.0',
                          'trades_count': 0}
                return result
        except Exception as x:
            logger.critical(x.__class__.__name__)
            return None

    def get_current_price(self, order_currency, payment_currency="KRW"):
        resp = None
        try:
            df = self.df_dict_org[order_currency]
            slicing_df = df.iloc[self.sub_index: self.sub_index + 1]
            # price = (float(slicing_df['high']) + float(slicing_df['low'])) / 2.0
            price = self.calculate_price(slicing_df)
            # resp = float(slicing_df['close'])
            resp = price

            return resp

        except Exception as x:
            logger.critical(x.__class__.__name__)
            return resp

    def sell_market_order(self, ticker, volume, contain_req=False):
        try:
            df = self.df_dict_org[ticker]
            slicing_df = df.iloc[self.sub_index: self.sub_index + 1]
            ticker_name = str(ticker).split("-")[1].strip()
            # logger.debug(ticker_name)
            i = 0
            for sim_balance in self.sim_balance:
                if sim_balance['currency'] == ticker_name:
                    # price = (float(slicing_df['high']) + float(slicing_df['low'])) / 2.0
                    price = self.calculate_price(slicing_df)
                    # price = float(slicing_df['close'])
                    # logger.debug((price * (1.0 - self.fee_ratio) * float(sim_balance['balance'])))
                    self.start_money += (price * (1.0 - self.fee_ratio) * float(sim_balance['balance']))
                    break
                else:
                    i += 1
            # logger.debug(self.sim_balance)
            del self.sim_balance[i]

            self.sim_balance[0] = {'currency': 'KRW',
                                   'balance': str(self.start_money),
                                   'locked': '0.0',
                                   'avg_buy_price': '0',
                                   'avg_buy_price_modified': True,
                                   'unit_currency': 'KRW'}

            # logger.debug("sell_market_order " + ticker + str(volume))
            # logger.debug(self.sim_balance)

            result = {'uuid': '62a6a95a-eec8-4bd3-a0fc-7981fb64db83',
                      'side': 'ask',
                      'ord_type': 'market',
                      'price': None,
                      'state': 'wait',
                      'market': ticker,
                      'created_at': str(datetime.datetime.now()),
                      'volume': str(volume),
                      'remaining_volume': str(volume),
                      'reserved_fee': '0.0',
                      'remaining_fee': '0.0',
                      'paid_fee': '0.0',
                      'locked': str(volume),
                      'executed_volume': '0.0',
                      'trades_count': 0}

            return result
        except Exception as x:
            logger.critical(x.__class__.__name__)
            return None

    def get_sim_start_time(self):
        file_name = "db/KRW-BTC_mod.xlsx"
        df = pandas.read_excel(file_name, engine='openpyxl')
        df.set_index('Unnamed: 0', inplace=True)
        return df.index[self.index-1]

    def set_sim_index(self, index):
        self.index = index
        self.sub_index = self.index * 24

    def set_sim_index_update(self):
        self.index += 1
        self.sub_index = self.index * 24

    def get_sim_index_update(self):
        return self.index

    def set_sim_sub_index_update(self):
        self.sub_index += 1

    def get_sim_sub_index_update(self):
        return self.sub_index

    def get_sim_day_num(self):
        return self.sim_day_num

    def fetch_market(self):
        market_lists = [{'market': 'KRW-BTC', 'korean_name': '비트코인', 'english_name': 'Bitcoin'},
                         {'market': 'KRW-ETH', 'korean_name': '이더리움', 'english_name': 'Ethereum'},
                         {'market': 'KRW-NEO', 'korean_name': '네오', 'english_name': 'NEO'},
                         {'market': 'KRW-MTL', 'korean_name': '메탈', 'english_name': 'Metal'},
                         {'market': 'KRW-LTC', 'korean_name': '라이트코인', 'english_name': 'Litecoin'},
                         {'market': 'KRW-XRP', 'korean_name': '리플', 'english_name': 'Ripple'},
                         {'market': 'KRW-ETC', 'korean_name': '이더리움클래식', 'english_name': 'Ethereum Classic'},
                         {'market': 'KRW-OMG', 'korean_name': '오미세고', 'english_name': 'OmiseGo'},
                         {'market': 'KRW-SNT', 'korean_name': '스테이터스네트워크토큰', 'english_name': 'Status Network Token'},
                         {'market': 'KRW-WAVES', 'korean_name': '웨이브', 'english_name': 'Waves'},
                         {'market': 'KRW-XEM', 'korean_name': '넴', 'english_name': 'NEM'},
                         {'market': 'KRW-QTUM', 'korean_name': '퀀텀', 'english_name': 'Qtum'},
                         {'market': 'KRW-LSK', 'korean_name': '리스크', 'english_name': 'Lisk'},
                         {'market': 'KRW-STEEM', 'korean_name': '스팀', 'english_name': 'Steem'},
                         {'market': 'KRW-XLM', 'korean_name': '스텔라루멘', 'english_name': 'Lumen'},
                         {'market': 'KRW-ARDR', 'korean_name': '아더', 'english_name': 'Ardor'},
                         {'market': 'KRW-ARK', 'korean_name': '아크', 'english_name': 'Ark'},
                         {'market': 'KRW-STORJ', 'korean_name': '스토리지', 'english_name': 'Storj'},
                         {'market': 'KRW-GRS', 'korean_name': '그로스톨코인', 'english_name': 'Groestlcoin'},
                         {'market': 'KRW-REP', 'korean_name': '어거', 'english_name': 'Augur'},
                         {'market': 'KRW-ADA', 'korean_name': '에이다', 'english_name': 'Ada'},
                         {'market': 'KRW-SBD', 'korean_name': '스팀달러', 'english_name': 'SteemDollars'},
                         {'market': 'KRW-POWR', 'korean_name': '파워렛저', 'english_name': 'Power ledger'},
                         {'market': 'KRW-BTG', 'korean_name': '비트코인골드', 'english_name': 'Bitcoin Gold'},
                         {'market': 'KRW-ICX', 'korean_name': '아이콘', 'english_name': 'Icon'},
                         {'market': 'KRW-EOS', 'korean_name': '이오스', 'english_name': 'EOS'},
                         {'market': 'KRW-TRX', 'korean_name': '트론', 'english_name': 'TRON'},
                         {'market': 'KRW-SC', 'korean_name': '시아코인', 'english_name': 'Siacoin'},
                         {'market': 'KRW-ONT', 'korean_name': '온톨로지', 'english_name': 'Ontology'},
                         {'market': 'KRW-ZIL', 'korean_name': '질리카', 'english_name': 'Zilliqa'},
                         {'market': 'KRW-POLY', 'korean_name': '폴리매쓰', 'english_name': 'Polymath'},
                         {'market': 'KRW-ZRX', 'korean_name': '제로엑스', 'english_name': '0x Protocol'},
                         {'market': 'KRW-LOOM', 'korean_name': '룸네트워크', 'english_name': 'Loom Network'},
                         {'market': 'KRW-BCH', 'korean_name': '비트코인캐시', 'english_name': 'Bitcoin Cash'},
                         {'market': 'KRW-BAT', 'korean_name': '베이직어텐션토큰', 'english_name': 'Basic Attention Token'},
                         {'market': 'KRW-IOST', 'korean_name': '아이오에스티', 'english_name': 'IOST'},
                         {'market': 'KRW-RFR', 'korean_name': '리퍼리움', 'english_name': 'Refereum'},
                         {'market': 'KRW-CVC', 'korean_name': '시빅', 'english_name': 'Civic'},
                         {'market': 'KRW-IQ', 'korean_name': '에브리피디아', 'english_name': 'Everipedia'},
                         {'market': 'KRW-IOTA', 'korean_name': '아이오타', 'english_name': 'IOTA'},
                         {'market': 'KRW-MFT', 'korean_name': '메인프레임', 'english_name': 'Mainframe'},
                         {'market': 'KRW-ONG', 'korean_name': '온톨로지가스', 'english_name': 'ONG'},
                         {'market': 'KRW-GAS', 'korean_name': '가스', 'english_name': 'GAS'},
                         {'market': 'KRW-UPP', 'korean_name': '센티넬프로토콜', 'english_name': 'Sentinel Protocol'},
                         {'market': 'KRW-ELF', 'korean_name': '엘프', 'english_name': 'aelf'},
                         {'market': 'KRW-KNC', 'korean_name': '카이버네트워크', 'english_name': 'Kyber Network'},
                         {'market': 'KRW-BSV', 'korean_name': '비트코인에스브이', 'english_name': 'Bitcoin SV'},
                         {'market': 'KRW-THETA', 'korean_name': '쎄타토큰', 'english_name': 'Theta Token'},
                         {'market': 'KRW-QKC', 'korean_name': '쿼크체인', 'english_name': 'QuarkChain'},
                         {'market': 'KRW-BTT', 'korean_name': '비트토렌트', 'english_name': 'BitTorrent'},
                         {'market': 'KRW-MOC', 'korean_name': '모스코인', 'english_name': 'Moss Coin'},
                         {'market': 'KRW-ENJ', 'korean_name': '엔진코인', 'english_name': 'Enjin'},
                         {'market': 'KRW-TFUEL', 'korean_name': '쎄타퓨엘', 'english_name': 'Theta Fuel'},
                         {'market': 'KRW-MANA', 'korean_name': '디센트럴랜드', 'english_name': 'Decentraland'},
                         {'market': 'KRW-ANKR', 'korean_name': '앵커', 'english_name': 'Ankr'},
                         {'market': 'KRW-AERGO', 'korean_name': '아르고', 'english_name': 'Aergo'},
                         {'market': 'KRW-ATOM', 'korean_name': '코스모스', 'english_name': 'Cosmos'},
                         {'market': 'KRW-TT', 'korean_name': '썬더토큰', 'english_name': 'Thunder Token'},
                         {'market': 'KRW-CRE', 'korean_name': '캐리프로토콜', 'english_name': 'Carry Protocol'},
                         {'market': 'KRW-MBL', 'korean_name': '무비블록', 'english_name': 'MovieBloc'},
                         {'market': 'KRW-WAXP', 'korean_name': '왁스', 'english_name': 'WAX'},
                         # {'market': 'KRW-HBAR', 'korean_name': '헤데라해시그래프', 'english_name': 'Hedera Hashgraph'},
                         {'market': 'KRW-MED', 'korean_name': '메디블록', 'english_name': 'MediBloc'},
                         # {'market': 'KRW-MLK', 'korean_name': '밀크', 'english_name': 'MiL.k'},
                         # {'market': 'KRW-STPT', 'korean_name': '에스티피', 'english_name': 'Standard Tokenization Protocol'},
                         # {'market': 'KRW-ORBS', 'korean_name': '오브스', 'english_name': 'Orbs'},
                         # {'market': 'KRW-VET', 'korean_name': '비체인', 'english_name': 'VeChain'},
                         # {'market': 'KRW-CHZ', 'korean_name': '칠리즈', 'english_name': 'Chiliz'},
                         {'market': 'KRW-STMX', 'korean_name': '스톰엑스', 'english_name': 'StormX'},
                         # {'market': 'KRW-DKA', 'korean_name': '디카르고', 'english_name': 'dKargo'},
                         # {'market': 'KRW-HIVE', 'korean_name': '하이브', 'english_name': 'Hive'},
                         # {'market': 'KRW-KAVA', 'korean_name': '카바', 'english_name': 'Kava'},
                         # {'market': 'KRW-AHT', 'korean_name': '아하토큰', 'english_name': 'AhaToken'},
                         # {'market': 'KRW-LINK', 'korean_name': '체인링크', 'english_name': 'Chainlink'},
                         # {'market': 'KRW-XTZ', 'korean_name': '테조스', 'english_name': 'Tezos'},
                         # {'market': 'KRW-BORA', 'korean_name': '보라', 'english_name': 'BORA'},
                         # {'market': 'KRW-JST', 'korean_name': '저스트', 'english_name': 'JUST'},
                         # {'market': 'KRW-CRO', 'korean_name': '크립토닷컴체인', 'english_name': 'Crypto.com Chain'},
                         # {'market': 'KRW-TON', 'korean_name': '톤', 'english_name': 'TON'},
                         # {'market': 'KRW-SXP', 'korean_name': '스와이프', 'english_name': 'Swipe'},
                         # {'market': 'KRW-HUNT', 'korean_name': '헌트', 'english_name': 'HUNT'},
                         # {'market': 'KRW-PLA', 'korean_name': '플레이댑', 'english_name': 'PlayDapp'},
                         # {'market': 'KRW-DOT', 'korean_name': '폴카닷', 'english_name': 'Polkadot'},
                         # {'market': 'KRW-SRM', 'korean_name': '세럼', 'english_name': 'Serum'},
                         # {'market': 'KRW-MVL', 'korean_name': '엠블', 'english_name': 'MVL'},
                         {'market': 'KRW-STRAX', 'korean_name': '스트라티스', 'english_name': 'Stratis'},
                         # {'market': 'KRW-AQT', 'korean_name': '알파쿼크', 'english_name': 'Alpha Quark Token'},
                         # {'market': 'KRW-BCHA', 'korean_name': '비트코인캐시에이비씨', 'english_name': 'Bitcoin Cash ABC'},
                         {'market': 'KRW-GLM', 'korean_name': '골렘', 'english_name': 'Golem'},
                         # {'market': 'KRW-SSX', 'korean_name': '썸씽', 'english_name': 'SOMESING'},
                         # {'market': 'KRW-META', 'korean_name': '메타디움', 'english_name': 'Metadium'},
                         # {'market': 'KRW-FCT2', 'korean_name': '피르마체인', 'english_name': 'FirmaChain'},
                         # {'market': 'KRW-CBK', 'korean_name': '코박토큰', 'english_name': 'Cobak Token'},
                         # {'market': 'KRW-SAND', 'korean_name': '샌드박스', 'english_name': 'The Sandbox'},
                         # {'market': 'KRW-HUM', 'korean_name': '휴먼스케이프', 'english_name': 'Humanscape'},
                         # {'market': 'KRW-DOGE', 'korean_name': '도지코인', 'english_name': 'Dogecoin'},
                         # {'market': 'KRW-STRK', 'korean_name': '스트라이크', 'english_name': 'Strike'},
                         {'market': 'KRW-PUNDIX', 'korean_name': '펀디엑스', 'english_name': 'Pundi X'},
                         # {'market': 'KRW-FLOW', 'korean_name': '플로우', 'english_name': 'Flow'},
                         # {'market': 'KRW-DAWN', 'korean_name': '던프로토콜', 'english_name': 'Dawn Protocol'},
                         # {'market': 'KRW-AXS', 'korean_name': '엑시인피니티', 'english_name': 'Axie Infinity'},
                         # {'market': 'KRW-STX', 'korean_name': '스택스', 'english_name': 'Stacks'}
                    ]
        # print(len(market_lists))
        return market_lists


back_exchange = None  # BackExchange()


def get_back_exchange():
    return back_exchange


def create_back_exchange():
    global back_exchange
    back_exchange = BackExchange()
    return back_exchange

import datetime

import pandas
from log.logging_api import *


class BackExchange:
    def __init__(self):
        self.index = 30  # for searching Max 30days Profit
        self.sub_index = self.index * 24
        self.start_money = 10000000
        self.sim_day_num = 500
        self.sim_balance = [{'currency': 'KRW',
                             'balance': str(float(self.start_money)),
                             'locked': '0.0',
                             'avg_buy_price': '0',
                             'avg_buy_price_modified': True,
                             'unit_currency': 'KRW'}]
        self.fee_ratio = 0.0005

        logger.debug("=== DataFrame Load Start ===")
        self.df_dict = {}
        tickers = self.get_tickers()
        count = 0
        for ticker in tickers:
            file_name = "db/" + ticker + "_org.xlsx"
            df = pandas.read_excel(file_name, engine='openpyxl')
            df.set_index('Unnamed: 0', inplace=True)
            self.df_dict[ticker] = df
            logger.debug(ticker + " DataFrame is Added " + str(count))
            count += 1

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
        file_name = "db/" + ticker + "_mod.xlsx"
        # print(file_name)
        df = pandas.read_excel(file_name, engine='openpyxl')
        df.set_index('Unnamed: 0', inplace=True)
        slicing_df = df.iloc[self.index - count: self.index]
        # print(slicing_df)
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
            print(x.__class__.__name__)
            return None

    def get_orderbook(self, tickers="KRW-BTC"):
        try:
            # file_name = "db/" + tickers + "_org.xlsx"
            # df = pandas.read_excel(file_name, engine='openpyxl')
            # df.set_index('Unnamed: 0', inplace=True)
            df = self.df_dict[tickers]
            slicing_df = df.iloc[self.sub_index: self.sub_index + 1]
            # print(slicing_df)
            contents = [{'market': tickers,
                         'timestamp': slicing_df.index[0],
                         'total_ask_size': float(slicing_df['volume']),
                         'total_bid_size': float(slicing_df['volume']),
                         'orderbook_units': [{'ask_price': float(slicing_df['high']),
                                              'bid_price': float(slicing_df['low']),
                                              'ask_size': float(slicing_df['volume']),
                                              'bid_size': float(slicing_df['volume'])}]}]

            # logger.debug("*****************")
            return contents
        except Exception as x:
            print(x.__class__.__name__)
            return None

    def buy_market_order(self, ticker, price, contain_req=False):
        try:
            df = self.df_dict[ticker]
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

            if is_already_has_ticker is True:
                target_price = float(slicing_df['high'])
                total_price = (float(self.sim_balance[i]['avg_buy_price']) * float(self.sim_balance[i]['balance']))\
                                 + float(price)
                balance = float(price) / target_price + float(self.sim_balance[i]['balance'])
                avg_buy_price = float(total_price) / float(balance)
                self.sim_balance[i]['balance'] = str(balance)
                self.sim_balance[i]['avg_buy_price'] = str(avg_buy_price)
            else:
                avg_buy_price = float(slicing_df['high'])
                balance = float(price) / avg_buy_price
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

            print(self.sim_balance)
            print(result)

            return result
        except Exception as x:
            print(x.__class__.__name__)
            return None

    def get_current_price(self, order_currency, payment_currency="KRW"):
        resp = None
        try:
            ticker = payment_currency + "-" + order_currency
            df = self.df_dict[ticker]
            slicing_df = df.iloc[self.sub_index: self.sub_index + 1]
            print(ticker)
            print(slicing_df)
            resp = float(slicing_df['close'])

            print("===========")
            print(resp)
            print("***********")
            return resp

        except Exception:
            print(x.__class__.__name__)
            return resp

    def get_sim_start_time(self):
        file_name = "db/KRW-BTC_mod.xlsx"
        df = pandas.read_excel(file_name, engine='openpyxl')
        df.set_index('Unnamed: 0', inplace=True)
        return df.index[self.index-1]

    def set_sim_index_update(self):
        self.index += 1
        self.sub_index = self.index * 24

    def get_sim_index_update(self):
        return self.index

    def set_sim_sub_index_update(self):
        self.sub_index += 1

    def get_sim_sub_index_update(self):
        return self.sub_index

    def fetch_market(self):
        # market_lists = [{'market': 'KRW-BTC', 'korean_name': '비트코인', 'english_name': 'Bitcoin'}, {'market': 'KRW-ETH', 'korean_name': '이더리움', 'english_name': 'Ethereum'}, {'market': 'BTC-ETH', 'korean_name': '이더리움', 'english_name': 'Ethereum'}, {'market': 'BTC-LTC', 'korean_name': '라이트코인', 'english_name': 'Litecoin'}, {'market': 'BTC-XRP', 'korean_name': '리플', 'english_name': 'Ripple'}, {'market': 'BTC-ETC', 'korean_name': '이더리움클래식', 'english_name': 'Ethereum Classic'}, {'market': 'BTC-OMG', 'korean_name': '오미세고', 'english_name': 'OmiseGo'}, {'market': 'BTC-CVC', 'korean_name': '시빅', 'english_name': 'Civic'}, {'market': 'BTC-DGB', 'korean_name': '디지바이트', 'english_name': 'DigiByte'}, {'market': 'BTC-SC', 'korean_name': '시아코인', 'english_name': 'Siacoin'}, {'market': 'BTC-SNT', 'korean_name': '스테이터스네트워크토큰', 'english_name': 'Status Network Token'}, {'market': 'BTC-WAVES', 'korean_name': '웨이브', 'english_name': 'Waves'}, {'market': 'BTC-NMR', 'korean_name': '뉴메레르', 'english_name': 'Numeraire'}, {'market': 'BTC-XEM', 'korean_name': '넴', 'english_name': 'NEM'}, {'market': 'BTC-QTUM', 'korean_name': '퀀텀', 'english_name': 'Qtum'}, {'market': 'BTC-BAT', 'korean_name': '베이직어텐션토큰', 'english_name': 'Basic Attention Token'}, {'market': 'BTC-LSK', 'korean_name': '리스크', 'english_name': 'Lisk'}, {'market': 'BTC-STEEM', 'korean_name': '스팀', 'english_name': 'Steem'}, {'market': 'BTC-DOGE', 'korean_name': '도지코인', 'english_name': 'Dogecoin'}, {'market': 'BTC-BNT', 'korean_name': '뱅코르', 'english_name': 'Bancor'}, {'market': 'BTC-XLM', 'korean_name': '스텔라루멘', 'english_name': 'Lumen'}, {'market': 'BTC-ARDR', 'korean_name': '아더', 'english_name': 'Ardor'}, {'market': 'BTC-ARK', 'korean_name': '아크', 'english_name': 'Ark'}, {'market': 'BTC-STORJ', 'korean_name': '스토리지', 'english_name': 'Storj'}, {'market': 'BTC-GRS', 'korean_name': '그로스톨코인', 'english_name': 'Groestlcoin'}, {'market': 'BTC-REP', 'korean_name': '어거', 'english_name': 'Augur'}, {'market': 'BTC-RLC', 'korean_name': '아이젝', 'english_name': 'iEx.ec'}, {'market': 'USDT-BTC', 'korean_name': '비트코인', 'english_name': 'Bitcoin'}, {'market': 'USDT-ETH', 'korean_name': '이더리움', 'english_name': 'Ethereum'}, {'market': 'USDT-LTC', 'korean_name': '라이트코인', 'english_name': 'Litecoin'}, {'market': 'USDT-XRP', 'korean_name': '리플', 'english_name': 'Ripple'}, {'market': 'USDT-ETC', 'korean_name': '이더리움클래식', 'english_name': 'Ethereum Classic'}, {'market': 'KRW-NEO', 'korean_name': '네오', 'english_name': 'NEO'}, {'market': 'KRW-MTL', 'korean_name': '메탈', 'english_name': 'Metal'}, {'market': 'KRW-LTC', 'korean_name': '라이트코인', 'english_name': 'Litecoin'}, {'market': 'KRW-XRP', 'korean_name': '리플', 'english_name': 'Ripple'}, {'market': 'KRW-ETC', 'korean_name': '이더리움클래식', 'english_name': 'Ethereum Classic'}, {'market': 'KRW-OMG', 'korean_name': '오미세고', 'english_name': 'OmiseGo'}, {'market': 'KRW-SNT', 'korean_name': '스테이터스네트워크토큰', 'english_name': 'Status Network Token'}, {'market': 'KRW-WAVES', 'korean_name': '웨이브', 'english_name': 'Waves'}, {'market': 'KRW-XEM', 'korean_name': '넴', 'english_name': 'NEM'}, {'market': 'KRW-QTUM', 'korean_name': '퀀텀', 'english_name': 'Qtum'}, {'market': 'KRW-LSK', 'korean_name': '리스크', 'english_name': 'Lisk'}, {'market': 'KRW-STEEM', 'korean_name': '스팀', 'english_name': 'Steem'}, {'market': 'KRW-XLM', 'korean_name': '스텔라루멘', 'english_name': 'Lumen'}, {'market': 'KRW-ARDR', 'korean_name': '아더', 'english_name': 'Ardor'}, {'market': 'KRW-ARK', 'korean_name': '아크', 'english_name': 'Ark'}, {'market': 'KRW-STORJ', 'korean_name': '스토리지', 'english_name': 'Storj'}, {'market': 'KRW-GRS', 'korean_name': '그로스톨코인', 'english_name': 'Groestlcoin'}, {'market': 'KRW-REP', 'korean_name': '어거', 'english_name': 'Augur'}, {'market': 'KRW-ADA', 'korean_name': '에이다', 'english_name': 'Ada'}, {'market': 'BTC-ADA', 'korean_name': '에이다', 'english_name': 'Ada'}, {'market': 'BTC-MANA', 'korean_name': '디센트럴랜드', 'english_name': 'Decentraland'}, {'market': 'USDT-OMG', 'korean_name': '오미세고', 'english_name': 'OmiseGo'}, {'market': 'KRW-SBD', 'korean_name': '스팀달러', 'english_name': 'SteemDollars'}, {'market': 'BTC-SBD', 'korean_name': '스팀달러', 'english_name': 'SteemDollars'}, {'market': 'KRW-POWR', 'korean_name': '파워렛저', 'english_name': 'Power ledger'}, {'market': 'BTC-POWR', 'korean_name': '파워렛저', 'english_name': 'Power ledger'}, {'market': 'KRW-BTG', 'korean_name': '비트코인골드', 'english_name': 'Bitcoin Gold'}, {'market': 'USDT-ADA', 'korean_name': '에이다', 'english_name': 'Ada'}, {'market': 'BTC-DNT', 'korean_name': '디스트릭트0x', 'english_name': 'district0x'}, {'market': 'BTC-ZRX', 'korean_name': '제로엑스', 'english_name': '0x Protocol'}, {'market': 'BTC-TRX', 'korean_name': '트론', 'english_name': 'TRON'}, {'market': 'BTC-TUSD', 'korean_name': '트루USD', 'english_name': 'TrueUSD'}, {'market': 'BTC-LRC', 'korean_name': '루프링', 'english_name': 'Loopring'}, {'market': 'KRW-ICX', 'korean_name': '아이콘', 'english_name': 'Icon'}, {'market': 'KRW-EOS', 'korean_name': '이오스', 'english_name': 'EOS'}, {'market': 'USDT-TUSD', 'korean_name': '트루USD', 'english_name': 'TrueUSD'}, {'market': 'KRW-TRX', 'korean_name': '트론', 'english_name': 'TRON'}, {'market': 'BTC-POLY', 'korean_name': '폴리매쓰', 'english_name': 'Polymath'}, {'market': 'USDT-SC', 'korean_name': '시아코인', 'english_name': 'Siacoin'}, {'market': 'USDT-TRX', 'korean_name': '트론', 'english_name': 'TRON'}, {'market': 'KRW-SC', 'korean_name': '시아코인', 'english_name': 'Siacoin'}, {'market': 'KRW-ONT', 'korean_name': '온톨로지', 'english_name': 'Ontology'}, {'market': 'KRW-ZIL', 'korean_name': '질리카', 'english_name': 'Zilliqa'}, {'market': 'KRW-POLY', 'korean_name': '폴리매쓰', 'english_name': 'Polymath'}, {'market': 'KRW-ZRX', 'korean_name': '제로엑스', 'english_name': '0x Protocol'}, {'market': 'KRW-LOOM', 'korean_name': '룸네트워크', 'english_name': 'Loom Network'}, {'market': 'BTC-BCH', 'korean_name': '비트코인캐시', 'english_name': 'Bitcoin Cash'}, {'market': 'USDT-BCH', 'korean_name': '비트코인캐시', 'english_name': 'Bitcoin Cash'}, {'market': 'KRW-BCH', 'korean_name': '비트코인캐시', 'english_name': 'Bitcoin Cash'}, {'market': 'BTC-MFT', 'korean_name': '메인프레임', 'english_name': 'Mainframe'}, {'market': 'BTC-LOOM', 'korean_name': '룸네트워크', 'english_name': 'Loom Network'}, {'market': 'KRW-BAT', 'korean_name': '베이직어텐션토큰', 'english_name': 'Basic Attention Token'}, {'market': 'KRW-IOST', 'korean_name': '아이오에스티', 'english_name': 'IOST'}, {'market': 'BTC-RFR', 'korean_name': '리퍼리움', 'english_name': 'Refereum'}, {'market': 'KRW-RFR', 'korean_name': '리퍼리움', 'english_name': 'Refereum'}, {'market': 'USDT-DGB', 'korean_name': '디지바이트', 'english_name': 'DigiByte'}, {'market': 'KRW-CVC', 'korean_name': '시빅', 'english_name': 'Civic'}, {'market': 'KRW-IQ', 'korean_name': '에브리피디아', 'english_name': 'Everipedia'}, {'market': 'KRW-IOTA', 'korean_name': '아이오타', 'english_name': 'IOTA'}, {'market': 'BTC-RVN', 'korean_name': '레이븐코인', 'english_name': 'Ravencoin'}, {'market': 'BTC-GO', 'korean_name': '고체인', 'english_name': 'GoChain'}, {'market': 'BTC-UPP', 'korean_name': '센티넬프로토콜', 'english_name': 'Sentinel Protocol'}, {'market': 'BTC-ENJ', 'korean_name': '엔진코인', 'english_name': 'Enjin'}, {'market': 'KRW-MFT', 'korean_name': '메인프레임', 'english_name': 'Mainframe'}, {'market': 'KRW-ONG', 'korean_name': '온톨로지가스', 'english_name': 'ONG'}, {'market': 'KRW-GAS', 'korean_name': '가스', 'english_name': 'GAS'}, {'market': 'BTC-MTL', 'korean_name': '메탈', 'english_name': 'Metal'}, {'market': 'KRW-UPP', 'korean_name': '센티넬프로토콜', 'english_name': 'Sentinel Protocol'}, {'market': 'KRW-ELF', 'korean_name': '엘프', 'english_name': 'aelf'}, {'market': 'USDT-DOGE', 'korean_name': '도지코인', 'english_name': 'Dogecoin'}, {'market': 'USDT-ZRX', 'korean_name': '제로엑스', 'english_name': '0x Protocol'}, {'market': 'USDT-RVN', 'korean_name': '레이븐코인', 'english_name': 'Ravencoin'}, {'market': 'USDT-BAT', 'korean_name': '베이직어텐션토큰', 'english_name': 'Basic Attention Token'}, {'market': 'KRW-KNC', 'korean_name': '카이버네트워크', 'english_name': 'Kyber Network'}, {'market': 'BTC-PAX', 'korean_name': '팩소스스탠다드', 'english_name': 'Paxos Standard'}, {'market': 'BTC-MOC', 'korean_name': '모스코인', 'english_name': 'Moss Coin'}, {'market': 'BTC-ZIL', 'korean_name': '질리카', 'english_name': 'Zilliqa'}, {'market': 'KRW-BSV', 'korean_name': '비트코인에스브이', 'english_name': 'Bitcoin SV'}, {'market': 'BTC-BSV', 'korean_name': '비트코인에스브이', 'english_name': 'Bitcoin SV'}, {'market': 'BTC-IOST', 'korean_name': '아이오에스티', 'english_name': 'IOST'}, {'market': 'KRW-THETA', 'korean_name': '쎄타토큰', 'english_name': 'Theta Token'}, {'market': 'BTC-DENT', 'korean_name': '덴트', 'english_name': 'Dent'}, {'market': 'KRW-QKC', 'korean_name': '쿼크체인', 'english_name': 'QuarkChain'}, {'market': 'BTC-ELF', 'korean_name': '엘프', 'english_name': 'aelf'}, {'market': 'KRW-BTT', 'korean_name': '비트토렌트', 'english_name': 'BitTorrent'}, {'market': 'BTC-BTT', 'korean_name': '비트토렌트', 'english_name': 'BitTorrent'}, {'market': 'BTC-IOTX', 'korean_name': '아이오텍스', 'english_name': 'IoTeX'}, {'market': 'BTC-SOLVE', 'korean_name': '솔브케어', 'english_name': 'Solve.Care'}, {'market': 'BTC-NKN', 'korean_name': '엔케이엔', 'english_name': 'NKN'}, {'market': 'BTC-META', 'korean_name': '메타디움', 'english_name': 'Metadium'}, {'market': 'KRW-MOC', 'korean_name': '모스코인', 'english_name': 'Moss Coin'}, {'market': 'BTC-ANKR', 'korean_name': '앵커', 'english_name': 'Ankr'}, {'market': 'BTC-CRO', 'korean_name': '크립토닷컴체인', 'english_name': 'Crypto.com Chain'}, {'market': 'KRW-ENJ', 'korean_name': '엔진코인', 'english_name': 'Enjin'}, {'market': 'KRW-TFUEL', 'korean_name': '쎄타퓨엘', 'english_name': 'Theta Fuel'}, {'market': 'KRW-MANA', 'korean_name': '디센트럴랜드', 'english_name': 'Decentraland'}, {'market': 'KRW-ANKR', 'korean_name': '앵커', 'english_name': 'Ankr'}, {'market': 'BTC-ORBS', 'korean_name': '오브스', 'english_name': 'Orbs'}, {'market': 'BTC-AERGO', 'korean_name': '아르고', 'english_name': 'Aergo'}, {'market': 'KRW-AERGO', 'korean_name': '아르고', 'english_name': 'Aergo'}, {'market': 'KRW-ATOM', 'korean_name': '코스모스', 'english_name': 'Cosmos'}, {'market': 'KRW-TT', 'korean_name': '썬더토큰', 'english_name': 'Thunder Token'}, {'market': 'KRW-CRE', 'korean_name': '캐리프로토콜', 'english_name': 'Carry Protocol'}, {'market': 'BTC-ATOM', 'korean_name': '코스모스', 'english_name': 'Cosmos'}, {'market': 'BTC-STPT', 'korean_name': '에스티피', 'english_name': 'Standard Tokenization Protocol'}, {'market': 'KRW-MBL', 'korean_name': '무비블록', 'english_name': 'MovieBloc'}, {'market': 'BTC-EOS', 'korean_name': '이오스', 'english_name': 'EOS'}, {'market': 'BTC-LUNA', 'korean_name': '루나', 'english_name': 'Luna'}, {'market': 'BTC-DAI', 'korean_name': '다이', 'english_name': 'Dai'}, {'market': 'BTC-MKR', 'korean_name': '메이커', 'english_name': 'Maker'}, {'market': 'BTC-BORA', 'korean_name': '보라', 'english_name': 'BORA'}, {'market': 'KRW-WAXP', 'korean_name': '왁스', 'english_name': 'WAX'}, {'market': 'BTC-WAXP', 'korean_name': '왁스', 'english_name': 'WAX'}, {'market': 'KRW-HBAR', 'korean_name': '헤데라해시그래프', 'english_name': 'Hedera Hashgraph'}, {'market': 'KRW-MED', 'korean_name': '메디블록', 'english_name': 'MediBloc'}, {'market': 'BTC-MED', 'korean_name': '메디블록', 'english_name': 'MediBloc'}, {'market': 'BTC-MLK', 'korean_name': '밀크', 'english_name': 'MiL.k'}, {'market': 'KRW-MLK', 'korean_name': '밀크', 'english_name': 'MiL.k'}, {'market': 'KRW-STPT', 'korean_name': '에스티피', 'english_name': 'Standard Tokenization Protocol'}, {'market': 'BTC-VET', 'korean_name': '비체인', 'english_name': 'VeChain'}, {'market': 'KRW-ORBS', 'korean_name': '오브스', 'english_name': 'Orbs'}, {'market': 'BTC-CHZ', 'korean_name': '칠리즈', 'english_name': 'Chiliz'}, {'market': 'KRW-VET', 'korean_name': '비체인', 'english_name': 'VeChain'}, {'market': 'BTC-FX', 'korean_name': '펑션엑스', 'english_name': 'Function X'}, {'market': 'BTC-OGN', 'korean_name': '오리진프로토콜', 'english_name': 'Origin Protocol'}, {'market': 'KRW-CHZ', 'korean_name': '칠리즈', 'english_name': 'Chiliz'}, {'market': 'BTC-XTZ', 'korean_name': '테조스', 'english_name': 'Tezos'}, {'market': 'BTC-HIVE', 'korean_name': '하이브', 'english_name': 'Hive'}, {'market': 'BTC-HBD', 'korean_name': '하이브달러', 'english_name': 'Hive Dollar'}, {'market': 'BTC-OBSR', 'korean_name': '옵저버', 'english_name': 'Observer'}, {'market': 'BTC-DKA', 'korean_name': '디카르고', 'english_name': 'dKargo'}, {'market': 'KRW-STMX', 'korean_name': '스톰엑스', 'english_name': 'StormX'}, {'market': 'BTC-STMX', 'korean_name': '스톰엑스', 'english_name': 'StormX'}, {'market': 'BTC-AHT', 'korean_name': '아하토큰', 'english_name': 'AhaToken'}, {'market': 'BTC-PCI', 'korean_name': '페이코인', 'english_name': 'PayCoin'}, {'market': 'KRW-DKA', 'korean_name': '디카르고', 'english_name': 'dKargo'}, {'market': 'BTC-LINK', 'korean_name': '체인링크', 'english_name': 'Chainlink'}, {'market': 'KRW-HIVE', 'korean_name': '하이브', 'english_name': 'Hive'}, {'market': 'KRW-KAVA', 'korean_name': '카바', 'english_name': 'Kava'}, {'market': 'BTC-KAVA', 'korean_name': '카바', 'english_name': 'Kava'}, {'market': 'KRW-AHT', 'korean_name': '아하토큰', 'english_name': 'AhaToken'}, {'market': 'KRW-LINK', 'korean_name': '체인링크', 'english_name': 'Chainlink'}, {'market': 'KRW-XTZ', 'korean_name': '테조스', 'english_name': 'Tezos'}, {'market': 'KRW-BORA', 'korean_name': '보라', 'english_name': 'BORA'}, {'market': 'BTC-JST', 'korean_name': '저스트', 'english_name': 'JUST'}, {'market': 'BTC-CHR', 'korean_name': '크로미아', 'english_name': 'Chromia'}, {'market': 'BTC-DAD', 'korean_name': '다드', 'english_name': 'DAD'}, {'market': 'BTC-TON', 'korean_name': '톤', 'english_name': 'TON'}, {'market': 'KRW-JST', 'korean_name': '저스트', 'english_name': 'JUST'}, {'market': 'BTC-CTSI', 'korean_name': '카르테시', 'english_name': 'Cartesi'}, {'market': 'BTC-DOT', 'korean_name': '폴카닷', 'english_name': 'Polkadot'}, {'market': 'KRW-CRO', 'korean_name': '크립토닷컴체인', 'english_name': 'Crypto.com Chain'}, {'market': 'BTC-COMP', 'korean_name': '컴파운드', 'english_name': 'Compound'}, {'market': 'BTC-SXP', 'korean_name': '스와이프', 'english_name': 'Swipe'}, {'market': 'BTC-HUNT', 'korean_name': '헌트', 'english_name': 'HUNT'}, {'market': 'KRW-TON', 'korean_name': '톤', 'english_name': 'TON'}, {'market': 'BTC-ONIT', 'korean_name': '온버프', 'english_name': 'ONBUFF'}, {'market': 'BTC-CRV', 'korean_name': '커브', 'english_name': 'Curve'}, {'market': 'BTC-ALGO', 'korean_name': '알고랜드', 'english_name': 'Algorand'}, {'market': 'BTC-RSR', 'korean_name': '리저브라이트', 'english_name': 'Reserve Rights'}, {'market': 'KRW-SXP', 'korean_name': '스와이프', 'english_name': 'Swipe'}, {'market': 'BTC-OXT', 'korean_name': '오키드', 'english_name': 'Orchid'}, {'market': 'BTC-PLA', 'korean_name': '플레이댑', 'english_name': 'PlayDapp'}, {'market': 'KRW-HUNT', 'korean_name': '헌트', 'english_name': 'HUNT'}, {'market': 'BTC-MARO', 'korean_name': '마로', 'english_name': 'Maro'}, {'market': 'BTC-SAND', 'korean_name': '샌드박스', 'english_name': 'The Sandbox'}, {'market': 'BTC-SUN', 'korean_name': '썬', 'english_name': 'SUN'}, {'market': 'KRW-PLA', 'korean_name': '플레이댑', 'english_name': 'PlayDapp'}, {'market': 'KRW-DOT', 'korean_name': '폴카닷', 'english_name': 'Polkadot'}, {'market': 'BTC-SRM', 'korean_name': '세럼', 'english_name': 'Serum'}, {'market': 'BTC-QTCON', 'korean_name': '퀴즈톡', 'english_name': 'Quiztok'}, {'market': 'BTC-MVL', 'korean_name': '엠블', 'english_name': 'MVL'}, {'market': 'KRW-SRM', 'korean_name': '세럼', 'english_name': 'Serum'}, {'market': 'KRW-MVL', 'korean_name': '엠블', 'english_name': 'MVL'}, {'market': 'BTC-GXC', 'korean_name': '지엑스체인', 'english_name': 'GXChain'}, {'market': 'BTC-AQT', 'korean_name': '알파쿼크', 'english_name': 'Alpha Quark Token'}, {'market': 'BTC-AXS', 'korean_name': '엑시인피니티', 'english_name': 'Axie Infinity'}, {'market': 'BTC-STRAX', 'korean_name': '스트라티스', 'english_name': 'Stratis'}, {'market': 'KRW-STRAX', 'korean_name': '스트라티스', 'english_name': 'Stratis'}, {'market': 'KRW-AQT', 'korean_name': '알파쿼크', 'english_name': 'Alpha Quark Token'}, {'market': 'BTC-BCHA', 'korean_name': '비트코인캐시에이비씨', 'english_name': 'Bitcoin Cash ABC'}, {'market': 'KRW-BCHA', 'korean_name': '비트코인캐시에이비씨', 'english_name': 'Bitcoin Cash ABC'}, {'market': 'BTC-GLM', 'korean_name': '골렘', 'english_name': 'Golem'}, {'market': 'KRW-GLM', 'korean_name': '골렘', 'english_name': 'Golem'}, {'market': 'BTC-FCT2', 'korean_name': '피르마체인', 'english_name': 'FirmaChain'}, {'market': 'BTC-SSX', 'korean_name': '썸씽', 'english_name': 'SOMESING'}, {'market': 'KRW-SSX', 'korean_name': '썸씽', 'english_name': 'SOMESING'}, {'market': 'KRW-META', 'korean_name': '메타디움', 'english_name': 'Metadium'}, {'market': 'KRW-FCT2', 'korean_name': '피르마체인', 'english_name': 'FirmaChain'}, {'market': 'BTC-FIL', 'korean_name': '파일코인', 'english_name': 'Filecoin'}, {'market': 'BTC-UNI', 'korean_name': '유니스왑', 'english_name': 'Uniswap'}, {'market': 'BTC-BASIC', 'korean_name': '베이직', 'english_name': 'Basic'}, {'market': 'BTC-INJ', 'korean_name': '인젝티브프로토콜', 'english_name': 'Injective Protocol'}, {'market': 'BTC-PROM', 'korean_name': '프로메테우스', 'english_name': 'Prometeus'}, {'market': 'BTC-VAL', 'korean_name': '밸리디티', 'english_name': 'Validity'}, {'market': 'BTC-PSG', 'korean_name': '파리생제르맹', 'english_name': 'Paris Saint-Germain Fan Token'}, {'market': 'BTC-JUV', 'korean_name': '유벤투스', 'english_name': 'Juventus Fan Token'}, {'market': 'BTC-CBK', 'korean_name': '코박토큰', 'english_name': 'Cobak Token'}, {'market': 'BTC-FOR', 'korean_name': '포튜브', 'english_name': 'ForTube'}, {'market': 'KRW-CBK', 'korean_name': '코박토큰', 'english_name': 'Cobak Token'}, {'market': 'BTC-BFC', 'korean_name': '바이프로스트', 'english_name': 'Bifrost'}, {'market': 'BTC-LINA', 'korean_name': '리니어파이낸스', 'english_name': 'Linear'}, {'market': 'BTC-HUM', 'korean_name': '휴먼스케이프', 'english_name': 'Humanscape'}, {'market': 'BTC-CELO', 'korean_name': '셀로', 'english_name': 'Celo'}, {'market': 'KRW-SAND', 'korean_name': '샌드박스', 'english_name': 'The Sandbox'}, {'market': 'KRW-HUM', 'korean_name': '휴먼스케이프', 'english_name': 'Humanscape'}, {'market': 'BTC-IQ', 'korean_name': '에브리피디아', 'english_name': 'Everipedia'}, {'market': 'BTC-STX', 'korean_name': '스택스', 'english_name': 'Stacks'}, {'market': 'KRW-DOGE', 'korean_name': '도지코인', 'english_name': 'Dogecoin'}, {'market': 'BTC-NEAR', 'korean_name': '니어프로토콜', 'english_name': 'NEAR Protocol'}, {'market': 'BTC-AUCTION', 'korean_name': '바운스토큰', 'english_name': 'Bounce'}, {'market': 'BTC-DAWN', 'korean_name': '던프로토콜', 'english_name': 'Dawn Protocol'}, {'market': 'BTC-FLOW', 'korean_name': '플로우', 'english_name': 'Flow'}, {'market': 'BTC-STRK', 'korean_name': '스트라이크', 'english_name': 'Strike'}, {'market': 'KRW-STRK', 'korean_name': '스트라이크', 'english_name': 'Strike'}, {'market': 'BTC-PUNDIX', 'korean_name': '펀디엑스', 'english_name': 'Pundi X'}, {'market': 'KRW-PUNDIX', 'korean_name': '펀디엑스', 'english_name': 'Pundi X'}, {'market': 'KRW-FLOW', 'korean_name': '플로우', 'english_name': 'Flow'}, {'market': 'KRW-DAWN', 'korean_name': '던프로토콜', 'english_name': 'Dawn Protocol'}, {'market': 'KRW-AXS', 'korean_name': '엑시인피니티', 'english_name': 'Axie Infinity'}, {'market': 'KRW-STX', 'korean_name': '스택스', 'english_name': 'Stacks'}, {'market': 'BTC-GRT', 'korean_name': '그래프', 'english_name': 'The Graph'}, {'market': 'BTC-SNX', 'korean_name': '신세틱스', 'english_name': 'Synthetix'}]
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
        # print(len(market_lists))
        return market_lists


back_exchange = None  # BackExchange()


def get_back_exchange():
    return back_exchange


def create_back_exchange():
    global back_exchange
    back_exchange = BackExchange()
    return back_exchange

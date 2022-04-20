class Historical_Price:

    def __init__(self):
        import pandas as pd
        self.__history = dict()
        self.__history['ETH'] = self.__get_price_dict(pd.read_csv('token_price/eth.csv').iloc[::-1])
        self.__history['BTC'] = self.__get_price_dict(pd.read_csv('token_price/btc.csv').iloc[::-1])
        self.__history['MANA'] = self.__get_price_dict(pd.read_csv('token_price/mana.csv').iloc[::-1])
        self.__history['SAND'] = self.__get_price_dict(pd.read_csv('token_price/sand.csv').iloc[::-1])

    def __get_price_dict(self, df):
        from datetime import datetime
        return dict(zip(list(df['Date'].apply(lambda d : datetime.strptime(d, '%b %d, %Y').strftime('%Y-%m-%d'))),
                        list(df['Price'].apply(lambda p : float(p.replace(',', '')) if isinstance(p, str) else float(p)))))
    
    def get_token_historical_price(self, currency, date = ''):
        if currency == 'USDC' or currency == 'DAI':
            return 1.0
        if currency == 'ETH' or currency == 'BTC' or currency == 'MANA' or  currency == 'SAND':
            if date in self.__history[currency].keys():
                return self.__history[currency][date]
            else:
                # print latest price in csv
                return list(self.__history[currency].items())[0][1]
        return 1.0
    
    def get_token_historical_list(self, currency):
        if currency in self.__history.keys():
            return self.__history[currency]
'''

Executes all activities through the IGMarkets API.
@author: Cheso7

'''
import pandas as pd
from trading_ig import IGService

# Get environment login variables and assign to python variables in config file
import trading_ig_config


def IG_connect():
    #Connect to IGService
    ig_service = IGService(trading_ig_config.config.username, trading_ig_config.config.password,
                           trading_ig_config.config.api_key, trading_ig_config.config.acc_type)

    ig_service.create_session()
    #Print account details
    account = ig_service.fetch_accounts()
    print('Account_ID:', account.accountId)
    return ig_service


class Trading:
    def __init__(self, ig_service):
        self.ig_service = ig_service

    def open_positions(self):
        open_pos = self.ig_service.fetch_open_positions()
        index = open_pos.index
        number_of_rows = len(index)
        if number_of_rows > 0:
            opm_dict = open_pos['market'].to_dict()
            opp_dict = open_pos['position'].to_dict()
            opm_df = pd.DataFrame(opm_dict)
            opp_df = pd.DataFrame(opp_dict)
            open_pos_market = opm_df.transpose()
            open_pos_position = opp_df.transpose()
            open_pos = open_pos_market.join(open_pos_position)
        return open_pos
        print('You have no open positions')

    def price_data(self, epic, resolution, num_points):
        price_data = self.ig_service.fetch_historical_prices_by_epic_and_num_points(
             epic,
             resolution,
             num_points)
        price_data_df = price_data['prices']
        ohlc = price_data_df.iloc[:, [4, 5, 6, 7,12]]
        ohlc.columns = ['Open', 'High', 'Close', 'Low', 'Volume']
        return ohlc

    def open_trade(self, direction, epic, pos_size,limit, trailing_stop_distance, trailing_stop_increment):
        'Open a trade in either BUY or SELL direction'
        self.ig_service.create_open_position(
            currency_code='USD',
            direction=direction,
            epic=epic,
            expiry='-',
            force_open='true',
            guaranteed_stop='false',
            level=None,
            limit_distance=limit,
            limit_level=None,
            order_type='MARKET',
            size=pos_size,
            quote_id=None,
            stop_distance=trailing_stop_distance,
            stop_level=None,
            trailing_stop='true',
            trailing_stop_increment=trailing_stop_increment)
        print('New', direction, 'position initiated for', epic)

    def close_trade(self, long_short, epic, open_pos_cur):
        if long_short == 'short':
            close_dir = 'BUY'
        else:
            close_dir = 'SELL'

        self.ig_service.close_open_position(
            deal_id=None,
            direction=close_dir,
            epic=epic,
            expiry='-',
            level=None,
            order_type='MARKET',
            quote_id=None,
            size=str(open_pos_cur['dealSize'].tolist()[0]))
        print('Existing', long_short, 'position closed for', epic)

    def transaction_history(self, milliseconds):
        trade_data = self.ig_service.fetch_transaction_history_by_type_and_period(
            milliseconds, "ALL_DEAL")
        return trade_data
    
    def client_sentiment(self, epic):
        market_ID = self.market_by_epic(epic)
        client_sentiment = ''
        client_sentiment_data = self.ig_service.fetch_client_sentiment_by_instrument(market_ID)
        long = client_sentiment_data['longPositionPercentage']
        short = client_sentiment_data['shortPositionPercentage']

        if long > short:
            client_sentiment = 'bullish'
        else:
            client_sentiment = 'bearish'
        return client_sentiment

    def market_by_epic(self, epic):
        market = self.ig_service.fetch_market_by_epic(epic)
        market_ID = market['instrument']['marketId']
        return market_ID
# -*- coding: utf-8 -*-
"""
Executes all activities through the IGMarkets API.

@author: Cheso7

"""
import pandas as pd
from trading_ig import IGService
# Get environment login variables and assign to python variables in config file
import trading_ig_config

def IG_connect():
    #Connect to IGService
    ig_service = IGService(trading_ig_config.config.username, trading_ig_config.config.password, trading_ig_config.config.api_key, trading_ig_config.config.acc_type)
    ig_service.create_session()
    #Print account details
    account = ig_service.fetch_accounts()
    print("Account_ID:", account.accountId)
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
            print("You have no open positions")

        
    def open_trade(self, direction, epic, pos_size):
        "Open a trade in either BUY or SELL direction"
        self.ig_service.create_open_position(
            currency_code='USD',
            direction=direction,
            epic=epic,
            expiry="-",
            force_open="true",
            guaranteed_stop="false",
            level=None,
            limit_distance=None,
            limit_level=None,
            order_type="MARKET",
            size=pos_size,
            quote_id=None,
            stop_distance=None,
            stop_level=None,
            trailing_stop="false",
            trailing_stop_increment = None)
        print("New ", direction," position initiated for ", epic)

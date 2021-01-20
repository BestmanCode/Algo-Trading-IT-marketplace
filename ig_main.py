"""
Created on Sat Jan 16 09:46:22 2021

@author: Cheso7
"""
# Populate system environment variables with login variables
from dotenv import load_dotenv
load_dotenv()

# Import packages
import trading_ig
import numpy as np
import statsmodels.api as sm
import time
import copy
import pandas as pd


import ig_execute
import technical_indicators

from stocktrends import Renko
from trading_ig import IGService

#new_epic = ig_service.search_markets('woodside')


#defining strategy parameters
pairs = ['CS.D.ETHUSD.CFD.IP','CS.D.BITCOIN.CFD.IP', 'CS.D.LTCUSD.CFD.IP'] #epic pairs to be included in the strategy
pos_size = "1" #max capital allocated/position size for any epic pair
resolution = '5Min' #resolution of ohlc data
trailing_stop_increment = "200"
stop_distance = "1000"
num_points = 250 #number of data points

     
def main():
    try:
        ig_service = ig_execute.IG_connect()
        trading = ig_execute.Trading(ig_service)
        trading.open_positions()
       
        for epic in pairs:
            long_short = ""
            if len(open_pos)>0:
                open_pos_cur = open_pos[open_pos["epic"]==epic]
            if len(open_pos_cur)>0:
                if open_pos_cur["direction"].tolist()[0]=='BUY':
                    long_short = "long"
                elif open_pos_cur["direction"].tolist()[0]=='SELL':
                    long_short = "short"   

            price_data = ig_service.fetch_historical_prices_by_epic_and_num_points(epic, resolution, num_points)
            price_data_df = price_data['prices']
            ohlc = price_data_df.iloc[:,[4,5,6,7,12]]
            ohlc.columns = ["Open","High","Close","Low","Volume"]
            
            signal = trade_signal(renko_merge(ohlc),long_short)
            
            if len(signal) > 1:
                print(signal, 'for', epic)
            else:
                print("No signal for", epic)
            
            if signal == "BUY":
                ig_execute.open_trade(signal, epic, pos_size)
                # ig_service.create_open_position(
                #     currency_code='USD',
                #     direction="BUY",
                #     epic=epic,
                #     expiry="-",
                #     force_open="true",
                #     guaranteed_stop="false",
                #     level=None,
                #     limit_distance=None,
                #     limit_level=None,
                #     order_type="MARKET",
                #     size=pos_size,
                #     quote_id=None,
                #     stop_distance=None,
                #     stop_level=None,
                #     trailing_stop="false",
                #     trailing_stop_increment = None)
                # print("New long position initiated for ", epic)
                
            elif signal == "SELL":
                ig_execute.open_trade(signal, epic, pos_size)                
                # ig_service.create_open_position(
                #     currency_code='USD',
                #     direction="SELL",
                #     epic=epic,
                #     expiry="-",
                #     force_open="true",
                #     guaranteed_stop="false",
                #     level=None,
                #     limit_distance=None,
                #     limit_level=None,
                #     order_type="MARKET",
                #     size=pos_size,
                #     quote_id=None,
                #     stop_distance=None,
                #     stop_level=None,
                #     trailing_stop="false",
                #     trailing_stop_increment = None)
                # print("New short position initiated for ", epic)
                
            elif signal == "Close":
            
                close_dir ="SELL"
                
                if open_pos_cur['direction'].tolist()[0] == 'SELL':
                    close_dir = 'BUY'
     
                ig_service.close_open_position(
                    deal_id = None,
                    direction = close_dir,
                    epic = epic,
                    expiry="-",
                    level = None,
                    order_type = "MARKET",
                    quote_id = None,
                    size = str(open_pos_cur['dealSize'].tolist()[0]))
                
                print("All positions closed for ", epic)
                
            elif signal == "Close_Buy":
                
                close_dir ="SELL"
                
                if open_pos_cur['direction'].tolist()[0] == 'SELL':
                    close_dir = 'BUY'
           
                ig_service.close_open_position(
                    deal_id = None,
                    direction = close_dir,
                    epic = epic,
                    expiry="-",
                    level = None,
                    order_type = "MARKET",
                    quote_id = None,
                    size = str(open_pos_cur['dealSize'].tolist()[0]))
                
                print("Existing Short position closed for ", epic)
                
                ig_service.create_open_position(
                    currency_code='USD',
                    direction="BUY",
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
                print("New long position initiated for ", epic)
                
            elif signal == "Close_Sell":
                
                close_dir ="SELL"
                
                if open_pos_cur['direction'].tolist()[0] == 'SELL':
                    close_dir = 'BUY'
           
                ig_service.close_open_position(
                    deal_id = None,
                    direction = close_dir,
                    epic = epic,
                    expiry="-",
                    level = None,
                    order_type = "MARKET",
                    quote_id = None,
                    size = str(open_pos_cur['dealSize'].tolist()[0]))
                print("Existing long position closed for ", epic)
                
                ig_service.create_open_position(
                    currency_code='USD',
                    direction="SELL",
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
                print("New short position initiated for ", epic)
    except Exception as e:
        print(e)

def trade_signal(MERGED_DF,l_s):
    "function to generate signal"
    signal = ""
    df = copy.deepcopy(MERGED_DF)
    if l_s == "":
        if df["bar_num"].tolist()[-1]>=2 and df["macd"].tolist()[-1]>df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]>df["macd_sig_slope"].tolist()[-1]:
            signal = "BUY"
        elif df["bar_num"].tolist()[-1]<=-2 and df["macd"].tolist()[-1]<df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]<df["macd_sig_slope"].tolist()[-1]:
            signal = "SELL"
            
    elif l_s == "long":
        if df["bar_num"].tolist()[-1]<=-2 and df["macd"].tolist()[-1]<df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]<df["macd_sig_slope"].tolist()[-1]:
            signal = "Close_Sell"
        elif df["macd"].tolist()[-1]<df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]<df["macd_sig_slope"].tolist()[-1]:
            signal = "Close"
            
    elif l_s == "short":
        if df["bar_num"].tolist()[-1]>=2 and df["macd"].tolist()[-1]>df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]>df["macd_sig_slope"].tolist()[-1]:
            signal = "Close_Buy"
        elif df["macd"].tolist()[-1]>df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]>df["macd_sig_slope"].tolist()[-1]:
            signal = "Close"
    return signal
    
starttime=time.time()
timeout = time.time() + 60*60*8  # 60 seconds times 60 meaning the script will run for 1 hr
while time.time() <= timeout:
    try:
        print("passthrough at ",time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        main()
        time.sleep(300 - ((time.time() - starttime) % 300.0)) # 5 minute interval between each new execution
    except KeyboardInterrupt:
        print('\n\nKeyboard exception received. Exiting.')
        exit()

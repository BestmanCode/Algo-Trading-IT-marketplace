'''
@author: Cheso7
'''
# Populate system environment variables with login variables
from dotenv import load_dotenv
load_dotenv()

# Import packages
import sys
import time
import ig_execute
import technical_indicators
import trading_strategy
import kpi


# Define trading parameters
pairs = ['CS.D.ETHUSD.CFD.IP',
         'CS.D.BITCOIN.CFD.IP', 
         'CS.D.LTCUSD.CFD.IP'] # Epic pairs to be included in the strategy
pos_size = '1' #max capital allocated/position size for any epic pair
resolution = '1Min' #resolution of ohlc data
trailing_stop_increment = '200'
stop_distance = '1000'
num_points = 250 #number of data points
runtime = 8 #run time of trading strategy in hours
trading_frequency = 1 #frequency to trade in minutes - match to data resolution
     
#Connect to the IG Markets API and return current positions
ig_service = ig_execute.IG_connect()
trading = ig_execute.Trading(ig_service)

def main():
    try:
        open_pos = trading.open_positions()
        #Determine if position is long or short
        for epic in pairs: 
            long_short = ''
            if len(open_pos)>0:
                open_pos_cur = open_pos[open_pos['epic']==epic]
        
                if len(open_pos_cur)>0:
                    if open_pos_cur['direction'].tolist()[0]=='BUY': 
                        long_short = 'long'
                    elif open_pos_cur['direction'].tolist()[0]=='SELL': 
                        long_short = 'short'   

            #Return historic OHLC price data for the epic based on resolution and number of points.
            ohlc = trading.price_data(epic, resolution, num_points)

            #Calculate the signal for the trade based off the chosen strategy
            signal = trading_strategy.signal_1(technical_indicators.renko_merge(ohlc),long_short)
            
            if len(signal) > 1:
                print(signal, 'for', epic)
            else:
                print('No signal for', epic)
            
            if signal in('BUY', 'SELL'):
                trading.open_trade(signal, epic, pos_size)
                             
            elif signal == 'Close':
                trading.close_trade(long_short, epic, open_pos_cur)
                
            elif signal == 'Close_Buy':
                direction = 'BUY'
                trading.close_trade(long_short, epic, open_pos_cur)
                trading.open_trade(direction, epic, pos_size)
                
            elif signal == 'Close_Sell':
                direction = 'SELL'
                trading.close_trade(long_short, epic, open_pos_cur)
                trading.open_trade(direction, epic, pos_size)   
            
    except Exception as e:
        print(e)


starttime=time.time()
timeout = time.time() + 60*60*runtime
session_time = timeout - starttime

while time.time() <= timeout:
    try:
        print('passthrough at ',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        main()
        time.sleep(trading_frequency*60 - ((time.time() - starttime) % trading_frequency*60))
    except KeyboardInterrupt:
        print('\n\nKeyboard exception received. Exiting.')
        sys.exit()

#trade_data = trading.trade_history(session_time)
trade_data = trading.transaction_history(36000000)
performance = kpi.performance_measure(trade_data, session_time)

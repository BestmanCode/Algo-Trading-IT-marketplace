"""
@author: Cheso7
   TODO: Database strategy performance
"""

# Import packages
import pandas as pd
import time
import sys

# Import Python scripts
import trading_performance
import trading_strategy
import technical_indicators
import ig_execute

# Populate system environment variables with login variables
from dotenv import load_dotenv

load_dotenv()

# Define trading parameters
pairs = ["CS.D.ETHUSD.CFD.IP"]
pos_size = "1"  # max capital allocated/position size for any epic pair
resolution = "1Min"  # resolution of ohlc data
trailing_stop_increment = "5"  # increment in pips to follow trailing stop
num_points = 250  # number of data points
runtime = 6  # run time of trading strategy in hours
trading_frequency = 1  # frequency to trade in minutes - match to data resolution
minimum_stop_distance = 0.025  # minimum stop distance in % of the instruments traded
trailing_stop_distance = "20"
limit = "30"
rsi_period = 9

# Connect to the IG Markets API and return current positions
ig_service = ig_execute.IG_connect()
trading = ig_execute.Trading(ig_service)


def main():
    try:
        # Retrieve currently open positions
        open_pos = trading.open_positions()

        for epic in pairs:
            # Determine if open position is long or short
            long_short = ""
            if len(open_pos) > 0:
                open_pos_cur = open_pos[open_pos["epic"] == epic]

                if len(open_pos_cur) > 0:
                    if open_pos_cur["direction"].tolist()[0] == "BUY":
                        long_short = "long"
                    elif open_pos_cur["direction"].tolist()[0] == "SELL":
                        long_short = "short"

            # Return historic OHLC price data for the epic based on resolution and number of points.
            ohlc = trading.price_data(epic, resolution, num_points)
            # client_sentiment = trading.client_sentiment(epic)

            """Set this for any instrument that has the trailing stop as a percentage and not in pips"""
            # trailing_stop_distance = str(ohlc.iloc[-1]['High']*minimum_stop_distance)

            # Calculate the signal for the trade based off the chosen strategy
            signal = trading_strategy.MACD_Renko(
                technical_indicators.renko_merge(ohlc), long_short
            )
            # signal = trading_strategy.RSI(technical_indicators.RSI(ohlc, rsi_period), long_short)
            # signal = trading_strategy.MACD_Renko_RSI(technical_indicators.renko_merge(ohlc), technical_indicators.RSI(ohlc,rsi_period), long_short)
            # signal = trading_strategy.sentiment_trading(client_sentiment, long_short)

            if len(signal) > 1:
                print(signal, "for", epic)
            else:
                print("No signal for", epic)

            if signal in ("BUY", "SELL"):
                trading.open_trade(
                    signal,
                    epic,
                    pos_size,
                    limit,
                    trailing_stop_distance,
                    trailing_stop_increment,
                )

            elif signal == "Close":
                trading.close_trade(long_short, epic, open_pos_cur)

            elif signal == "Close_Buy":
                direction = "BUY"
                trading.close_trade(long_short, epic, open_pos_cur)
                trading.open_trade(
                    direction,
                    epic,
                    pos_size,
                    limit,
                    trailing_stop_distance,
                    trailing_stop_increment,
                )

            elif signal == "Close_Sell":
                direction = "SELL"
                trading.close_trade(long_short, epic, open_pos_cur)
                trading.open_trade(
                    direction,
                    epic,
                    pos_size,
                    limit,
                    trailing_stop_distance,
                    trailing_stop_increment,
                )

    except Exception as e:
        print(e)


starttime = time.time()
timeout = time.time() + 60 * 60 * runtime
trading_summary = pd.DataFrame(
    columns=[
        "Date",
        "Duration (min)",
        "Net Profit",
        "Max Win",
        "Max Loss",
        "Winners",
        "Losers",
        "R Factor",
    ]
)

while time.time() <= timeout:
    try:
        print(
            "\nPassthrough at ",
            time.strftime("%H:%M:%S %d-%m-%Y", time.localtime(time.time())),
            "\n",
        )
        main()
        session_duration = time.time() - starttime

        # Retrieve historical trade data for the length of the session
        trade_data = trading.transaction_history(int(session_duration * 1000))

        # Calculate trade performance for each trading interval
        trading_summary = trading_performance.measure_performance(
            trade_data, session_duration, trading_summary
        )
        if len(trading_summary) > 0:
            print("\n", trading_summary)
        else:
            print("\nNo closed trades in current session")

        # Sleep until ready for next trade
        time.sleep(trading_frequency * 60)

    except KeyboardInterrupt:
        print("\n\nKeyboard exception received. Exiting.")
        sys.exit()

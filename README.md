# IGMarket
This script uses the IG Markets API Python Library(https://github.com/ig-python/ig-markets-api-python-library) to create an algorithmic trading bot for use on IGMarkets.

# Login
The example.env file shows the configuration of your username, password, API key, account type and account number for connecting to the IG Markets API. Enter your credentials and save this as .env to connect. 

API Keys are generated through your account settings on the IG Markets website. If you are trading with a demo account you will also need to generate a new username and password for the

# Trading Parameters
IG Markets use their own proprietry 'EPIC' instead of standard tickers for instruments. Search for the instrument you wish to trade on the new Trading Platform, find the instrument in (for example) a watchlist, right click it and choose "Open in new window". This opens a tear-off window, and the EPIC appears on the end of the web address. For example, AUD/USD FX is CS.D.AUDUSD.MINI.IP.

Set the remainder of the trading parameters as you wish and the automatic trading strategy as defined in trading_strategy.py should be executed. The ongoing performance of the strategy is recorded and printed by trading_performance.py.

The execution of trades to through the IG MArket API are handled by ig_execute.py. This has trailing stops enabled by default for opening trades, however could be adjust for different types of orders.

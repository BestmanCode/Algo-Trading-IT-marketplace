"""

@author: Cheso7

"""

import copy

# MACD Renko Strategy from Mayank Rasu 'Quant Finance & Algo Trading for Python' Udemy Course
def MACD_Renko(MERGED_DF, l_s):
    "function to generate signal"
    signal = ""
    df = copy.deepcopy(MERGED_DF)
    if l_s == "":
        if (
            df["bar_num"].tolist()[-1] >= 2
            and df["macd"].tolist()[-1] > df["macd_sig"].tolist()[-1]
            and df["macd_slope"].tolist()[-1] > df["macd_sig_slope"].tolist()[-1]
        ):
            signal = "BUY"
        elif (
            df["bar_num"].tolist()[-1] <= -2
            and df["macd"].tolist()[-1] < df["macd_sig"].tolist()[-1]
            and df["macd_slope"].tolist()[-1] < df["macd_sig_slope"].tolist()[-1]
        ):
            signal = "SELL"

    elif l_s == "long":
        if (
            df["bar_num"].tolist()[-1] <= -2
            and df["macd"].tolist()[-1] < df["macd_sig"].tolist()[-1]
            and df["macd_slope"].tolist()[-1] < df["macd_sig_slope"].tolist()[-1]
        ):
            signal = "Close_Sell"
        elif (
            df["macd"].tolist()[-1] < df["macd_sig"].tolist()[-1]
            and df["macd_slope"].tolist()[-1] < df["macd_sig_slope"].tolist()[-1]
        ):
            signal = "Close"

    elif l_s == "short":
        if (
            df["bar_num"].tolist()[-1] >= 2
            and df["macd"].tolist()[-1] > df["macd_sig"].tolist()[-1]
            and df["macd_slope"].tolist()[-1] > df["macd_sig_slope"].tolist()[-1]
        ):
            signal = "Close_Buy"
        elif (
            df["macd"].tolist()[-1] > df["macd_sig"].tolist()[-1]
            and df["macd_slope"].tolist()[-1] > df["macd_sig_slope"].tolist()[-1]
        ):
            signal = "Close"
    return signal


def RSI(RSI, l_s):
    "function to generate signal"
    signal = ""
    if l_s == "":
        if RSI < 30:
            signal = "BUY"
        elif RSI > 70:
            signal = "SELL"

    elif l_s == "long":
        if RSI < 70:
            signal = "Close"

    elif l_s == "short":
        if RSI < 30:
            signal = "Close"
    return signal


def MACD_Renko_RSI(MERGED_DF, RSI, l_s):
    "function to generate signal"
    signal = ""
    df = copy.deepcopy(MERGED_DF)
    if l_s == "":
        if (
            df["bar_num"].tolist()[-1] >= 2
            and df["macd"].tolist()[-1] > df["macd_sig"].tolist()[-1]
            and df["macd_slope"].tolist()[-1] > df["macd_sig_slope"].tolist()[-1]
            and RSI < 30
        ):
            signal = "BUY"
        elif (
            df["bar_num"].tolist()[-1] <= -2
            and df["macd"].tolist()[-1] < df["macd_sig"].tolist()[-1]
            and df["macd_slope"].tolist()[-1] < df["macd_sig_slope"].tolist()[-1]
            and RSI > 70
        ):
            signal = "SELL"

    elif l_s == "long":
        if (
            df["bar_num"].tolist()[-1] <= -2
            and df["macd"].tolist()[-1] < df["macd_sig"].tolist()[-1]
            and df["macd_slope"].tolist()[-1] < df["macd_sig_slope"].tolist()[-1]
            and RSI > 70
        ):
            signal = "Close_Sell"
        elif (
            df["macd"].tolist()[-1] < df["macd_sig"].tolist()[-1]
            and df["macd_slope"].tolist()[-1] < df["macd_sig_slope"].tolist()[-1]
        ):
            signal = "Close"

    elif l_s == "short":
        if (
            df["bar_num"].tolist()[-1] >= 2
            and df["macd"].tolist()[-1] > df["macd_sig"].tolist()[-1]
            and df["macd_slope"].tolist()[-1] > df["macd_sig_slope"].tolist()[-1]
            and RSI > 30
        ):
            signal = "Close_Buy"
        elif (
            df["macd"].tolist()[-1] > df["macd_sig"].tolist()[-1]
            and df["macd_slope"].tolist()[-1] > df["macd_sig_slope"].tolist()[-1]
        ):
            signal = "Close"
    return signal


def sentiment_trading(client_sentiment, l_s):
    signal = ""
    if l_s == "":
        if client_sentiment == "bullish":
            signal = "BUY"
        elif client_sentiment == "bearish":
            signal = "SELL"

    elif l_s == "long":
        if client_sentiment == "bearish":
            signal = "Close"

    elif l_s == "short":
        if client_sentiment == "bullish":
            signal = "Close"
    return signal

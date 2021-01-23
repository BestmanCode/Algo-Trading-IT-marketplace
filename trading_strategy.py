'''

@author: Cheso7

'''

import copy

# MACD Renko Strategy from Mayank Rasu 'Quant Finance & Algo Trading for Python' Udemy Course
def MACD_Renko(MERGED_DF, l_s):
    'function to generate signal'
    signal = ''
    df = copy.deepcopy(MERGED_DF)
    if l_s == '':
        if df['bar_num'].tolist()[-1] >= 2 and df['macd'].tolist()[-1] > df['macd_sig'].tolist()[-1] and df['macd_slope'].tolist()[-1] > df['macd_sig_slope'].tolist()[-1]:
            signal = 'BUY'
        elif df['bar_num'].tolist()[-1] <= -2 and df['macd'].tolist()[-1] < df['macd_sig'].tolist()[-1] and df['macd_slope'].tolist()[-1] < df['macd_sig_slope'].tolist()[-1]:
            signal = 'SELL'

    elif l_s == 'long':
        if df['bar_num'].tolist()[-1] <= -2 and df['macd'].tolist()[-1] < df['macd_sig'].tolist()[-1] and df['macd_slope'].tolist()[-1] < df['macd_sig_slope'].tolist()[-1]:
            signal = 'Close_Sell'
        elif df['macd'].tolist()[-1] < df['macd_sig'].tolist()[-1] and df['macd_slope'].tolist()[-1] < df['macd_sig_slope'].tolist()[-1]:
            signal = 'Close'

    elif l_s == 'short':
        if df['bar_num'].tolist()[-1] >= 2 and df['macd'].tolist()[-1] > df['macd_sig'].tolist()[-1] and df['macd_slope'].tolist()[-1] > df['macd_sig_slope'].tolist()[-1]:
            signal = 'Close_Buy'
        elif df['macd'].tolist()[-1] > df['macd_sig'].tolist()[-1] and df['macd_slope'].tolist()[-1] > df['macd_sig_slope'].tolist()[-1]:
            signal = 'Close'
    return signal

def RSI(MERGED_DF, l_s):
    'function to generate signal'
    signal = ''
    df = copy.deepcopy(MERGED_DF)
    if l_s == '':
        if df['RSI'].tolist()[-1] < 30:
            signal = 'BUY'
        elif df['RSI'].tolist()[-1] > 70:
            signal = 'SELL'

    elif l_s == 'long':
        if df['RSI'].tolist()[-1] < 70:
            signal = 'Close'

    elif l_s == 'short':
        if df['RSI'].tolist()[-1] < 30:
            signal = 'Close'
    return signal

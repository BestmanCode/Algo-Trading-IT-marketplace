'''

@author: Cheso7
Technical Indicator functions courtesy of Mayank Rasu

'''
import numpy as np
import statsmodels.api as sm
import copy
from stocktrends import Renko
import pandas as pd

pd.set_option('mode.chained_assignment', None)


def MACD(DF, a, b, c):
    '''function to calculate MACD
       typical values a = 12; b =26, c =9'''
    df = DF.copy()
    df['MA_Fast'] = df['Close'].ewm(span=a, min_periods=a).mean()
    df['MA_Slow'] = df['Close'].ewm(span=b, min_periods=b).mean()
    df['MACD'] = df['MA_Fast']-df['MA_Slow']
    df['Signal'] = df['MACD'].ewm(span=c, min_periods=c).mean()
    df.dropna(inplace=True)
    return (df['MACD'], df['Signal'])


def ATR(DF, n):
    'function to calculate True Range and Average True Range'
    df = DF.copy()
    df['H-L'] = abs(df['High']-df['Low'])
    df['H-PC'] = abs(df['High']-df['Close'].shift(1))
    df['L-PC'] = abs(df['Low']-df['Close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    #df['ATR'] = df['TR'].ewm(span=n,adjust=False,min_periods=n).mean()
    df2 = df.drop(['H-L', 'H-PC', 'L-PC'], axis=1)
    return df2


def slope(ser, n):
    'function to calculate the slope of n consecutive points on a plot'
    slopes = [i*0 for i in range(n-1)]
    for i in range(n, len(ser)+1):
        y = ser[i-n:i]
        x = np.array(range(n))
        y_scaled = (y - y.min())/(y.max() - y.min())
        x_scaled = (x - x.min())/(x.max() - x.min())
        x_scaled = sm.add_constant(x_scaled)
        model = sm.OLS(y_scaled, x_scaled)
        results = model.fit()
        slopes.append(results.params[-1])
    slope_angle = (np.rad2deg(np.arctan(np.array(slopes))))
    return np.array(slope_angle)


def renko_DF(DF):
    'function to convert ohlc data into renko bricks'
    df = DF.copy()
    df.reset_index(inplace=True)
    df = df.iloc[:, [0, 1, 2, 3, 4, 5]]
    df.columns = ['date', 'open', 'close', 'high', 'low', 'volume']
    df2 = Renko(df)
    df2.brick_size = round(ATR(DF, 120)['ATR'][-1], 4)
    renko_df = df2.get_ohlc_data()
    renko_df['bar_num'] = np.where(
        renko_df['uptrend'] == True, 1, np.where(renko_df['uptrend'] == False, -1, 0))
    for i in range(1, len(renko_df['bar_num'])):
        if renko_df['bar_num'][i] > 0 and renko_df['bar_num'][i-1] > 0:
            renko_df['bar_num'][i] += renko_df['bar_num'][i-1]
        elif renko_df['bar_num'][i] < 0 and renko_df['bar_num'][i-1] < 0:
            renko_df['bar_num'][i] += renko_df['bar_num'][i-1]
    renko_df.drop_duplicates(subset='date', keep='last', inplace=True)
    return renko_df


def renko_merge(DF):
    'function to merging renko df with original ohlc df'
    df = copy.deepcopy(DF)
    df['Date'] = df.index
    renko = renko_DF(df)
    renko.columns = ['Date', 'open', 'high',
                     'low', 'close', 'uptrend', 'bar_num']
    merged_df = df.merge(
        renko.loc[:, ['Date', 'bar_num']], how='outer', on='Date')
    merged_df['bar_num'].fillna(method='ffill', inplace=True)
    merged_df['macd'] = MACD(merged_df, 12, 26, 9)[0]
    merged_df['macd_sig'] = MACD(merged_df, 12, 26, 9)[1]
    merged_df['macd_slope'] = slope(merged_df['macd'], 5)
    merged_df['macd_sig_slope'] = slope(merged_df['macd_sig'], 5)
    return merged_df

def RSI(DF,n):
    "function to calculate RSI"
    df = DF.copy()
    df['delta']=df['Adj Close'] - df['Adj Close'].shift(1)
    df['gain']=np.where(df['delta']>=0,df['delta'],0)
    df['loss']=np.where(df['delta']<0,abs(df['delta']),0)
    avg_gain = []
    avg_loss = []
    gain = df['gain'].tolist()
    loss = df['loss'].tolist()
    for i in range(len(df)):
        if i < n:
            avg_gain.append(np.NaN)
            avg_loss.append(np.NaN)
        elif i == n:
            avg_gain.append(df['gain'].rolling(n).mean().tolist()[n])
            avg_loss.append(df['loss'].rolling(n).mean().tolist()[n])
        elif i > n:
            avg_gain.append(((n-1)*avg_gain[i-1] + gain[i])/n)
            avg_loss.append(((n-1)*avg_loss[i-1] + loss[i])/n)
    df['avg_gain']=np.array(avg_gain)
    df['avg_loss']=np.array(avg_loss)
    df['RS'] = df['avg_gain']/df['avg_loss']
    df['RSI'] = 100 - (100/(1+df['RS']))
    return df['RSI']
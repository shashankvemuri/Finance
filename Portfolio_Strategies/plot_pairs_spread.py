import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import pandas_datareader.data as pdr
import yfinance as yf
import datetime as dt
yf.pdr_override()

stocks = ['CFG', 'JPM']

num_of_years = 1
start = dt.date.today() - dt.timedelta(days = int(365.25*num_of_years))
end = dt.date.today()

df = pdr.get_data_yahoo(stocks, start, end)['Adj Close'].reset_index()
df = df.set_index('Date', drop=True)
df.index = pd.to_datetime(df.index)


def plot_spread(df, ticker1, ticker2, idx, th, stop):
  
    px1 = df[ticker1].iloc[idx] / df[ticker1].iloc[idx[0]]
    px2 = df[ticker2].iloc[idx] / df[ticker2].iloc[idx[0]]

    sns.set(style='white')
    
    # Set plotting figure
    plt.close()
    fig, ax = plt.subplots(2, 1, gridspec_kw={'height_ratios': [2, 1]})
    
    # Plot the 1st subplot
    sns.lineplot(data=[px1, px2], linewidth=1.2, ax=ax[0])
    ax[0].legend(loc='upper left')
    
    # Calculate the spread and other thresholds
    spread = df[ticker1].iloc[idx] - df[ticker2].iloc[idx]
    mean_spread = spread.mean()
    sell_th = mean_spread + th
    buy_th = mean_spread - th
    sell_stop = mean_spread + stop
    buy_stop = mean_spread - stop
    
    # Plot the 2nd subplot
    sns.lineplot(data=spread, color='#85929E', ax=ax[1], linewidth=1.2)
    ax[1].axhline(sell_th,   color='b', ls='--', linewidth=1, label='sell_th')
    ax[1].axhline(buy_th,    color='r', ls='--', linewidth=1, label='buy_th')
    ax[1].axhline(sell_stop, color='g', ls='--', linewidth=1, label='sell_stop')
    ax[1].axhline(buy_stop,  color='y', ls='--', linewidth=1, label='buy_stop')
    ax[1].fill_between(idx, sell_th, buy_th, facecolors='r', alpha=0.3)
    ax[1].legend(loc='upper left', labels=['Spread', 'sell_th', 'buy_th', 'sell_stop', 'buy_stop'], prop={'size':6.5})
    plt.show()

idx = range(0, len(df))
plot_spread(df, stocks[0], stocks[1], idx, 0.5, 1)
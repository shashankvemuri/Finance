import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pandas_datareader.data as pdr
import yfinance as yf
import datetime as dt

# Override the pandas_datareader's default Yahoo API with yfinance
yf.pdr_override()

# Function to fetch stock data
def fetch_stock_data(tickers, start_date, end_date):
    data = pdr.get_data_yahoo(tickers, start=start_date, end=end_date)['Adj Close']
    data.index = pd.to_datetime(data.index)
    return data

# Function to plot the spread of two stocks
def plot_stock_spread(df, ticker1, ticker2, threshold=0.5, stop_loss=1):
    spread = df[ticker1] - df[ticker2]
    mean_spread = spread.mean()
    sell_threshold = mean_spread + threshold
    buy_threshold = mean_spread - threshold
    sell_stop = mean_spread + stop_loss
    buy_stop = mean_spread - stop_loss

    sns.set(style='white')
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), gridspec_kw={'height_ratios': [2, 1]})
    df[[ticker1, ticker2]].plot(ax=axes[0])
    spread.plot(ax=axes[1], color='#85929E', linewidth=1.2)

    axes[1].axhline(sell_threshold, color='b', ls='--', linewidth=1)
    axes[1].axhline(buy_threshold, color='r', ls='--', linewidth=1)
    axes[1].axhline(sell_stop, color='g', ls='--', linewidth=1)
    axes[1].axhline(buy_stop, color='y', ls='--', linewidth=1)
    axes[1].fill_between(spread.index, sell_threshold, buy_threshold, facecolors='r', alpha=0.3)
    
    plt.legend(['Spread', 'Sell Threshold', 'Buy Threshold', 'Sell Stop', 'Buy Stop'])
    plt.show()

# Main
stocks = ['CFG', 'JPM']
start_date = dt.date.today() - dt.timedelta(days=365)
end_date = dt.date.today()
df = fetch_stock_data(stocks, start_date, end_date)
plot_stock_spread(df, stocks[0], stocks[1])
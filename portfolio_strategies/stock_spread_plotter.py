# Import necessary libraries
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import pandas_datareader.data as pdr
import yfinance as yf
import datetime as dt

# Override the pandas_datareader's default Yahoo API with yfinance
yf.pdr_override()

# Define the list of stocks and number of years for data fetching
stocks = ['CFG', 'JPM']
num_of_years = 1

# Define the start and end dates for data fetching
start = dt.date.today() - dt.timedelta(days=int(365.25*num_of_years))
end = dt.date.today()

# Fetch the historical stock data for the defined time period and stocks
df = pdr.get_data_yahoo(stocks, start, end)['Adj Close'].reset_index()

# Set the index of the data frame as date
df = df.set_index('Date', drop=True)

# Convert the index to datetime format
df.index = pd.to_datetime(df.index)

# Define the function to plot the spread of two stocks
def plot_spread(df, ticker1, ticker2, idx, threshold, stop_loss):
  
    # Calculate the prices of the two stocks at the current index relative to the first day's price
    px1 = df[ticker1].iloc[idx] / df[ticker1].iloc[idx[0]]
    px2 = df[ticker2].iloc[idx] / df[ticker2].iloc[idx[0]]

    # Set the style for the plot
    sns.set(style='white')
    
    # Set the plotting figure
    fig, ax = plt.subplots(2, 1, gridspec_kw={'height_ratios': [2, 1]})
    
    # Plot the first subplot with the relative prices of the two stocks
    sns.lineplot(data=[px1, px2], linewidth=1.2, ax=ax[0])
    ax[0].legend(loc='upper left')
    
    # Calculate the spread and other thresholds
    spread = df[ticker1].iloc[idx] - df[ticker2].iloc[idx]
    mean_spread = spread.mean()
    sell_th = mean_spread + threshold
    buy_th = mean_spread - threshold
    sell_stop = mean_spread + stop_loss
    buy_stop = mean_spread - stop_loss
    
    # Plot the second subplot with the spread and thresholds
    sns.lineplot(data=spread, color='#85929E', ax=ax[1], linewidth=1.2)
    ax[1].axhline(sell_th,   color='b', ls='--', linewidth=1, label='sell_th')
    ax[1].axhline(buy_th,    color='r', ls='--', linewidth=1, label='buy_th')
    ax[1].axhline(sell_stop, color='g', ls='--', linewidth=1, label='sell_stop')
    ax[1].axhline(buy_stop,  color='y', ls='--', linewidth=1, label='buy_stop')
    ax[1].fill_between(idx, sell_th, buy_th, facecolors='r', alpha=0.3)
    ax[1].legend(loc='upper left', labels=['Spread', 'sell_th', 'buy_th', 'sell_stop', 'buy_stop'], prop={'size':6.5})
    plt.show()

# Plot spread
idx = range(0, len(df))
plot_spread(df, stocks[0], stocks[1], idx, 0.5, 1)
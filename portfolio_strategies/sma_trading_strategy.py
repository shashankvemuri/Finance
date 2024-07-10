import datetime as dt
import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf

# Define the function to get historical data
def get_stock_data(stock, num_of_years):
    start = dt.date.today() - dt.timedelta(days=365 * num_of_years)
    end = dt.datetime.now()
    return yf.download(stock, start, end, interval='1d')

# Define the function for SMA Trading Strategy
def sma_trading_strategy(df, short_sma, long_sma):
    df[f"SMA_{short_sma}"] = df['Adj Close'].rolling(window=short_sma).mean()
    df[f"SMA_{long_sma}"] = df['Adj Close'].rolling(window=long_sma).mean()

    position = 0
    percent_change = []
    for i in df.index:
        close = df['Adj Close'][i]
        SMA_short = df[f"SMA_{short_sma}"][i]
        SMA_long = df[f"SMA_{long_sma}"][i]

        if SMA_short > SMA_long and position == 0:
            buyP, position = close, 1
            print("Buy at the price:", buyP)
        elif SMA_short < SMA_long and position == 1:
            sellP, position = close, 0
            print("Sell at the price:", sellP)
            percent_change.append((sellP / buyP - 1) * 100)

    if position == 1:
        position = 0
        sellP = df['Adj Close'][-1]
        print("Sell at the price:", sellP)
        percent_change.append((sellP / buyP - 1) * 100)

    return percent_change

# Main script
stock = 'NFLX'
num_of_years = 10
short_sma = 20
long_sma = 50

df = get_stock_data(stock, num_of_years)
percent_change = sma_trading_strategy(df, short_sma, long_sma)
current_price = round(df['Adj Close'][-1], 2)
print('Current Price:', current_price)

# Calculate strategy statistics
gains = 0
numGains = 0
losses = 0
numLosses = 0
totReturn = 1
for i in percent_change:
    if i > 0:
        gains += i
        numGains += 1
    else:
        losses += i
        numLosses += 1
    totReturn = totReturn * ((i / 100) + 1)
totReturn = round((totReturn - 1) * 100, 2)
print("This statistics is from " + str(df.index[0]) + " up to now with " + str(numGains + numLosses) + " trades:")
print("SMAs used: " + str(short_sma) + ", " + str(long_sma))
print("Total return over " + str(numGains + numLosses) + " trades: " + str(totReturn) + "%")

# Calculate strategy advanced statistics
if numGains > 0:
    avgGain = gains / numGains
    maxReturn = str(max(percent_change))
else:
    avgGain = 0
    maxReturn = 'unknown'

if numLosses > 0:
    avgLoss=losses/numLosses
    maxLoss=str(min(percent_change))
    ratioRR=str(-avgGain/avgLoss)  # risk-reward ratio
else:
    avgLoss=0
    maxLoss='unknown'
    ratioRR='inf'

if(numGains>0 or numLosses>0):
    batAvg=numGains/(numGains+numLosses)
else:
    batAvg=0

# Print statistics
df['PC'] = df['Close'].pct_change()
hold = round(df['PC'].sum() * 100, 2)
print ("Total return for a B&H strategy: " + str(hold)+'%')
print("Average Gain: "+ str(round(avgGain, 2)))
print("Average Loss: "+ str(round(avgLoss, 2)))
print("Max Return: "+ maxReturn)
print("Max Loss: "+ maxLoss)
print("Gain/loss ratio: "+ ratioRR)
print("Batting Avg: "+ str(batAvg))

# Plot price history
mpf.plot(df, type = 'ohlc',figratio=(14,7), mav=(short_sma,long_sma), 
         volume=True, title= str(stock), style='default')
plt.show()
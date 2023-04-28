import yfinance
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
import datetime as dt

# Define the stock symbol and the number of days forward
symbol = "TSLA"
days_forward = 10

# Define the number of years of historical data to use
num_of_years = 10
start_date = dt.datetime.now() - dt.timedelta(int(365.25 * num_of_years))
end_date = dt.datetime.now()

# Set up the plot size and font size
plt.rcParams['figure.figsize'] = [15, 7]
plt.rc('font', size=14)

# Create a random dataset with noise
np.random.seed(0)
y = np.arange(0, 100, 1) + np.random.normal(0, 10, 100)

# Calculate the simple moving average (SMA) of the random dataset
sma = pd.Series(y).rolling(20).mean()

# Get the historical data of the stock from Yahoo Finance API
ticker = yfinance.Ticker(symbol)
data = ticker.history(interval="1d", start='2010-01-01', end=end_date)

# Plot the historical stock price and its SMAs
plt.plot(data['Close'], label=f'{symbol}')
plt.plot(data['Close'].rolling(20).mean(), label="20-periods SMA")
plt.plot(data['Close'].rolling(50).mean(), label="50-periods SMA")
plt.plot(data['Close'].rolling(200).mean(), label="200-periods SMA")

# Set the plot title, labels, and limits
plt.legend()
plt.xlim((dt.date(2019, 1, 1), dt.date(2020, 6, 15)))
plt.ylim((100, 250))
plt.title('Stock Price and SMAs')
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()

# Get the historical data of the stock from Yahoo Finance API
ticker = yfinance.Ticker(symbol)
data = ticker.history(interval="1d", start=start_date, end=end_date)

# Add a column for the forward close price and calculate the forward return
data['Forward Close'] = data['Close'].shift(-days_forward)
data['Forward Return'] = (data['Forward Close'] - data['Close']) / data['Close']

result = []
train_size = 0.6

# Loop through different SMA lengths to find the best one for predicting the forward return
for sma_length in range(20, 500):
    # Calculate the SMA of the stock price and add a binary input based on whether the price is above or below the SMA
    data['SMA'] = data['Close'].rolling(sma_length).mean()
    data['input'] = [int(x) for x in data['Close'] > data['SMA']]

    # Drop rows with missing values
    df = data.dropna()

    # Split the data into training and test sets
    training = df.head(int(train_size * df.shape[0]))
    test = df.tail(int((1 - train_size) * df.shape[0]))

    # Calculate the mean forward return for the training and test sets
    tr_returns = training[training['input'] == 1]['Forward Return']
    test_returns = test[test['input'] == 1]['Forward Return']
    meadays_forward_return_training = tr_returns.mean()
    meadays_forward_return_test = test_returns.mean()

    # Calculate the p-value of the difference in means between the training and test sets
    pvalue = ttest_ind(tr_returns,test_returns,equal_var=False)[1]

    result.append({
        f'Best SMA for {days_forward} days forward':sma_length,
        'Training Forward Return': meadays_forward_return_training,
        'Test Forward Return': meadays_forward_return_test,
        'p-value':pvalue
    })

# Sort result by training forward return
result.sort(key = lambda x : -x['Training Forward Return'])

# Print each return %
for key, value in result[0].items():
    if key == "Training Forward Return":
        value = str(round(value, 4) * 100) + '%'
        print (key + ':', value)
    elif key == "Test Forward Return":
        value = str(round(value, 4) * 100) + '%'
        print (key + ':', value)
    else:
        print (key + ':', value)
        
# Display best SMA
best_sma = result[0][f'Best SMA for {days_forward} days forward']
data['SMA'] = data['Close'].rolling(best_sma).mean()

# Show Best SMA on stock
plt.subplots()
plt.gcf()
plt.plot(data['Close'],label=symbol)
plt.plot(data['SMA'],label = "{} periods SMA".format(best_sma))
plt.title('')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()
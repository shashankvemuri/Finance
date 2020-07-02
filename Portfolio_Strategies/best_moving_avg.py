import yfinance
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
import datetime as dt

symbol = "TSLA"
days_forward = 10

num_of_years = 10
start_date = dt.datetime.now() - dt.timedelta(int(365.25 * num_of_years))
end_date = dt.datetime.now() 


plt.rcParams['figure.figsize'] = [15, 7]
plt.rc('font', size=14)

np.random.seed(0)
y = np.arange(0,100,1) + np.random.normal(0,10,100)

sma = pd.Series(y).rolling(20).mean()

ticker = yfinance.Ticker(symbol)
data = ticker.history(interval="1d",start='2010-01-01',end=end_date)
plt.plot(data['Close'],label=f'{symbol}')

plt.plot(data['Close'].rolling(20).mean(),label = "20-periods SMA")
plt.plot(data['Close'].rolling(50).mean(),label = "50-periods SMA")
plt.plot(data['Close'].rolling(200).mean(),label = "200-periods SMA")

plt.legend()
plt.xlim((dt.date(2019,1,1),dt.date(2020,6,15)))
plt.ylim((100,250))
plt.title('')
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()

ticker = yfinance.Ticker(symbol)
data = ticker.history(interval="1d",start=start_date,end=end_date)
data['Forward Close'] = data['Close'].shift(-days_forward)
data['Forward Return'] = (data['Forward Close'] - data['Close'])/data['Close']

result = []
train_size = 0.6

for sma_length in range(20,500):  
  data['SMA'] = data['Close'].rolling(sma_length).mean()
  data['input'] = [int(x) for x in data['Close'] > data['SMA']]
  
  df = data.dropna()

  training = df.head(int(train_size * df.shape[0]))
  test = df.tail(int((1 - train_size) * df.shape[0]))
  
  tr_returns = training[training['input'] == 1]['Forward Return']
  test_returns = test[test['input'] == 1]['Forward Return']

  meadays_forward_return_training = tr_returns.mean()
  meadays_forward_return_test = test_returns.mean()

  pvalue = ttest_ind(tr_returns,test_returns,equal_var=False)[1]
 
  result.append({
      f'Best SMA for {days_forward} days forward':sma_length,
      'Training Forward Return': meadays_forward_return_training,
      'Test Forward Return': meadays_forward_return_test,
      'p-value':pvalue
  })

result.sort(key = lambda x : -x['Training Forward Return'])

for key, value in result[0].items():
    if key == "Training Forward Return":
        value = round(value, 4) * 100
        value = str(value) + '%'
        print (key + ':', value)
    elif key == "Test Forward Return":
        value = round(value, 4) * 100
        value = str(value) + '%'
        print (key + ':', value)
    else:
        print (key + ':', value)
        
best_sma = result[0][f'Best SMA for {days_forward} days forward']
data['SMA'] = data['Close'].rolling(best_sma).mean()

plt.subplots()
plt.gcf()
plt.plot(data['Close'],label=symbol)
plt.plot(data['SMA'],label = "{} periods SMA".format(best_sma))
plt.title('')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()
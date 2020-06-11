import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fbprophet import Prophet
import yfinance as yf
from pandas_datareader import data as pdr
import datetime as dt

stock = 'RAD'
start = dt.date.today() - dt.timedelta(days = 365*3)
end = dt.date.today()

df = pdr.get_data_yahoo(stock, start, end)

df['Adj Close'].plot(figsize=(14,7))
plt.show()

df = df.reset_index().rename(columns={'Date':'ds', 'Adj Close':'y'})
#df['ds'] = pd.to_datetime(df.index)
#df['y'] = pd.DataFrame(df['Adj Close'])


# Log Transform Data
df['y'] = pd.DataFrame(np.log(df['y']))

# plot data
ax = df['y'].plot(color='#006699')
ax.set_ylabel('Price')
ax.set_xlabel('Date')
plt.show()

# train test split
df_train = df[:740]
df_test = df[740:]

# Model Fitting
# instantiate the Prophet class
mdl = Prophet(interval_width=0.95, daily_seasonality=True)
 
# fit the model on the training data
mdl.fit(df_train)
 
# define future time frame
future = mdl.make_future_dataframe(periods=24, freq='MS')

# instantiate the Prophet class
mdl = Prophet(interval_width=0.95, daily_seasonality=True)
 
# fit the model on the training data
mdl.fit(df_train)
 
# define future time frame
future = mdl.make_future_dataframe(periods=24, freq='MS')

# generate the forecast
forecast = mdl.predict(future)
print (forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())
print (forecast['yhat_lower'].head())

mdl.plot(forecast)
plt.show()

# plot time series components
mdl.plot_components(forecast)
plt.show()

import math
# retransform using e
y_hat = np.exp(forecast['yhat'][740:])
y_true = np.exp(df['y'])
 
# compute the mean square error
mse = ((y_hat - y_true) ** 2).mean()
print('Prediction quality: {:.2f} MSE ({:.2f} RMSE)'.format(mse, math.sqrt(mse)))

plt.plot(y_true, label='Original', color='#006699')
plt.plot(y_hat, color='#ff0066', label='Forecast')
plt.ylabel('Price')
plt.xlabel('Date')
plt.show()
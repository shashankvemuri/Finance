import pandas as pd
import datetime 

stock = 'AAPL'
start = '2019-01-10'
end = '2019-01-11'

url = f'https://api.tiingo.com/iex/{stock}/prices?startDate={start}&endDate={end}&resampleFreq=5min&token=ef79e455ba9b04c3df719407e34f05e1b051b4d6'

df = pd.read_json(url)
print (df)
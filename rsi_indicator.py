import requests
import datetime
import talib
from pandas_datareader import DataReader
import pickle 
import bs4 as bs 
import time 

#Get Dates
start_date = datetime.datetime.now() - datetime.timedelta(days=365)
end_date = datetime.date.today()

def save_spx_tickers():
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class':'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.find_all('td') [0].text.strip()
        tickers.append(ticker)
        
    with open('spxTickers.pickle', 'wb') as f:
            pickle.dump(tickers, f)       
    return tickers
        
tickers = save_spx_tickers()

# Make the ticker symbols readable by Yahoo Finance
tickers = [item.replace(".", "-") for item in tickers]

tickers = ['AAPL']

oversold = []
overbought = []
for ticker in tickers:
    data = DataReader(ticker, 'yahoo', start_date, end_date)
    data["rsi"] = talib.RSI(data["Close"])
    values = data["rsi"].tail(14)
    value = values.mean()
    print ('{} has an rsi value of {}'.format(ticker, round(value, 2)))
    time.sleep(1)
    
    if value <= 30:
        oversold.append(ticker)
        
    elif value >= 70:
        overbought.append(ticker)
        
print (oversold)
print (overbought)
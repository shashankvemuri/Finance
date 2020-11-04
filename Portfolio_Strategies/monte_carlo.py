from datetime import datetime
import pandas_datareader as web
import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd

ticker = 'NIO'
start_date = '01-01-2015'
end_date = '01-01-2020'

def download_data(symbol, source, start_date, end_date):
    start = datetime.strptime(start_date, '%d-%m-%Y')
    end = datetime.strptime(end_date, '%d-%m-%Y')
    df = web.DataReader(symbol, data_source=source, start=start, end=end)
    return df

def annual_volatility(ticker, source, start_date, end_date):    
    df = download_data(ticker, source, start_date,end_date)
    quote = df.filter(['Close'])
    quote['Returns'] = quote['Close'].pct_change()
    vol = quote['Returns'].std()*np.sqrt(252)
    return vol

def compound_annual_growth_rate(ticker, source, start_date, end_date):
    df = download_data(ticker, source, start_date,end_date)
    quote = df.filter(['Close'])
    days = (quote.index[-1] - quote.index[0]).days
    cagr = ((((quote['Close'][-1]) / quote['Close'][1])) ** (365.0/days)) - 1
    return cagr

def advanced_montecarlo_simulation(ticker, source, start_date, end_date, simulations, days_predicted):
    result = []
    
    df = download_data(ticker, source, start_date, end_date)
    quote = df.filter(['Close'])
    
    S = quote['Close'][-1]
    T = days_predicted # number of trading days
    mu = compound_annual_growth_rate(ticker, source, start_date, end_date)
    vol = annual_volatility(ticker, source, start_date, end_date)
    
    plt.subplot(2,1,1)
    for i in range(simulations):
        daily_returns=np.random.normal(mu/T,vol/math.sqrt(T),T)+1
        price_list = [S]
        for x in daily_returns:
            price_list.append(price_list[-1]*x)
        plt.plot(price_list)
        result.append(price_list[-1])
    
    plt.subplot(2,1,2)
    plt.hist(result,bins=100)
    plt.axvline(np.percentile(result,5), color='black', linestyle='dashed', linewidth=2)
    plt.axvline(np.percentile(result,95), color='black', linestyle='dashed', linewidth=2)
    plt.show()
    
    cabeceras = ['Percentile 5%', 'Percentile 95%', 'CAGR', 'Annual Volatility']
    df_percentile = pd.DataFrame(columns=cabeceras)
    
    df_percentile.loc[len(df_percentile)]=[np.percentile(result,5),np.percentile(result,95),mu,vol]
    
    return df_percentile

x = advanced_montecarlo_simulation(ticker, 'yahoo', start_date, end_date, 10000, 252)
print (x)
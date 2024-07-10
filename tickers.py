import pandas as pd
import requests

def tickers_sp500():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = requests.get(url).text
    df = pd.read_html(html, header=0)[0]
    tickers = df['Symbol'].tolist()
    return tickers

def tickers_nasdaq():
    url = 'http://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt'
    data = requests.get(url).text
    # The data is '|' separated and last two lines are not needed
    lines = data.split('\n')
    # Convert to DataFrame
    df = pd.DataFrame([sub.split("|") for sub in lines[1:-2]], columns=lines[0].split("|"))
    return df['Symbol'].tolist()

def tickers_nyse():
    url = 'http://www.nasdaqtrader.com/dynamic/symdir/otherlisted.txt'
    data = requests.get(url).text
    # The data is '|' separated and the last two lines are not needed
    lines = data.split('\n')
    # Convert to DataFrame
    df = pd.DataFrame([sub.split("|") for sub in lines[1:-2]], columns=lines[0].split("|"))
    # Filter out only NYSE symbols
    nyse_df = df[df['Exchange'] == 'N']
    return nyse_df['ACT Symbol'].tolist()

def tickers_dow():
    url = 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average'
    html = requests.get(url).text
    df = pd.read_html(html, header=0, attrs = {'id': 'constituents'})[0]
    tickers = df['Symbol'].tolist()
    return tickers

def tickers_amex():
    url = 'http://www.nasdaqtrader.com/dynamic/symdir/otherlisted.txt'
    data = requests.get(url).text
    # The data is '|' separated and the last two lines are not needed
    lines = data.split('\n')
    # Convert to DataFrame
    df = pd.DataFrame([sub.split("|") for sub in lines[1:-2]], columns=lines[0].split("|"))
    # Filter out only AMEX symbols
    amex_df = df[df['Exchange'] == 'A']
    return amex_df['ACT Symbol'].tolist()
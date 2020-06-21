# Import libraries
import os
import time
import pickle
import requests
import datetime
import bs4 as bs
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from yahoo_fin import stock_info as si
from urllib.request import urlopen, Request
from nltk.sentiment.vader import SentimentIntensityAnalyzer

pd.set_option('display.max_columns', 6)

mylist = []
today = datetime.date.today()
mylist.append(today)
today = mylist[0]

finwiz_url = 'https://finviz.com/quote.ashx?t='

news_tables = {}

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

for ticker in tickers:
    url = finwiz_url + ticker
    req = Request(url=url,headers={'user-agent': 'my-app/0.0.1'}) 
    response = urlopen(req)    
    html = BeautifulSoup(response, features="lxml")
    news_table = html.find(id='news-table')
    news_tables[ticker] = news_table
    time.sleep(2)
    print (ticker + ' done')

parsed_news = []

# Iterate through the news
for file_name, news_table in news_tables.items():
    for x in news_table.findAll('tr'):
        text = x.a.get_text() 
        date_scrape = x.td.text.split()

        if len(date_scrape) == 1:
            time = date_scrape[0]
            
        else:
            date = date_scrape[0]
            time = date_scrape[1]

        ticker = file_name.split('_')[0]
        
        parsed_news.append([ticker, date, time, text])
        
vader = SentimentIntensityAnalyzer()

columns = ['ticker', 'date', 'time', 'headline']
parsed_and_scored_news = pd.DataFrame(parsed_news, columns=columns)
scores = parsed_and_scored_news['headline'].apply(vader.polarity_scores).tolist()

scores_df = pd.DataFrame(scores)
parsed_and_scored_news = parsed_and_scored_news.join(scores_df, rsuffix='_right')

parsed_and_scored_news['date'] = pd.to_datetime(parsed_and_scored_news.date).dt.date

unique_ticker = parsed_and_scored_news['ticker'].unique().tolist()
parsed_and_scored_news_dict = {name: parsed_and_scored_news.loc[parsed_and_scored_news['ticker'] == name] for name in unique_ticker}

values = []

for ticker in tickers: 
    dataframe = parsed_and_scored_news_dict[ticker]
    dataframe = dataframe.set_index('ticker')
    
    mean = round(dataframe['compound'].mean(), 2)
    values.append(mean)

df = pd.read_csv('/Users/shashank/Documents/GitHub/Code/sentiment-values/sentiments-values.csv')
df['{}'.format(today)] = values
df = df.set_index('Ticker')
df.to_csv('/Users/shashank/Documents/GitHub/Code/sentiment-values/sentiments-values.csv')

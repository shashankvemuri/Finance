# Import libraries
import os
import pickle
import requests
import bs4 as bs
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from urllib.request import urlopen, Request
from nltk.sentiment.vader import SentimentIntensityAnalyzer

pd.set_option('display.max_columns', 6)

n = 3 #the number of article headlines you want to see for eaxh ticker

finwiz_url = 'https://finviz.com/quote.ashx?t='

news_tables = {}

# save_sp500_tickers()
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
    resp = urlopen(req)    
    html = BeautifulSoup(resp, features="lxml")
    news_table = html.find(id='news-table')
    news_tables[ticker] = news_table

try:
    for ticker in tickers:
        df = news_tables[ticker]
        df_tr = df.findAll('tr')
    
        print ('\n')    
        print ('Recent News Headlines for {}: '.format(ticker))
        
        for i, table_row in enumerate(df_tr):
            a_text = table_row.a.text
            td_text = table_row.td.text
            td_text = td_text.strip()
            print(a_text,'(',td_text,')')
            if i == n:
                break
except KeyError:
    pass

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
        
#print (parsed_news)

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
    #dataframe = dataframe.drop(columns = ['headline'])
    #print (dataframe.head())
    
    mean = round(dataframe['compound'].mean(), 2)
    values.append(mean)
    
df = pd.DataFrame(list(zip(tickers, values)), columns =['Ticker', 'Sentiment Value']) 
df = df.set_index('Ticker')
df = df.sort_values('Sentiment Value', ascending=False)
print ('\n')
print (df)

'''
#plot 
plt.rcParams['figure.figsize'] = [10, 6]
mean_scores = parsed_and_scored_news.groupby(['ticker','date']).mean()
mean_scores = mean_scores.unstack()

mean_scores = mean_scores.xs('compound', axis="columns").transpose()

mean_scores.plot(kind = 'bar')
plt.grid()
'''
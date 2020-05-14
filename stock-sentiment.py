# Import libraries
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import os
import pandas as pd
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer

pd.set_option('display.max_columns', 6)

finwiz_url = 'https://finviz.com/quote.ashx?t='

news_tables = {}
tickers = ['NFLX', 'MRK', 'M']

for ticker in tickers:
    url = finwiz_url + ticker
    req = Request(url=url,headers={'user-agent': 'my-app/0.0.1'}) 
    response = urlopen(req)    
    html = BeautifulSoup(response, features="lxml")
    news_table = html.find(id='news-table')
    news_tables[ticker] = news_table

for ticker in tickers:
    var = news_tables[ticker]
    var_tr = var.findAll('tr')

    print ('\n')    
    print ('Recent News Headlines for {}: '.format(ticker))
    
    for i, table_row in enumerate(var_tr):
        a_text = table_row.a.text
        td_text = table_row.td.text
        td_text = td_text.strip()
        print(a_text,'(',td_text,')')
        if i == 3:
            break
        

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
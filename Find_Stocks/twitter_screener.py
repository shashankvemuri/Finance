# Import dependencies
import requests 
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import yahoo_fin.stock_info as ya
from alpha_vantage.sectorperformance import SectorPerformances

# Set option to display all columns in dataframes
pd.set_option('display.max_columns', None)

# Get most active stocks for the day
movers = ya.get_day_most_active()

# Keep only stocks with positive percentage change
movers = movers[movers['% Change'] >= 0]

# Scrape sentiment data from Sentdex website
res = requests.get('http://www.sentdex.com/financial-analysis/?tf=30d')
soup = BeautifulSoup(res.text, features="lxml")
table = soup.find_all('tr')

stock = []
sentiment = []
mentions = []
sentiment_trend = []

for ticker in table:
    ticker_info = ticker.find_all('td')
    try:
        stock.append(ticker_info[0].get_text())
    except:
        stock.append(None)
    try:
        sentiment.append(ticker_info[3].get_text())
    except:
        sentiment.append(None)
    try:
        mentions.append(ticker_info[2].get_text())
    except:
        mentions.append(None)
    try:
        if (ticker_info[4].find('span',{"class":"glyphicon glyphicon-chevron-up"})):
            sentiment_trend.append('up')
        else:
            sentiment_trend.append('down')
    except:
        sentiment_trend.append(None)

# Create a dataframe with stock sentiment data
company_info = pd.DataFrame(data={'Symbol': stock, 'Sentiment': sentiment, 'Direction': sentiment_trend, 'Mentions':mentions})

# Merge most active stocks data with sentiment data
top_stocks = movers.merge(company_info, on='Symbol', how='left')

# Drop unnecessary columns from the merged dataframe
top_stocks.drop(['Market Cap','PE Ratio (TTM)'], axis=1, inplace=True)

# Scrape Twitter data from Trade Followers website
res = requests.get("https://www.tradefollowers.com/strength/twitter_strongest.jsp?tf=1m")
soup = BeautifulSoup(res.text, features="lxml")
stock_twitter = soup.find_all('tr')

twit_stock = []
sector = []
twit_score = []

for stock in stock_twitter:
    try:
        score = stock.find_all("td",{"class": "datalistcolumn"})
        twit_stock.append(score[0].get_text().replace('$','').strip())
        sector.append(score[2].get_text().replace('\n','').strip())
        twit_score.append(score[4].get_text().replace('\n','').strip())
    except:
        twit_stock.append(np.nan)
        sector.append(np.nan)
        twit_score.append(np.nan)

# Create a dataframe with Twitter data
twitter_df = pd.DataFrame({'Symbol': twit_stock, 'Sector': sector, 'Twit_Bull_score': twit_score})

# Remove NA values and duplicates from the dataframe
twitter_df.dropna(inplace=True)
twitter_df.drop_duplicates(subset ="Symbol", keep='first', inplace=True)
twitter_df.reset_index(drop=True,inplace=True)

# Merge the previous dataframe with the Twitter momentum data
Final_list = top_stocks.merge(twitter_df, on='Symbol', how='left')

# Scrape more Twitter data from Trade Followers website
res2 = requests.get("https://www.tradefollowers.com/active/twitter_active.jsp?tf=1m")
soup2 = BeautifulSoup(res2.text, features="lxml")
stock_twitter2 = soup2.find_all('tr')

twit_stock2 = []
sector2 = []
twit_score2 = []

for stock in stock_twitter2:
    try:
        score2 = stock.find_all("td",{"class": "datalistcolumn"})
        twit_stock2.append(score2[0].get_text().replace('$','').strip())
        sector2.append(score2[2].get_text().replace('\n','').strip())
        twit_score2.append(score2[4].get_text().replace('\n','').strip())
    except:
        twit_stock2.append(np.nan)
        sector2.append(np.nan)
        twit_score2.append(np.nan)
        
twitter_df2 = pd.DataFrame({'Symbol': twit_stock2, 'Sector': sector2, 'Twit_mom': twit_score2})

# Remove NA values 
twitter_df2.dropna(inplace=True)
twitter_df2.drop_duplicates(subset ="Symbol", 
                     keep = 'first', inplace = True)
twitter_df2.reset_index(drop=True,inplace=True)

# Create and print list
recommender_list = Final_list.merge(twitter_df2, on='Symbol', how='left')
recommender_list.drop(['Volume','Avg Vol (3 month)'],axis=1, inplace=True)
print('\nFinal Recommended List: ')
print(recommender_list.set_index('Symbol'))
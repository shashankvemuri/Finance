# Import dependencies
import requests
import pandas as pd
from bs4 import BeautifulSoup

# Set pandas option to display all columns
pd.set_option('display.max_columns', None)

# Function to scrape most active stocks from Yahoo Finance
def scrape_most_active_stocks():
    url = 'https://finance.yahoo.com/most-active/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    df = pd.read_html(str(soup), attrs={'class': 'W(100%)'})[0]
    df = df.drop(columns=['52 Week High'])
    return df

# Scrape and filter most active stocks
movers = scrape_most_active_stocks()
movers = movers[movers['% Change'] >= 0]

# Scrape sentiment data from Sentdex
def scrape_sentdex():
    res = requests.get('http://www.sentdex.com/financial-analysis/?tf=30d')
    soup = BeautifulSoup(res.text, 'html.parser')
    table = soup.find_all('tr')
    data = {'Symbol': [], 'Sentiment': [], 'Direction': [], 'Mentions': []}

    for ticker in table:
        ticker_info = ticker.find_all('td')
        try:
            data['Symbol'].append(ticker_info[0].get_text())
            data['Sentiment'].append(ticker_info[3].get_text())
            data['Mentions'].append(ticker_info[2].get_text())
            trend = 'up' if ticker_info[4].find('span', {"class": "glyphicon glyphicon-chevron-up"}) else 'down'
            data['Direction'].append(trend)
        except:
            continue
    
    return pd.DataFrame(data)

sentdex_data = scrape_sentdex()

# Merge most active stocks with sentiment data
top_stocks = movers.merge(sentdex_data, on='Symbol', how='left')
top_stocks.drop(['Market Cap', 'PE Ratio (TTM)'], axis=1, inplace=True)

# Function to scrape Twitter data from Trade Followers
def scrape_twitter(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    stock_twitter = soup.find_all('tr')
    data = {'Symbol': [], 'Sector': [], 'Score': []}

    for stock in stock_twitter:
        try:
            score = stock.find_all("td", {"class": "datalistcolumn"})
            data['Symbol'].append(score[0].get_text().replace('$', '').strip())
            data['Sector'].append(score[2].get_text().strip())
            data['Score'].append(score[4].get_text().strip())
        except:
            continue
    
    return pd.DataFrame(data).dropna().drop_duplicates(subset="Symbol").reset_index(drop=True)

# Scrape Twitter data and merge with previous data
twitter_data = scrape_twitter("https://www.tradefollowers.com/strength/twitter_strongest.jsp?tf=1m")
final_list = top_stocks.merge(twitter_data, on='Symbol', how='left')

# Further scrape and merge Twitter data
twitter_data2 = scrape_twitter("https://www.tradefollowers.com/active/twitter_active.jsp?tf=1m")
recommender_list = final_list.merge(twitter_data2, on='Symbol', how='left')
recommender_list.drop(['Volume', 'Avg Vol (3 month)'], axis=1, inplace=True)

# Print final recommended list
print('\nFinal Recommended List: ')
print(recommender_list.set_index('Symbol'))
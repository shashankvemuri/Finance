# Import dependencies
import smtplib
import datetime
import numpy as np
import pandas as pd
from email.mime.text import MIMEText
from yahoo_fin import stock_info as si
from pandas_datareader import DataReader
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import talib

# Define list of stocks
STOCK_LIST = ['AAPL', 'MSFT', 'AMZN']

# Define interval for TradingView recommendation
# Options are: '1m', '5m', '15m', '1h', '4h', '1D', '1W', '1M
INTERVAL = "1M"

# Path to Chromedriver
CHROMEDRIVER_PATH = 'chromedriver.exe'

# Chromedriver options for running in headless mode
CHROMEDRIVER_OPTIONS = Options()
CHROMEDRIVER_OPTIONS.add_argument("--headless")

# Instantiate Chromedriver
CHROMEDRIVER = webdriver.Chrome(
    executable_path=CHROMEDRIVER_PATH,
    options=CHROMEDRIVER_OPTIONS
)

# Define start and end dates for stock data
START_DATE = datetime.datetime.now() - datetime.timedelta(days=365)
END_DATE = datetime.datetime.now()

def send_message(text):
    """
    Function to send email message
    """
    email = ""
    password = ""
    sms_gateway = ''
    smtp_server = "smtp.gmail.com" 
    port = 587
    
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    server.login(email, password)

    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = sms_gateway
    msg['Subject'] = "Stock Data\n"
    body = "{}\n".format(text)
    msg.attach(MIMEText(body, 'plain'))

    sms = msg.as_string()

    server.sendmail(email, sms_gateway, sms)
    
    server.quit()
    
    print ('done')

def get_data(stock_list):
    """
    Function to retrieve stock data, compute sharpe ratio and sentiment score, and
    obtain TradingView recommendation
    """
    for stock in stock_list:
        # Retrieve stock data using Yahoo Finance API
        df = DataReader(stock, 'yahoo', START_DATE, END_DATE)
        print(stock)
        
        # Compute current price using Yahoo Finance API
        price = si.get_live_price('{}'.format(stock))
        price = round(price, 2)
        
        # Compute Sharpe Ratio using portfolio of $5000
        portfolio_size = 5000
        stock_df = df
        stock_df['Norm return'] = stock_df['Adj Close'] / stock_df.iloc[0]['Adj Close']
        allocation = float(portfolio_size / portfolio_size)
        stock_df['Allocation'] = stock_df['Norm return'] * allocation
        stock_df['Position'] = stock_df['Allocation'] * portfolio_size
        val = pd.concat([stock_df['Position']], axis=1)
        val.columns = [f'{stock} Pos']
        val['Total Pos'] = val.sum(axis=1)
        val.tail(1)
        val['Daily Return'] = val['Total Pos'].pct_change(1)
        sharpe_ratio = val['Daily Return'].mean() / val['Daily Return'].std()
        a_sharpe_ratio = (252**0.5) * sharpe_ratio        
        a_sharpe_ratio = round(a_sharpe_ratio, 2)
        
        # News Sentiment 
        finviz_url = 'https://finviz.com/quote.ashx?t='
        news_tables = {}
        
        url = finviz_url + stock
        req = Request(url=url,headers={'user-agent': 'my-app/0.0.1'}) 
        response = urlopen(req)    
        html = BeautifulSoup(response, features="lxml")
        news_table = html.find(id='news-table')
        news_tables[stock] = news_table
        
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
        dataframe = pd.DataFrame(parsed_news, columns=columns)
        scores = dataframe['headline'].apply(vader.polarity_scores).tolist()
        scores_df = pd.DataFrame(scores)
        dataframe = dataframe.join(scores_df, rsuffix='_right')
        dataframe['date'] = pd.to_datetime(dataframe.date).dt.date
        dataframe = dataframe.set_index('ticker')
        
        sentiment = round(dataframe['compound'].mean(), 2)
        
        # Relative Strength Index
        df["rsi"] = talib.RSI(df["Close"])
        values = df["rsi"].tail(14)
        value = values.mean()
        rsi = round(value, 2)

        # Message
        output = ("\nTicker: " + str(stock) + "\nCurrent Price : " + str(price) + "\nSharpe Ratio: " + str(a_sharpe_ratio) + "\nNews Sentiment: " + str(sentiment) + "\nRelative Strength Index: " + str(rsi))
        send_message(output)

if __name__ == '__main__':
    get_data(STOCK_LIST)
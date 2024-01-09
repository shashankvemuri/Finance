import os
import sys
import datetime
import pandas as pd
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from pandas_datareader import data as pdr

# Adding the parent directory to the path for importing custom modules
parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)
import ta_functions as ta

# Define list of stocks
tickers = ['AAPL', 'MSFT', 'AMZN']

# Define start and end dates for stock data
start_date = datetime.datetime.now() - datetime.timedelta(days=365)
end_date = datetime.datetime.now()

def send_message(text, sender_email, receiver_email, password):
    """
    Function to send an email message.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = "Stock Data"
        msg.attach(MIMEText(text, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print('Email sent successfully')
    except Exception as e:
        print(f'Error sending email: {e}')

def get_data(tickers):
    """
    Function to retrieve stock data, compute sentiment score, and obtain other metrics.
    """
    sender_email = ""  # Sender's email
    receiver_email = ""  # Receiver's email
    password = ""  # Sender's email password

    for stock in tickers:
        try:
            # Retrieve stock data
            df = pdr.get_data_yahoo(stock, start_date, end_date)
            print(f'Retrieving data for {stock}')

            # Compute current price
            price = round(df['Adj Close'][-1], 2)

            # Retrieve and process news data
            finviz_url = 'https://finviz.com/quote.ashx?t='
            req = Request(url=finviz_url + stock, headers={'user-agent': 'Mozilla/5.0'})
            response = urlopen(req).read()
            html = BeautifulSoup(response, "html.parser")
            news_df = pd.read_html(str(html), attrs={'id': 'news-table'})[0]
            news_df.columns = ['datetime', 'headline']
            news_df['date'] = pd.to_datetime(news_df['datetime'].str.split(' ').str[0], errors='coerce')
            news_df['date'] = news_df['date'].fillna(method='ffill')
            news_df['time'] = news_df['datetime'].str.split(' ').str[-1]
            news_df['ticker'] = stock

            # Sentiment Analysis
            vader = SentimentIntensityAnalyzer()
            news_df['sentiment'] = news_df['headline'].apply(lambda x: vader.polarity_scores(x)['compound'])
            sentiment = round(news_df['sentiment'].mean(), 2)

            # RSI Calculation
            df["rsi"] = ta.RSI(df["Adj Close"])
            rsi = round(df["rsi"].tail(14).mean(), 2)

            # Prepare and send message
            output = f"\nTicker: {stock}\nCurrent Price: {price}\nNews Sentiment: {sentiment}\nRSI: {rsi}"
            send_message(output, sender_email, receiver_email, password)

        except Exception as e:
            print(f'Error processing data for {stock}: {e}')

if __name__ == '__main__':
    get_data(tickers)
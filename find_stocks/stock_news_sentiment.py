# Import necessary libraries
import pandas as pd
from urllib.request import Request, urlopen
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from datetime import datetime

# Download necessary NLTK data
nltk.download('vader_lexicon')

# Define parameters
num_headlines = 3  # Number of article headlines displayed per ticker
tickers = ['AAPL', 'TSLA', 'AMZN']  # List of tickers to analyze

# Initialize SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()

# Function to fetch and process news data
def fetch_news(ticker):
    finviz_url = 'https://finviz.com/quote.ashx?t='
    url = finviz_url + ticker
    req = Request(url=url, headers={'user-agent': 'Mozilla/5.0'})
    response = urlopen(req)
    df = pd.read_html(response.read(), attrs={'id': 'news-table'})[0]
    df.columns = ['Datetime', 'Headline']
    return df.head(num_headlines)

# Function to perform sentiment analysis
def sentiment_analysis(df):
    df['Sentiment'] = df['Headline'].apply(lambda x: analyzer.polarity_scores(x)['compound'])
    return df

# Process and analyze news for each ticker
for ticker in tickers:
    news_df = fetch_news(ticker)
    news_df['Ticker'] = ticker
    sentiment_df = sentiment_analysis(news_df)
    print('\nRecent News Headlines and Sentiment for {}: '.format(ticker))
    print(sentiment_df)

# Group news by ticker and calculate mean sentiment for each
mean_sentiments = {ticker: sentiment_analysis(fetch_news(ticker))['Sentiment'].mean() for ticker in tickers}

# Create and display dataframe of tickers with mean sentiment scores
sentiments_df = pd.DataFrame(list(mean_sentiments.items()), columns=['Ticker', 'Mean Sentiment'])
sentiments_df = sentiments_df.set_index('Ticker').sort_values('Mean Sentiment', ascending=False)
print('\nMean Sentiment Scores for Each Ticker:')
print(sentiments_df)
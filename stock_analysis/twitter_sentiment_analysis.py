# Import dependencies
import re
import csv
import time
import tweepy
import requests
import numpy as np
import pandas as pd
import seaborn as sns

# Importing twitter_api() function from config.py which contains the API keys
from config import twitter_api

# Importing libraries required for text analysis and visualization
import matplotlib.pyplot as plt
from googletrans import Translator
from wordcloud import WordCloud, STOPWORDS
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Retrieve the API keys and access tokens from config.py
consumer_key, consumer_secret, access_token, access_token_secret = twitter_api()

# Create an instance of SentimentIntensityAnalyzer and Translator
analyser = SentimentIntensityAnalyzer()
translator = Translator()

# Prompt user to input a stock symbol
stock = input("Enter a stock: ")

# Define a function to get the name of a stock from its symbol using Yahoo Finance API
def get_symbol(symbol):
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(symbol)
    result = requests.get(url).json()
    for x in result['ResultSet']['Result']:
        if x['symbol'] == symbol:
            return x['name']
            
# Get the name of the company corresponding to the stock symbol
company_name = get_symbol(stock.upper())

# Define a function to generate word cloud from a list of words
def word_cloud(wd_list):
    stopwords = set(STOPWORDS)
    all_words = ' '.join([text for text in wd_list])
    wordcloud = WordCloud(
        background_color='white',
        stopwords=stopwords,
        width=1600,
        height=800,
        random_state=21,
        colormap='jet',
        max_words=50,
        max_font_size=200).generate(all_words)

    plt.figure(figsize=(15, 10))
    plt.axis('off')
    plt.imshow(wordcloud, interpolation="bilinear");

# Define a function to calculate sentiment score using VADER sentiment analyzer
def sentiment_analyzer_scores(text, engl=True):
    if engl:
        trans = text
    else:
        trans = translator.translate(text).text

    score = analyser.polarity_scores(trans)
    lb = score['compound']
    if lb >= 0.05:
        return 1
    elif (lb > -0.05) and (lb < 0.05):
        return 0
    else:
        return -1

# Authenticate with Twitter API using the API keys and access tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Define a Twitter user_id to fetch tweets from and display the latest 3 tweets
user_id = 'Benzinga'
print ('-' * 50)
print (f'{user_id}')
tweets = api.user_timeline(user_id, count=3, tweet_mode='extended')
for t in tweets:
    print(t.full_text)
    print()

# Define a function to retrieve the latest tweets from a Twitter user
def list_tweets(username, count, prt=False):
    tweets = api.user_timeline("@" + username, count=count, tweet_mode='extended')
    tw = []
    for t in tweets:
        tw.append(t.full_text)
        if prt:
            print(t.full_text)
            print()
    return tw

def remove_pattern(input_txt, pattern):
    """Remove a pattern from a string."""
    r = re.findall(pattern, input_txt)
    for i in r:
        input_txt = re.sub(i, '', input_txt)        
    return input_txt 

def clean_tweets(lst):
    """Clean a list of tweets by removing special characters, URLs, and Twitter handles."""
    # Remove Twitter Return handles (RT @xxx:)
    lst = np.vectorize(remove_pattern)(lst, "RT @[\w]*:")
    # Remove Twitter handles (@xxx)
    lst = np.vectorize(remove_pattern)(lst, "@[\w]*")
    # Remove URL links (httpxxx)
    lst = np.vectorize(remove_pattern)(lst, "https?://[A-Za-z0-9./]*")
    # Remove special characters, numbers, punctuations (except for #)
    lst = np.core.defchararray.replace(lst, "[^a-zA-Z#]", " ")
    return lst

def sentiment_analyzer_scores(sentence, engl=True):
    """Analyze the sentiment of a sentence using VADER."""
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    sid = SentimentIntensityAnalyzer()
    if engl:
        trans = str.maketrans("", "", string.punctuation)
        sentence = sentence.translate(trans)
    return sid.polarity_scores(sentence)

def anl_tweets(lst, title='Tweets Sentiment', engl=True ):
    """Analyze the sentiment of a list of tweets and plot a histogram."""
    sents = []
    for tw in lst:
        try:
            st = sentiment_analyzer_scores(tw, engl)
            sents.append(st['compound'])
        except:
            sents.append(0)
    plt.rcParams['figure.figsize'] = (15, 10)
    ax = sns.distplot(sents, kde=False, bins=3)
    ax.set(xlabel='Negative                Neutral                 Positive',
            ylabel='#Tweets',
            title="Tweets of @" + title)
    return sents

def twitter_stream_listener(file_name, filter_track, follow=None, locations=None, languages=None, time_limit=20):
    """Stream tweets containing a specified keyword"""
    class CustomStreamListener(tweepy.StreamListener):
        def __init__(self, time_limit):
            self.start_time = time.time()
            self.limit = time_limit
            super(CustomStreamListener, self).__init__()

        def on_status(self, status):
            if (time.time() - self.start_time) < self.limit:
                print(".", end="")
                # Writing status data
                with open(file_name, 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        status.author.screen_name, status.created_at,
                        status.text
                    ])
            else:
                print("\n\n[INFO] Closing file and ending streaming")
                return False

        def on_error(self, status_code):
            if status_code == 420:
                print('Encountered error code 420. Disconnecting the stream')
                # returning False in on_data disconnects the stream
                return False
            else:
                print('Encountered error with status code: {}'.format(
                    status_code))
                return True  # Don't kill the stream

        def on_timeout(self):
            print('Timeout...')
            return True  # Don't kill the stream

    # Writing csv titles
    print(
        '\n[INFO] Open file: [{}] and starting {} seconds of streaming for {}\n'
        .format(file_name, time_limit, filter_track))
    with open(file_name, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['author', 'date', 'text'])

    streamingAPI = tweepy.streaming.Stream(
        auth, CustomStreamListener(time_limit=time_limit))
    streamingAPI.filter(
        track=filter_track,
        follow=follow,
        locations=locations,
        languages=languages,
    )
    f.close()

# Call twitter stream listener
filter_track = [stock, company_name, company_name.split()[0]]
file_name = f'{stock}_twitter.csv'
twitter_stream_listener(file_name, filter_track, time_limit=60)

# Get shape of dataframe
df_tws = pd.read_csv(file_name)
print(df_tws.shape)

# Print first few rows of dataframe
df_tws['text'] =  clean_tweets(df_tws['text'])
df_tws['sent'] = anl_tweets(df_tws.text)
print(df_tws.head())

# Words in positive tweets
tws_pos = df_tws['text'][df_tws['sent'] == 1]
print (tws_pos)

# Words in negative tweets
tws_neg = df_tws['text'][df_tws['sent'] == -1]
print (tws_neg)
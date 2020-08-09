import re
import sys
import csv
import time
import nltk
import tweepy
import requests
import warnings 
import numpy as np
import pandas as pd
import seaborn as sns
from config import twitter_api
import matplotlib.pyplot as plt
from googletrans import Translator
from wordcloud import WordCloud, STOPWORDS
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

consumer_key, consumer_secret, access_token, access_token_secret = twitter_api()
warnings.filterwarnings("ignore", category=DeprecationWarning)
analyser = SentimentIntensityAnalyzer()
translator = Translator()

stock = input("Enter a stock: ")
def get_symbol(symbol):
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(symbol)
    result = requests.get(url).json()
    for x in result['ResultSet']['Result']:
        if x['symbol'] == symbol:
            return x['name']
company_name = get_symbol(stock.upper())

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

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

user_id = 'Benzinga'
print ('-' * 50)
print (f'{user_id}')
tweets = api.user_timeline(user_id, count=3, tweet_mode='extended')
for t in tweets:
    print(t.full_text)
    print()

def list_tweets(user_id, count, prt=False):
    tweets = api.user_timeline(
        "@" + user_id, count=count, tweet_mode='extended')
    tw = []
    for t in tweets:
        tw.append(t.full_text)
        if prt:
            print(t.full_text)
            print()
    return tw

user_id = 'Stocktwits' 
count=20

print ('-' * 50)
print (f'{user_id}')
tw = list_tweets(user_id, count)
print('Latest Tweet: ' + tw[0])

def remove_pattern(input_txt, pattern):
    r = re.findall(pattern, input_txt)
    for i in r:
        input_txt = re.sub(i, '', input_txt)        
    return input_txt 

def clean_tweets(lst):
    # remove twitter Return handles (RT @xxx:)
    lst = np.vectorize(remove_pattern)(lst, "RT @[\w]*:")
    # remove twitter handles (@xxx)
    lst = np.vectorize(remove_pattern)(lst, "@[\w]*")
    # remove URL links (httpxxx)
    lst = np.vectorize(remove_pattern)(lst, "https?://[A-Za-z0-9./]*")
    # remove special characters, numbers, punctuations (except for #)
    lst = np.core.defchararray.replace(lst, "[^a-zA-Z#]", " ")
    return lst

tw = clean_tweets(tw)
print('Latest Tweet (cleaned): ' + tw[0])
print('Latest Tweet (sentiment): ' + str(sentiment_analyzer_scores(tw[0])))

def anl_tweets(lst, title='Tweets Sentiment', engl=True ):
    sents = []
    for tw in lst:
        try:
            st = sentiment_analyzer_scores(tw, engl)
            sents.append(st)
        except:
            sents.append(0)
    plt.rcParams['figure.figsize'] = (15, 10)
    ax = sns.distplot(
        sents,
        kde=False,
        bins=3)
    ax.set(xlabel='Negative                Neutral                 Positive',
            ylabel='#Tweets',
          title="Tweets of @"+title)
    return sents

tw_sent = anl_tweets(tw, user_id)
# word_cloud(tw)

user_id = 'CNBC' 
print ('-' * 50)
print (f'{user_id}')
tw2 = list_tweets(user_id, count)
tw2 = clean_tweets(tw2)
tw2_sent = anl_tweets(tw2, user_id)
print('Latest Tweet (cleaned): ' + tw2[0])
print('Latest Tweet (sentiment): ' + str(sentiment_analyzer_scores(tw2[0])))
# word_cloud(tw2)

print ('-' * 50)
def twitter_stream_listener(file_name,
                            filter_track,
                            follow=['@CNBC', '@Benzinga', '@Stocktwits', '@BreakoutStocks', '@bespokeinvest', '@WSJmarkets', '@Stephanie_Link', '@nytimesbusiness', '@IBDinvestors', '@WSJDealJournal'],
                            locations=None,
                            languages=None,
                            time_limit=20):
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

filter_track = [stock, company_name, company_name.split()[0]]#, 'breakout', 'drawback', 'indicator', 'ratio']
file_name = f'/Users/shashank/Documents/Code/Python/Outputs/stock_tweets/{stock}_twitter.csv'
twitter_stream_listener (file_name, filter_track, time_limit=60)

df_tws = pd.read_csv(file_name)
print(df_tws.shape)

df_tws['text'] =  clean_tweets(df_tws['text'])
df_tws['sent'] = anl_tweets(df_tws.text)
print(df_tws.head())

# word_cloud(df_tws.text)

# Words in positive tweets
tws_pos = df_tws['text'][df_tws['sent'] == 1]
# word_cloud(tws_pos)

# Words in negative tweets
tws_pos = df_tws['text'][df_tws['sent'] == -1]
# word_cloud(tws_pos)
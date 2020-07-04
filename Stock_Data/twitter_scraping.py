# Twitter Library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import config
from twython import Twython

class StdOutListener(StreamListener):
    def on_data(self, data):
        print(data)
        return True

    def on_error(self, status):
        print(status)

if __name__ == '__main__':
    # Twitter authetification and connection to Twiter Streaming API
    l = StdOutListener()
    auth = OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
    auth.set_access_token(twitter_access_key, twitter_access_secret)
    stream = Stream(auth, l)

    # Twitter Streams to capture data Keywords
    stream.filter(track=['NIO', 'TSLA', 'AAPL', 'FB', 'Tesla Inc.', 'Apple', 'Facebook'])
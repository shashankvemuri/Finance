from textblob import TextBlob
import numpy as np
import requests
import pandas as pd
import nltk
demo = 'your api key'
#nltk.download('punkt')
company = 'AAPL'

transcript = requests.get(f'https://financialmodelingprep.com/api/v3/earning_call_transcript/{company}?quarter=3&year=2020&apikey={demo}').json()

transcript = transcript[0]['content']
print(transcript)

sentiment_call = TextBlob(transcript)

print(sentiment_call.sentiment)
print(sentiment_call.sentences)

sentiment_call.sentences
negative = 0
positive = 0
neutral = 0
all_sentences = []

for sentence in sentiment_call.sentences:
  #print(sentence.sentiment.polarity)
  if sentence.sentiment.polarity < 0:
    negative +=1
  if sentence.sentiment.polarity > 0:
    positive += 1
  else:
    neutral += 1
 
  all_sentences.append(sentence.sentiment.polarity) 

print('positive: ' +  str(positive))
print('negative: ' +  str(negative))
print('neutral: ' + str(neutral))

all_sentences = np.array(all_sentences)
print('sentence polarity: ' + str(all_sentences.mean()))

for sentence in sentiment_call.sentences:
  if sentence.sentiment.polarity > 0.8:
     print(sentence)
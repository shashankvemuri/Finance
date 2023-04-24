# Import necessary packages
from textblob import TextBlob
import numpy as np
import requests
import pandas as pd
import nltk

# Set API key and company
demo = 'your api key'
company = 'AAPL'

# Get earnings call transcript from API
transcript = requests.get(f'https://financialmodelingprep.com/api/v3/earning_call_transcript/{company}?quarter=3&year=2020&apikey={demo}').json()

# Extract transcript content
transcript = transcript[0]['content']

# Print the transcript content
print(transcript)

# Create a TextBlob object to perform sentiment analysis on transcript
sentiment_call = TextBlob(transcript)

# Print overall sentiment of the transcript
print(sentiment_call.sentiment)

# Print all the individual sentences in the transcript
print(sentiment_call.sentences)

# Perform sentiment analysis on each sentence in the transcript
negative = 0
positive = 0
neutral = 0
all_sentences = []

for sentence in sentiment_call.sentences:
    # Print sentence sentiment polarity (for debugging purposes)
    # print(sentence.sentiment.polarity)
    
    # Count number of negative, positive, and neutral sentences
    if sentence.sentiment.polarity < 0:
        negative +=1
    elif sentence.sentiment.polarity > 0:
        positive += 1
    else:
        neutral += 1
    
    # Append sentence polarity to all_sentences list
    all_sentences.append(sentence.sentiment.polarity) 

# Print number of negative, positive, and neutral sentences
print('positive: ' +  str(positive))
print('negative: ' +  str(negative))
print('neutral: ' + str(neutral))

# Print the mean sentence polarity
all_sentences = np.array(all_sentences)
print('sentence polarity: ' + str(all_sentences.mean()))

# Print sentences with very positive sentiment polarity
for sentence in sentiment_call.sentences:
    if sentence.sentiment.polarity > 0.8:
        print(sentence)